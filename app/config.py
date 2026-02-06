from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_telegram_id: int
    db_path: str
    tz: str


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_id_raw = os.getenv("ADMIN_TELEGRAM_ID", "").strip()
    db_path = os.getenv("DB_PATH", "mega_stroy.sqlite3").strip()
    tz = os.getenv("TZ", "Asia/Tashkent").strip()

    if not bot_token:
        raise RuntimeError("BOT_TOKEN .env da yo‘q")
    if not admin_id_raw or not admin_id_raw.isdigit():
        raise RuntimeError("ADMIN_TELEGRAM_ID .env da noto‘g‘ri")

    return Config(
        bot_token=bot_token,
        admin_telegram_id=int(admin_id_raw),
        db_path=db_path,
        tz=tz,
    )

