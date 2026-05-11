"""Reindex qmd's vault collection.

Runs `qmd embed` to (re)generate embeddings for new/changed markdown files.
Scheduled hourly under launchd. Reports failures to #cleo-log.

Usage:
    python -m cleo.scheduled.qmd_reindex
"""

from __future__ import annotations

import asyncio
import logging

from ..config import load
from ._util import post_webhook

log = logging.getLogger("cleo.qmd_reindex")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load()
    if not settings.qmd_enabled:
        log.info("qmd disabled (QMD_ENABLED=false); skipping reindex")
        return

    proc = await asyncio.create_subprocess_exec(
        settings.qmd_bin,
        "embed",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    out = stdout.decode(errors="replace").strip()
    err = stderr.decode(errors="replace").strip()

    if proc.returncode == 0:
        log.info("qmd embed ok: %s", out[-400:] if out else "(no output)")
        return

    msg = (
        f"`qmd embed` failed (exit {proc.returncode})\n"
        f"```\n{err[-1500:] or out[-1500:] or '(no output)'}\n```"
    )
    log.error(msg)
    await post_webhook(settings.alerts_webhook or settings.cleo_log_webhook, msg)
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    asyncio.run(main())
