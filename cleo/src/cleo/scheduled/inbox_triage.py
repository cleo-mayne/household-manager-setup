"""Inbox triage — file new captures into the right PARA bucket.

Loads the inbox-triage skill. Writable.

Usage:
    python -m cleo.scheduled.inbox_triage
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
    summary = await run_skill(settings, "inbox-triage", writable=True)
    if summary:
        await post_webhook(settings.cleo_log_webhook, summary)
    else:
        print("(no output)")


if __name__ == "__main__":
    asyncio.run(main())
