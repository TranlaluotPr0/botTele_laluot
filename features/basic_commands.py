from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/menu", "/chuc_nang"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Dùng /menu để xem chức năng.", reply_markup=markup)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot đang hoạt động bình thường.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Gõ /menu để xem danh sách chức năng đầy đủ.",
        parse_mode="HTML"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 <b>Menu cơ bản:</b>\n"
        "/start – Khởi động bot\n"
        "/ping – Kiểm tra bot\n"
        "/help – Hướng dẫn sử dụng\n"
        "/chuc_nang – Xem chức năng mở rộng",
        parse_mode="HTML"
    )
