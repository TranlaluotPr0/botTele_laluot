import os
import pytz
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, BotCommand, Document
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)

# Load biến môi trường từ .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Danh sách lưu file đã nhận (RAM)
received_files = []
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Gõ /menu để xem các chức năng.")

# /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot đang hoạt động bình thường.")

# /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Danh sách lệnh có sẵn:\n"
        "/start - Bắt đầu\n"
        "/ping - Kiểm tra trạng thái bot\n"
        "/menu - Hiển thị menu lệnh\n"
        "/list - Xem danh sách file đã gửi"
    )

# /list
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

# Nhận file
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document: Document = update.message.document
    if not document:
        return

    file_name = document.file_name
    file_size = document.file_size
    message_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    readable_time = sent_time.strftime("%H:%M:%S %d-%m-%Y")

    if file_size >= 1024 * 1024:
        size_text = f"{file_size / (1024 * 1024):.2f} MB"
    else:
        size_text = f"{file_size / 1024:.2f} KB"

    # Lưu vào danh sách
    received_files.append({
        "id": message_id,
        "name": file_name,
        "size": size_text,
        "time": readable_time
    })

    await update.message.reply_html(
        f"📄 <b>Tên file:</b> {file_name}\n"
        f"📦 <b>Dung lượng:</b> {size_text}\n"
        f"⏰ <b>Thời gian gửi:</b> {readable_time}\n"
        f"🆔 <b>ID tin nhắn:</b> <code>{message_id}</code>"
    )

# Đăng ký lệnh menu Telegram
async def setup_bot_commands(app):
    commands = [
        BotCommand("start", "Bắt đầu sử dụng bot"),
        BotCommand("ping", "Kiểm tra trạng thái bot"),
        BotCommand("menu", "Xem danh sách chức năng"),
        BotCommand("list", "Xem danh sách file đã gửi")
    ]
    await app.bot.set_my_commands(commands)

# Chạy bot
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ Không tìm thấy BOT_TOKEN trong biến môi trường!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    app.post_init = setup_bot_commands

    print("🚀 Bot Telegram đã sẵn sàng...")
    app.run_polling()

if __name__ == "__main__":
    main()
