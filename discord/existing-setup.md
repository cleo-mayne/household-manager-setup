# Existing Discord Setup

Greg already created a Discord server and configured Cleo as a bot. This documents what exists.

## Server

- **Guild ID**: `1477094930647355626`
- **Created by**: Greg
- **Status**: Server exists, bot was connected via OpenClaw

## Bot

- **Bot token**: Stored in OpenClaw secrets at `/discord_token`
  - Token prefix: `MTQ3NzA4OTk1MDA5OTgzMjk3Mw.GbToTw...`
  - This is a Discord bot token (the `MTQ3...` prefix is a base64-encoded bot user ID)
  - **Bot user ID** (decoded): `1477089950099832973`
- **Application**: Created in Discord Developer Portal (details TBD — Greg has access)

## Previous Configuration (OpenClaw)

```json
{
  "discord": {
    "enabled": true,
    "token": {"source": "file", "provider": "secrets", "id": "/discord_token"},
    "groupPolicy": "allowlist",
    "streaming": "off",
    "dmPolicy": "pairing",
    "guilds": {
      "1477094930647355626": {
        "requireMention": true
      }
    }
  }
}
```

### What the config means

- **groupPolicy: allowlist** — Bot only responds in explicitly allowed servers/channels
- **requireMention: true** — Bot only responds when @mentioned (not every message)
- **dmPolicy: pairing** — DMs require a prior interaction or explicit pairing
- **streaming: off** — No real-time token streaming in responses

## Security Hardening Notes

The security audit flagged the Discord multi-user context:
- OpenClaw detected multi-user setup but lacked proper isolation
- Recommendation was to restrict the discord-agent's tool access:
  - **Allow**: messaging profile tools
  - **Deny**: exec, process, browser, gateway, cron
- This ensures Cleo on Discord can send/receive messages but can't be tricked into running commands via Discord messages

## What Needs to Happen

1. Verify the Discord server still exists and bot token is still valid
2. Decide on channel structure (see integration-plan.md)
3. Connect Cleo's new second brain tools to Discord
4. Apply security restrictions for the Discord context
