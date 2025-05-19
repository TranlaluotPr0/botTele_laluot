import os
from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import logging
import pytz
from datetime import datetime

# === Flask app để xử lý webhook ===
app_flask = Flask(__name__)

# === Load biến môi trường ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://trannguyengiadat-tele.onrender.com/")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# === Khu vực giờ Việt Nam ===
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")

# === Bộ nhớ tạm để lưu file đã nhận ===
received_files = []

# === Lệnh bot ===
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
            f"⏰ <b>Thời gian:</b> {f['time']}\n"
            "───\n"
        )
    await update.message.reply_html(text)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        return

    file_name = doc.file_name
    file_size = doc.file_size
    msg_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    readable_time = sent_time.strftime("%H:%M:%S %d-%m-%Y")

    size_text = f"{file_size / 1024:.2f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024*1024):.2f} MB"

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

# === Route gốc để tránh lỗi 404 trên Render ===
@app_flask.route("/", methods=["GET"])
def home():
    return "<h3>🤖 Bot Telegram đã triển khai thành công trên Render!</h3>", 200

# === Route webhook để nhận dữ liệu từ Telegram ===
@app_flask.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    await telegram_app.update_queue.put(Update.de_json(request.get_json(force=True), telegram_app.bot))
    return {"ok": True}

# === Tạo Telegram App ===
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("ping", ping))
telegram_app.add_handler(CommandHandler("menu", menu))
telegram_app.add_handler(CommandHandler("list", list_files))
telegram_app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

# === Đăng ký lệnh /menu vào Telegram ===
async def setup_bot_commands(app):
    commands = [
        BotCommand("start", "Bắt đầu sử dụng bot"),
        BotCommand("ping", "Kiểm tra bot"),
        BotCommand("menu", "Hiển thị menu lệnh"),
        BotCommand("list", "Xem danh sách file")
    ]
    await app.bot.set_my_commands(commands)

telegram_app.post_init = setup_bot_commands

# === Khởi động Flask + Telegram app ===
if __name__ == "__main__":
    import asyncio

    async def main():
        await telegram_app.bot.delete_webhook()
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        print(f"🚀 Webhook set tại: {WEBHOOK_URL}")
        await telegram_app.initialize()
        await telegram_app.start()
        app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

    asyncio.run(main())
