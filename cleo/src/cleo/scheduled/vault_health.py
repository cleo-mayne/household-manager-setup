"""Vault health — weekly scan for broken links, orphans, and staleness.

Read-only. Posts report to #cleo-log.

Usage:
    python -m cleo.scheduled.vault_health
"""

from __future__ import annotations

import asyncio
import logging

from ..agent import run_one_shot
from ..config import load
from ._util import post_webhook

PROMPT = """Generate a weekly vault health report.

Scan the Obsidian vault and identify:
1. Broken wiki-links: [[target]] where target doesn't exist.
2. Orphaned notes: files with no inbound links (excluding daily/, inbox/).
3. Stale notes: files not modified in >90 days, flagged #followup or #wip.
4. Duplicate titles across folders.

Output markdown with 4 short sections. Include counts and a few examples per
section. Don't list every file — this is a triage document, not an audit."""


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load()
    report = await run_one_shot(settings, PROMPT, writable=False)
    if report:
        await post_webhook(
            settings.cleo_log_webhook,
            f"**Weekly vault health**\n{report}",
        )
    else:
        print("(no output)")


if __name__ == "__main__":
    asyncio.run(main())
