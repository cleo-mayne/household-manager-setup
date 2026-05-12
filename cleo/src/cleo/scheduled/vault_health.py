"""Vault health — weekly scan for broken links, orphans, and staleness.

Loads the vault-health skill. Read-only.

Usage:
    python -m cleo.scheduled.vault_health
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
    report = await run_skill(settings, "vault-health", writable=False)
    if report:
        await post_webhook(settings.cleo_log_webhook, report)
    else:
        print("(no output)")


if __name__ == "__main__":
    asyncio.run(main())
