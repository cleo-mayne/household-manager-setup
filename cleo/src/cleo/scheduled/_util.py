"""Shared helpers for scheduled pipelines."""

from __future__ import annotations

import httpx


async def post_webhook(url: str, content: str) -> None:
    if not url or not content:
        return
    async with httpx.AsyncClient(timeout=30) as client:
        # Discord message limit is 2000 chars; chunk if needed.
        for i in range(0, len(content), 2000):
            r = await client.post(url, json={"content": content[i : i + 2000]})
            r.raise_for_status()
