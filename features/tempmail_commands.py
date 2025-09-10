import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

# Token API từ tempmail.id.vn (lưu ý token chỉ hiển thị 1 lần khi tạo)
API_KEY = "5341|xY8Se18unOkA09mFh9Fb6hE1MycuYA67RPnAQkKa376f110d"

# Base URL chuẩn từ docs
BASE_URL = "https://tempmail.id.vn/api"

# 📧 Tạo email mới
async def tempmail_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/email/create", headers=headers, json={}) as resp:
            data = await resp.json()
    if "email" in data:
        await update.message.reply_text(f"📧 Email mới: {data['email']}")
    else:
        await update.message.reply_text(f"⚠️ Lỗi khi tạo email: {data}")

# 📭 Danh sách mail của bạn
async def tempmail_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/email", headers=headers) as resp:
            data = await resp.json()

    if isinstance(data, list) and data:
        reply = "✉️ Danh sách email:\n\n"
        for i, mail in enumerate(data[:5], 1):
            reply += f"{i}. {mail.get('email')} (ID: {mail.get('id')})\n"
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("📭 Không có email nào.")

# 📬 Danh sách thư trong inbox của 1 mail
async def tempmail_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /tempmail_inbox <mail_id>")
        return
    mail_id = context.args[0]
    headers = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/email/{mail_id}", headers=headers) as resp:
            data = await resp.json()

    inbox = data if isinstance(data, list) else []
    if not inbox:
        await update.message.reply_text("📭 Inbox trống.")
    else:
        reply = f"✉️ Inbox của mail {mail_id}:\n\n"
        for i, mail in enumerate(inbox[:5], 1):
            reply += f"{i}. {mail.get('from')} → {mail.get('subject')} (ID: {mail.get('id')})\n"
        await update.message.reply_text(reply)

# 📖 Đọc chi tiết thư theo ID
async def tempmail_read(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /tempmail_read <message_id>")
        return
    message_id = context.args[0]
    headers = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/message/{message_id}", headers=headers) as resp:
            data = await resp.json()

    if "subject" in data:
        await update.message.reply_text(
            f"📧 Từ: {data.get('from')}\n"
            f"📌 Tiêu đề: {data.get('subject')}\n\n"
            f"{data.get('body', 'Không có nội dung')}"
        )
    else:
        await update.message.reply_text(f"⚠️ Lỗi khi đọc mail: {data}")
# 🗑️ Xóa email theo ID
async def tempmail_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /tempmail_delete <mail_id>")
        return

    mail_id = context.args[0]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{BASE_URL}/email/{mail_id}", headers=headers) as resp:
            data = await resp.json()

    if "success" in data or resp.status == 200:
        await update.message.reply_text(f"🗑️ Đã xóa email ID {mail_id} thành công.")
    else:
        await update.message.reply_text(f"⚠️ Lỗi khi xóa email {mail_id}: {data}")
