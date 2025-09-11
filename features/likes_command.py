import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://zx-gelmi-like.vercel.app/like"

# Lệnh /likes <uid> [region]
async def likes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng lệnh: /likes <uid> [region]")
        return

    uid = context.args[0]
    region = context.args[1] if len(context.args) > 1 else "vn"

    params = {
        "server_name": region,
        "uid": uid
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    await update.message.reply_text(f"❌ API trả về HTTP {resp.status}")
                    return

                try:
                    data = await resp.json()
                except Exception:
                    text = await resp.text()
                    await update.message.reply_text(f"📦 Raw response:\n{text}")
                    return

        # Format kết quả đẹp hơn
        likes_before = data.get("LikesBeforeCommand", "❓")
        likes_after = data.get("LikesAfterCommand", "❓")
        likes_given = data.get("LikesGivenByAPI", "❓")
        nickname = data.get("PlayerNickname", "Không rõ")
        status = data.get("status", "❓")

        reply = (
            f"✅ Kết quả Like\n"
            f"👤 Người chơi: {nickname}\n"
            f"🆔 UID: {uid}\n"
            f"🌍 Region: {region.upper()}\n\n"
            f"👍 Likes Trước: {likes_before}\n"
            f"✨ Likes Sau: {likes_after}\n"
            f"📥 Likes Cộng Thêm: {likes_given}\n\n"
            f"📌 Status: {status}\n\n"
            f"🙏 Cảm ơn bạn đã sử dụng Bot của DatTranDev"
        )

        await update.message.reply_text(reply)

    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")
