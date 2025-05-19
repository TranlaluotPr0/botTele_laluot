import os
import logging
from flask import Flask, request
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import (
    Application, ApplicationBuilder,
    CommandHandler, MessageHandler, ContextTypes, filters
)
import pytz
from datetime import datetime
import asyncio

# Tải biến môi trường
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Flask app
app = Flask(__name__)

# Múi giờ Việt Nam
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
received_files = []

# Logging
logging.basicConfig(level=logging.INFO)

# Xử lý lệnh
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

# Route mặc định
@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot Telegram đã sẵn sàng!", 200

# Route webhook
@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        await application.process_update(update)
        return {"ok": True}
    except Exception as e:
        print(f"❌ Webhook lỗi: {e}")
        return {"ok": False, "error": str(e)}, 500

# Khởi tạo bot
application: Application = ApplicationBuilder().token(BOT_TOKEN).build()
bot = application.bot

# Đăng ký lệnh
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ping", ping))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CommandHandler("list", list_files))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

async def set_commands():
    commands = [
        BotCommand("start", "Bắt đầu sử dụng bot"),
        BotCommand("ping", "Kiểm tra bot"),
        BotCommand("menu", "Xem menu"),
        BotCommand("list", "Xem file đã gửi")
    ]
    await bot.set_my_commands(commands)

# Hàm khởi chạy chính
if __name__ == "__main__":
    async def main():
        await bot.delete_webhook()
        await bot.set_webhook(WEBHOOK_URL)
        print(f"🚀 Webhook set tại: {WEBHOOK_URL}")
        await set_commands()
        await application.initialize()
        await application.start()
        # Flask sẽ tự chạy trong Render nên KHÔNG gọi app.run()

    asyncio.run(main())
