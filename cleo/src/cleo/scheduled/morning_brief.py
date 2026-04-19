"""Morning brief — posts a summary to #daily-brief at 8am via launchd.

Usage:
    python -m cleo.scheduled.morning_brief
"""

from __future__ import annotations

import asyncio
import logging

import httpx

from ..agent import run_one_shot
from ..config import load

PROMPT = """Generate today's morning brief for the family.

Steps:
1. Read today's daily note in the Obsidian vault (daily/YYYY-MM-DD.md).
2. List Todoist tasks due today for each family member.
3. Check the vault inbox for new captures since yesterday.
4. Note anything time-sensitive (appointments, deliveries, school).

Output a concise markdown summary. Keep the Cleo voice. Short. 🦞 at the end."""


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load()
    text = await run_one_shot(settings, PROMPT, writable=False)

    if not settings.daily_brief_webhook:
        print(text)
        return

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(settings.daily_brief_webhook, json={"content": text})
        r.raise_for_status()


if __name__ == "__main__":
    asyncio.run(main())
