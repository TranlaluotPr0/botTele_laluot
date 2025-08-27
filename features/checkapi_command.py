from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

API_URL = "https://searchaccountbyname-aya.vercel.app/search"
KEY = "aya"

# Hàm gọi API
def search_player(nickname, region="vn"):
    url = f"{API_URL}?nickname={nickname}&key={KEY}&region={region}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("players", [])
    return None

# Lệnh check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng lệnh: /check <nickname>")
        return

    nickname = context.args[0]
    players = search_player(nickname)

    if not players:
        await update.message.reply_text("❌ Không tìm thấy tài khoản nào")
        return

    msg = f"🔍 Kết quả tìm kiếm cho **{nickname}**:\n\n"
    for p in players:
        msg += f"👤 {p['nickname']} (Level {p['level']})\n"
        msg += f"   🆔 {p['accountId']}\n"
        msg += f"   🌍 {p['countryCode']} | Version: {p['gameVersion']}\n"
        msg += f"   ⏰ Last login: {p['lastLogin']}\n\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# Chạy bot
app = Application.builder().token("7370672219:AAEGlSpgVepH1GN3Zplm6pnFo3QnScxdbPA").build()
app.add_handler(CommandHandler("check", check))
app.run_polling()
