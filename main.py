import os
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, CommandHandler
)

# === Import các chức năng còn tồn tại ===

from features.events_command import events_command
from features.basic_commands import handle_message, menu_callback, start, ping, fallback_menu
from features.jwt_command import jwt_command
from features.likes_command import likes_command
from features.additem_command import additem_command
from features.sp_command import sp_command
from features.like_command import like_command
from features.changebio_command import changebio_command
from features.tags import handle_tag_input, get_waiting_tag_action
from features.file_handlers import handle_received_file, load_from_csv, append_to_csv
from features import import_export

# === Biến toàn cục ===
event_loop = None
received_files = []
waiting_import = import_export.get_waiting_import_set()

# === Load biến môi trường ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

# === Flask và khởi tạo Telegram Application ===
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

load_from_csv(received_files)
application.bot_data["received_files"] = received_files

# === Xử lý file nhận được ===
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    user_id = update.effective_user.id

    # Import log từ CSV
    if user_id in waiting_import and doc.file_name.endswith(".csv"):
        file = await doc.get_file()
        await file.download_to_drive("log.csv")
        received_files.clear()
        load_from_csv(received_files)
        application.bot_data["received_files"] = received_files
        waiting_import.remove(user_id)
        await update.message.reply_text(f"✅ Đã nhập {len(received_files)} file từ log.csv.")
        return

    # File thường
    data = handle_received_file(update.message, doc.file_id, doc.file_name, doc.file_size)
    received_files.append(data)
    append_to_csv(data)
    print(f"[📄] Nhận file: {data['name']} ({data['size']})")

# === Xử lý ảnh nhận được ===
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    data = handle_received_file(update.message, photo.file_id, "Ảnh (no name)", photo.file_size)
    received_files.append(data)
    append_to_csv(data)
    print(f"[🖼] Nhận ảnh ({data['size']})")

# === Xử lý tin nhắn văn bản ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    print(f"[DEBUG] User={user_id}, text='{text}'")

    # Tag
    if get_waiting_tag_action(user_id):
        await handle_tag_input(update, context)
        return

    # ZW
    if user_id in get_waiting_zw_set():
        print(f"[ZW] User {user_id} nhập: {text}")
        await handle_zw_text(update, context)
        return

# === Đăng ký handlers ===

application.add_handler(CommandHandler("jwt", jwt_command))
application.add_handler(CommandHandler("events", events_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CommandHandler("likes", likes_command))
application.add_handler(CommandHandler("additem", additem_command))
application.add_handler(CommandHandler("sp", sp_command))
application.add_handler(CommandHandler("like", like_command))
application.add_handler(CommandHandler("changebio", changebio_command))
application.add_handler(MessageHandler(filters.Regex("^/start$"), start))
application.add_handler(MessageHandler(filters.Regex("^/ping$"), ping))
application.add_handler(MessageHandler(filters.Regex("^/menu$"), fallback_menu))
application.add_handler(CallbackQueryHandler(menu_callback, pattern="^(menu|cmd|loc)_"))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# === Webhook Flask routes ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), event_loop)
    return {"ok": True}

@app.route("/")
def home():
    return "<h3>🤖 Bot Telegram đang chạy!</h3>"

# === Khởi động song song bot + Flask ===
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
