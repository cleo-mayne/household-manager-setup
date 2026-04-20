"""Knowledge-graph link discovery — suggest backlinks between related notes.

Read-only; suggestions post to #cleo-log as an approval gate (human adds the
links manually, or a follow-up writable pass approves them).

Usage:
    python -m cleo.scheduled.knowledge_graph
"""

from __future__ import annotations

import asyncio
import logging

from ..agent import run_one_shot
from ..config import load
from ._util import post_webhook

PROMPT = """Suggest backlinks for recently-modified notes.

For notes modified in the last 7 days:
1. Identify 1-3 strong candidate backlinks per note (semantic relevance, not
   just keyword match).
2. Skip suggestions where the link already exists.
3. Skip if confidence is low — over-linking is worse than under-linking.

Output markdown: one section per source note, bullet list of suggestions with
a one-line reason for each. No changes made — this is review material."""


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load()
    report = await run_one_shot(settings, PROMPT, writable=False)
    if report:
        await post_webhook(
            settings.cleo_log_webhook,
            f"**Link suggestions**\n{report}",
        )
    else:
        print("(no output)")


if __name__ == "__main__":
    asyncio.run(main())
