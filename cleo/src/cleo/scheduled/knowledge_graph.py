"""Knowledge-graph backlink suggestions for review.

Loads the knowledge-graph skill. Read-only.

Usage:
    python -m cleo.scheduled.knowledge_graph
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
    report = await run_skill(settings, "knowledge-graph", writable=False)
    if report:
        await post_webhook(settings.cleo_log_webhook, report)
    else:
        print("(no output)")


if __name__ == "__main__":
    asyncio.run(main())
