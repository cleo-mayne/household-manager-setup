"""Inbox triage — file new captures into the right vault directories.

Posts a summary to #cleo-log. Runs writable so Cleo can actually move files.

Usage:
    python -m cleo.scheduled.inbox_triage
"""

from __future__ import annotations

import asyncio
import logging

from ..agent import run_one_shot
from ..config import load
from ._util import post_webhook

PROMPT = """Triage the Obsidian vault inbox.

For each file in $OBSIDIAN_VAULT/inbox/ that's older than 1 hour:
1. Read it.
2. Classify: person note, project note, idea, reference, ephemeral.
3. Move (Write new, Edit old to empty) to the correct directory:
   - people/ for person notes
   - projects/ for project notes
   - ideas/ for ideas
   - 3-resources/ for reference material
   - Delete ephemeral items outright (via Bash `rm`).
4. Skip anything ambiguous — leave it in inbox for human triage.

Output a short summary (markdown) of what you filed and what you left."""


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load()
    summary = await run_one_shot(settings, PROMPT, writable=True)
    if summary:
        await post_webhook(
            settings.cleo_log_webhook,
            f"**Inbox triage**\n{summary}",
        )
    else:
        print("(no output)")


if __name__ == "__main__":
    asyncio.run(main())
