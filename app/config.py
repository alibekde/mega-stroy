from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_telegram_ids: tuple[int, ...]
    db_path: str
    tz: str


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_ids_env = os.getenv("ADMIN_TELEGRAM_IDS", "").strip()
    admin_id_raw = os.getenv("ADMIN_TELEGRAM_ID", "").strip()
    db_path = os.getenv("DB_PATH", "mega_stroy.sqlite3").strip()
    tz = os.getenv("TZ", "Asia/Tashkent").strip()

    if not bot_token:
        raise RuntimeError("BOT_TOKEN .env da yo‘q")

    ids: list[int] = []
    if admin_ids_env:
        for p in admin_ids_env.split(","):
            p = p.strip()
            if p.isdigit():
                ids.append(int(p))
    elif admin_id_raw and admin_id_raw.isdigit():
        ids.append(int(admin_id_raw))

    if not ids:
        raise RuntimeError("ADMIN_TELEGRAM_ID(S) .env da noto‘g‘ri")

    return Config(
        bot_token=bot_token,
        admin_telegram_ids=tuple(ids),
        db_path=db_path,
        tz=tz,
    )

