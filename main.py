import os
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, Application, CommandHandler,
    MessageHandler, ContextTypes, filters
)
import pytz
from datetime import datetime

# === Biến toàn cục để giữ event loop chính ===
event_loop = None

# === Load biến môi trường ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

# === Flask app ===
app = Flask(__name__)
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
received_files = []

# === Telegram bot application ===
application = ApplicationBuilder().token(BOT_TOKEN).build()

# === Các lệnh bot ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📥 /start từ {update.effective_user.username}")
    await update.message.reply_text("👋 Xin chào! Gõ /menu để xem các chức năng.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📥 /ping từ {update.effective_user.username}")
    await update.message.reply_text("🏓 Bot đang hoạt động bình thường.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📥 /menu từ {update.effective_user.username}")
    await update.message.reply_text(
        "📋 Danh sách lệnh có sẵn:\n"
        "/start - Bắt đầu\n"
        "/ping - Kiểm tra bot\n"
        "/menu - Danh sách lệnh\n"
        "/list - Xem file đã gửi\n"
        "/list_ngay <dd-mm-yyyy> - Lọc file theo ngày"
    )

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📥 /list từ {update.effective_user.username}")
    if not received_files:
        await update.message.reply_text("📭 Chưa có file nào được gửi.")
        return

    username = context.bot.username
    text = "📂 Danh sách file đã gửi:\n\n"
    for f in received_files:
        text += (
            f"🆔 <b>ID:</b> <a href='tg://resolve?domain={username}&message_id={f['id']}'>{f['id']}</a>\n"
            f"📄 <b>Tên:</b> {f['name']}\n"
            f"📦 <b>Dung lượng:</b> {f['size']}\n"
            f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
        )

    await update.message.reply_html(text, disable_web_page_preview=True)

async def list_files_by_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not received_files:
        await update.message.reply_text("📭 Chưa có file nào được gửi.")
        return

    if not context.args:
        await update.message.reply_text("📅 Vui lòng nhập ngày theo định dạng: /list_ngay dd-mm-yyyy")
        return

    try:
        filter_date = context.args[0].strip()
        datetime.strptime(filter_date, "%d-%m-%Y")  # Kiểm tra định dạng

        username = context.bot.username
        filtered = [f for f in received_files if f["time"].endswith(filter_date)]

        if not filtered:
            await update.message.reply_text(f"❌ Không có file nào gửi vào ngày {filter_date}.")
            return

        text = f"📅 Danh sách file gửi ngày {filter_date}:\n\n"
        for f in filtered:
            text += (
                f"🆔 <b>ID:</b> <a href='tg://resolve?domain={username}&message_id={f['id']}'>{f['id']}</a>\n"
                f"📄 <b>Tên:</b> {f['name']}\n"
                f"📦 <b>Dung lượng:</b> {f['size']}\n"
                f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
            )

        await update.message.reply_html(text, disable_web_page_preview=True)

    except ValueError:
        await update.message.reply_text("❌ Sai định dạng ngày. Dùng: /list_ngay 19-05-2025")

# === Xử lý file document ===
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        return
    file_name = doc.file_name
    file_size = doc.file_size
    msg_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    readable_time = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    size_text = f"{file_size / 1024:.2f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.2f} MB"

    print(f"📥 Nhận file: {file_name} từ {update.effective_user.username}")

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

# === Xử lý ảnh (photo) ===
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    photo = update.message.photo[-1]
    msg_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    readable_time = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    file_size = photo.file_size or 0
    size_text = f"{file_size / 1024:.2f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.2f} MB"

    print(f"📸 Nhận ảnh từ {update.effective_user.username}")

    received_files.append({
        "id": msg_id,
        "name": "Ảnh (không có tên)",
        "size": size_text,
        "time": readable_time
    })

    await update.message.reply_html(
        f"🖼 <b>Ảnh nhận được</b>\n"
        f"📦 <b>Dung lượng:</b> {size_text}\n"
        f"⏰ <b>Thời gian gửi:</b> {readable_time}\n"
        f"🆔 <b>ID tin nhắn:</b> <code>{msg_id}</code>"
    )

# === Gắn handler ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ping", ping))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CommandHandler("list", list_files))
application.add_handler(CommandHandler("list_ngay", list_files_by_date))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# === Đăng ký menu lệnh Telegram ===
async def set_bot_commands(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Bắt đầu sử dụng bot"),
        BotCommand("ping", "Kiểm tra bot"),
        BotCommand("menu", "Hiển thị menu lệnh"),
        BotCommand("list", "Xem danh sách file"),
        BotCommand("list_ngay", "Lọc file theo ngày gửi")
    ])
application.post_init = set_bot_commands

# === Flask route nhận webhook ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update_data = request.get_json(force=True)
    print("📩 Nhận dữ liệu webhook:", update_data)

    update = Update.de_json(update_data, application.bot)

    asyncio.run_coroutine_threadsafe(
        application.process_update(update),
        event_loop
    )

    return {"ok": True}

@app.route("/", methods=["GET"])
def home():
    return "<h3>🤖 Bot Telegram đã triển khai thành công trên Render!</h3>"

# === Khởi động bot và Flask song song ===
if __name__ == "__main__":
    def run_flask():
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port)

    async def main():
        global event_loop
        event_loop = asyncio.get_event_loop()

        print(f"🌐 WEBHOOK_URL: {WEBHOOK_URL}")
        await application.bot.delete_webhook()
        await application.bot.set_webhook(WEBHOOK_URL)
        print(f"🚀 Đã set webhook tại: {WEBHOOK_URL}")
        await application.initialize()
        await application.start()

    threading.Thread(target=run_flask).start()
    asyncio.run(main())
