# Cleo Deployment Runbook

End-to-end: clean Mac Studio → Cleo running 24/7 under launchd. ~60–90 min if nothing goes sideways.

> Before you start: this scaffold has not been smoke-tested against the live `claude-agent-sdk`. Verify the SDK import path and `ClaudeAgentOptions` signature in step 4 (smoke test) before installing launchd jobs. If the SDK has renamed `can_use_tool` or `mcp_servers`, fix `agent.py` and `permissions.py` accordingly — everything else is plain Python.

---

## 0. Prerequisites on the Mac Studio

- macOS with Python 3.11+ (`brew install python@3.11` if needed)
- Node.js ≥ 22 or Bun ≥ 1.0 (for `qmd`)
- The Obsidian vault on disk at a known path
- The existing `brain` MCP server (`python -m brain.mcp_server`) reachable from the venv — either pip-install it or vendor it under `cleo/`
- BlueBubbles server already running locally (separate setup; see https://bluebubbles.app)
- Discord bot token from OpenClaw secrets (`discord/existing-setup.md`)
- Anthropic API key

---

## 1. Pull and install

```bash
cd ~/code   # or wherever you keep services
git clone <repo-url> household-manager-setup
cd household-manager-setup/cleo

python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .

mkdir -p logs
cp .env.example .env
```

Don't fill `.env` yet — we need a few IDs first.

---

## 1b. Install and prime qmd

Cleo uses [qmd](https://github.com/tobi/qmd) as its primary vault search backend (local hybrid BM25 + vector + LLM rerank).

```bash
# Install globally
npm install -g @tobilu/qmd   # or: bun install -g @tobilu/qmd

# Verify
qmd --version
which qmd                    # capture this path → QMD_BIN in .env if not on $PATH

# Point qmd at the Obsidian vault. The collection name "vault" is what
# Cleo's QMD_COLLECTION env var defaults to.
qmd collection add "$OBSIDIAN_VAULT" --name vault
qmd context add qmd://vault "Household Obsidian vault — notes, daily, projects, people"

# Build the initial index. First run downloads ~2GB of GGUF models and
# embeds the vault — expect 5-30 minutes depending on vault size.
qmd embed

# Sanity-check
qmd query "test query that should match something in your vault"
qmd status
```

`qmd_reindex.py` keeps the index fresh hourly under launchd; the initial run above is the only manual step.

If you don't want qmd (yet), set `QMD_ENABLED=false` in `.env` and skip this section — Cleo falls back to `brain` MCP for search.

---

## 2. Collect the IDs you need

### Discord IDs

In Discord client: **Settings → Advanced → Developer Mode** → ON. Then right-click anything to "Copy ID".

You need:
- **Bot token**: from OpenClaw secrets, or regenerate at https://discord.com/developers (Application → Bot → Reset Token). The token in `discord/existing-setup.md` decodes to bot user ID `1477089950099832973`.
- **Guild ID**: `1477094930647355626` (already known)
- **Trusted user IDs**: right-click Lesley and Greg's Discord names → Copy ID. Comma-separate.
- **Nanny channel IDs**: right-click each nanny-visible channel → Copy ID. Comma-separate.
- **Webhook URLs** for `#daily-brief` and `#cleo-log`: Channel settings → Integrations → Webhooks → New Webhook → Copy URL.

### iMessage handles

The handle BlueBubbles uses is the email or phone number on the iMessage account. Check the BlueBubbles app's "Contacts" / message history for the canonical form Lesley and Greg appear as. Comma-separate.

### Bot intents

Make sure the Discord application has these privileged intents enabled at https://discord.com/developers (Application → Bot):
- **Message Content Intent** (required — `discord_handler.py` reads `message.clean_content`)
- Server Members Intent and Presence are not required.

---

## 3. Fill `.env`

```bash
$EDITOR .env
```

Fill every variable from step 2. Double-check:
- No trailing spaces in comma-separated lists
- `OBSIDIAN_VAULT` is the *absolute* path
- `BRAIN_MCP_CMD` and `BRAIN_MCP_ARGS` actually launch the MCP server (`python -c "import brain.mcp_server"` should succeed in the venv)

---

## 4. Smoke test (do not skip)

Verify the agent loop works before installing launchd jobs.

```bash
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)

# 1. One-shot pipeline (no Discord/iMessage involvement)
python -m cleo.scheduled.morning_brief
# Expect: a markdown brief printed to stdout (webhook posts only if URL is set).
# If you get an ImportError on claude_agent_sdk, check the SDK version + import paths.

# 2. Discord bot, foreground
python -m cleo.discord_handler
# Expect: "Cleo online as <bot>" in logs.
# In Discord, @mention the bot in a non-nanny channel: "@Cleo what's in my vault about X?"
# She should reply within a few seconds and remember context across follow-up messages.
# Ctrl-C to stop.

# 3. iMessage bridge, foreground
python -m cleo.imessage_handler
# Expect: "iMessage bridge listening on 127.0.0.1:8787"
# Configure BlueBubbles to POST new-message webhooks to http://127.0.0.1:8787/webhook
# (BlueBubbles app → Settings → Webhooks → Add). Send yourself an iMessage; she should reply.
# Ctrl-C to stop.
```

If any step fails, fix locally before continuing. **Do not install launchd until all three smoke tests pass.**

---

## 5. Install launchd jobs

Substitute the absolute paths into the plists, then bootstrap them.

```bash
CLEO_DIR=$PWD
CLEO_PY=$PWD/.venv/bin/python

# Substitute placeholders into the staged plists. Write into ~/Library/LaunchAgents.
mkdir -p ~/Library/LaunchAgents
for plist in launchd/*.plist; do
  out=~/Library/LaunchAgents/$(basename "$plist")
  sed -e "s|__CLEO_DIR__|$CLEO_DIR|g" -e "s|__PYTHON__|$CLEO_PY|g" "$plist" > "$out"
done

# Load each one
for label in com.cleo.discord com.cleo.imessage com.cleo.morning-brief \
             com.cleo.inbox-triage com.cleo.vault-health com.cleo.knowledge-graph \
             com.cleo.qmd-reindex; do
  launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/$label.plist
done

# Verify they're loaded
launchctl list | grep com.cleo
```

The two long-running services (`com.cleo.discord`, `com.cleo.imessage`) start immediately. The four pipelines fire on their schedule (see plist `StartCalendarInterval`).

---

## 6. Verify it's actually working

```bash
# Live tail the bot logs
tail -f logs/discord.err.log logs/discord.out.log

# Trigger a pipeline manually to confirm it runs end-to-end under launchd
launchctl kickstart -p gui/$(id -u)/com.cleo.morning-brief
tail -f logs/morning-brief.err.log

# Sanity-check launchd's view of each job
for label in discord imessage morning-brief inbox-triage vault-health knowledge-graph qmd-reindex; do
  launchctl print gui/$(id -u)/com.cleo.$label | grep -E '(state|last exit|pid)' | head -3
  echo "---"
done
```

Healthy state: long-running services show `state = running`, pipelines show `last exit code = 0` after a manual kickstart.

---

## 7. Cut over from OpenClaw

Once Cleo's running cleanly under launchd:

1. **Pick one channel** as the cutover canary (e.g. `#cleo-log`). Run both Cleo and OpenClaw side by side; verify Cleo's behaviour for a day.
2. **Disable OpenClaw's Discord routing** — but keep OpenClaw running so you can roll back.
3. **Watch for a few days.** If conversation continuity, persona switching, or pipelines drift, fix locally and reload only the affected job (`launchctl bootout … && launchctl bootstrap …`).
4. **Decommission OpenClaw** once you've gone a week without a fallback need.

---

## 8. Rollback

Each piece is independently reversible.

```bash
# Stop a single job
launchctl bootout gui/$(id -u)/com.cleo.discord

# Stop everything
for label in discord imessage morning-brief inbox-triage vault-health knowledge-graph qmd-reindex; do
  launchctl bootout gui/$(id -u)/com.cleo.$label || true
done

# Re-enable OpenClaw's Discord integration
# (whatever the OpenClaw command for that is)
```

If you need to debug a stuck job, `launchctl print gui/$(id -u)/com.cleo.<label>` shows full state including last exit code, throttle status, and out/err paths.

---

## 9. Operating the running system

**Where to look when something's off:**
- `logs/<service>.err.log` — exceptions, agent-loop failures
- `logs/<service>.out.log` — normal operation
- `launchctl print gui/$(id -u)/com.cleo.<label>` — launchd's view (last exit, throttle, pid)

**Common tweaks** (no code change needed):
- Persona/voice → edit `prompts/cleo-system.md` or `prompts/cleo-nanny-mode.md`. Discord bot picks it up on next session (or `/reset` in a channel).
- Add a trusted user → append their ID to `TRUSTED_DISCORD_IDS` in `.env`, then `launchctl kickstart -k gui/$(id -u)/com.cleo.discord`.
- Pipeline schedule → edit the relevant plist in `~/Library/LaunchAgents/`, then `launchctl bootout && bootstrap` it.

**Code changes:**
- `git pull && pip install -e . && launchctl kickstart -k gui/$(id -u)/com.cleo.<label>` for any service that needs the new code.

**Cost watch:**
- `logs/*.err.log` will surface 429/quota errors loudly.
- For per-call cost visibility, instrument `agent.py:run_one_shot` to log token usage from the `result` event before shipping prompt-caching.
