# Gresley Home Discord Server: Household Communication Hub

## 1. Executive Summary

Moving the Gresley household's primary communication from iMessage to Discord gives you organized channels, granular permissions, bot automation, and clean separation between family conversations and employee coordination -- all things iMessage fundamentally cannot do.

**The core insight:** Discord is not replacing iMessage entirely. It is becoming the **structured command center** for the household, while iMessage remains the **quick-text fallback** for urgent/personal messages between Lesley, Greg, and Genn. Think of Discord as the household intranet and iMessage as the walkie-talkie.

**What this buys you:**
- Nannies get exactly the information they need (schedules, kids info, emergency contacts) without seeing family finances, personal conversations, or Cleo's full capabilities
- Clean offboarding when a nanny leaves (kick from server, done)
- Cleo can post automated feeds (morning briefs, calendar updates, task reminders) without cluttering anyone's text messages
- Searchable history organized by topic, not one endless scroll
- Different notification levels per channel (urgent alerts ping everyone; grocery lists don't)

**Timeline:** 1-2 weeks for setup and migration. Greg handles technical setup. Lesley and Genn onboard first (Week 1). Crystal onboards next (Week 1-2). Morning nannies join last (Week 2+).

---

## 2. Recommended Channel Structure

```
GRESLEY HOME (Server)
│
├── 📋 INFO (Category) ─────────────── Visible to: Everyone
│   ├── #welcome                       Server rules, who's who, how to use this
│   ├── #emergency-contacts            Pediatrician, poison control, addresses, allergies
│   └── #house-rules                   Wi-Fi password, alarm codes, parking, deliveries
│
├── 👨‍👩‍👧‍👦 FAMILY (Category) ──────────── Visible to: Family role only
│   ├── #family-chat                   General family conversation (replaces iMessage group)
│   ├── #family-planning               Vacations, events, big decisions, extended family
│   └── #random                        Memes, links, fun stuff, Titan photos
│
├── 👶 KIDS (Category) ─────────────── Visible to: Family + All Nannies
│   ├── #mira                          Mira-specific updates, milestones, school stuff
│   ├── #reya                          Reya-specific updates, milestones
│   ├── #kids-daily-log                Daily handoff notes: meals, naps, moods, incidents
│   └── #kids-photos                   Photo/video sharing of the girls
│
├── 📅 HOUSEHOLD OPS (Category) ────── Visible to: Family + All Nannies
│   ├── #schedule                      Weekly nanny schedule, shift changes, time-off requests
│   ├── #grocery-shopping              Lists, Instacart orders, pantry needs
│   ├── #house-maintenance             Repairs, cleaners (Monday), electrician visits
│   └── #meal-planning                 Meal ideas, kids food prep, dietary notes
│
├── 🤖 CLEO (Category) ─────────────── Visible to: Family only
│   ├── #cleo-morning-brief            Automated daily briefing (read-only for humans)
│   ├── #cleo-alerts                   Calendar reminders, urgent notifications
│   ├── #cleo-commands                 Slash commands and interactive requests
│   └── #cleo-logs                     Automated activity log (muted by default)
│
├── 💰 PRIVATE (Category) ──────────── Visible to: Lesley + Greg only
│   ├── #finances                      Budget, bills, investments, nanny payroll
│   ├── #private-chat                  Couple-only conversation
│   └── #cleo-private                  Cleo tasks involving sensitive info
│
├── 🏢 NANNY HUB (Category) ────────── Visible to: Family + All Nannies
│   ├── #nanny-announcements           One-way: family posts, nannies read (read-only)
│   └── #nanny-questions               Nannies can ask questions, report issues
│
└── 🔧 ADMIN (Category) ────────────── Visible to: Greg only
    └── #bot-testing                   Cleo dev/testing, webhook debugging
```

### Design Principles

1. **Default-deny for nannies.** Nannies see only the categories explicitly granted to them.
2. **Family chat replaces the iMessage group.** `#family-chat` is the new inner circle.
3. **Kids category is shared.** Both family and nannies need this for handoffs.
4. **Cleo's automated feeds are separated** from human conversation to avoid noise.
5. **Private category** is invisible to everyone except Lesley and Greg -- not even Genn.
6. **Nanny Hub** gives nannies a clear place to ask questions without texting individuals.
7. **Keep it lean.** Start with these channels. Add more only when a real need emerges.

---

## 3. Role and Permission Matrix

### Roles (highest to lowest priority)

| Role | Color | Members | Purpose |
|------|-------|---------|---------|
| `Admin` | Red | Greg | Full server control, bot testing |
| `Parents` | Gold | Lesley, Greg | Access to Private/finances category |
| `Family` | Green | Lesley, Greg, Genn | All family channels |
| `Nanny-Senior` | Blue | Crystal | Extended nanny access |
| `Nanny` | Teal | Sophia, Ashlee, Maddie | Basic nanny access |
| `Bot` | Purple | Cleo | Posting access everywhere |
| `@everyone` | -- | All | Baseline: can see only INFO category |

### Permission Matrix

| Category | @everyone | Family | Parents | Nanny-Senior | Nanny | Bot |
|----------|-----------|--------|---------|--------------|-------|-----|
| INFO | View, Read | View, Read, Write | View, Read, Write | View, Read | View, Read | Write |
| FAMILY | **Denied** | View, Read, Write | View, Read, Write | -- | -- | Write |
| KIDS | **Denied** | View, Read, Write | View, Read, Write | View, Read, Write | View, Read, Write | Write |
| HOUSEHOLD OPS | **Denied** | View, Read, Write | View, Read, Write | View, Read, Write | View, Read, Write | Write |
| CLEO | **Denied** | View, Read | View, Read | -- | -- | Write |
| PRIVATE | **Denied** | **Denied** | View, Read, Write | -- | -- | Write |
| NANNY HUB | **Denied** | View, Read, Write | View, Read, Write | View, Read | View, Read | Write |
| ADMIN | **Denied** | -- | -- | -- | -- | Write |

### Setup Steps

1. **@everyone role**: Deny "View Channels" globally (makes server default-closed)
2. **Per category**: Add role overrides granting View Channel to appropriate roles
3. **PRIVATE category**: Add explicit Deny for Family role, explicit Allow for Parents role (Genn has Family but not Parents)
4. **#nanny-announcements**: Nanny roles get View but Deny Send Messages (read-only)
5. **#cleo-morning-brief, #cleo-logs**: Family gets View but Deny Send Messages (read-only, bot posts only)
6. **Bot role**: Grant View Channels, Send Messages, Embed Links, Attach Files, Read History, Add Reactions, Manage Messages, Use Application Commands. Do NOT give Administrator.

### Testing Permissions

After setup, go to Server Settings > Roles > select a role > "View Server As Role" and verify each role sees only what it should. Do this for every role before inviting anyone.

---

## 4. Onboarding Playbook

### Phase 1: Greg Sets Up (Day 1)
- [ ] Create all roles
- [ ] Create all categories and channels
- [ ] Set all permissions per the matrix
- [ ] Assign himself Admin + Parents + Family
- [ ] Configure server settings (Section 7)
- [ ] Test with "View Server As Role" for every role
- [ ] Set up Cleo's bot role and permissions

### Phase 2: Lesley (Day 1-2)

1. Greg generates a **permanent, single-use invite link**
2. Texts it to Lesley on iMessage: "Here's the invite to our household Discord. Download the app first."
3. Lesley downloads Discord, creates account, taps invite link
4. Greg assigns `Parents` and `Family` roles

**First 5 minutes together (in person):**
- Walk through the channel list
- Set notification preferences:
  - Server-level: **Only @mentions**
  - Mute: #cleo-logs
  - Unmute: #family-chat, #cleo-alerts, #schedule
  - Suppress @everyone and @here
- Show long-press to mute/unmute channels
- Pin the server so it's at the top of the server list

### Phase 3: Genn (Day 2-4)

**The pitch:** "You can see everything family-related, organized by topic, and nothing gets lost in a wall of texts."

1. Explain the move in person or on iMessage
2. Send permanent, single-use invite link
3. Assign `Family` role (not Parents -- she shouldn't see finances)
4. Same notification setup as Lesley

**If she resists:**
- "I don't want another app" → It replaces the group chat, not adds to it
- "Discord is for gamers" → Show her the app. It's been repositioned for communities
- "I'll miss iMessage" → Reactions work, photos work, calls work. Only Siri is lost

**Be upfront about the private channel:** "There's a private channel for Lesley and Greg's finances -- that's the only thing you can't see. Everything else family-related is open to you." Transparency prevents the structure from feeling opaque.

### Phase 4: Crystal (Day 5-7)

**The tone:** Professional but friendly. This is an employer-employee channel.

1. Tell Crystal in person: "We're setting up a Discord server for household coordination. It'll have the kids' schedule, daily logs, emergency contacts, and a place to ask questions."
2. Generate a **permanent, single-use** invite link (she's long-term staff)
3. Help her download and set up if needed
4. Assign `Nanny-Senior` and `Nanny` roles

**Crystal's notification setup:**
- Server-level: Only @mentions
- Unmute: #schedule, #nanny-announcements, #kids-daily-log
- Everything else muted (she won't see most channels anyway)

**What Crystal sees:** INFO, KIDS, HOUSEHOLD OPS, NANNY HUB. That's it.

### Phase 5: Morning Nannies (Week 2+)

1. Generate **expiring invite links** (7-day expiry, single-use) for each nanny as needed
2. Assign only the `Nanny` role
3. Give them this one-page guide:

```
Welcome to the Gresley Home Discord!

1. Download Discord (free) from the App Store
2. Create an account and tap the invite link we sent you

What you'll find:
- #schedule — Your shifts and any changes
- #kids-daily-log — Post updates during your shift
- #emergency-contacts — Pediatrician, poison control, addresses
- #nanny-questions — Ask us anything
- #nanny-announcements — Check here for updates from us

Notifications: Set the server to "Only @mentions" so you're
not pinged constantly. We'll @mention you for anything urgent.
```

---

## 5. iMessage Transition Plan

### What Stays on iMessage

| Use Case | Why |
|----------|-----|
| Urgent/emergency texts | Faster, guaranteed delivery, Siri |
| Quick 1:1 between Lesley and Greg | Habit, convenience |
| Extended family (Kaitlin, etc.) | They won't join Discord |
| Friends, external contacts | Not appropriate for household server |
| Cleo quick commands | Already works well |

### What Moves to Discord

| Use Case | Channel |
|----------|---------|
| Family group conversation | #family-chat |
| Nanny schedule coordination | #schedule |
| Kids daily updates/handoffs | #kids-daily-log |
| Grocery/shopping lists | #grocery-shopping |
| House maintenance tracking | #house-maintenance |
| Cleo automated feeds | #cleo-morning-brief, #cleo-alerts |
| Financial discussions | #finances |
| Nanny communication | #nanny-hub channels |

### Transition Timeline

**Week 1: Parallel.** Both iMessage group and Discord #family-chat are active. Start posting logistics in Discord.

**Week 2: Nudge.** When someone posts logistics in iMessage, redirect: "Hey, can you drop that in #schedule?" Cleo stops duplicating automated content to iMessage.

**Week 3+: Discord-primary.** Household logistics live on Discord. iMessage group still exists for quick personal messages but is naturally less active.

### Should Cleo Bridge Messages?

**No full bridge.** It defeats the purpose of organized channels and creates duplicate conversations.

**Instead, selective bridging:**
- Cleo forwards **urgent alerts** from Discord to iMessage (e.g., nanny posts something tagged urgent)
- Cleo responds to quick commands on **both** platforms (already does this)
- Cleo can post a **daily digest** to iMessage: "Here's what happened on Discord today" -- gives people a reason to check

---

## 6. Nanny Communication Guidelines

### Privacy Boundaries

**Nannies should NOT see:**
- Family personal conversations (#family-chat, #random, #family-planning)
- Financial information (#finances)
- Cleo's full capabilities (#cleo-commands, #cleo-logs, #cleo-morning-brief)
- Private couple conversations (#private-chat)

**To nannies, Cleo is "a household scheduling bot."** Not a sophisticated AI with broad access.

### Crystal vs Morning Nannies

Both get the same channel access for now. Crystal has `Nanny-Senior` role as a future hook if you want to:
- Give her access to #kids-photos
- Let her post in #nanny-announcements
- Create a #crystal-private channel for 1:1 with the family

### Offboarding a Nanny

1. Right-click name > Kick from Server (immediate, 10 seconds)
2. Server Settings > Invites > delete their invite link
3. Their past messages remain as useful history
4. Morning nannies' expiring invite links auto-invalidate

Discord's offboarding is far cleaner than iMessage -- no visible "X left the conversation" messages.

### Legal/HR Notes

- **Wage and hour:** If you require nannies to monitor Discord off-shift, that could be compensable time. Make clear: Discord is for **on-shift communication only**.
- **Employment agreement:** Add: "Household coordination is managed via Discord. You are expected to check relevant channels during your shift. You are not required to monitor Discord outside scheduled work hours."
- **Documentation:** Discord is timestamped and searchable -- great for incident logs, but careless messages are on the record. Keep nanny-visible channels professional.
- **Official records:** For termination, policy changes, or anything legally significant, use email or paper. Not Discord.

---

## 7. Server Settings Checklist

- [ ] **Server Name:** "Gresley Home"
- [ ] **Server Icon:** Warm, non-gaming image (family photo, house illustration)
- [ ] **Verification Level:** Low (requires verified email)
- [ ] **Explicit Content Filter:** Scan messages from all members
- [ ] **Default Notifications:** Only @mentions (critical -- prevents notification overload)
- [ ] **Community Server:** OFF (this is a private server)
- [ ] **2FA for Moderation:** ON (Greg should have 2FA on his account)
- [ ] **System Messages Channel:** #welcome
- [ ] **Server Discovery:** OFF
- [ ] Pin important messages in #emergency-contacts, #house-rules, #schedule

---

## 8. Cleo Integration Plan

### Channel Behavior

| Channel | Cleo's Behavior | Trigger |
|---------|-----------------|---------|
| #cleo-morning-brief | Automated daily post at 8am | Cron job |
| #cleo-alerts | Push notifications for calendar, deliveries, urgent emails | Event-driven |
| #cleo-commands | Interactive -- slash commands, buttons, natural language | User-initiated |
| #cleo-logs | Silent logging of all automated actions | Automated, muted |
| #cleo-private | Sensitive tasks for Lesley/Greg | User-initiated |
| #schedule | Weekly auto-post Sunday evening: coming week's nanny schedule | Scheduled |
| #grocery-shopping | On request -- build lists, check prices | User-initiated |
| #family-chat | Participates naturally (respond when asked, quiet otherwise) | Mentioned or relevant |
| #kids-daily-log | Does not auto-post. Reacts to nanny posts with acknowledgment | Passive |
| #nanny-announcements | Drafts for Lesley/Greg to approve. Does not post autonomously | User-initiated |
| Nanny-visible channels | Minimal. Simple scheduling bot persona, no personality quirks | Mentioned only |

### Preventing Noise

1. Automated posts go to dedicated channels only (#cleo-morning-brief, #cleo-alerts, #cleo-logs)
2. #cleo-logs is muted by default for all humans
3. Batch alerts instead of sending 5 separate pings
4. No automated posts 10pm-7am unless urgent
5. In #family-chat: participate, don't dominate. Use reactions.
6. In nanny channels: speak only when directly asked

### Cleo's Persona by Context

- **Family channels:** Full Cleo personality (lobster emoji, playful, opinionated)
- **Nanny channels:** Simple scheduling bot (straightforward, no personality quirks, no "Clawd" persona)

---

## 9. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Too many channels | Start with 17. Only add when a topic keeps cluttering an existing channel. |
| Notification overload drives people back to iMessage | Set server default to "Only @mentions." Walk each person through settings on Day 1. |
| Nobody checks Discord (iMessage habits) | Make Discord the **only** place certain info lives. If the nanny schedule is only on Discord, people will check it. |
| Nannies feel surveilled | Keep nanny channels simple and practical. Don't require Discord for things they handle fine via text. |
| Permission misconfiguration | Use "View Server As Role" to verify every role after setup. Check again whenever you add channels. |
| Cleo floods channels | Strict channel discipline. Automated content in dedicated channels only. |
| Forgetting to offboard a nanny | Add "remove from Discord" to your offboarding checklist. 10 seconds. |
| Bot token has too many permissions | Never give Administrator. Grant only specific permissions listed in Section 3. |
| Genn feels excluded from private channels | Be upfront: "Finances is the only thing you can't see." |
| Server becomes a ghost town | Cleo's daily morning brief gives everyone a reason to open the app every day. |

---

*Sources: How-To Geek family Discord guides, Discord Safety documentation, Discord Support (permissions, notifications, invites, verification), Pavillion Agency household staff communication guide, International Nanny Association communication resources.*
