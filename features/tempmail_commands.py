import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

# 🔑 API key tempmail (copy từ web của bạn)
API_KEY = "5341|xY8Se18unOkA09mFh9Fb6hE1MycuYA67RPnAQkKa376f110d"
BASE_URL = "https://tempmail.id.vn/api"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}


# 📧 Tạo email mới
async def tempmail_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/email/create", headers=HEADERS) as resp:
                data = await resp.json()
        await update.message.reply_text(f"📧 Email mới: {data.get('email')} (ID: {data.get('id')})")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi tạo email: {e}")


# 📭 Danh sách email
async def tempmail_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/email", headers=HEADERS) as resp:
                data = await resp.json()

        if not data:
            await update.message.reply_text("📭 Chưa có email nào.")
        else:
            reply = "📬 Danh sách email:\n"
            for mail in data:
                reply += f"- {mail.get('email')} (ID: {mail.get('id')})\n"
            await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi lấy danh sách: {e}")


# 📩 Chi tiết email theo ID
async def tempmail_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /tempmail_get {id}")
        return
    mail_id = context.args[0]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/email/{mail_id}", headers=HEADERS) as resp:
                data = await resp.json()
        await update.message.reply_text(f"📩 Email: {data}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi lấy email {mail_id}: {e}")


# 📨 Danh sách tin nhắn của 1 email
async def tempmail_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /tempmail_messages {id_email}")
        return
    mail_id = context.args[0]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/message/{mail_id}", headers=HEADERS) as resp:
                data = await resp.json()

        if not data:
            await update.message.reply_text("📭 Hộp thư trống.")
        else:
            reply = f"📨 Tin nhắn trong email {mail_id}:\n"
            for msg in data:
                reply += f"- ID: {msg.get('id')} | From: {msg.get('from')} | Subject: {msg.get('subject')}\n"
            await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi lấy tin nhắn: {e}")


# 📨 Chi tiết tin nhắn
async def tempmail_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /tempmail_message {id_message}")
        return
    msg_id = context.args[0]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/message/{msg_id}", headers=HEADERS) as resp:
                data = await resp.json()
        await update.message.reply_text(f"📨 Nội dung tin nhắn:\nFrom: {data.get('from')}\nSubject: {data.get('subject')}\n\n{data.get('body')}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi lấy tin nhắn {msg_id}: {e}")


# ❌ Xoá email
async def tempmail_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /tempmail_delete {id}")
        return
    mail_id = context.args[0]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{BASE_URL}/email/{mail_id}", headers=HEADERS) as resp:
                data = await resp.json()
        await update.message.reply_text(f"🗑️ Đã xoá email {mail_id}: {data}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi xoá email {mail_id}: {e}")


# 📖 Hướng dẫn
async def tempmail_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 Lệnh TempMail:\n"
        "/tempmail_create - Tạo email mới\n"
        "/tempmail_list - Danh sách email\n"
        "/tempmail_get {id} - Chi tiết 1 email\n"
        "/tempmail_messages {id_email} - Danh sách tin nhắn\n"
        "/tempmail_message {id_message} - Xem tin nhắn\n"
        "/tempmail_delete {id} - Xoá email\n"
        "/tempmail_help - Xem hướng dẫn"
    )
    await update.message.reply_text(help_text)
