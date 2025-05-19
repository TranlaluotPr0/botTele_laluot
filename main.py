import os
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

# Load biến môi trường từ .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Hàm xử lý /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Gõ /menu để xem các chức năng.")

# Hàm xử lý /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot đang hoạt động bình thường.")

# Hàm xử lý /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Danh sách lệnh có sẵn:\n"
        "/start - Bắt đầu\n"
        "/ping - Kiểm tra trạng thái bot\n"
        "/menu - Hiển thị menu lệnh"
    )

# Đăng ký các lệnh vào Telegram Bot API (hiển thị trong menu Telegram)
async def setup_bot_commands(application):
    commands = [
        BotCommand("start", "Bắt đầu sử dụng bot"),
        BotCommand("ping", "Kiểm tra trạng thái bot"),
        BotCommand("menu", "Xem danh sách chức năng")
    ]
    await application.bot.set_my_commands(commands)

# Chạy bot
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ Không tìm thấy BOT_TOKEN trong biến môi trường!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Đăng ký handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("menu", menu))

    # Thiết lập menu lệnh
    app.post_init = setup_bot_commands

    print("🚀 Bot Telegram đã sẵn sàng...")
    app.run_polling()

if __name__ == "__main__":
    main()
