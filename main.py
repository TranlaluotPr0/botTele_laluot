import os
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, Application, CommandHandler,
    MessageHandler, CallbackQueryHandler, ContextTypes, filters
)

# Import các chức năng đã tách
from features.basic_commands import start, ping, help_command, menu
from features.tags import add_tag, filter_by_tag, remove_tag, clear_tags, rename_tag
from features.chon_ngay import chon_ngay, handle_ngay_callback, handle_ngay_text
from features.file_list import list_files, list_files_by_date, filter_by_size
from features.import_export import export_csv, import_csv, get_waiting_import_set
from features.file_handlers import handle_received_file, load_from_csv, append_to_csv

# === Biến toàn cục ===
event_loop = None
received_files = []
waiting_import = get_waiting_import_set()

# === Load biến môi trường .env ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

# === Khởi tạo Flask và Telegram Bot ===
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()
load_from_csv(received_files)
application.bot_data["received_files"] = received_files

# === Xử lý file upload ===
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    user_id = update.effective_user.id

    if user_id in waiting_import and doc.file_name.endswith(".csv"):
        file = await doc.get_file()
        await file.download_to_drive("log.csv")
        received_files.clear()
        load_from_csv(received_files)
        application.bot_data["received_files"] = received_files
        waiting_import.remove(user_id)
        await update.message.reply_text(f"✅ Đã nhập {len(received_files)} file từ log.csv.")
        return

    data = handle_received_file(update.message, doc.file_id, doc.file_name, doc.file_size)
    received_files.append(data)
    append_to_csv(data)
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
    await update.message.reply_html(
        f"🖼 <b>Ảnh nhận được</b>\n"
        f"📦 <b>Dung lượng:</b> {data['size']}\n"
        f"⏰ <b>Thời gian:</b> {data['time']}\n"
        f"🆔 <code>{data['id']}</code>"
    )

# === Đăng ký HANDLER cho các lệnh ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ping", ping))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CommandHandler("chuc_nang", menu))

application.add_handler(CommandHandler("list", list_files))
application.add_handler(CommandHandler("list_ngay", list_files_by_date))
application.add_handler(CommandHandler("filter_size", filter_by_size))

application.add_handler(CommandHandler("export", export_csv))
application.add_handler(CommandHandler("import", import_csv))

application.add_handler(CommandHandler("chon_ngay", chon_ngay))
application.add_handler(CommandHandler("addtag", add_tag))
application.add_handler(CommandHandler("tag", filter_by_tag))
application.add_handler(CommandHandler("removetag", remove_tag))
application.add_handler(CommandHandler("cleartags", clear_tags))
application.add_handler(CommandHandler("renametag", rename_tag))

application.add_handler(CallbackQueryHandler(handle_ngay_callback))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ngay_text))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# === Thiết lập menu lệnh Telegram ===
async def set_bot_commands(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Bắt đầu"),
        BotCommand("ping", "Kiểm tra bot"),
        BotCommand("help", "Hướng dẫn sử dụng"),
        BotCommand("menu", "Xem menu chính")
    ])
application.post_init = set_bot_commands

# === Định tuyến Flask cho webhook ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), event_loop)
    return {"ok": True}

@app.route("/")
def home(): return "<h3>🤖 Bot Telegram đang hoạt động!</h3>"

# === Chạy bot + Flask song song ===
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
