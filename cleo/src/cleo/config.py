"""Environment and persona configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def _ids(var: str) -> set[int]:
    raw = os.getenv(var, "").strip()
    if not raw:
        return set()
    return {int(x) for x in raw.split(",") if x.strip()}


def _handles(var: str) -> set[str]:
    raw = os.getenv(var, "").strip()
    if not raw:
        return set()
    return {x.strip() for x in raw.split(",") if x.strip()}


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    model: str
    discord_token: str
    guild_id: int
    trusted_discord_ids: frozenset[int]
    nanny_channel_ids: frozenset[int]
    obsidian_vault: Path
    brain_mcp_cmd: str
    brain_mcp_args: list[str]
    daily_brief_webhook: str
    alerts_webhook: str
    cleo_log_webhook: str
    # iMessage (BlueBubbles)
    bluebubbles_url: str
    bluebubbles_password: str
    imessage_listen_host: str
    imessage_listen_port: int
    trusted_imessage_handles: frozenset[str]
    # qmd (local hybrid search over the vault)
    qmd_enabled: bool
    qmd_bin: str
    qmd_collection: str


def load() -> Settings:
    return Settings(
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
        model=os.getenv("CLEO_MODEL", "claude-sonnet-4-6"),
        discord_token=os.environ.get("DISCORD_TOKEN", ""),
        guild_id=int(os.getenv("DISCORD_GUILD_ID", "0")),
        trusted_discord_ids=frozenset(_ids("TRUSTED_DISCORD_IDS")),
        nanny_channel_ids=frozenset(_ids("NANNY_CHANNEL_IDS")),
        obsidian_vault=Path(os.environ.get("OBSIDIAN_VAULT", "~/Obsidian")).expanduser(),
        brain_mcp_cmd=os.getenv("BRAIN_MCP_CMD", "python"),
        brain_mcp_args=os.getenv("BRAIN_MCP_ARGS", "-m,brain.mcp_server").split(","),
        daily_brief_webhook=os.getenv("DISCORD_DAILY_BRIEF_WEBHOOK", ""),
        alerts_webhook=os.getenv("DISCORD_ALERTS_WEBHOOK", ""),
        cleo_log_webhook=os.getenv("DISCORD_CLEO_LOG_WEBHOOK", ""),
        bluebubbles_url=os.getenv("BLUEBUBBLES_URL", "http://localhost:1234"),
        bluebubbles_password=os.getenv("BLUEBUBBLES_PASSWORD", ""),
        imessage_listen_host=os.getenv("IMESSAGE_LISTEN_HOST", "127.0.0.1"),
        imessage_listen_port=int(os.getenv("IMESSAGE_LISTEN_PORT", "8787")),
        trusted_imessage_handles=frozenset(_handles("TRUSTED_IMESSAGE_HANDLES")),
        qmd_enabled=os.getenv("QMD_ENABLED", "true").lower() in {"1", "true", "yes"},
        qmd_bin=os.getenv("QMD_BIN", "qmd"),
        qmd_collection=os.getenv("QMD_COLLECTION", "vault"),
    )


def system_prompt(nanny_mode: bool) -> str:
    name = "cleo-nanny-mode.md" if nanny_mode else "cleo-system.md"
    return (PROMPTS_DIR / name).read_text()
