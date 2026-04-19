"""Discord bot: @mention + slash commands route into the Agent SDK.

Per-channel sessions preserve conversation memory. Persona switches to
nanny-mode in channels listed in NANNY_CHANNEL_IDS. Only TRUSTED_DISCORD_IDS
get write-capable tool access.
"""

from __future__ import annotations

import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks

from .config import Settings, load
from .conversation import ConversationStore

log = logging.getLogger("cleo.discord")

DISCORD_MSG_LIMIT = 2000


def _chunks(text: str, size: int = DISCORD_MSG_LIMIT) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)] or [""]


class Cleo(commands.Cog):
    def __init__(self, bot: commands.Bot, settings: Settings) -> None:
        self.bot = bot
        self.settings = settings
        self.store = ConversationStore(settings)
        self.idle_sweeper.start()

    def cog_unload(self) -> None:
        self.idle_sweeper.cancel()

    @tasks.loop(minutes=5)
    async def idle_sweeper(self) -> None:
        try:
            await self.store.sweep_idle()
        except Exception:
            log.exception("idle_sweeper failed")

    def _persona(self, channel: discord.abc.Messageable) -> bool:
        """True → nanny mode."""
        cid = getattr(channel, "id", 0)
        return cid in self.settings.nanny_channel_ids

    def _writable(self, user: discord.abc.User) -> bool:
        return user.id in self.settings.trusted_discord_ids

    async def _send(self, target: discord.abc.Messageable, text: str) -> None:
        if not text:
            text = "(no response)"
        for chunk in _chunks(text):
            await target.send(chunk)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if self.bot.user is None or not self.bot.user.mentioned_in(message):
            return

        nanny = self._persona(message.channel)
        writable = self._writable(message.author) and not nanny

        channel_name = getattr(message.channel, "name", "dm")
        framed = f"[channel: {channel_name}] {message.author.display_name}: {message.clean_content}"

        async with message.channel.typing():
            try:
                reply = await self.store.reply(
                    channel_id=message.channel.id,
                    prompt=framed,
                    nanny_mode=nanny,
                    writable=writable,
                )
            except Exception:
                log.exception("agent query failed")
                await message.reply("Something broke on my end. Greg, check the logs.")
                return

        await self._send(message.channel, reply)

    @app_commands.command(name="reset", description="Clear Cleo's memory of this channel's conversation.")
    async def reset_cmd(self, interaction: discord.Interaction) -> None:
        await self.store.reset(interaction.channel_id or 0)
        await interaction.response.send_message("Fresh slate. 🦞", ephemeral=True)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load()

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    cog = Cleo(bot, settings)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.reset_cmd)

    @bot.event
    async def on_ready() -> None:
        if settings.guild_id:
            guild = discord.Object(id=settings.guild_id)
            await bot.tree.sync(guild=guild)
        log.info("Cleo online as %s", bot.user)

    await bot.start(settings.discord_token)


if __name__ == "__main__":
    asyncio.run(main())
