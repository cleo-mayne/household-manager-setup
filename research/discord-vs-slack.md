# Discord vs Slack for Household AI Assistant: Deep Research Comparison

## 1. Executive Summary

**Discord wins for this use case, and it is not close.**

For a household AI assistant managing a family of two adults, a young child, and an AI agent, Discord is the clear choice. It offers a completely free tier with no message history limits, no integration caps, a mature bot ecosystem purpose-built for exactly this kind of always-on automation, and a casual atmosphere that fits a home (not an office). Slack's free tier is crippled by a 90-day message history deletion policy and a 10-integration cap that would strangle a serious home automation setup. Slack's strengths -- enterprise security, compliance, and business integrations -- are irrelevant to a household.

The one area where Slack genuinely excels -- its official MCP server with OAuth-scoped access and enterprise-grade AI agent support -- is impressive but overkill. Discord's community-built MCP servers and native bot framework get the job done for a personal setup without the enterprise overhead.

**Recommendation: Use Discord. Spend $0. Keep iMessage as the quick-command layer for Lesley and Greg, and use Discord as the rich dashboard/automation channel.**

---

## 2. Feature Comparison Table

| Dimension | Discord | Slack | Winner |
|---|---|---|---|
| **Cost (free tier)** | Fully free, no meaningful limits for this use case | Free but 90-day message deletion, 10 app cap, 5 GB storage | **Discord** |
| **Cost (paid)** | Nitro $9.99/mo (unnecessary) | Pro $7.25/user/mo = $14.50+/mo minimum | **Discord** |
| **Message history** | Unlimited, forever, free | 90 days on free; >1 year permanently deleted | **Discord** |
| **Bot framework** | Native, mature, well-documented, free | Native, mature, well-documented, free | Tie |
| **Webhook support** | Simple URL-based, 30 req/min, rich embeds | Simple URL-based, Block Kit, rich formatting | Tie |
| **Message formatting** | Markdown, embeds, Components V2 (buttons, selects) | mrkdwn, Block Kit (sections, headers, buttons, menus) | **Slack** (slightly) |
| **MCP server ecosystem** | Community-built (Composio, saseq/discord-mcp) | Official Slack MCP server (GA Feb 2026), enterprise-grade | **Slack** |
| **Media sharing** | Images, video, files; 25 MB free, 500 MB with Nitro | Images, video, files; 5 GB total on free tier | **Discord** |
| **Mobile experience** | Good but notification quirks when desktop is open | Good, smart notification deduplication | **Slack** (slightly) |
| **Privacy** | Collects data, ads via Quests, no self-host option | Collects data, no self-host, enterprise compliance focus | Tie (both mediocre) |
| **Casual/family vibe** | Built for communities, gamers, friends | Built for workplaces | **Discord** |
| **Voice channels** | Always-on voice channels, free | Huddles (1:1 only on free) | **Discord** |
| **Thread support** | Forum channels, threads in channels | Robust threading | **Slack** (slightly) |
| **Multi-device** | Desktop, mobile, web, all synced | Desktop, mobile, web, all synced | Tie |

**Score: Discord 7, Slack 3, Tie 4.**

---

## 3. Deep Dive

### 3.1 Bot Integration

**Discord** has a first-class bot framework. Create an Application in the Developer Portal, get a bot token, and go. The bot appears as a user in the server with full message access, slash commands, embeds, and components. The entire API is free with no tier gating. Rate limits: 50 req/s global, 5 msg/5s per channel -- irrelevant for household scale.

**Slack** also has a mature bot framework via Slack Apps with OAuth scopes. However, on the free tier, your bot counts toward the 10-integration limit. If Cleo is one integration and you add calendar sync, home automation webhooks, etc., you burn through that cap fast.

### 3.2 Webhook Support

Both platforms support simple incoming webhooks. Discord's are easier to set up (no app creation needed). Slack's Block Kit is more visually flexible. Discord's per-message username/avatar customization is more fun for a household bot with different personas.

### 3.3 Message Formatting

Discord uses standard Markdown plus embeds and Components V2 (buttons, selects, text inputs). Slack uses mrkdwn and Block Kit with headers, sections, dividers, and interactive elements. Slack edges ahead on formatting power, but Discord is more than adequate for grocery lists and reminders.

### 3.4 Media Sharing

Discord: 25 MB per file free, no cumulative cap. Slack free tier: 5 GB total across all users, then uploads fail. For a household sharing photos and screenshots, Slack's cap would be reached within months.

---

## 4. Bot/Automation Capabilities

### Discord (Free)
- Full API access, no tier restrictions
- Slash commands (`/cleo grocery add milk`)
- Message components: buttons, select menus, modals
- Voice channel integration (announcements via TTS)
- Role-based permissions ("Adult" vs "Kid" roles)
- Presence/status updates

### Slack (Free Tier)
- Full API but counts as 1 of 10 integrations
- Slash commands, shortcuts, workflows
- Block Kit interactive messages
- No voice on free tier
- Workflow Builder (limited on free)

---

## 5. Privacy and Data Considerations

Neither platform offers E2E encryption or self-hosting. Both can read your messages.

- **Discord**: Collects usage data, expanding ad personalization. Messages stored indefinitely for free. A private household server sees minimal ad interference.
- **Slack**: No ads (subscription-based revenue). But data older than 90 days is hidden, and >1 year is permanently deleted on free tier. Salesforce ownership raises data ecosystem questions.

Discord's indefinite retention is actually better for a household wanting persistent history.

---

## 6. Cost Analysis

| | Discord | Slack (Free) | Slack (Pro) |
|---|---|---|---|
| Platform cost | **$0/month** | $0 (crippled) | **$14.50+/month** (2 users) |
| Message history | Unlimited, forever | 90 days visible | Unlimited |
| Integrations | Unlimited | 10 max | Unlimited |
| File storage | 25 MB/file, no total cap | 5 GB total | 10 GB/user |

$0 vs $174/year is not a contest.

---

## 7. Mobile Experience

Both apps work well. The critical scenario is Cleo sending proactive alerts. Both suppress mobile notifications when desktop is active. Discord's implementation is slightly buggier. Workaround: Cleo DMs users for urgent alerts (DMs always push).

Slack has a slight edge on notification reliability, but not worth $174/year.

---

## 8. Integration Ecosystem

| Integration | Discord | Slack |
|---|---|---|
| Incoming webhooks | Channel-level, no app needed | App-level, app creation required |
| Real-time events | Gateway WebSocket | Events API or Socket Mode |
| MCP server | Community-built | Official, enterprise-grade |
| Zapier / n8n / Make | Full support | Full support |
| Home Assistant | Community integrations | Community integrations |

Slack wins on MCP; Discord wins on simplicity and unlimited free integrations.

---

## 9. Recommendation

### Use Discord. Here is exactly how.

**Architecture:**
- **iMessage**: Keep as the quick-command layer. Low-friction, always-available.
- **Discord**: Add as the rich dashboard and automation channel.

**Server structure:**
- `#general` -- family chat
- `#cleo-log` -- Cleo's activity log (automated)
- `#grocery` -- grocery list with interactive buttons
- `#calendar` -- daily schedule posts
- `#alerts` -- urgent notifications (packages, security)
- Voice channel for whole-house TTS announcements

**Why Discord:**
1. $0 vs $174/year
2. Unlimited integrations (no 10-app cap)
3. Permanent message history (searchable forever)
4. Voice channels for TTS announcements
5. Family-appropriate vibe (communities, not workplaces)
6. Bot ecosystem built for always-on automation

**The one thing you give up:** Slack's official MCP server. But since you're building Cleo yourself, direct Discord API access via a custom bot is simpler and more flexible than MCP abstraction.

---

*Sources: Discord API docs, Slack pricing page, Cloudwards comparison, Zapier comparison, Discord/Slack privacy policies, Slack MCP server docs, community Discord MCP implementations.*
