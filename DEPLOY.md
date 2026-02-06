# Railway Deploy Qo'llanmasi

## Qadamlari

### 1. GitHub'ga yuklash

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mega_stroy.git
git push -u origin main
```

### 2. Railway'da loyiha yaratish

1. [railway.app](https://railway.app) ga kiring va login qiling
2. **"New Project"** → **"Deploy from GitHub repo"**
3. GitHub reponi tanlang
4. Railway avtomatik deploy qiladi

### 3. Environment Variables qo'shish

Railway dashboard → **Variables** bo'limida:

| Key | Value | Izoh |
|-----|-------|------|
| `BOT_TOKEN` | `123456:ABC...` | BotFather dan olingan token |
| `ADMIN_TELEGRAM_ID` | `123456789` | Sizning Telegram ID |
| `DB_PATH` | `/tmp/mega_stroy.sqlite3` | Database yo'li |
| `TZ` | `Asia/Tashkent` | Vaqt mintaqasi |

**Telegram ID ni qanday topish:**
- [@userinfobot](https://t.me/userinfobot) ga yuboring
- Yoki [@getidsbot](https://t.me/getidsbot) ga yuboring

### 4. Deploy tekshirish

1. Railway dashboard → **Deployments** → **View Logs**
2. Agar xatolik bo'lsa, loglarni ko'ring
3. Muvaffaqiyatli bo'lsa: **"Deployed successfully"** ko'rinadi

### 5. Botni sinash

Telegram'da botga `/start` yuboring va admin menyuni ko'ring.

---

## Xatoliklar va Yechimlar

### ❌ `ModuleNotFoundError: No module named 'aiogram'`

**Yechim:** Railway avtomatik o'rnatadi, lekin agar xatolik bo'lsa:
- Railway dashboard → **Settings** → **Build Command** → bo'sh qoldiring
- **Start Command:** `python -m app.main`

### ❌ `BOT_TOKEN .env da yo'q`

**Yechim:** Railway dashboard → **Variables** → `BOT_TOKEN` qo'shing

### ❌ `ADMIN_TELEGRAM_ID noto'g'ri`

**Yechim:** 
- `ADMIN_TELEGRAM_ID` raqam bo'lishi kerak
- Bir nechta admin: `ADMIN_TELEGRAM_IDS=123,456,789` (vergul bilan)

### ❌ Database xatolik

**Yechim:**
- Railway da `/tmp` ishlatiladi (vaqtinchalik)
- Doimiy saqlash uchun **Volume** qo'shing:
  1. Railway dashboard → **New** → **Volume**
  2. Mount path: `/data`
  3. `DB_PATH=/data/mega_stroy.sqlite3` qiling

### ❌ Bot ishlamayapti

**Yechim:**
1. Loglarni tekshiring: Railway → **Deployments** → **View Logs**
2. Environment variables to'g'ri ekanligini tekshiring
3. Bot token to'g'ri ekanligini tekshiring

---

## Database Backup

Railway da database `/tmp` da saqlanadi va restart qilinganda yo'qolishi mumkin. Doimiy saqlash uchun:

1. **Volume qo'shing** (yuqorida ko'rsatilgan)
2. Yoki **PostgreSQL** ishlating (Railway → New → Database → PostgreSQL)

---

## Monitoring

Railway dashboard → **Metrics** bo'limida:
- CPU foydalanish
- Memory foydalanish
- Network trafik
- Loglar

---

## Qo'shimcha Ma'lumot

- [Railway Docs](https://docs.railway.app)
- [Telegram Bot API](https://core.telegram.org/bots/api)
