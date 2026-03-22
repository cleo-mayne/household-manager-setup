# Task Management: Stay on Todoist or Migrate?

## 1. Executive Summary

**Stay on Todoist. It is not close.**

Todoist remains the only task management platform that simultaneously offers (a) best-in-class natural language capture, (b) a real, well-documented REST API with official SDKs, (c) solid shared household list support with assignees, and (d) a reasonable price. You already survived the v2-to-v1 API migration, which was the worst disruption Todoist has caused in years. Every alternative requires giving up at least one critical capability, and most require giving up two or three.

The only scenario where migration makes sense is if you go all-in on Notion (replacing Obsidian + Todoist with one platform). That is not recommended.

---

## 2. Feature Comparison Table

| Feature | Todoist | TickTick | Things 3 | Apple Reminders | Linear | Notion | Obsidian Tasks |
|---|---|---|---|---|---|---|---|
| **REST API** | Excellent (v1) | Decent (OpenAPI) | None | None (EventKit) | Excellent (GraphQL) | Good (3 req/s) | N/A (files) |
| **Official SDKs** | Python + JS | None | None | Swift only | JS/TS | JS | N/A |
| **Natural Language** | Best in class | Good | Good (on Apple) | Basic | None | Basic | None |
| **Shared Lists** | Yes, assignees | Yes, assignees | No | Yes (iCloud) | Yes (teams) | Yes | No |
| **Recurring Tasks** | Excellent, NLP | Good | Good | Basic | Basic | Manual | Plugin |
| **Mobile Quality** | Excellent (all) | Excellent (all) | Excellent (Apple) | Excellent (Apple) | Good | Slow | Poor |
| **Cross-Platform** | All | All | Apple only | Apple only | Web + mobile | All | All |
| **Obsidian Integration** | Via API + custom sync | Rebuild needed | SQLite hack only | AppleScript only | Rebuild needed | Replaces Obsidian | Native |
| **AI Features** | Task Assist, Ramble | None | None | None | AI triage | Notion AI | None |

---

## 3. API Deep Dive (Critical)

### Todoist (Current) -- Grade: A
- Unified v1 API with pagination, webhooks, error handling
- Official Python + JS SDKs
- **Quick Add API** parses natural language server-side: "Buy groceries tomorrow p2 @lesley" creates a task with date, priority, and label
- Rate limit: 450 req/15 min (generous)
- Your existing `todoist-sync`, `TodoistClient`, and `TaskTracker` all work

### TickTick -- Grade: C+
- OpenAPI docs, OAuth2 auth. No official SDKs. No webhooks (polling only). No server-side NLP.
- Community MCP server exists but thin.

### Things 3 -- Grade: F
- **No API.** URL scheme (write-only), AppleScript (macOS only), SQLite hacks (fragile).
- **Disqualified.** An AI agent cannot depend on AppleScript on a specific Mac.

### Apple Reminders -- Grade: D
- EventKit (Swift/ObjC only). Cannot access tags, subtasks, rich links programmatically.
- AppleScript workarounds are fragile and macOS-only.
- **Disqualified.** No headless server access.

### Linear -- Grade: A
- Excellent GraphQL API, TypeScript SDK, webhooks.
- **But:** Data model is issue-tracker-shaped (teams, sprints), not task-list-shaped. "Buy birthday present for Aunt Susan by March 30" does not fit.
- **Viable only for:** Agent Development / technical project work alongside Todoist.

### Notion -- Grade: B-
- REST API, 3 req/s rate limit (restrictive for batch ops). No NLP. Creating a task = creating a DB row with properties (verbose).
- Adopting Notion tasks leads to replacing Obsidian entirely -- a much larger decision.

### Obsidian Tasks -- Grade: N/A
- No API. Markdown checkboxes in files. No mobile capture, no shared lists, no NLP.
- **Viable only if:** You accept degraded mobile experience and no real-time sharing.

**Only Todoist and Linear have APIs good enough for a production AI agent. Linear's data model is wrong for household tasks.**

---

## 4. Shared Household Task Management

| Platform | Shared Lists | Assignment | Real-time Sync | Non-Technical Partner |
|---|---|---|---|---|
| **Todoist** | Native | Yes | Yes | Excellent UX |
| **TickTick** | Yes (29 members) | Yes | Yes | Good UX |
| **Things 3** | No | No | No | N/A |
| **Apple Reminders** | iCloud shared | Implicit | Yes | Dead simple |
| **Linear** | Team workspace | Yes | Yes | No (developer UI) |
| **Notion** | Shared workspace | Property-based | Yes | Depends on comfort |
| **Obsidian Tasks** | No | No | No (git) | No |

---

## 5. Natural Language Capture

- **Todoist**: "Buy milk tomorrow p2 @lesley #Household" -- Quick Add API handles this server-side. New "Ramble" feature converts voice memos to structured tasks.
- **TickTick**: Client-side NLP only, no API endpoint for it.
- **Things 3**: Good NLP in app, but no API.
- **All others**: Zero NLP for task creation.

For an AI agent that receives natural language from iMessage and needs to create tasks, Todoist's Quick Add API is uniquely valuable.

---

## 6. Cost Analysis (Annual, 2 Users)

| Platform | Annual Cost | Notes |
|---|---|---|
| **Todoist Pro** | $96/year | All API features, shared projects |
| **TickTick Premium** | $72/year | Cheaper, but weaker API |
| **Things 3** | ~$160 once | No API |
| **Apple Reminders** | $0 | No API |
| **Linear** | $0-153/year | Free personal; $6.40/user/mo for teams |
| **Notion Plus** | $192/year | More expensive, less task capability |
| **Obsidian Tasks** | $0-96/year | Free or Obsidian Sync cost |

Todoist Pro at $96/year is the sweet spot.

---

## 7. Migration Risk Assessment

| Target | Effort | Risk | Gain |
|---|---|---|---|
| **TickTick** | 2-3 days dev, rebuild sync | Medium (thinner API, OAuth complexity) | Save $24/year |
| **Things 3** | Not feasible | Critical (no API) | Beautiful app you can't automate |
| **Apple Reminders** | Not feasible | Critical (no API) | Zero cost, can't automate |
| **Linear** | 2-3 days dev | Medium-low API, high UX risk | Great for tech projects only |
| **Notion** | 1-2 weeks | High (replaces entire stack) | Single unified system |
| **Obsidian Tasks** | 1-2 days | Medium (lose mobile, shared lists, NLP) | Zero dependencies |
| **Stay on Todoist** | Zero | Near-zero | Keep working system |

---

## 8. Recommendation

**Stay on Todoist Pro.** Specific reasoning:

1. **Your AI agent depends on programmatic task access.** Only Todoist and Linear have good enough APIs. Linear's model is wrong for household tasks.

2. **You already built the integration.** `todoist-sync` (bash), `TodoistClient` (JS), `TaskTracker` (Python) -- all working on v1 API. Real engineering time that would be thrown away.

3. **Natural language capture is a force multiplier.** Cleo pipes Lesley's text messages to Todoist's Quick Add and gets the right date, priority, and project without a custom parser.

4. **The API migration fear is behind you.** You survived v2 → v1. The unified API is designed for long-term stability.

5. **$96/year is reasonable.** Less than Notion, barely more than TickTick, with superior API and NLP.

6. **Shared household lists work well.** Both adults use the app natively with assigned tasks.

**Consider adding Linear alongside Todoist** for Agent Development / technical project work only. Free tier, excellent GraphQL API, built for developer workflows. But this would be an addition, not a replacement.

---

*Sources: Todoist API v1 docs, TickTick developer portal, Things 3 unofficial API, Apple EventKit docs, Linear API docs, Notion API rate limits, Obsidian Tasks plugin, community comparisons.*
