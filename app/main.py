from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from .config import load_config
from .db import Db, migrate
from .handlers import build_router
from .services import customers_inactive_days, monthly_report
from .utils import fmt_amount


async def setup_jobs(bot: Bot, db: Db, tz: str, admin_id: int) -> None:
    scheduler = AsyncIOScheduler(timezone=tz)

    async def monthly_job() -> None:
        from datetime import date

        today = date.today()
        rep = await monthly_report(db, year=today.year, month=today.month)
        msg = (
            f"📅 Oylik hisobot ({rep['start']} .. {rep['end']})\n"
            f"Jami: {fmt_amount(rep['total'])}\n"
            f"Savdolar soni: {rep['count']}\n"
            f"O‘sish: {rep['growth_pct']:.2f}%"
        )
        try:
            await bot.send_message(admin_id, msg)
        except Exception:
            pass

    async def inactivity_job() -> None:
        inacts = await customers_inactive_days(db, days=30, tz=tz)
        if not inacts:
            return
        try:
            names = ", ".join([f"#{c.id} {c.full_name}" for c in inacts[:20]])
            await bot.send_message(admin_id, f"⏰ 30 kun inaktiv mijozlar: {names}")
        except Exception:
            pass

        # optional reminder to customers
        for c in inacts:
            if not c.chat_id:
                continue
            try:
                await bot.send_message(int(c.chat_id), "Siz uzoq vaqt savdo qilmagansiz. Yangiliklar va aksiyalarni kuzatib boring!")
            except Exception:
                continue

    scheduler.add_job(monthly_job, "cron", day=1, hour=9, minute=0)
    scheduler.add_job(inactivity_job, "cron", hour=10, minute=0)
    scheduler.start()


async def amain() -> None:
    load_dotenv(override=True)
    cfg = load_config()
    db = Db(path=cfg.db_path)
    await migrate(db)

    bot = Bot(cfg.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(build_router(db, cfg))

    await setup_jobs(bot, db, cfg.tz, cfg.admin_telegram_id)
    await dp.start_polling(bot)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()

