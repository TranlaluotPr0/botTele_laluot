import os
from telegram import Update
from telegram.ext import ContextTypes

# Bộ set theo dõi user đang chờ nhập file log
waiting_import = set()

def get_waiting_import_set():
    return waiting_import

# Gửi file log.csv cho người dùng
async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message

    if os.path.exists("log.csv"):
        await message.reply_document(open("log.csv", "rb"))
    else:
        await message.reply_text("⚠️ Chưa có file log nào.")

# Gửi yêu cầu nhập log.csv
async def import_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message
    user_id = update.effective_user.id

    waiting_import.add(user_id)
    await message.reply_text("📤 Gửi file <b>log.csv</b> để nhập dữ liệu.", parse_mode="HTML")
