import os
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, Application,
    MessageHandler, CallbackQueryHandler, ContextTypes, filters
)

# === Import các chức năng đã tách ===
from features.basic_commands import menu, menu_callback, start, ping, fallback_menu
from features.chon_ngay import chon_ngay, handle_ngay_callback, handle_ngay_text
from features.tags import add_tag, filter_by_tag, remove_tag, clear_tags, rename_tag
from features.file_list import list_files_by_date, filter_by_size
from features.import_export import export_csv, import_csv, get_waiting_import_set
from features.file_handlers import handle_received_file, load_from_csv, append_to_csv
from features.loc_dungluong_debug import (
    loc_dungluong_menu,
    handle_dungluong_text,
    set_received_files as set_file_luong,
    get_waiting_set as get_waiting_luong_set
)

# === Biến toàn cục ===
event_loop = None
received_files = []
waiting_import = get_waiting_import_set()

# === Load biến môi trường ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

# === Flask và khởi tạo Telegram Application ===
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Load file log.csv vào danh sách received_files
load_from_csv(received_files)
application.bot_data["received_files"] = received_files
set_file_luong(received_files)  # cho module lọc dung lượng

# === Xử lý file nhận được ===
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    user_id = update.effective_user.id

    if user_id in waiting_import and doc.file_name.endswith(".csv"):
        file = await doc.get_file()
        await file.download_to_drive("log.csv")
        received_files.clear()
        load_from_csv(received_files)
        application.bot_data["received_files"] = received_files
        set_file_luong(received_files)
        waiting_import.remove(user_id)
        await update.message.reply_text(f"✅ Đã nhập {len(received_files)} file từ log.csv.")
        return

    data = handle_received_file(update.message, doc.file_id, doc.file_name, doc.file_size)
    received_files.append(data)
    append_to_csv(data)
    application.bot_data["received_files"] = received_files
    set_file_luong(received_files)

    await update.message.reply_html(
        f"📄 <b>Tên file:</b> {data['name']}\n"
        f"📦 <b>Dung lượng:</b> {data['size']}\n"
        f"⏰ <b>Thời gian:</b> {data['time']}\n"
        f"🆔 <code>{data['id']}</code>"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    data = handle_received_file(update.message, photo.file_id, "Ảnh (không có tên)", photo.file_size)
    received_files.append(data)
    append_to_csv(data)
    application.bot_data["received_files"] = received_files
    set_file_luong(received_files)

    await update.message.reply_html(
        f"🖼 <b>Ảnh nhận được</b>\n"
        f"📦 <b>Dung lượng:</b> {data['size']}\n"
        f"⏰ <b>Thời gian:</b> {data['time']}\n"
        f"🆔 <code>{data['id']}</code>"
    )

# === Xử lý tin nhắn văn bản ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in get_waiting_luong_set():
        await handle_dungluong_text(update, context)
    else:
        await handle_ngay_text(update, context)

# === Đăng ký handlers ===
application.add_handler(MessageHandler(filters.Regex("^/start$"), start))
application.add_handler(MessageHandler(filters.Regex("^/ping$"), ping))
application.add_handler(MessageHandler(filters.Regex("^/menu$"), fallback_menu))

application.add_handler(CallbackQueryHandler(menu_callback, pattern="^(menu|cmd|loc)_"))
application.add_handler(CallbackQueryHandler(handle_ngay_callback))

application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# === Webhook Flask routes ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), event_loop)
    return {"ok": True}

@app.route("/")
def home():
    return "<h3>🤖 Bot Telegram đang hoạt động!</h3>"

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
