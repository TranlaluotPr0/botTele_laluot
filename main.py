import os
import csv
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update, BotCommand, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, Application, CommandHandler,
    MessageHandler, ContextTypes, filters
)
import pytz
from datetime import datetime

# === Biến toàn cục ===
event_loop = None
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
received_files = []
waiting_import = set()

# === Load file log.csv vào bộ nhớ ===
def load_from_csv():
    if not os.path.exists("log.csv"):
        return
    with open("log.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 4:
                received_files.append({
                    "id": int(row[0]),
                    "name": row[1],
                    "size": row[2],
                    "time": row[3]
                })

# === Ghi log vào file CSV ===
def append_to_csv(data):
    with open("log.csv", "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([data["id"], data["name"], data["size"], data["time"]])

# Tải từ .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

# Flask + Telegram app
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

load_from_csv()

# === Lệnh bot ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["/menu", "/list"],
        ["/export", "/import"],
        ["/filter_size", "/list_ngay"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Xin chào! Dưới đây là menu nhanh, hoặc bạn có thể gõ /menu để xem tất cả chức năng.",
        reply_markup=reply_markup
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot đang hoạt động bình thường.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Danh sách lệnh:\n"
        "/start - Bắt đầu\n"
        "/ping - Kiểm tra bot\n"
        "/menu - Hiển thị menu\n"
        "/list - Xem file đã gửi\n"
        "/list_ngay <dd-mm-yyyy> - Lọc theo ngày\n"
        "/filter_size <min> <max> - Lọc theo dung lượng MB\n"
        "/export - Tải log.csv\n"
        "/import - Nhập file log.csv (sẽ chờ bạn gửi file)"
    )

async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists("log.csv"):
        await update.message.reply_document(open("log.csv", "rb"))
    else:
        await update.message.reply_text("⚠️ Chưa có file log nào.")

async def import_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    waiting_import.add(user_id)
    await update.message.reply_text("📤 Vui lòng gửi file log.csv để nhập dữ liệu.")

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not received_files:
        await update.message.reply_text("📭 Chưa có file nào.")
        return
    username = context.bot.username
    text = "📂 Danh sách file:\n\n"
    for f in received_files:
        text += (
            f"🆔 <b>ID:</b> <a href='tg://resolve?domain={username}&message_id={f['id']}'>{f['id']}</a>\n"
            f"📄 <b>Tên:</b> {f['name']}\n"
            f"📦 <b>Dung lượng:</b> {f['size']}\n"
            f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
        )
    await update.message.reply_html(text, disable_web_page_preview=True)

async def list_files_by_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📅 Dùng: /list_ngay dd-mm-yyyy")
        return
    try:
        filter_date = context.args[0].strip()
        datetime.strptime(filter_date, "%d-%m-%Y")
        username = context.bot.username
        filtered = [f for f in received_files if f["time"].endswith(filter_date)]
        if not filtered:
            await update.message.reply_text("❌ Không có file nào ngày đó.")
            return
        text = f"📅 File ngày {filter_date}:\n\n"
        for f in filtered:
            text += (
                f"🆔 <b>ID:</b> <a href='tg://resolve?domain={username}&message_id={f['id']}'>{f['id']}</a>\n"
                f"📄 <b>Tên:</b> {f['name']}\n"
                f"📦 <b>Dung lượng:</b> {f['size']}\n"
                f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
            )
        await update.message.reply_html(text, disable_web_page_preview=True)
    except:
        await update.message.reply_text("❌ Sai định dạng ngày. Dùng: /list_ngay dd-mm-yyyy")

async def filter_by_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("📏 Dùng: /filter_size <min_MB> <max_MB>")
        return
    try:
        min_mb = float(context.args[0])
        max_mb = float(context.args[1])
        matched = []
        username = context.bot.username
        for f in received_files:
            size = float(f["size"].replace("KB", "").strip()) / 1024 if "KB" in f["size"] else float(f["size"].replace("MB", "").strip())
            if min_mb <= size <= max_mb:
                matched.append(f)
        if not matched:
            await update.message.reply_text("❌ Không có file phù hợp.")
            return
        text = f"📦 File từ {min_mb}MB đến {max_mb}MB:\n\n"
        for f in matched:
            text += (
                f"🆔 <b>ID:</b> <a href='tg://resolve?domain={username}&message_id={f['id']}'>{f['id']}</a>\n"
                f"📄 <b>Tên:</b> {f['name']}\n"
                f"📦 <b>Dung lượng:</b> {f['size']}\n"
                f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
            )
        await update.message.reply_html(text, disable_web_page_preview=True)
    except:
        await update.message.reply_text("❌ Lỗi định dạng. Dùng: /filter_size <min> <max>")

# === Xử lý file và ảnh ===
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    user_id = update.effective_user.id

    if user_id in waiting_import and doc.file_name.endswith(".csv"):
        file = await doc.get_file()
        await file.download_to_drive("log.csv")
        received_files.clear()
        load_from_csv()
        waiting_import.remove(user_id)
        await update.message.reply_text(f"✅ Đã nhập {len(received_files)} file từ log.csv.")
        return

    file_name = doc.file_name
    file_size = doc.file_size
    msg_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    time_str = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    size_text = f"{file_size/1024:.2f} KB" if file_size < 1024*1024 else f"{file_size/1024/1024:.2f} MB"
    data = {"id": msg_id, "name": file_name, "size": size_text, "time": time_str}
    received_files.append(data)
    append_to_csv(data)

    await update.message.reply_html(
        f"📄 <b>Tên file:</b> {file_name}\n"
        f"📦 <b>Dung lượng:</b> {size_text}\n"
        f"⏰ <b>Thời gian:</b> {time_str}\n"
        f"🆔 <b>ID:</b> <code>{msg_id}</code>"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    msg_id = update.message.message_id
    file_size = photo.file_size
    sent_time = update.message.date.astimezone(vn_tz)
    time_str = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    size_text = f"{file_size/1024:.2f} KB" if file_size < 1024*1024 else f"{file_size/1024/1024:.2f} MB"
    data = {"id": msg_id, "name": "Ảnh (không có tên)", "size": size_text, "time": time_str}
    received_files.append(data)
    append_to_csv(data)

    await update.message.reply_html(
        f"🖼 <b>Ảnh nhận được</b>\n"
        f"📦 <b>Dung lượng:</b> {size_text}\n"
        f"⏰ <b>Thời gian:</b> {time_str}\n"
        f"🆔 <b>ID:</b> <code>{msg_id}</code>"
    )

# === Handlers ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ping", ping))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CommandHandler("list", list_files))
application.add_handler(CommandHandler("list_ngay", list_files_by_date))
application.add_handler(CommandHandler("filter_size", filter_by_size))
application.add_handler(CommandHandler("export", export_csv))
application.add_handler(CommandHandler("import", import_csv))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# === Đăng ký menu / lệnh Telegram ===
async def set_bot_commands(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Bắt đầu"),
        BotCommand("ping", "Kiểm tra bot"),
        BotCommand("menu", "Hiển thị menu"),
        BotCommand("list", "Xem file đã gửi"),
        BotCommand("list_ngay", "Lọc theo ngày"),
        BotCommand("filter_size", "Lọc theo dung lượng"),
        BotCommand("export", "Tải log.csv"),
        BotCommand("import", "Nhập từ file log.csv")
    ])

application.post_init = set_bot_commands

# === Webhook route ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), event_loop)
    return {"ok": True}

@app.route("/")
def home(): return "<h3>🤖 Bot Telegram đang chạy!</h3>"

# === Chạy Flask và Telegram song song ===
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
