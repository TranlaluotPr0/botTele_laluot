import os
import json
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, Application, CommandHandler,
    MessageHandler, ContextTypes, filters
)
import pytz
from datetime import datetime

# === Tạo credentials.json tự động ===
CREDENTIAL_JSON = {
  "type": "service_account",
  "project_id": "telegrambot-460310",
  "private_key_id": "da8c8924eead97d61c9bc4e2656fc624a7454a3b",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCmkQFgcSZhyJL9...\\n-----END PRIVATE KEY-----\\n",
  "client_email": "telegram-bot-access@telegrambot-460310.iam.gserviceaccount.com",
  "token_uri": "https://oauth2.googleapis.com/token"
}
CREDENTIALS_PATH = "credentials.json"
if not os.path.exists(CREDENTIALS_PATH):
    with open(CREDENTIALS_PATH, "w", encoding="utf-8") as f:
        json.dump(CREDENTIAL_JSON, f)

# === Google Sheets ===
import gspread
from google.oauth2.service_account import Credentials
SHEET_ID = "16Jq_50T8hKGkgLkvbDlydnsoN-eHXSamCRq06sLMy8"
SHEET_NAME = "Trang tính1"
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

def append_to_sheet(data):
    sheet.append_row([data["id"], data["name"], data["size"], data["time"]])

# === Biến toàn cục ===
event_loop = None
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
received_files = []

# === Load env & cấu hình webhook ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# === Các lệnh bot ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Gõ /menu để xem các chức năng.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot đang hoạt động bình thường.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Danh sách lệnh có sẵn:\n"
        "/start - Bắt đầu\n"
        "/ping - Kiểm tra bot\n"
        "/menu - Danh sách lệnh\n"
        "/list - Xem file đã gửi\n"
        "/list_ngay <dd-mm-yyyy> - Lọc file theo ngày"
    )

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not received_files:
        await update.message.reply_text("📭 Chưa có file nào được gửi.")
        return
    username = context.bot.username
    text = "📂 Danh sách file đã gửi:\n\n"
    for f in received_files:
        text += (
            f"🆔 <b>ID:</b> <a href='tg://resolve?domain={username}&message_id={f['id']}'>{f['id']}</a>\n"
            f"📄 <b>Tên:</b> {f['name']}\n"
            f"📦 <b>Dung lượng:</b> {f['size']}\n"
            f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
        )
    await update.message.reply_html(text, disable_web_page_preview=True)

async def list_files_by_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📅 Dùng: /list_ngay dd-mm-yyyy")
        return
    filter_date = context.args[0].strip()
    try:
        datetime.strptime(filter_date, "%d-%m-%Y")
        username = context.bot.username
        filtered = [f for f in received_files if f["time"].endswith(filter_date)]
        if not filtered:
            await update.message.reply_text(f"❌ Không có file nào ngày {filter_date}.")
            return
        text = f"📅 File gửi ngày {filter_date}:\n\n"
        for f in filtered:
            text += (
                f"🆔 <b>ID:</b> <a href='tg://resolve?domain={username}&message_id={f['id']}'>{f['id']}</a>\n"
                f"📄 <b>Tên:</b> {f['name']}\n"
                f"📦 <b>Dung lượng:</b> {f['size']}\n"
                f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
            )
        await update.message.reply_html(text, disable_web_page_preview=True)
    except ValueError:
        await update.message.reply_text("❌ Sai định dạng. Dùng: /list_ngay 19-05-2025")

# === Xử lý file & ảnh ===
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc: return
    msg_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    time_str = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    size = f"{doc.file_size/1024:.2f} KB" if doc.file_size < 1024*1024 else f"{doc.file_size/1024/1024:.2f} MB"
    data = {"id": msg_id, "name": doc.file_name, "size": size, "time": time_str}
    received_files.append(data)
    append_to_sheet(data)
    await update.message.reply_html(
        f"📄 <b>Tên file:</b> {doc.file_name}\n📦 <b>Dung lượng:</b> {size}\n"
        f"⏰ <b>Thời gian:</b> {time_str}\n🆔 <b>ID:</b> <code>{msg_id}</code>"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    msg_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    time_str = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    size = f"{photo.file_size/1024:.2f} KB" if photo.file_size < 1024*1024 else f"{photo.file_size/1024/1024:.2f} MB"
    data = {"id": msg_id, "name": "Ảnh (không có tên)", "size": size, "time": time_str}
    received_files.append(data)
    append_to_sheet(data)
    await update.message.reply_html(
        f"🖼 <b>Ảnh nhận được</b>\n📦 <b>Dung lượng:</b> {size}\n"
        f"⏰ <b>Thời gian:</b> {time_str}\n🆔 <b>ID:</b> <code>{msg_id}</code>"
    )

# === Gắn handler & command ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ping", ping))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CommandHandler("list", list_files))
application.add_handler(CommandHandler("list_ngay", list_files_by_date))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# === Menu lệnh Telegram ===
async def set_bot_commands(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Bắt đầu"),
        BotCommand("ping", "Kiểm tra bot"),
        BotCommand("menu", "Hiển thị menu"),
        BotCommand("list", "Xem danh sách file"),
        BotCommand("list_ngay", "Lọc file theo ngày")
    ])
application.post_init = set_bot_commands

# === Webhook route ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), event_loop)
    return {"ok": True}

@app.route("/")
def home(): return "🤖 Bot Telegram đang chạy trên Render!"

# === Chạy Flask + Bot song song ===
if __name__ == "__main__":
    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

    async def main():
        global event_loop
        event_loop = asyncio.get_event_loop()
        await application.bot.delete_webhook()
        await application.bot.set_webhook(WEBHOOK_URL)
        await application.initialize()
        await application.start()

    threading.Thread(target=run_flask).start()
    asyncio.run(main())
