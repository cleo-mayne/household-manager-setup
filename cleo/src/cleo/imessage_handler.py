"""iMessage bridge via BlueBubbles.

Runs an aiohttp webhook receiver. BlueBubbles (self-hosted on the Mac Studio)
POSTs new-message events here; we feed them into the same ConversationStore as
Discord, then send the reply back through BlueBubbles' REST API.

One chat (thread) = one channel_id for conversation memory purposes.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from aiohttp import web

from .config import Settings, load
from .conversation import ConversationStore

log = logging.getLogger("cleo.imessage")


def _chat_key(chat_guid: str) -> int:
    # ConversationStore keys are int; hash the chat guid to a stable int.
    return abs(hash(chat_guid)) % (2**31)


class IMessageBridge:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = ConversationStore(settings)
        self._http = httpx.AsyncClient(timeout=30)

    async def close(self) -> None:
        await self._http.aclose()

    async def _send(self, chat_guid: str, text: str) -> None:
        url = f"{self.settings.bluebubbles_url}/api/v1/message/text"
        params = {"password": self.settings.bluebubbles_password}
        payload = {"chatGuid": chat_guid, "method": "private-api", "message": text}
        r = await self._http.post(url, params=params, json=payload)
        if r.status_code >= 300:
            log.warning("BlueBubbles send failed: %s %s", r.status_code, r.text)

    async def handle_webhook(self, request: web.Request) -> web.Response:
        payload: dict[str, Any] = await request.json()
        if payload.get("type") != "new-message":
            return web.json_response({"ok": True})

        data = payload.get("data", {})
        text = (data.get("text") or "").strip()
        if not text or data.get("isFromMe"):
            return web.json_response({"ok": True})

        sender = (data.get("handle") or {}).get("address", "")
        chats = data.get("chats") or []
        if not chats:
            return web.json_response({"ok": True})
        chat = chats[0]
        chat_guid = chat.get("guid", "")
        chat_name = chat.get("displayName") or sender or "imessage"

        trusted = sender in self.settings.trusted_imessage_handles
        writable = trusted
        nanny_mode = not trusted  # unknown senders get neutral read-only Cleo

        framed = f"[channel: imessage:{chat_name}] {sender}: {text}"

        try:
            reply = await self.store.reply(
                channel_id=_chat_key(chat_guid),
                prompt=framed,
                nanny_mode=nanny_mode,
                writable=writable,
            )
        except Exception:
            log.exception("agent query failed")
            reply = "Something broke on my end. Try again in a bit."

        if reply:
            await self._send(chat_guid, reply)
        return web.json_response({"ok": True})


async def _sweep_loop(store: ConversationStore) -> None:
    while True:
        await asyncio.sleep(300)
        try:
            await store.sweep_idle()
        except Exception:
            log.exception("idle sweeper failed")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load()
    bridge = IMessageBridge(settings)

    app = web.Application()
    app.router.add_post("/webhook", bridge.handle_webhook)

    sweeper = asyncio.create_task(_sweep_loop(bridge.store))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner, settings.imessage_listen_host, settings.imessage_listen_port
    )
    await site.start()
    log.info(
        "iMessage bridge listening on %s:%s",
        settings.imessage_listen_host,
        settings.imessage_listen_port,
    )

    try:
        await asyncio.Event().wait()
    finally:
        sweeper.cancel()
        await bridge.close()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
