import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

# Token API từ tempmail.id.vn
API_KEY = "5341|xY8Se18unOkA09mFh9Fb6hE1MycuYA67RPnAQkKa376f110d"

BASE_URL = "https://tempmail.id.vn/api/mail"

# 📧 Tạo email mới
async def tempmail_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/create", headers=headers) as resp:
            data = await resp.json()
    await update.message.reply_text(f"📧 Email mới: {data.get('email')}")

# 📭 Danh sách mail trong inbox
async def tempmail_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/list", headers=headers) as resp:
            data = await resp.json()
    inbox = data.get("inbox", [])
    if not inbox:
        await update.message.reply_text("📭 Inbox trống.")
    else:
        reply = "✉️ Inbox:\n\n"
        for i, mail in enumerate(inbox[:5], 1):
            reply += f"{i}. {mail.get('from')} → {mail.get('subject')} (ID: {mail.get('id')})\n"
        await update.message.reply_text(reply)

# 📖 Đọc chi tiết mail theo ID
async def tempmail_read(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /tempmail_read <id>")
        return
    mail_id = context.args[0]
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/read/{mail_id}", headers=headers) as resp:
            data = await resp.json()
    await update.message.reply_text(
        f"📧 Từ: {data.get('from')}\n"
        f"📌 Tiêu đề: {data.get('subject')}\n\n"
        f"{data.get('body', 'Không có nội dung')}"
    )

# 🗑️ Xóa mail theo ID
async def tempmail_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /tempmail_delete <id>")
        return
    mail_id = context.args[0]
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{BASE_URL}/delete/{mail_id}", headers=headers) as resp:
            data = await resp.json()
    await update.message.reply_text(f"🗑️ Xóa mail {mail_id}: {data}")
