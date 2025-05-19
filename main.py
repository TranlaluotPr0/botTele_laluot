import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# Bot token (nên đặt vào ENV VAR)
TOKEN = os.environ.get("BOT_TOKEN", "7548237225:AAFjkvaYLHIkIDXGe3k_LxwNlW17gQPgHD4")

saved_files = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "📖 Hướng dẫn:\n"
        "/start - Khởi động bot\n"
        "/files - Danh sách tất cả file\n"
        "/files YYYY-MM-DD - Lọc file theo ngày\n"
        "/delete <file_id> - Xoá file khỏi danh sách\n"
        "/stats - Thống kê số file đã lưu"
    )
    await update.message.reply_text(message)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if document:
        file_id = document.file_id
        name = document.file_name
        size = round(document.file_size / 1024 / 1024, 2)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for fid, info in saved_files.items():
            if info["name"] == name:
                await update.message.reply_text(f"⚠️ Đã có file trùng tên: `{name}`", parse_mode="Markdown")
                return
            if abs(info["size"] - size) < 0.01:
                await update.message.reply_text(f"⚠️ Đã có file khác trùng dung lượng: {size} MB", parse_mode="Markdown")
                return

        saved_files[file_id] = {"name": name, "size": size, "date": now}
        await update.message.reply_text(f"✅ Đã lưu file: `{name}` ({size} MB)", parse_mode="Markdown")

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    filtered = saved_files
    if args:
        try:
            date_filter = args[0]
            filtered = {fid: info for fid, info in saved_files.items() if info["date"].startswith(date_filter)}
        except ValueError:
            await update.message.reply_text("⚠️ Định dạng ngày không hợp lệ. Dùng: `/files YYYY-MM-DD`", parse_mode="Markdown")
            return

    if not filtered:
        await update.message.reply_text("📂 Không có file nào.")
        return

    message = "📁 Danh sách file đã lưu:\n"
    for fid, info in filtered.items():
        message += f"🗂️ `{info['name']}` - {info['size']} MB - `{fid}`\n"
    await update.message.reply_text(message, parse_mode="Markdown")

async def delete_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Vui lòng nhập file_id để xoá: `/delete <file_id>`", parse_mode="Markdown")
        return
    file_id = args[0]
    if file_id in saved_files:
        name = saved_files[file_id]["name"]
        del saved_files[file_id]
        await update.message.reply_text(f"🗑️ Đã xoá file `{name}`.", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Không tìm thấy file_id.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = len(saved_files)
    total_size = sum(info["size"] for info in saved_files.values())
    await update.message.reply_text(f"📊 Tổng cộng {count} file, dung lượng khoảng {total_size:.2f} MB.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("files", list_files))
    app.add_handler(CommandHandler("delete", delete_file))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Webhook config for Render
    WEBHOOK_HOST = "trannguyengiadat-tele.onrender.com"
    WEBHOOK_URL = f"https://{WEBHOOK_HOST}/webhook"
    PORT = int(os.environ.get("PORT", 8443))

    print("🤖 Bot chạy webhook tại:", WEBHOOK_URL)

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )
