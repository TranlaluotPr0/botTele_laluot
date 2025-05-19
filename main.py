import os
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

# === Load biến môi trường ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")  # Dùng domain Render tự cấp
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

# === Flask app ===
app = Flask(__name__)
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
received_files = []

# === Telegram bot app ===
application = ApplicationBuilder().token(BOT_TOKEN).build()

# === Các command ===
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
        "/list - Xem file đã gửi"
    )

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not received_files:
        await update.message.reply_text("📭 Chưa có file nào được gửi.")
        return
    text = "📂 Danh sách file đã gửi:\n\n"
    for f in received_files:
        text += (
            f"🆔 <b>ID:</b> <code>{f['id']}</code>\n"
            f"📄 <b>Tên:</b> {f['name']}\n"
            f"📦 <b>Dung lượng:</b> {f['size']}\n"
            f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
        )
    await update.message.reply_html(text)

# === Handle file gửi đến bot ===
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        return
    file_name = doc.file_name
    file_size = doc.file_size
    msg_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    readable_time = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    size_text = f"{file_size / 1024:.2f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.2f} MB"

    received_files.append({
        "id": msg_id,
        "name": file_name,
        "size": size_text,
        "time": readable_time
    })

    await update.message.reply_html(
        f"📄 <b>Tên file:</b> {file_name}\n"
        f"📦 <b>Dung lượng:</b> {size_text}\n"
        f"⏰ <b>Thời gian gửi:</b> {readable_time}\n"
        f"🆔 <b>ID tin nhắn:</b> <code>{msg_id}</code>"
    )

# === Đăng ký lệnh và handler ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ping", ping))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CommandHandler("list", list_files))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

# === Menu lệnh Telegram bot ===
async def set_bot_commands(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Bắt đầu sử dụng bot"),
        BotCommand("ping", "Kiểm tra bot"),
        BotCommand("menu", "Hiển thị menu lệnh"),
        BotCommand("list", "Xem danh sách file")
    ])
application.post_init = set_bot_commands

# === Webhook route ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return {"ok": True}

@app.route("/", methods=["GET"])
def home():
    return "<h3>🤖 Bot Telegram đã triển khai thành công trên Render!</h3>"

# === Chạy Flask và bot song song ===
if __name__ == "__main__":
    def run_flask():
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port)

    async def main():
        await application.bot.delete_webhook()
        await application.bot.set_webhook(WEBHOOK_URL)
        print(f"🚀 Webhook set tại: {WEBHOOK_URL}")
        await application.initialize()
        await application.start()

    # Flask chạy trên thread riêng
    threading.Thread(target=run_flask).start()
    asyncio.run(main())
