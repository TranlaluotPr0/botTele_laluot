# features/like_command.py
import requests
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://like-xp-v12.vercel.app/like"

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Kiểm tra tham số UID
        if len(context.args) < 1:
            await update.message.reply_text("❌ Vui lòng nhập UID.\nVí dụ: /like 2518332290")
            return

        uid = context.args[0]
        region = "vn"  # mặc định VN
        key = "xp"

        # Gọi API
        params = {
            "server_name": region,
            "uid": uid,
            "key": key
        }
        response = requests.get(API_URL, params=params)
        data = response.json()

        if data.get("status") == 1:
            msg = (
                f"🔥 Like thành công!\n\n"
                f"👤 Nickname: {data.get('PlayerNickname')}\n"
                f"🆔 UID: {data.get('UID')}\n"
                f"👍 Likes trước: {data.get('LikesbeforeCommand')}\n"
                f"✨ Likes thêm: {data.get('LikesGivenByAPI')}\n"
                f"✅ Likes sau: {data.get('LikesafterCommand')}"
            )
        else:
            msg = "❌ Không thể thực hiện like, vui lòng thử lại sau!"

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")
