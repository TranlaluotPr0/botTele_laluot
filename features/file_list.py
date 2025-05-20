from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    received_files = context.application.bot_data["received_files"]
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
    received_files = context.application.bot_data["received_files"]
    if not context.args:
        await update.message.reply_text("📅 Dùng: /list_ngay dd-mm-yyyy")
        return
    try:
        filter_date = context.args[0].strip().replace("/", "-")
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
        await update.message.reply_text("❌ Sai định dạng ngày. Dùng: dd-mm-yyyy")

async def filter_by_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    received_files = context.application.bot_data["received_files"]
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
        await update.message.reply_text("❌ Lỗi định dạng.")
