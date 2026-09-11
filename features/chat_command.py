import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ContextTypes

# Khởi tạo client kết nối tới API Xpiki
client = OpenAI(
    base_url="https://api.xpiki.com/v1",
    api_key=os.getenv("XPIKI_API_KEY", "sk-MLUewGJrExBmDd4IK5Uta657NLQ0F4d6K8Bhdo1AZZM")
)

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sử dụng lệnh: /ask <nội dung câu hỏi>
    Ví dụ: /ask Viết giúp tôi một đoạn code Python
    """
    if not context.args:
        await update.message.reply_text("Vui lòng nhập câu hỏi sau lệnh. Ví dụ: `/ask Xin chào`", parse_mode="Markdown")
        return

    user_query = " ".join(context.args)
    
    # Hiển thị trạng thái đang soạn tin nhắn trên Telegram
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.chat.completions.create(
            model="gpt-6-astra",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý AI hữu ích."},
                {"role": "user", "content": user_query}
            ]
        )
        reply_content = response.choices[0].message.content
        await update.message.reply_text(reply_content)
    except Exception as e:
        await update.message.reply_text(f"Lỗi khi kết nối AI: {e}")
