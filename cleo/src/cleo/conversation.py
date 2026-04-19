"""Per-channel conversation memory.

Keeps a persistent `ClaudeSDKClient` per Discord channel so Cleo has continuity
inside a conversation. Idle channels are evicted after IDLE_TIMEOUT_SEC.

This is the piece that preserves the "talk to Cleo" feel — consecutive messages
in the same channel share context, so she remembers what you just said.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from claude_agent_sdk import ClaudeSDKClient

from .agent import build_options
from .config import Settings

IDLE_TIMEOUT_SEC = 30 * 60  # 30 minutes of silence → tear down session


@dataclass
class _Session:
    client: ClaudeSDKClient
    last_used: float
    nanny_mode: bool
    writable: bool


class ConversationStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._sessions: dict[int, _Session] = {}
        self._lock = asyncio.Lock()

    async def reply(
        self,
        channel_id: int,
        prompt: str,
        *,
        nanny_mode: bool = False,
        writable: bool = False,
    ) -> str:
        session = await self._get_or_create(channel_id, nanny_mode, writable)
        await session.client.query(prompt)

        chunks: list[str] = []
        async for event in session.client.receive_response():
            text = getattr(event, "text", None)
            if event.type == "assistant" and text:
                chunks.append(text)

        session.last_used = time.monotonic()
        return "\n".join(chunks).strip()

    async def reset(self, channel_id: int) -> None:
        """Drop a channel's session (e.g. via a /reset slash command)."""
        async with self._lock:
            session = self._sessions.pop(channel_id, None)
        if session is not None:
            await session.client.disconnect()

    async def sweep_idle(self) -> None:
        """Tear down sessions idle longer than IDLE_TIMEOUT_SEC. Call periodically."""
        cutoff = time.monotonic() - IDLE_TIMEOUT_SEC
        async with self._lock:
            stale = [cid for cid, s in self._sessions.items() if s.last_used < cutoff]
            to_close = [self._sessions.pop(cid) for cid in stale]
        for session in to_close:
            await session.client.disconnect()

    async def _get_or_create(
        self, channel_id: int, nanny_mode: bool, writable: bool
    ) -> _Session:
        async with self._lock:
            session = self._sessions.get(channel_id)
            if session and (
                session.nanny_mode != nanny_mode or session.writable != writable
            ):
                # Persona/trust changed — start fresh so we don't leak context.
                await session.client.disconnect()
                session = None

            if session is None:
                options = build_options(
                    self._settings, nanny_mode=nanny_mode, writable=writable
                )
                client = ClaudeSDKClient(options=options)
                await client.connect()
                session = _Session(
                    client=client,
                    last_used=time.monotonic(),
                    nanny_mode=nanny_mode,
                    writable=writable,
                )
                self._sessions[channel_id] = session
            return session
