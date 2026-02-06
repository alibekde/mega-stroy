from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu_admin() -> ReplyKeyboardMarkup:
    """Admin uchun asosiy reply keyboard - input tagida ko'rinadi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Mijozlar"), KeyboardButton(text="💰 Savdo")],
            [KeyboardButton(text="📊 Hisobotlar"), KeyboardButton(text="🎁 Bonuslar")],
            [KeyboardButton(text="📢 Xabar yuborish"), KeyboardButton(text="📤 Eksport")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Buyruq yoki matn kiriting...",
    )


def main_menu_admin_inline() -> InlineKeyboardMarkup:
    """Admin uchun inline keyboard (callback uchun)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Mijozlar", callback_data="admin:customers")],
            [InlineKeyboardButton(text="💰 Savdo", callback_data="admin:sales")],
            [InlineKeyboardButton(text="📊 Hisobotlar", callback_data="admin:reports")],
            [InlineKeyboardButton(text="🎁 Bonuslar", callback_data="admin:bonuses")],
            [InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin:broadcast")],
            [InlineKeyboardButton(text="📤 Eksport", callback_data="admin:export")],
        ]
    )


def main_menu_customer() -> ReplyKeyboardMarkup:
    """Mijoz uchun asosiy reply keyboard - input tagida ko'rinadi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Shaxsiy kabinet"), KeyboardButton(text="💰 Mening savdolarim")],
            [KeyboardButton(text="🧾 Savdo tarixi"), KeyboardButton(text="🎁 Bonuslar")],
            [KeyboardButton(text="⬅️ Asosiy menyuga qaytish")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Matn kiriting...",
    )


def main_menu_customer_inline() -> InlineKeyboardMarkup:
    """Mijoz uchun inline keyboard (callback uchun)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Shaxsiy kabinet", callback_data="c:profile")],
            [InlineKeyboardButton(text="💰 Mening savdolarim", callback_data="c:total")],
            [InlineKeyboardButton(text="🧾 Savdo tarixi", callback_data="c:history")],
            [InlineKeyboardButton(text="🎁 Bonuslar", callback_data="c:rewards")],
        ]
    )


def back_to_menu(role: str) -> InlineKeyboardMarkup:
    cb = "admin:menu" if role == "admin" else "c:menu"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Menyuga qaytish", callback_data=cb)]])


def customers_menu_reply() -> ReplyKeyboardMarkup:
    """Mijozlar submenyu - input tagida ko'rinadi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Yangi mijoz qo'shish")],
            [KeyboardButton(text="📋 Mijozlar ro'yxati")],
            [KeyboardButton(text="🔍 Qidirish")],
            [KeyboardButton(text="🗑️ Mijozni o'chirish")],
            [KeyboardButton(text="🔙 Orqaga")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Buyruq yoki matn kiriting...",
    )


def customers_menu() -> ReplyKeyboardMarkup:
    return customers_menu_reply()


def sales_menu_reply() -> ReplyKeyboardMarkup:
    """Savdo submenyu - input tagida ko'rinadi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Yangi savdo kiritish")],
            [KeyboardButton(text="🗑️ Oxirgi savdoni o'chirish")],
            [KeyboardButton(text="🗑️ Savdoni ID bo'yicha o'chirish")],
            [KeyboardButton(text="🔙 Orqaga")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Buyruq yoki matn kiriting...",
    )


def sales_menu() -> ReplyKeyboardMarkup:
    return sales_menu_reply()


def reports_menu_reply() -> ReplyKeyboardMarkup:
    """Hisobotlar submenyu - input tagida ko'rinadi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Oylik hisobot")],
            [KeyboardButton(text="👤 Mijoz tarixi")],
            [KeyboardButton(text="📆 Sana oralig'i hisobot")],
            [KeyboardButton(text="🔙 Orqaga")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Buyruq yoki matn kiriting...",
    )


def reports_menu() -> ReplyKeyboardMarkup:
    return reports_menu_reply()


def bonuses_menu_reply() -> ReplyKeyboardMarkup:
    """Bonuslar submenyu - input tagida ko'rinadi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📜 Bonuslar ro'yxati")],
            [KeyboardButton(text="➕ Yutuq kiritish")],
            [KeyboardButton(text="🗑️ Yutuqni o'chirish")],
            [KeyboardButton(text="🏆 Oylik g'oliblar")],
            [KeyboardButton(text="🔙 Orqaga")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Buyruq yoki matn kiriting...",
    )


def bonuses_menu() -> ReplyKeyboardMarkup:
    return bonuses_menu_reply()


def export_menu_reply() -> ReplyKeyboardMarkup:
    """Eksport submenyu - input tagida ko'rinadi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Mijozlar (PDF)")],
            [KeyboardButton(text="📊 Mijozlar (Excel)")],
            [KeyboardButton(text="📊 Savdolar (Excel)")],
            [KeyboardButton(text="🔙 Orqaga")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Buyruq yoki matn kiriting...",
    )


def export_menu() -> ReplyKeyboardMarkup:
    return export_menu_reply()


def customers_menu_inline() -> InlineKeyboardMarkup:
    """Callback uchun (eski inline)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yangi mijoz qo'shish", callback_data="admin:customer_add")],
            [InlineKeyboardButton(text="📋 Mijozlar ro'yxati", callback_data="admin:customer_list")],
            [InlineKeyboardButton(text="🔍 Qidirish", callback_data="admin:customer_search")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:menu")],
        ]
    )


def sales_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yangi savdo kiritish", callback_data="admin:sale_add")],
            [InlineKeyboardButton(text="🗑️ Oxirgi savdoni o'chirish", callback_data="admin:sale_delete_last")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:menu")],
        ]
    )


def reports_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Oylik hisobot", callback_data="admin:report_monthly")],
            [InlineKeyboardButton(text="👤 Mijoz tarixi", callback_data="admin:report_customer_history")],
            [InlineKeyboardButton(text="📆 Sana oralig'i hisobot", callback_data="admin:report_range")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:menu")],
        ]
    )


def bonuses_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📜 Bonuslar ro'yxati", callback_data="admin:bonus_list")],
            [InlineKeyboardButton(text="➕ Yutuq kiritish", callback_data="admin:bonus_manual_add")],
            [InlineKeyboardButton(text="🏆 Oylik g'oliblar", callback_data="admin:winners_monthly")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:menu")],
        ]
    )


def export_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Mijozlar (PDF)", callback_data="admin:export_customers_pdf")],
            [InlineKeyboardButton(text="📊 Mijozlar (Excel)", callback_data="admin:export_customers_xlsx")],
            [InlineKeyboardButton(text="📊 Savdolar (Excel)", callback_data="admin:export_sales_range_xlsx")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:menu")],
        ]
    )


def ask_phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
        selective=True,
    )


def customer_history_filters() -> InlineKeyboardMarkup:
    """Mijoz savdo tarixi uchun filtrlash tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Oxirgi 7 kun", callback_data="c:filter:7days")],
            [InlineKeyboardButton(text="📆 Bu oy", callback_data="c:filter:month")],
            [InlineKeyboardButton(text="📊 Bu yil", callback_data="c:filter:year")],
            [InlineKeyboardButton(text="📋 Barchasi", callback_data="c:filter:all")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="c:history")],
        ]
    )

