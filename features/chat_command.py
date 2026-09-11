import os
import requests
from telegram import Update
from telegram.ext import ContextTypes

# Lấy key từ biến môi trường hoặc điền trực tiếp
XPIKI_API_KEY = os.getenv("XPIKI_API_KEY", "sk-MLUewGJrExBmDd4IK5Uta657NLQ0F4d6K8Bhdo1AZZM")
API_URL = "https://api.xpiki.com/v1/chat/completions"

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh: /ask <câu hỏi>"""
    if not context.args:
        await update.message.reply_text("Vui lòng nhập câu hỏi sau lệnh `/ask`. Ví dụ:\n`/ask Xin chào`", parse_mode="Markdown")
        return

    user_query = " ".join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    headers = {
        "Authorization": f"Bearer {XPIKI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-6-astra",
        "messages": [
            {"role": "system", "content": "Bạn là trợ lý AI hữu ích."},
            {"role": "user", "content": user_query}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        data = response.json()

        if response.status_code == 200:
            reply_text = data["choices"][0]["message"]["content"]
            await update.message.reply_text(reply_text)
        else:
            err_msg = data.get("error", {}).get("message", response.text)
            await update.message.reply_text(f"⚠️ Lỗi API ({response.status_code}): {err_msg}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi kết nối: {e}")
