# features/like_command.py
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://api-likes-alliff-v3.vercel.app/like"

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng lệnh: /like <uid>")
        return
    
    uid = context.args[0]

    params = {
        "uid": uid
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=15) as resp:
                if resp.status != 200:
                    await update.message.reply_text(f"❌ API trả về HTTP {resp.status}")
                    return
                data = await resp.json()

        # Check nếu không thêm được like
        likes_added = data.get("likes_added", 0)
        name = data.get("name", "Unknown")
        uid = data.get("uid", "?")

        if likes_added == 0:
            reply = (
                f"👤 Nickname: {name}\n"
                f"🆔 UID: {uid}\n\n"
                "❌ Hôm nay đã tối đa lượt like, vui lòng thử ID khác."
            )
        else:
            reply = (
                f"✅ Like thành công!\n\n"
                f"👤 Nickname: {name}\n"
                f"🆔 UID: {uid}\n"
                f"❤️ Likes trước: {data.get('likes_before')}\n"
                f"➕ Likes thêm: {likes_added}\n"
                f"📈 Likes sau: {data.get('likes_after')}\n\n"
                f"Cảm ơn bạn đã sử dụng Bot của TranDatDev 🙏"
            )

        await update.message.reply_text(reply)

    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu (timeout).")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")
