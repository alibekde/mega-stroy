# Mega Stroy CRM Telegram Bot

Telegram bot orqali:
- Admin panel: mijozlar, savdolar, hisobotlar, bonuslar, xabarnomalar, eksport
- Mijoz panel: kabinet, savdo tarixi, bonuslar, shaxsiy xabarlar

## 🚀 Railway ga Deploy Qilish

### 1. Railway'da yangi loyiha yarating

1. [Railway.app](https://railway.app) ga kiring
2. "New Project" → "Deploy from GitHub repo" (yoki "Empty Project")
3. GitHub reponi tanlang yoki kodni yuklang

### 2. Environment Variables (O'zgaruvchilar) qo'shing

Railway dashboard → **Variables** bo'limida quyidagilarni qo'shing:

```env
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_TELEGRAM_ID=123456789
DB_PATH=/tmp/mega_stroy.sqlite3
TZ=Asia/Tashkent
```

**Muhim:**
- `BOT_TOKEN` - BotFather dan olingan token
- `ADMIN_TELEGRAM_ID` - Sizning Telegram ID (bir nechta bo'lsa: `123456789,987654321`)
- `DB_PATH` - Railway da `/tmp` ishlatiladi (doimiy saqlash uchun volume qo'shing)
- `TZ` - Vaqt mintaqasi

### 3. Deploy

Railway avtomatik ravishda:
- `requirements.txt` dan paketlarni o'rnatadi
- `Procfile` yoki `railway.json` bo'yicha botni ishga tushiradi

### 4. Botni tekshirish

Telegram'da botga `/start` yuboring va admin menyuni ko'ring.

---

## 💻 Lokal O'rnatish

### Talablar
- Python 3.11+ (tavsiya)
- Windows/Linux/Mac

### Qadamlari

1. **`.env` yarating** (`.env.example` dan nusxa qilib):

```env
BOT_TOKEN=your_bot_token
ADMIN_TELEGRAM_ID=123456789
DB_PATH=mega_stroy.sqlite3
TZ=Asia/Tashkent
```

2. **Kutubxonalarni o'rnating:**

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Botni ishga tushiring:**

```bash
python -m app.main
```

---

## 📖 Foydalanish

### Admin
- Botga `/start` → **Admin menyu** ko'rinadi
- **👤 Mijozlar** → Yangi mijoz qo'shish, ro'yxat, qidirish
- **💰 Savdo** → Savdo kiritish, oxirgi savdoni o'chirish
- **📊 Hisobotlar** → Oylik hisobot, mijoz tarixi, sana oralig'i
- **🎁 Bonuslar** → Bonuslar ro'yxati, yutuq kiritish, oylik g'oliblar
- **📢 Xabar yuborish** → Barcha yoki faol mijozlarga xabar
- **📤 Eksport** → PDF/Excel formatida eksport

### Mijoz
- Botga `/start` → Telefon raqamni yuborish
- Admin bazada telefon bo'lsa → **Mijoz menyu** ko'rinadi
- **👤 Shaxsiy kabinet** → Ma'lumotlar va jami savdo
- **💰 Jami savdo** → Umumiy va oylik statistika
- **🧾 Savdo tarixi** → Barcha xaridlar
- **🎁 Bonuslar** → Olingan bonuslar va keyingi bosqich

---

## 🔧 Xatolarni Tuzatish

### Railway'da xatolik bo'lsa:

1. **Loglarni tekshiring:** Railway dashboard → **Deployments** → **View Logs**
2. **Environment variables:** Barcha o'zgaruvchilar to'g'ri qo'shilganligini tekshiring
3. **Database:** `/tmp` da saqlanadi, lekin volume qo'shish tavsiya etiladi

### Umumiy xatolar:

- `ModuleNotFoundError` → `pip install -r requirements.txt` qayta bajaring
- `BOT_TOKEN yo'q` → `.env` faylida `BOT_TOKEN` ni tekshiring
- `ADMIN_TELEGRAM_ID noto'g'ri` → ID raqam ekanligini tekshiring

---

## 📝 Eslatma

- Mijozlar admin tomonidan qo'shiladi (ism + telefon)
- Mijoz botga birinchi marta `/start` qilganda telefon raqamini **Contact** sifatida yuboradi
- Admin bazada telefon bo'lsa, akkaunt avtomatik bog'lanadi
- Barcha amallar audit log'da saqlanadi
# mega_stroy
