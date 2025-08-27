# features/like_command.py
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "http://103.149.253.241:2010/like"
KEY = "conbo"

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # /like UID [region]
        if len(context.args) < 1:
            await update.message.reply_text(
                "❌ Vui lòng nhập UID.\n\n"
                "Ví dụ:\n"
                "   /like 447582027\n"
                "   /like 447582027 sg"
            )
            return

        uid = context.args[0]
        region = context.args[1] if len(context.args) > 1 else "vn"

        params = {
            "key": KEY,
            "uid": uid,
            "region": region
        }

        # Gọi API bất đồng bộ
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params) as resp:
                if resp.status != 200:
                    await update.message.reply_text("❌ API không phản hồi, vui lòng thử lại sau.")
                    return
                data = await resp.json()

        # Kiểm tra dữ liệu
        if data.get("status") == 1 or data.get("status") == 2:
            msg = (
                f"🔥 Kết quả Like:\n\n"
                f"👤 Nickname: {data.get('PlayerNickname','N/A')}\n"
                f"🆔 UID: {data.get('UID')}\n"
                f"⭐ Level: {data.get('Level')}\n"
                f"📍 Region: {data.get('Region')}\n\n"
                f"👍 Likes trước: {data.get('LikesbeforeCommand')}\n"
                f"✨ Likes thêm: {data.get('LikesGivenByAPI')}\n"
                f"✅ Likes sau: {data.get('LikesafterCommand')}"
            )
        else:
            msg = "❌ Không thể thực hiện like, vui lòng thử lại sau!"

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")
