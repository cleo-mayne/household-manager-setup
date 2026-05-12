"""End-of-day digest — bracket to morning-brief.

Loads the eod-digest skill. Writable because the skill appends a one-line
running-log entry to $OBSIDIAN_VAULT/CLEO.md.

Usage:
    python -m cleo.scheduled.eod_digest
"""

from __future__ import annotations

import asyncio
import logging

from ..agent import run_skill
from ..config import load
from ._util import post_webhook


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load()
    text = await run_skill(settings, "eod-digest", writable=True)
    if settings.daily_brief_webhook:
        await post_webhook(settings.daily_brief_webhook, text)
    else:
        print(text)


if __name__ == "__main__":
    asyncio.run(main())
