import os
import json
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

# === Google Sheets: credentials trực tiếp ===
import gspread
from google.oauth2.service_account import Credentials

raw_credential = """
{
  "type": "service_account",
  "project_id": "telegrambot-460310",
  "private_key_id": "da8c8924eead97d61c9bc4e2656fc624a7454a3b",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCmkQFgcSZhyJL9\nCb/kwGH8MQVTp8mYty6wBJ3u2woQbE4buTKl1wrLXt+oTEdaEDx/le27RjN0hZAR\nKDoGfeK49nhctZZKeLUEm8C5am0EgXhqsBjHU2Qx4qgXgLWmZw+4snpQwwLOizps\nSMmRRqGg04pXYsmkoZKxOhpTYvRcMLjn109gTs1BXsuJtsvFSzZUTnzyK9TGbWLm\nEgYYWu+DL03wHicHgPILgQ1kMHUxeWPpUrXR0DrL2RpgLk2a/vPOENhKaUGbqxE9\nb0YbYlAp0q6k226/0v9vVvDYOXSJ9yTwF9sTZB8fe5OQxikIFwp5ETYfil/a0QS7\nu+BrO7RlAgMBAAECggEACoPkw6f3ZaMdNTbS2iGTbf5rcpFvZohivNjykXXBgZgc\nwp8WUllF6xQ4gWFQL21CX6zHq8cHdsEumNUVyK6H/04/LfcgUqyitnSqUR1ykWvz\nZD5tHTqnliCgpPWXdVBUGHOOYwY7AwgC4a6JdXYXvDvuiiXusRZ3WMatJJUYJ31D\nDY84Y/FLmGji3tHSXiTAosiU9nRIoZcJ/pLa39VNqICPVCcAhdbwBFqKVLHDlO8V\njzJImMx9YZhzA+cja2MsaPunGJxdwRON0tlbIvYqamQSEgrYyrcCd79timDuEyBL\nd66p0jsTqtPW+xX2URygNZwmW8jPbGRIpiIJFgM/twKBgQDRNW7jy3/AWf1h1DpT\ng4P0iXwKiMJMgKzgtdwG+TdLbCltVZfjME4JngzvelbuAuCfx94UBsHbggaX7YKY\naldO8sk0Hao5fbAt9fIJiE0AoXWbMr8bNBJxM3XLd2MbT+xMF9wfWwQffiqDIeJ4\nxd1Rja9uSk6xxTtg4zo7c6TgmwKBgQDL0gWk8uxYrU+Zm1s+ObodpFvYnDwBOSsQ\n/Daf7qLMAYBXM2Zc/Aer7PbcrOPDitM+40xjYT4d93gxzTRcGWiPuoM3h19OK6w2\nXDAiOgMwRopnEHaAoZaRSxBrigexAcMCYJgO8ztOX5dniNmXFTn+R8WNNAXnK8wv\n/nsSbd6O/wKBgFt/qiMY4qPG9+nsfyH9eB3gb47P52K8OGADSdsG7mcfRDMcZ1Sm\n0MqmBHRMpm5sdb+ME5XgqrKNeMLDzwVIJS1TRCp1+vgv/3jqg1Ql97+Z3izlke2c\n5Z/66L73VTIhz3AsU0qnbPM1I/S8QieeKkC73gk3mJlpcKHcX6CW4HqXAoGAD6vb\nUT54W60ftLDUSCmKHONZSINivblWjVzHGm7vx33KD2pdUYLzWA3FQVxtusg+y9QQ\nOIfujcFMVY/wmbA+cOanViqrckg7WoamEMujGSAjXh9O7T7/Y7aA0bPwOXToOJOS\nvXuIMNN6wbQs/sfcCKgeEWhRl9+vOHV5owYdmaMCgYB9V7G39iA+Wo44/JBzdhQ/\n6TxbmwnhtNzznWlfQ5WkJVVi+tm+PVQAoEJIUA76rFECumYjTW34n7cB1S6ODOrp\n3I6nIXMi525zogs9wM4gZSlifwUliNCJR7ULKcCZ+ZmEnRfeR3E7uHzzR5Cm9gN+\nflIHrPvjcoDNaboyg+/oKA==\n-----END PRIVATE KEY-----\n",
  "client_email": "telegram-bot-access@telegrambot-460310.iam.gserviceaccount.com",
  "client_id": "105115100495018451508",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/telegram-bot-access@telegrambot-460310.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""

credential_info = json.loads(raw_credential)
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(credential_info, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16Jq_50T8hKGkgLkvbDlydnsoN-eHXSamCRq06sLMy8").worksheet("Trang tính1")

def append_to_sheet(data):
    sheet.append_row([data["id"], data["name"], data["size"], data["time"]])


# === Biến toàn cục ===
event_loop = None
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
received_files = []

# === Webhook và bot ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# === Các command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Gõ /menu để xem các chức năng.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot đang hoạt động bình thường.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Danh sách lệnh có sẵn:\n"
        "/start - Bắt đầu\n"
        "/ping - Kiểm tra bot\n"
        "/menu - Danh sách lệnh\n"
        "/list - Xem file đã gửi\n"
        "/list_ngay <dd-mm-yyyy> - Lọc file theo ngày"
    )

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if not context.args:
        await update.message.reply_text("📅 Dùng: /list_ngay dd-mm-yyyy")
        return
    filter_date = context.args[0].strip()
    try:
        datetime.strptime(filter_date, "%d-%m-%Y")
        username = context.bot.username
        filtered = [f for f in received_files if f["time"].endswith(filter_date)]
        if not filtered:
            await update.message.reply_text(f"❌ Không có file nào ngày {filter_date}.")
            return
        text = f"📅 File gửi ngày {filter_date}:\n\n"
        for f in filtered:
            text += (
                f"🆔 <b>ID:</b> <a href='tg://resolve?domain={username}&message_id={f['id']}'>{f['id']}</a>\n"
                f"📄 <b>Tên:</b> {f['name']}\n"
                f"📦 <b>Dung lượng:</b> {f['size']}\n"
                f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
            )
        await update.message.reply_html(text, disable_web_page_preview=True)
    except ValueError:
        await update.message.reply_text("❌ Sai định dạng. Dùng: /list_ngay 19-05-2025")

# === Xử lý file & ảnh ===
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc: return
    msg_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    time_str = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    size = f"{doc.file_size/1024:.2f} KB" if doc.file_size < 1024*1024 else f"{doc.file_size/1024/1024:.2f} MB"
    data = {"id": msg_id, "name": doc.file_name, "size": size, "time": time_str}
    received_files.append(data)
    append_to_sheet(data)
    await update.message.reply_html(
        f"📄 <b>Tên file:</b> {doc.file_name}\n📦 <b>Dung lượng:</b> {size}\n"
        f"⏰ <b>Thời gian:</b> {time_str}\n🆔 <b>ID:</b> <code>{msg_id}</code>"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    msg_id = update.message.message_id
    sent_time = update.message.date.astimezone(vn_tz)
    time_str = sent_time.strftime("%H:%M:%S %d-%m-%Y")
    size = f"{photo.file_size/1024:.2f} KB" if photo.file_size < 1024*1024 else f"{photo.file_size/1024/1024:.2f} MB"
    data = {"id": msg_id, "name": "Ảnh (không có tên)", "size": size, "time": time_str}
    received_files.append(data)
    append_to_sheet(data)
    await update.message.reply_html(
        f"🖼 <b>Ảnh nhận được</b>\n📦 <b>Dung lượng:</b> {size}\n"
        f"⏰ <b>Thời gian:</b> {time_str}\n🆔 <b>ID:</b> <code>{msg_id}</code>"
    )

# === Gắn handler ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ping", ping))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CommandHandler("list", list_files))
application.add_handler(CommandHandler("list_ngay", list_files_by_date))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

async def set_bot_commands(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Bắt đầu"),
        BotCommand("ping", "Kiểm tra bot"),
        BotCommand("menu", "Hiển thị menu"),
        BotCommand("list", "Xem file đã gửi"),
        BotCommand("list_ngay", "Lọc theo ngày")
    ])
application.post_init = set_bot_commands

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), event_loop)
    return {"ok": True}

@app.route("/")
def home(): return "🤖 Bot Telegram đang chạy!"

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
