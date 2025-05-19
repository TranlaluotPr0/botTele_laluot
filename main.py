# main.py
import os
import csv
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask, request
from features.tags import add_tag, filter_by_tag, remove_tag, clear_tags, rename_tag
from features.chon_ngay import chon_ngay, handle_ngay_callback, handle_ngay_text
from telegram import Update, BotCommand, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, Application, CommandHandler,
    MessageHandler, CallbackQueryHandler, ContextTypes, filters
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
            if len(row) >= 4:
                file_data = {
                    "id": int(row[0]),
                    "name": row[1],
                    "size": row[2],
                    "time": row[3]
                }
                if len(row) >= 5:
                    file_data["file_id"] = row[4]
                received_files.append(file_data)

# === Ghi log vào file CSV ===
def append_to_csv(data):
    with open("log.csv", "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([data["id"], data["name"], data["size"], data["time"], data.get("file_id", "")])

# === Tải từ .env ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

# === Khởi tạo bot + Flask ===
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()
load_from_csv()
application.bot_data["received_files"] = received_files  # rất quan trọng!

# === Lệnh cơ bản ===
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/menu", "/chuc_nang"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Chào bạn! Dùng /menu hoặc /chuc_nang để xem chức năng.", reply_markup=reply_markup)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot đang hoạt động bình thường.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 <b>Hướng dẫn sử dụng bot:</b>\n\n"
        "🟢 <b>Cơ bản:</b>\n"
        "/start – Bắt đầu bot\n"
        "/ping – Kiểm tra bot\n"
        "/help – Hiển thị hướng dẫn\n"
        "/chuc_nang – Hiện các chức năng nâng cao\n\n"
        "📂 <b>Quản lý file:</b>\n"
        "/list – Danh sách tất cả file đã gửi\n"
        "/filter_size &lt;min&gt; &lt;max&gt; – Lọc theo dung lượng (MB)\n"
        "/export – Xuất file log.csv\n"
        "/import – Nhập file log.csv\n\n"
        "📅 <b>Quản lý theo ngày:</b>\n"
        "/list_ngay dd-mm-yyyy – Lọc file theo ngày\n"
        "/chon_ngay – Chọn ngày bằng nút hoặc nhập tay (VD: 19/5)\n\n"
        "🏷 <b>Gắn tag & lọc:</b>\n"
        "/addtag &lt;id&gt; &lt;tag&gt; – Gắn tag cho file\n"
        "/tag &lt;tag&gt; – Lọc file theo tag\n"
        "/removetag &lt;id&gt; &lt;tag&gt; – Gỡ 1 tag khỏi file\n"
        "/cleartags &lt;id&gt; – Xoá toàn bộ tag của file\n"
        "/renametag &lt;tag_cu&gt; &lt;tag_moi&gt; – Đổi tên tag\n\n"
        "📌 <i>Lưu ý:</i>\n"
        "– ID là số hiển thị khi gửi file hoặc xem trong /list\n"
        "– Bạn có thể nhập ngày dưới dạng: 19/5, 19-05-2025,...\n\n"
        "👨‍💻 Bot đang được nâng cấp thêm tính năng mới!"
        , parse_mode="HTML"
    )

async def chuc_nang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙️ <b>Các chức năng mở rộng:</b>\n\n"
        "📂 Quản lý file:\n"
        "/list – Danh sách file\n"
        "/list_ngay dd-mm-yyyy – Lọc theo ngày\n"
        "/filter_size &lt;min&gt; &lt;max&gt; – Lọc theo dung lượng\n"
        "/chon_ngay – Chọn ngày bằng nút hoặc tay\n"
        "/export – Tải log.csv\n"
        "/import – Nhập file log.csv\n\n"
        "🏷️ Gắn tag:\n"
        "/addtag &lt;id&gt; &lt;tag&gt;\n"
        "/tag &lt;tag&gt;\n"
        "/removetag &lt;id&gt; &lt;tag&gt;\n"
        "/cleartags &lt;id&gt;\n"
        "/renametag &lt;tag_cu&gt; &lt;tag_moi&gt;"
        , parse_mode="HTML"
    )

# === Xử lý gửi file ===
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    user_id = update.effective_user.id

    if user_id in waiting_import and doc.file_name.endswith(".csv"):
        file = await doc.get_file()
        await file.download_to_drive("log.csv")
        received_files.clear()
        load_from_csv()
        application.bot_data["received_files"] = received_files
        waiting_import.remove(user_id)
        await update.message.reply_text(f"✅ Đã nhập {len(received_files)} file từ log.csv.")
        return

    file_name = doc.file_name
    file_size = doc.file_size
    msg_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    time_str = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    size_text = f"{file_size/1024:.2f} KB" if file_size < 1024*1024 else f"{file_size/1024/1024:.2f} MB"
    data = {
        "id": msg_id,
        "name": file_name,
        "size": size_text,
        "time": time_str,
        "file_id": doc.file_id
    }
    received_files.append(data)
    append_to_csv(data)
    await update.message.reply_html(
        f"📄 <b>Tên file:</b> {file_name}\n📦 <b>Dung lượng:</b> {size_text}\n⏰ <b>Thời gian:</b> {time_str}\n🆔 <code>{msg_id}</code>"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    msg_id = update.message.message_id
    file_size = photo.file_size
    sent_time = update.message.date.astimezone(vn_tz)
    time_str = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    size_text = f"{file_size/1024:.2f} KB" if file_size < 1024*1024 else f"{file_size/1024/1024:.2f} MB"
    data = {
        "id": msg_id,
        "name": "Ảnh (không có tên)",
        "size": size_text,
        "time": time_str,
        "file_id": photo.file_id
    }
    received_files.append(data)
    append_to_csv(data)
    await update.message.reply_html(
        f"🖼 <b>Ảnh nhận được</b>\n📦 <b>Dung lượng:</b> {size_text}\n⏰ <b>Thời gian:</b> {time_str}\n🆔 <code>{msg_id}</code>"
    )

# === Các command quản lý file (list, lọc...) sẽ giữ nguyên không đổi ===

# === Đăng ký HANDLERS ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ping", ping))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("menu", chuc_nang))
application.add_handler(CommandHandler("chuc_nang", chuc_nang))
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

# === Menu Telegram mặc định rút gọn ===
async def set_bot_commands(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Bắt đầu"),
        BotCommand("ping", "Kiểm tra bot"),
        BotCommand("help", "Hướng dẫn"),
        BotCommand("chuc_nang", "Chức năng nâng cao")
    ])
application.post_init = set_bot_commands

# === Webhook routes ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), event_loop)
    return {"ok": True}

@app.route("/")
def home(): return "<h3>🤖 Bot Telegram đang hoạt động!</h3>"

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
