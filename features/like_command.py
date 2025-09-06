# features/like_command.py
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://ffgarena.vercel.app/like"

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng lệnh: /like <uid> [region]")
        return
    
    uid = context.args[0]
    # Nếu không có region thì mặc định = vn
    region = context.args[1].lower() if len(context.args) > 1 else "vn"

    params = {
        "uid": uid,
        "region": region,
        "key": "ScromnyiDev"  # key API
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    await update.message.reply_text(f"❌ API trả về HTTP {resp.status}")
                    return
                data = await resp.json()

        # Format response
        reply = (
            f"✅ Like thành công!\n\n"
            f"👤 Nickname: {data.get('PlayerNickname', 'Unknown')}\n"
            f"🆔 UID: {data.get('UID')}\n"
            f"❤️ Likes trước: {data.get('LikesBeforeCommand')}\n"
            f"➕ Likes thêm: {data.get('LikesGivenByAPI')}\n"
            f"📈 Likes sau: {data.get('LikesAfterCommand')}\n"
            f"🌍 Region: {region.upper()}\n"
            f"📊 Status: {data.get('status')}\n\n"
            f"Cảm ơn bạn đã sử dụng Bot của DatTranDev 🙏"
        )
        await update.message.reply_text(reply)

    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")
