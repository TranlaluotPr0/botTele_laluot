import os
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
from flask import Flask
from threading import Thread
from datetime import datetime
import pytz
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN")
user_files = {}

# ====== LỆNH ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("👋 Chào bạn! Gửi file để lưu trữ.\nDùng /help để xem hướng dẫn.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Hướng dẫn:\n"
        "/start - Khởi động bot\n"
        "/files - Danh sách tất cả file\n"
        "/files YYYY-MM-DD - Lọc file theo ngày\n"
        "/delete <file_id> - Xoá file khỏi danh sách\n"
        "/stats - Thống kê số file đã lưu"
    )

async def files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    files = user_files.get(user_id, [])
    args = context.args

    if not files:
         update.message.reply_text("📂 Bạn chưa lưu file nào.")
        return

    if args:
        date_filter = args[0]
        filtered = [f for f in files if f['timestamp'].startswith(date_filter)]
        if not filtered:
             update.message.reply_text(f"❌ Không có file nào vào ngày {date_filter}.")
            return
        reply = "\n".join([
            f"{f['name']} ({f['size_kb']} KB, {f['timestamp']}) [ID: {f['id']}]"
            for f in filtered
        ])
        await update.message.reply_text(f"📁 File ngày {date_filter}:\n{reply}")
    else:
        reply = "\n".join([
            f"{f['name']} ({f['size_kb']} KB, {f['timestamp']}) [ID: {f['id']}]"
            for f in files
        ])
        await update.message.reply_text("📄 Danh sách file:\n" + reply)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    files = user_files.get(user_id, [])
    file_id = update.message.text.replace('/delete', '').strip()

    if not file_id:
        await update.message.reply_text("❗ Dùng đúng cú pháp: /delete <file_id>")
        return

    for f in files:
        if f['id'] == file_id:
            files.remove(f)
            await update.message.reply_text(f"🗑️ Đã xoá file: {f['name']}\n⚠️ File vẫn tồn tại trên Telegram nếu bạn còn file_id.")
            return

    await update.message.reply_text("❌ Không tìm thấy file có ID đó.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    count = len(user_files.get(user_id, []))
    await update.message.reply_text(f"📊 Bạn đã lưu {count} file.")

# ====== XỬ LÝ FILE ======
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    msg = update.message
    user_id = update.effective_user.id

    file = msg.document or msg.audio or msg.video or msg.voice
    file_type = "file"

    if not file and msg.photo:
        file = msg.photo[-1]
        file_type = "photo"

    if not file:
        return

    if file_type == "photo":
        file_name = f"photo_{file.file_unique_id}.jpg"
        size_bytes = None
        is_original = False
    else:
        file_name = getattr(file, 'file_name', 'unknown')
        size_bytes = getattr(file, 'file_size', None)
        is_original = True

    file_id = file.file_id
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    if size_bytes:
        size_kb = round(size_bytes / 1024, 2)
        size_str = f"{round(size_kb / 1024, 2)} MB" if size_kb > 1024 else f"{size_kb} KB"
    else:
        size_kb = 0
        size_str = "Không xác định"

    user_files.setdefault(user_id, []).append({
        "id": file_id,
        "name": file_name,
        "timestamp": timestamp,
        "size_kb": size_kb
    })

    await msg.reply_text(
        f"✅ Đã lưu: {file_name}\n"
        f"🕒 {timestamp}\n"
        f"📦 Dung lượng: {size_str}\n"
        f"🆔 File ID: {file_id}" +
        ("\n⚠️ Ảnh gửi dạng *photo* hoặc forward có thể bị nén, không giữ tên/dung lượng gốc." if not is_original else "")
    )

# ====== KEEP ALIVE ======
app = Flask('')
@app.route('/')
def home(): return "Bot is running."

def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

# ====== KHỞI ĐỘNG BOT ======
async def run_bot():
    print("🔑 Đang chạy bot Telegram...")
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    await app_bot.initialize()

    await app_bot.bot.set_my_commands([
        BotCommand("start", "Khởi động bot"),
        BotCommand("help", "Hướng dẫn sử dụng"),
        BotCommand("files", "Danh sách file đã lưu"),
        BotCommand("delete", "Xoá file theo ID"),
        BotCommand("stats", "Thống kê số file đã lưu"),
    ])

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("help", help_command))
    app_bot.add_handler(CommandHandler("files", files))
    app_bot.add_handler(CommandHandler("delete", delete))
    app_bot.add_handler(CommandHandler("stats", stats))
    app_bot.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.AUDIO | filters.VIDEO | filters.VOICE,
        handle_file
    ))

    await app_bot.run_polling()


    await app_bot.run_polling()


if not BOT_TOKEN:
    print("❌ Lỗi: Chưa thiết lập biến môi trường BOT_TOKEN!")
else:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            print("🔄 Loop đang chạy → tạo task chạy bot.")
            loop.create_task(run_bot())
        else:
            loop.run_until_complete(run_bot())
    except RuntimeError:
        print("⚠️ Không thể lấy event loop, tạo mới.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(run_bot())
