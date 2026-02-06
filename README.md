## Mega Stroy CRM Telegram Bot

Telegram bot orqali:
- Admin panel: mijozlar, savdolar, hisobotlar, bonuslar, xabarnomalar, eksport
- Mijoz panel: kabinet, savdo tarixi, bonuslar, shaxsiy xabarlar

### Talablar
- Python 3.10+ (tavsiya 3.11)
- Windows/Linux/Mac

### O‘rnatish

1) `.env` yarating:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
ADMIN_TELEGRAM_ID=123456789
DB_PATH=mega_stroy.sqlite3
TZ=Asia/Tashkent
```

2) Kutubxonalar:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3) Ishga tushirish:

```bash
python -m app.main
```

### Admin ishlatishi (qisqa)
- Botga `/start`
- **Admin menyu** → **Mijoz qo‘shish** (ism, telefon)
- **Savdo qo‘shish** → mijoz tanlash → summa → mahsulot → izoh

### Eslatma
Mijoz botga birinchi kirganda `/start` qiladi va telefon raqamini **Contact** sifatida yuboradi (button bor). Admin bazada o‘sha telefon bo‘lsa, akkaunt chat_id bilan bog‘lanadi.

# mega_stroy
# mega_stroy_bot
# mega_stroy
# mega_stroy
