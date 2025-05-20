import os
from telegram import Update
from telegram.ext import ContextTypes

waiting_import = set()

def get_waiting_import_set():
    return waiting_import

async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists("log.csv"):
        await update.message.reply_document(open("log.csv", "rb"))
    else:
        await update.message.reply_text("⚠️ Chưa có file log nào.")

async def import_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    waiting_import.add(user_id)
    await update.message.reply_text("📤 Gửi file <b>log.csv</b> để nhập dữ liệu.", parse_mode="HTML")
