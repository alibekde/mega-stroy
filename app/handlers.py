from __future__ import annotations

from datetime import date, datetime, timedelta
import re

from aiogram import F, Router  # pyright: ignore[reportMissingImports]
from aiogram.filters import Command, CommandStart  # pyright: ignore[reportMissingImports]
from aiogram.fsm.context import FSMContext  # pyright: ignore[reportMissingImports]
from aiogram.types import CallbackQuery, Message  # pyright: ignore[reportMissingImports]

from .config import Config
from .db import Db
from .exporting import customers_to_pdf, customers_to_xlsx, sales_to_xlsx
from .keyboards import (
    ask_phone_keyboard,
    back_to_menu,
    bonuses_menu,
    bonuses_menu_inline,
    customer_history_filters,
    customers_menu,
    customers_menu_inline,
    export_menu,
    export_menu_inline,
    main_menu_admin,
    main_menu_admin_inline,
    main_menu_customer,
    main_menu_customer_inline,
    reports_menu,
    reports_menu_inline,
    sales_menu,
    sales_menu_inline,
)
from .services import (
    add_manual_reward,
    add_sale,
    all_customers_with_chat,
    active_customers_with_chat,
    create_customer,
    delete_last_sale,
    delete_customer,
    delete_reward,
    delete_sale_by_id,
    find_customer,
    get_customer,
    get_customer_by_chat,
    link_customer_chat,
    list_customers,
    list_rewards,
    list_sales_for_customer,
    monthly_report,
    sales_between,
    set_customer_status,
)
from .states import (
    AdminBroadcast,
    AdminCustomerAdd,
    AdminCustomerDelete,
    AdminCustomerSearch,
    AdminExportSalesRange,
    AdminManualReward,
    AdminRewardDelete,
    AdminReportCustomerHistory,
    AdminReportMonthly,
    AdminReportRange,
    AdminSaleDeleteById,
    AdminSaleAdd,
)
from .utils import fmt_amount, parse_amount


def build_router(db: Db, cfg: Config) -> Router:
    router = Router()

    def is_admin(telegram_id: int) -> bool:
        return telegram_id == cfg.admin_telegram_id

    async def show_menu(message: Message) -> None:
        if is_admin(message.from_user.id):
            text = (
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⚙️ ADMIN PANELI\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Quyidagi bo'limlardan birini tanlang:"
            )
            await message.answer(text, reply_markup=main_menu_admin(), parse_mode="HTML")
            return
        customer = await get_customer_by_chat(db, chat_id=message.from_user.id)
        if not customer:
            text = (
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👋 Assalomu alaykum!\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Botdan foydalanish uchun telefon raqamingizni yuboring."
            )
            await message.answer(text, reply_markup=ask_phone_keyboard(), parse_mode="HTML")
            return
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 MIJOZ PANELI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi bo'limlardan birini tanlang:"
        )
        await message.answer(text, reply_markup=main_menu_customer(), parse_mode="HTML")

    @router.message(CommandStart())
    async def cmd_start(message: Message, state: FSMContext) -> None:
        await state.clear()
        await show_menu(message)

    @router.message(Command("admin"))
    @router.message(F.text == "/admin")
    async def cmd_admin(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚙️ ADMIN PANELI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi bo'limlardan birini tanlang:"
        )
        await message.answer(text, reply_markup=main_menu_admin(), parse_mode="HTML")

    @router.message(Command("whoami"))
    async def cmd_whoami(message: Message) -> None:
        tid = int(message.from_user.id)
        role = "admin" if is_admin(tid) else "mijoz"
        await message.answer(
            f"Sizning Telegram ID: <code>{tid}</code>\n"
            f"Sozlangan ADMIN_TELEGRAM_ID: <code>{cfg.admin_telegram_id}</code>\n"
            f"Rol: <b>{role}</b>",
            parse_mode="HTML",
        )

    # ---- Customer phone linking
    @router.message(F.contact)
    async def on_contact(message: Message) -> None:
        phone = (message.contact.phone_number or "").replace("+", "").strip()
        linked = await link_customer_chat(db, phone=phone, chat_id=message.from_user.id, tz=cfg.tz)
        if not linked:
            await message.answer("Bu telefon admin bazasida topilmadi. Iltimos adminga murojaat qiling.")
            return
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✅ TELEFON TASDIQLANDI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Endi siz botdan to'liq foydalanishingiz mumkin!"
        )
        await message.answer(text, reply_markup=main_menu_customer(), parse_mode="HTML")

    # ---- Common menu callbacks
    # ---- Reply keyboard text handlers (tugmalar text sifatida keladi)
    @router.message(F.text == "👤 Mijozlar")
    async def msg_admin_customers(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 MIJOZLAR BOSHQARISH\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi amallardan birini tanlang:"
        )
        await message.answer(text, reply_markup=customers_menu(), parse_mode="HTML")

    @router.message(F.text == "💰 Savdo")
    async def msg_admin_sales(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💰 SAVDO OPERATSIYALARI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi amallardan birini tanlang:"
        )
        await message.answer(text, reply_markup=sales_menu(), parse_mode="HTML")

    @router.message(F.text == "📊 Hisobotlar")
    async def msg_admin_reports(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📊 STATISTIKA VA HISOBOTLAR\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi hisobotlardan birini tanlang:"
        )
        await message.answer(text, reply_markup=reports_menu(), parse_mode="HTML")

    @router.message(F.text == "🎁 Bonuslar")
    async def msg_admin_bonuses(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 BONUS TIZIMI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi amallardan birini tanlang:"
        )
        await message.answer(text, reply_markup=bonuses_menu(), parse_mode="HTML")

    @router.message(F.text == "📢 Xabar yuborish")
    async def msg_admin_broadcast(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminBroadcast.audience)
        await message.answer("Kimga yuborilsin? `all` yoki `active` deb yozing:", reply_markup=main_menu_admin())

    @router.message(F.text == "📤 Eksport")
    async def msg_admin_export(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📤 EKSPORT VA SAQLASH\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi formatlardan birini tanlang:"
        )
        await message.answer(text, reply_markup=export_menu(), parse_mode="HTML")

    # ---- Submenyu reply tugmalari (pastda ko'rinadi)
    @router.message(F.text == "➕ Yangi mijoz qo'shish")
    async def msg_customer_add(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminCustomerAdd.full_name)
        await message.answer("Yangi mijoz ismini kiriting:", reply_markup=customers_menu())

    @router.message(F.text == "📋 Mijozlar ro'yxati")
    async def msg_customer_list(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        rows = await list_customers(db, limit=50)
        if not rows:
            await message.answer("Mijozlar yo'q.", reply_markup=customers_menu())
            return
        text = "Mijozlar (oxirgi 50):\n\n" + "\n".join(
            [f"#{c.id} {c.full_name} | {c.phone} | {c.status} | {fmt_amount(c.total_spent)} | {c.level}" for c in rows]
        )
        await message.answer(text, reply_markup=customers_menu())

    @router.message(F.text == "🔍 Qidirish")
    async def msg_customer_search(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminCustomerSearch.query)
        await message.answer("Qidiruv: ism/telefon/ID kiriting:", reply_markup=customers_menu())

    @router.message(F.text == "🗑️ Mijozni o'chirish")
    async def msg_customer_delete(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminCustomerDelete.customer_query)
        await message.answer("O‘chirish uchun mijoz ID yoki ism/telefon kiriting:", reply_markup=customers_menu())

    @router.message(AdminCustomerDelete.customer_query)
    async def st_customer_delete(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        q = (message.text or "").strip()
        cid: int | None = None
        if q.isdigit():
            cid = int(q)
        else:
            res = await find_customer(db, query=q, limit=1)
            if res:
                cid = res[0].id
        await state.clear()
        if cid is None:
            await message.answer("Topilmadi.", reply_markup=customers_menu())
            return
        ok = await delete_customer(db, customer_id=cid, tz=cfg.tz, actor_telegram_id=message.from_user.id)
        if not ok:
            await message.answer("O‘chirish mumkin emas yoki topilmadi.", reply_markup=customers_menu())
            return
        await message.answer(f"🗑️ Mijoz o‘chirildi: #{cid}", reply_markup=customers_menu())

    @router.message(F.text == "➕ Yangi savdo kiritish")
    async def msg_sale_add(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminSaleAdd.customer_query)
        await message.answer("Mijoz tanlang: ism/telefon/ID yozing:", reply_markup=sales_menu())

    @router.message(F.text == "🗑️ Oxirgi savdoni o'chirish")
    async def msg_sale_delete_last(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminReportCustomerHistory.customer_query)
        await message.answer("Oxirgi savdoni o'chirish: mijoz ism/telefon/ID kiriting:", reply_markup=sales_menu())

    @router.message(F.text == "🗑️ Savdoni ID bo'yicha o'chirish")
    async def msg_sale_delete_by_id(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminSaleDeleteById.sale_id)
        await message.answer("Savdo ID kiriting:", reply_markup=sales_menu())

    @router.message(AdminSaleDeleteById.sale_id)
    async def st_sale_delete_by_id(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        raw = (message.text or "").strip()
        if not raw.isdigit():
            await message.answer("ID noto‘g‘ri.", reply_markup=sales_menu())
            return
        sid = int(raw)
        await state.clear()
        deleted = await delete_sale_by_id(db, sale_id=sid, tz=cfg.tz, actor_telegram_id=message.from_user.id)
        if deleted is None:
            await message.answer("Savdo topilmadi.", reply_markup=sales_menu())
            return
        await message.answer(f"🗑️ Savdo o‘chirildi. SaleID={sid}", reply_markup=sales_menu())
    @router.message(F.text == "📅 Oylik hisobot")
    async def msg_report_monthly(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminReportMonthly.year_month)
        await message.answer("Oylik hisobot: YYYY-MM kiriting (masalan 2026-02):", reply_markup=reports_menu())

    @router.message(F.text == "👤 Mijoz tarixi")
    async def msg_report_customer_history(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminReportCustomerHistory.customer_query)
        await message.answer("Mijoz tarixi: ism/telefon/ID kiriting:", reply_markup=reports_menu())

    @router.message(F.text == "📆 Sana oralig'i hisobot")
    async def msg_report_range(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminReportRange.start)
        await message.answer("Boshlanish sana (YYYY-MM-DD):", reply_markup=reports_menu())

    @router.message(F.text == "📜 Bonuslar ro'yxati")
    async def msg_bonus_list(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        text = (
            "Bonuslar ro'yxati:\n\n"
            "- 50 000 000 so'm: Chang yutqich\n"
            "- 100 000 000 so'm: Super yutuq"
        )
        await message.answer(text, reply_markup=bonuses_menu())

    @router.message(F.text == "➕ Yutuq kiritish")
    async def msg_bonus_manual_add(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminManualReward.customer_query)
        await message.answer("Yutuq kiritish: mijoz ism/telefon/ID kiriting:", reply_markup=bonuses_menu())

    @router.message(F.text == "🗑️ Yutuqni o'chirish")
    async def msg_bonus_delete(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminRewardDelete.customer_query)
        await message.answer("Mijoz tanlang: ism/telefon/ID kiriting:", reply_markup=bonuses_menu())

    @router.message(AdminRewardDelete.customer_query)
    async def st_reward_delete_customer(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        q = (message.text or "").strip()
        res = await find_customer(db, query=q, limit=1)
        if not res:
            await message.answer("Mijoz topilmadi. Qayta kiriting.", reply_markup=bonuses_menu())
            return
        c = res[0]
        rws = await list_rewards(db, customer_id=c.id, limit=20)
        if not rws:
            await state.clear()
            await message.answer("Bu mijozda yutuq yo‘q.", reply_markup=bonuses_menu())
            return
        await state.update_data(customer_id=c.id)
        await state.set_state(AdminRewardDelete.reward_id)
        lines = [f"#{r['id']} {r['reward_type']} | {r['reward_name']}" for r in rws]
        await message.answer("Yutuqlar (oxirgi 20):\n\n" + "\n".join(lines) + "\n\nO‘chirish uchun RewardID kiriting:", reply_markup=bonuses_menu())

    @router.message(AdminRewardDelete.reward_id)
    async def st_reward_delete_id(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        raw = (message.text or "").strip()
        if not raw.isdigit():
            await message.answer("ID noto‘g‘ri.", reply_markup=bonuses_menu())
            return
        rid = int(raw)
        await state.clear()
        deleted = await delete_reward(db, reward_id=rid, tz=cfg.tz, actor_telegram_id=message.from_user.id)
        if deleted is None:
            await message.answer("Yutuq topilmadi.", reply_markup=bonuses_menu())
            return
        await message.answer(f"🗑️ Yutuq o‘chirildi. RewardID={rid}", reply_markup=bonuses_menu())
    @router.message(F.text == "🏆 Oylik g'oliblar")
    async def msg_winners_monthly(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        today = date.today()
        rep = await monthly_report(db, year=today.year, month=today.month)
        text = "🏆 Oylik g'oliblar (Top 5):\n\n" + "\n".join(
            [f"- #{t['customer_id']} {t['full_name']} ({t['phone']}): {fmt_amount(int(t['sum_amount']))}" for t in rep["top5"]]
        )
        await message.answer(text, reply_markup=bonuses_menu())

    @router.message(F.text == "📄 Mijozlar (PDF)")
    async def msg_export_customers_pdf(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        rows = await list_customers(db, limit=5000)
        data = [c.__dict__ for c in rows]
        bio = customers_to_pdf(data)
        await message.answer_document(("customers.pdf", bio), caption="Mijozlar ro'yxati (PDF)", reply_markup=export_menu())

    @router.message(F.text == "📊 Mijozlar (Excel)")
    async def msg_export_customers_xlsx(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        rows = await list_customers(db, limit=5000)
        data = [c.__dict__ for c in rows]
        bio = customers_to_xlsx(data)
        await message.answer_document(("customers.xlsx", bio), caption="Mijozlar ro'yxati (Excel)", reply_markup=export_menu())

    @router.message(F.text == "📊 Savdolar (Excel)")
    async def msg_export_sales_range(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.set_state(AdminExportSalesRange.start)
        await message.answer("Savdolar eksporti: start sana (YYYY-MM-DD):", reply_markup=export_menu())

    @router.message(F.text == "🔙 Orqaga")
    async def msg_admin_back(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        await state.clear()
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚙️ ADMIN PANELI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi bo'limlardan birini tanlang:"
        )
        await message.answer(text, reply_markup=main_menu_admin(), parse_mode="HTML")

    # Mijozlar uchun reply keyboard handlers
    @router.message(F.text == "👤 Shaxsiy kabinet")
    async def msg_customer_profile(message: Message) -> None:
        customer = await get_customer_by_chat(db, chat_id=message.from_user.id)
        if not customer:
            await message.answer("Telefonni yuboring:", reply_markup=ask_phone_keyboard())
            return
        level_emoji = {"Bronze": "🥉", "Silver": "🥈", "Gold": "🥇"}.get(customer.level, "⭐")
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 SHAXSIY KABINET\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 Ism: <b>{customer.full_name}</b>\n"
            f"📱 Telefon: <code>{customer.phone}</code>\n\n"
            f"💰 Jami savdo:\n"
            f"   <b>{fmt_amount(customer.total_spent)}</b>\n\n"
            f"{level_emoji} Daraja: <b>{customer.level}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await message.answer(text, reply_markup=main_menu_customer(), parse_mode="HTML")

    @router.message(F.text == "💰 Mening savdolarim")
    async def msg_customer_total(message: Message) -> None:
        customer = await get_customer_by_chat(db, chat_id=message.from_user.id)
        if not customer:
            await message.answer("Telefonni yuboring:", reply_markup=ask_phone_keyboard())
            return
        all_sales = await list_sales_for_customer(db, customer_id=customer.id, limit=10000)
        sales_count = len(all_sales)
        today = date.today()
        month_start = date(today.year, today.month, 1)
        month_sales = [s for s in all_sales if s['sale_date'] >= month_start.isoformat()]
        month_total = sum(int(s['amount']) for s in month_sales)
        level_emoji = {"Bronze": "🥉", "Silver": "🥈", "Gold": "🥇"}.get(customer.level, "⭐")
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💰 MENING SAVDOLARIM\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 Umumiy:\n"
            f"   <b>{fmt_amount(customer.total_spent)}</b>\n"
            f"   Savdolar soni: <b>{sales_count}</b> ta\n\n"
            f"📅 Bu oy:\n"
            f"   <b>{fmt_amount(month_total)}</b>\n"
            f"   Savdolar: <b>{len(month_sales)}</b> ta\n\n"
            f"{level_emoji} Daraja: <b>{customer.level}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await message.answer(text, reply_markup=main_menu_customer(), parse_mode="HTML")

    @router.message(F.text == "🧾 Savdo tarixi")
    async def msg_customer_history(message: Message) -> None:
        customer = await get_customer_by_chat(db, chat_id=message.from_user.id)
        if not customer:
            await message.answer("Telefonni yuboring:", reply_markup=ask_phone_keyboard())
            return
        sales = await list_sales_for_customer(db, customer_id=customer.id, limit=30)
        if not sales:
            text = (
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🧾 SAVDO TARIXI\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "❌ Savdo tarixi bo'sh.\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
            await message.answer(text, reply_markup=main_menu_customer(), parse_mode="HTML")
            return
        total = sum(int(s['amount']) for s in sales)
        lines = []
        for s in sales[:30]:
            lines.append(f"📅 {s['sale_date']}\n   💰 {fmt_amount(int(s['amount']))}\n   📦 {s['product']}\n")
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🧾 SAVDO TARIXI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 Jami: <b>{fmt_amount(total)}</b>\n"
            f"📈 Savdolar: <b>{len(sales)}</b> ta\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(lines) +
            "\n━━━━━━━━━━━━━━━━━━━━"
        )
        await message.answer(text, reply_markup=customer_history_filters(), parse_mode="HTML")

    @router.message(F.text == "🎁 Bonuslar")
    async def msg_customer_rewards(message: Message) -> None:
        customer = await get_customer_by_chat(db, chat_id=message.from_user.id)
        if not customer:
            await message.answer("Telefonni yuboring:", reply_markup=ask_phone_keyboard())
            return
        rewards = await list_rewards(db, customer_id=customer.id, limit=30)
        need_50 = max(0, 50_000_000 - customer.total_spent)
        need_100 = max(0, 100_000_000 - customer.total_spent)
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 BONUSLAR VA YUTUQLAR\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        if rewards:
            text += "✅ Olingan bonuslar:\n"
            for r in rewards:
                emoji = "🏆" if r['reward_type'] == 'threshold' else "🎁"
                text += f"   {emoji} <b>{r['reward_name']}</b>\n"
            text += "\n"
        else:
            text += "❌ Hozircha bonus yo'q.\n\n"
        text += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎯 Keyingi bosqich:\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🥈 Chang yutqich (50M):\n"
            f"   Qolgan: <b>{fmt_amount(need_50)}</b>\n\n"
            f"🥇 Super yutuq (100M):\n"
            f"   Qolgan: <b>{fmt_amount(need_100)}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await message.answer(text, reply_markup=main_menu_customer(), parse_mode="HTML")

    @router.message(F.text == "⬅️ Asosiy menyuga qaytish")
    async def msg_customer_back_to_menu(message: Message, state: FSMContext) -> None:
        await state.clear()
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 MIJOZ PANELI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi bo'limlardan birini tanlang:"
        )
        await message.answer(text, reply_markup=main_menu_customer(), parse_mode="HTML")

    @router.callback_query(F.data == "admin:menu")
    async def cb_admin_menu(cb: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚙️ ADMIN PANELI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi bo'limlardan birini tanlang:"
        )
        # Reply keyboard qaytaramiz (input tagida ko'rinadi)
        await cb.message.answer(text, reply_markup=main_menu_admin(), parse_mode="HTML")
        await cb.answer()

    @router.callback_query(F.data == "c:menu")
    async def cb_customer_menu(cb: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 MIJOZ PANELI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi bo'limlardan birini tanlang:"
        )
        # Reply keyboard qaytaramiz (input tagida ko'rinadi)
        await cb.message.answer(text, reply_markup=main_menu_customer(), parse_mode="HTML")
        await cb.answer()

    # =========================
    # ADMIN: Customers
    # =========================
    @router.callback_query(F.data == "admin:customers")
    async def cb_customers(cb: CallbackQuery) -> None:
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 MIJOZLAR BOSHQARISH\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi amallardan birini tanlang:"
        )
        await cb.message.edit_text(text, reply_markup=customers_menu_inline(), parse_mode="HTML")
        await cb.answer()

    @router.callback_query(F.data == "admin:customer_add")
    async def cb_customer_add(cb: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AdminCustomerAdd.full_name)
        await cb.message.edit_text("Yangi mijoz ismini kiriting:")
        await cb.answer()

    @router.message(AdminCustomerAdd.full_name)
    async def st_customer_add_name(message: Message, state: FSMContext) -> None:
        await state.update_data(full_name=message.text.strip())
        await state.set_state(AdminCustomerAdd.phone)
        await message.answer("Telefon raqam (faqat raqam): masalan 998901234567")

    @router.message(AdminCustomerAdd.phone)
    async def st_customer_add_phone(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        phone = re.sub(r"[^\d]", "", message.text or "")
        if len(phone) < 9:
            await message.answer("Telefon noto‘g‘ri. Qayta kiriting.")
            return
        data = await state.get_data()
        cid = await create_customer(
            db,
            full_name=data["full_name"],
            phone=phone,
            chat_id=None,
            tz=cfg.tz,
            actor_telegram_id=message.from_user.id,
        )
        await state.clear()
        await message.answer(f"Mijoz qo‘shildi. ID: {cid}", reply_markup=main_menu_admin())

    @router.callback_query(F.data == "admin:customer_list")
    async def cb_customer_list(cb: CallbackQuery) -> None:
        rows = await list_customers(db, limit=50)
        if not rows:
            await cb.message.edit_text("Mijozlar yo‘q.", reply_markup=back_to_menu("admin"))
            await cb.answer()
            return
        text = "Mijozlar (oxirgi 50):\n\n" + "\n".join(
            [f"#{c.id} {c.full_name} | {c.phone} | {c.status} | {fmt_amount(c.total_spent)} | {c.level}" for c in rows]
        )
        await cb.message.edit_text(text, reply_markup=back_to_menu("admin"))
        await cb.answer()

    @router.callback_query(F.data == "admin:customer_search")
    async def cb_customer_search(cb: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AdminCustomerSearch.query)
        await cb.message.edit_text("Qidiruv: ism/telefon/ID kiriting:")
        await cb.answer()

    @router.message(AdminCustomerSearch.query)
    async def st_customer_search(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        q = (message.text or "").strip()
        res = await find_customer(db, query=q, limit=20)
        await state.clear()
        if not res:
            await message.answer("Topilmadi.", reply_markup=main_menu_admin())
            return
        text = "Natija:\n\n" + "\n".join([f"#{c.id} {c.full_name} | {c.phone} | {c.status}" for c in res])
        text += "\n\nStatus o‘zgartirish: `status ID active` yoki `status ID inactive`"
        await message.answer(text, reply_markup=main_menu_admin(), parse_mode="Markdown")

    @router.message(F.text.regexp(r"^status\s+\d+\s+(active|inactive)$"))
    async def cmd_status(message: Message) -> None:
        if not is_admin(message.from_user.id):
            return
        parts = (message.text or "").split()
        customer_id = int(parts[1])
        status = parts[2]
        cust = await get_customer(db, customer_id=customer_id)
        if not cust:
            await message.answer("Mijoz topilmadi.")
            return
        await set_customer_status(db, customer_id=customer_id, status=status, tz=cfg.tz, actor_telegram_id=message.from_user.id)
        await message.answer(f"OK. #{customer_id} status -> {status}")

    # =========================
    # ADMIN: Sales
    # =========================
    @router.callback_query(F.data == "admin:sales")
    async def cb_sales(cb: CallbackQuery) -> None:
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💰 SAVDO OPERATSIYALARI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi amallardan birini tanlang:"
        )
        await cb.message.edit_text(text, reply_markup=sales_menu(), parse_mode="HTML")
        await cb.answer()

    @router.callback_query(F.data == "admin:sale_add")
    async def cb_sale_add(cb: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AdminSaleAdd.customer_query)
        await cb.message.edit_text("Mijoz tanlang: ism/telefon/ID yozing:")
        await cb.answer()

    @router.message(AdminSaleAdd.customer_query)
    async def st_sale_customer(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        q = (message.text or "").strip()
        res = await find_customer(db, query=q, limit=5)
        if not res:
            await message.answer("Mijoz topilmadi. Qayta kiriting.")
            return
        c = res[0]
        await state.update_data(customer_id=c.id)
        await state.set_state(AdminSaleAdd.amount)
        await message.answer(f"Tanlandi: #{c.id} {c.full_name}\nSumma kiriting (so‘m):")

    @router.message(AdminSaleAdd.amount)
    async def st_sale_amount(message: Message, state: FSMContext) -> None:
        amount = parse_amount(message.text or "")
        if amount is None or amount <= 0:
            await message.answer("Summa noto‘g‘ri. Qayta kiriting.")
            return
        await state.update_data(amount=amount)
        await state.set_state(AdminSaleAdd.product)
        await message.answer("Mahsulot/tovar nomi:")

    @router.message(AdminSaleAdd.product)
    async def st_sale_product(message: Message, state: FSMContext) -> None:
        product = (message.text or "").strip()
        if len(product) < 2:
            await message.answer("Mahsulot nomi qisqa. Qayta kiriting.")
            return
        await state.update_data(product=product)
        await state.set_state(AdminSaleAdd.comment)
        await message.answer("Izoh (ixtiyoriy). Bo‘sh qoldirsangiz ham bo‘ladi:")

    @router.message(AdminSaleAdd.comment)
    async def st_sale_comment(message: Message, state: FSMContext) -> None:
        comment = (message.text or "").strip()
        await state.update_data(comment=comment)
        await state.set_state(AdminSaleAdd.date)
        await message.answer("Sana (YYYY-MM-DD) yoki `0` (bugun):")

    @router.message(AdminSaleAdd.date)
    async def st_sale_date(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        raw = (message.text or "").strip()
        if raw == "0":
            sale_date = date.today().isoformat()
        else:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
                await message.answer("Format noto‘g‘ri. YYYY-MM-DD yoki 0.")
                return
            sale_date = raw

        data = await state.get_data()
        customer_id = int(data["customer_id"])
        amount = int(data["amount"])
        product = str(data["product"])
        comment = str(data.get("comment") or "")
        sale_id, earned = await add_sale(
            db,
            customer_id=customer_id,
            amount=amount,
            product=product,
            comment=comment,
            sale_date=sale_date,
            tz=cfg.tz,
            actor_telegram_id=message.from_user.id,
        )
        await state.clear()

        cust = await get_customer(db, customer_id=customer_id)
        txt = (
            f"✅ Savdo qo‘shildi. SaleID={sale_id}\n"
            f"Mijoz: #{customer_id} {cust.full_name}\n"
            f"Summa: {fmt_amount(amount)}\n"
            f"Mahsulot: {product}\n"
            f"Sana: {sale_date}"
        )
        if earned:
            txt += "\n\n🎁 Bonuslar: " + ", ".join(earned)
        await message.answer(txt, reply_markup=main_menu_admin())

        # Client notification
        if cust and cust.chat_id:
            try:
                await message.bot.send_message(cust.chat_id, f"Siz bugun {fmt_amount(amount)} so'mlik {product} xarid qildingiz")
                for b in earned:
                    await message.bot.send_message(cust.chat_id, f"Tabriklaymiz! Siz {b} sovg'asini qo'lga kiritdingiz")
            except Exception:
                pass

    @router.callback_query(F.data == "admin:sale_delete_last")
    async def cb_sale_delete_last(cb: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AdminReportCustomerHistory.customer_query)
        await cb.message.edit_text("Oxirgi savdoni o‘chirish: mijoz ism/telefon/ID kiriting:")
        await cb.answer()

    @router.message(AdminReportCustomerHistory.customer_query)
    async def st_delete_last_sale(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        q = (message.text or "").strip()
        res = await find_customer(db, query=q, limit=5)
        await state.clear()
        if not res:
            await message.answer("Mijoz topilmadi.", reply_markup=main_menu_admin())
            return
        c = res[0]
        sale_id = await delete_last_sale(db, customer_id=c.id, tz=cfg.tz, actor_telegram_id=message.from_user.id)
        if sale_id is None:
            await message.answer("Savdo topilmadi.", reply_markup=main_menu_admin())
            return
        await message.answer(f"🗑 Oxirgi savdo o‘chirildi. SaleID={sale_id} (mijoz #{c.id})", reply_markup=main_menu_admin())

    # =========================
    # ADMIN: Reports
    # =========================
    @router.callback_query(F.data == "admin:reports")
    async def cb_reports(cb: CallbackQuery) -> None:
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📊 STATISTIKA VA HISOBOTLAR\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi hisobotlardan birini tanlang:"
        )
        await cb.message.edit_text(text, reply_markup=reports_menu_inline(), parse_mode="HTML")
        await cb.answer()

    @router.callback_query(F.data == "admin:report_monthly")
    async def cb_report_monthly(cb: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AdminReportMonthly.year_month)
        await cb.message.edit_text("Oylik hisobot: YYYY-MM kiriting (masalan 2026-02):")
        await cb.answer()

    @router.message(AdminReportMonthly.year_month)
    async def st_report_monthly(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        ym = (message.text or "").strip()
        if not re.match(r"^\d{4}-\d{2}$", ym):
            await message.answer("Format noto‘g‘ri. YYYY-MM.")
            return
        y, m = ym.split("-")
        rep = await monthly_report(db, year=int(y), month=int(m))
        await state.clear()
        text = (
            f"📅 Oylik hisobot ({rep['start']} .. {rep['end']})\n"
            f"Jami: {fmt_amount(rep['total'])}\n"
            f"Savdolar soni: {rep['count']}\n"
            f"O‘tgan oy: {fmt_amount(rep['prev_total'])}\n"
            f"O‘sish: {rep['growth_pct']:.2f}%\n\n"
            "Top 5:\n"
            + "\n".join([f"- #{t['customer_id']} {t['full_name']} ({t['phone']}): {fmt_amount(int(t['sum_amount']))}" for t in rep["top5"]])
        )
        await message.answer(text, reply_markup=main_menu_admin())

    @router.callback_query(F.data == "admin:report_customer_history")
    async def cb_report_customer_history(cb: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AdminReportCustomerHistory.customer_query)
        await cb.message.edit_text("Mijoz tarixi: ism/telefon/ID kiriting:")
        await cb.answer()

    @router.message(AdminReportCustomerHistory.customer_query)
    async def st_report_customer_history(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        q = (message.text or "").strip()
        res = await find_customer(db, query=q, limit=5)
        await state.clear()
        if not res:
            await message.answer("Topilmadi.", reply_markup=main_menu_admin())
            return
        c = res[0]
        sales = await list_sales_for_customer(db, customer_id=c.id, limit=50)
        if not sales:
            await message.answer("Savdo yo‘q.", reply_markup=main_menu_admin())
            return
        lines = [f"#{s['id']} {s['sale_date']} | {fmt_amount(int(s['amount']))} | {s['product']}" for s in sales]
        await message.answer(f"👤 #{c.id} {c.full_name} tarixi (oxirgi 50):\n\n" + "\n".join(lines), reply_markup=main_menu_admin())

    @router.callback_query(F.data == "admin:report_range")
    async def cb_report_range(cb: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AdminReportRange.start)
        await cb.message.edit_text("Boshlanish sana (YYYY-MM-DD):")
        await cb.answer()

    @router.message(AdminReportRange.start)
    async def st_report_range_start(message: Message, state: FSMContext) -> None:
        s = (message.text or "").strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            await message.answer("Format noto‘g‘ri. YYYY-MM-DD.")
            return
        await state.update_data(start=s)
        await state.set_state(AdminReportRange.end)
        await message.answer("Tugash sana (YYYY-MM-DD):")

    @router.message(AdminReportRange.end)
    async def st_report_range_end(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        e = (message.text or "").strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", e):
            await message.answer("Format noto‘g‘ri. YYYY-MM-DD.")
            return
        data = await state.get_data()
        start = data["start"]
        await state.clear()
        docs = await sales_between(db, start_date=start, end_date=e)
        total = sum(int(d["amount"]) for d in docs)
        text = f"📆 Hisobot ({start} .. {e})\nSavdolar: {len(docs)}\nJami: {fmt_amount(total)}"
        await message.answer(text, reply_markup=main_menu_admin())

    # =========================
    # ADMIN: Bonuses
    # =========================
    @router.callback_query(F.data == "admin:bonuses")
    async def cb_bonuses(cb: CallbackQuery) -> None:
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 BONUS TIZIMI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi amallardan birini tanlang:"
        )
        await cb.message.edit_text(text, reply_markup=bonuses_menu(), parse_mode="HTML")
        await cb.answer()

    @router.callback_query(F.data == "admin:bonus_list")
    async def cb_bonus_list(cb: CallbackQuery) -> None:
        await cb.message.edit_text(
            "Bonuslar ro‘yxati:\n\n- 50 000 000 so‘m: Chang yutqich\n- 100 000 000 so‘m: Super yutuq",
            reply_markup=back_to_menu("admin"),
        )
        await cb.answer()

    @router.callback_query(F.data == "admin:bonus_manual_add")
    async def cb_manual_reward(cb: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AdminManualReward.customer_query)
        await cb.message.edit_text("Yutuq kiritish: mijoz ism/telefon/ID kiriting:")
        await cb.answer()

    @router.message(AdminManualReward.customer_query)
    async def st_manual_reward_customer(message: Message, state: FSMContext) -> None:
        q = (message.text or "").strip()
        res = await find_customer(db, query=q, limit=5)
        if not res:
            await message.answer("Topilmadi. Qayta kiriting.")
            return
        c = res[0]
        await state.update_data(customer_id=c.id)
        await state.set_state(AdminManualReward.reward_name)
        await message.answer(f"Tanlandi: #{c.id} {c.full_name}\nYutuq nomi:")

    @router.message(AdminManualReward.reward_name)
    async def st_manual_reward_name(message: Message, state: FSMContext) -> None:
        name = (message.text or "").strip()
        if len(name) < 2:
            await message.answer("Nom qisqa. Qayta kiriting.")
            return
        await state.update_data(reward_name=name)
        await state.set_state(AdminManualReward.note)
        await message.answer("Izoh (ixtiyoriy):")

    @router.message(AdminManualReward.note)
    async def st_manual_reward_note(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        data = await state.get_data()
        customer_id = int(data["customer_id"])
        reward_name = str(data["reward_name"])
        note = (message.text or "").strip()
        await state.clear()
        rid = await add_manual_reward(db, customer_id=customer_id, reward_name=reward_name, note=note, tz=cfg.tz, actor_telegram_id=message.from_user.id)
        cust = await get_customer(db, customer_id=customer_id)
        await message.answer(f"✅ Yutuq kiritildi. RewardID={rid}", reply_markup=main_menu_admin())
        if cust and cust.chat_id:
            try:
                await message.bot.send_message(cust.chat_id, f"Tabriklaymiz! Siz {reward_name} sovg'asini qo'lga kiritdingiz")
            except Exception:
                pass

    @router.callback_query(F.data == "admin:winners_monthly")
    async def cb_winners_monthly(cb: CallbackQuery) -> None:
        today = date.today()
        rep = await monthly_report(db, year=today.year, month=today.month)
        text = "🏆 Oylik g‘oliblar (Top 5):\n\n" + "\n".join(
            [f"- #{t['customer_id']} {t['full_name']} ({t['phone']}): {fmt_amount(int(t['sum_amount']))}" for t in rep["top5"]]
        )
        await cb.message.edit_text(text, reply_markup=back_to_menu("admin"))
        await cb.answer()

    # =========================
    # ADMIN: Broadcast
    # =========================
    @router.callback_query(F.data == "admin:broadcast")
    async def cb_broadcast(cb: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AdminBroadcast.audience)
        await cb.message.edit_text("Kimga yuborilsin? `all` yoki `active` deb yozing:")
        await cb.answer()

    @router.message(AdminBroadcast.audience)
    async def st_broadcast_audience(message: Message, state: FSMContext) -> None:
        a = (message.text or "").strip().lower()
        if a not in ("all", "active"):
            await message.answer("Faqat `all` yoki `active`.")
            return
        await state.update_data(audience=a)
        await state.set_state(AdminBroadcast.text)
        targets = await (all_customers_with_chat(db) if a == "all" else active_customers_with_chat(db))
        await message.answer(f"Xabar matnini yuboring.\nAuditoriya: <b>{len(targets)}</b> ta foydalanuvchi.", parse_mode="HTML")

    @router.message(AdminBroadcast.text)
    async def st_broadcast_text(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        data = await state.get_data()
        await state.clear()
        audience = data["audience"]
        text = message.text or ""
        targets = await (all_customers_with_chat(db) if audience == "all" else active_customers_with_chat(db))
        ok = 0
        for c in targets:
            try:
                await message.bot.send_message(int(c.chat_id), text)
                ok += 1
            except Exception:
                continue
        await message.answer(f"✅ Yuborildi: {ok}/{len(targets)}", reply_markup=main_menu_admin())

    # =========================
    # ADMIN: Export
    # =========================
    @router.callback_query(F.data == "admin:export")
    async def cb_export(cb: CallbackQuery) -> None:
        await cb.message.edit_text("Eksport:", reply_markup=export_menu_inline())
        await cb.answer()

    @router.callback_query(F.data == "admin:export_customers_xlsx")
    async def cb_export_customers_xlsx(cb: CallbackQuery) -> None:
        rows = await list_customers(db, limit=5000)
        data = [c.__dict__ for c in rows]
        bio = customers_to_xlsx(data)
        await cb.message.answer_document(("customers.xlsx", bio), caption="Mijozlar ro‘yxati (Excel)")
        await cb.answer()

    @router.callback_query(F.data == "admin:export_customers_pdf")
    async def cb_export_customers_pdf(cb: CallbackQuery) -> None:
        rows = await list_customers(db, limit=5000)
        data = [c.__dict__ for c in rows]
        bio = customers_to_pdf(data)
        await cb.message.answer_document(("customers.pdf", bio), caption="Mijozlar ro‘yxati (PDF)")
        await cb.answer()

    @router.callback_query(F.data == "admin:export_sales_range_xlsx")
    async def cb_export_sales_range(cb: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AdminExportSalesRange.start)
        await cb.message.edit_text("Savdolar eksporti: start sana (YYYY-MM-DD):")
        await cb.answer()

    @router.message(AdminExportSalesRange.start)
    async def st_export_sales_start(message: Message, state: FSMContext) -> None:
        s = (message.text or "").strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            await message.answer("Format noto‘g‘ri.")
            return
        await state.update_data(start=s)
        await state.set_state(AdminExportSalesRange.end)
        await message.answer("End sana (YYYY-MM-DD):")

    @router.message(AdminExportSalesRange.end)
    async def st_export_sales_end(message: Message, state: FSMContext) -> None:
        if not is_admin(message.from_user.id):
            return
        e = (message.text or "").strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", e):
            await message.answer("Format noto‘g‘ri.")
            return
        data = await state.get_data()
        start = data["start"]
        await state.clear()
        docs = await sales_between(db, start_date=start, end_date=e)
        bio = sales_to_xlsx(docs)
        await message.answer_document((f"sales_{start}_{e}.xlsx", bio), caption=f"Savdolar ({start}..{e})")

    # =========================
    # CUSTOMER PANEL
    # =========================
    @router.callback_query(F.data == "c:profile")
    async def cb_profile(cb: CallbackQuery) -> None:
        customer = await get_customer_by_chat(db, chat_id=cb.from_user.id)
        if not customer:
            await cb.message.answer("Telefonni yuboring:", reply_markup=ask_phone_keyboard())
            await cb.answer()
            return
        text = (
            "👤 Kabinet\n\n"
            f"Ism: {customer.full_name}\n"
            f"Telefon: {customer.phone}\n"
            f"Jami savdo: {fmt_amount(customer.total_spent)}\n"
            f"Daraja: {customer.level}\n"
        )
        await cb.message.edit_text(text, reply_markup=back_to_menu("customer"))
        await cb.answer()

    @router.callback_query(F.data == "c:history")
    async def cb_history(cb: CallbackQuery) -> None:
        customer = await get_customer_by_chat(db, chat_id=cb.from_user.id)
        if not customer:
            await cb.message.answer("Telefonni yuboring:", reply_markup=ask_phone_keyboard())
            await cb.answer()
            return
        sales = await list_sales_for_customer(db, customer_id=customer.id, limit=30)
        if not sales:
            text = (
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🧾 SAVDO TARIXI\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "❌ Savdo tarixi bo'sh.\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
            await cb.message.edit_text(text, reply_markup=back_to_menu("customer"), parse_mode="HTML")
            await cb.answer()
            return
        
        total = sum(int(s['amount']) for s in sales)
        lines = []
        for s in sales[:30]:
            lines.append(f"📅 {s['sale_date']}\n   💰 {fmt_amount(int(s['amount']))}\n   📦 {s['product']}\n")
        
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🧾 SAVDO TARIXI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 Jami: <b>{fmt_amount(total)}</b>\n"
            f"📈 Savdolar: <b>{len(sales)}</b> ta\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(lines) +
            "\n━━━━━━━━━━━━━━━━━━━━"
        )
        await cb.message.edit_text(text, reply_markup=customer_history_filters(), parse_mode="HTML")
        await cb.answer()

    @router.callback_query(F.data.startswith("c:filter:"))
    async def cb_history_filter(cb: CallbackQuery) -> None:
        """Savdo tarixini filtrlash"""
        customer = await get_customer_by_chat(db, chat_id=cb.from_user.id)
        if not customer:
            await cb.answer("Telefonni yuboring:", show_alert=True)
            return
        
        filter_type = cb.data.split(":")[-1]
        all_sales = await list_sales_for_customer(db, customer_id=customer.id, limit=10000)
        
        today = date.today()
        filtered_sales = []
        
        if filter_type == "7days":
            cutoff = (today - timedelta(days=7)).isoformat()
            filtered_sales = [s for s in all_sales if s['sale_date'] >= cutoff]
            title = "📅 Oxirgi 7 kun"
        elif filter_type == "month":
            month_start = date(today.year, today.month, 1).isoformat()
            filtered_sales = [s for s in all_sales if s['sale_date'] >= month_start]
            title = "📅 Bu oy"
        elif filter_type == "year":
            year_start = date(today.year, 1, 1).isoformat()
            filtered_sales = [s for s in all_sales if s['sale_date'] >= year_start]
            title = "📅 Bu yil"
        else:  # all
            filtered_sales = all_sales[:100]  # limit
            title = "📋 Barcha savdolar"
        
        if not filtered_sales:
            text = (
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{title}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"❌ Savdo topilmadi.\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            )
            await cb.message.edit_text(text, reply_markup=customer_history_filters(), parse_mode="HTML")
            await cb.answer()
            return
        
        total = sum(int(s['amount']) for s in filtered_sales)
        lines = []
        for s in filtered_sales[:50]:  # max 50
            lines.append(f"📅 {s['sale_date']}\n   💰 {fmt_amount(int(s['amount']))}\n   📦 {s['product']}\n")
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{title}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 Jami: <b>{fmt_amount(total)}</b>\n"
            f"📈 Savdolar: <b>{len(filtered_sales)}</b> ta\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(lines) +
            "\n━━━━━━━━━━━━━━━━━━━━"
        )
        await cb.message.edit_text(text, reply_markup=customer_history_filters(), parse_mode="HTML")
        await cb.answer()

    @router.callback_query(F.data == "c:rewards")
    async def cb_rewards(cb: CallbackQuery) -> None:
        customer = await get_customer_by_chat(db, chat_id=cb.from_user.id)
        if not customer:
            await cb.message.answer("Telefonni yuboring:", reply_markup=ask_phone_keyboard())
            await cb.answer()
            return
        rewards = await list_rewards(db, customer_id=customer.id, limit=30)
        need_50 = max(0, 50_000_000 - customer.total_spent)
        need_100 = max(0, 100_000_000 - customer.total_spent)
        
        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 BONUSLAR VA YUTUQLAR\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        if rewards:
            text += "✅ Olingan bonuslar:\n"
            for r in rewards:
                emoji = "🏆" if r['reward_type'] == 'threshold' else "🎁"
                text += f"   {emoji} <b>{r['reward_name']}</b>\n"
            text += "\n"
        else:
            text += "❌ Hozircha bonus yo'q.\n\n"
        
        text += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎯 Keyingi bosqich:\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🥈 Chang yutqich (50M):\n"
            f"   Qolgan: <b>{fmt_amount(need_50)}</b>\n\n"
            f"🥇 Super yutuq (100M):\n"
            f"   Qolgan: <b>{fmt_amount(need_100)}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await cb.message.edit_text(text, reply_markup=back_to_menu("customer"), parse_mode="HTML")
        await cb.answer()

    return router

