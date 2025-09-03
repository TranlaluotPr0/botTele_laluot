# features/like_command.py
import aiohttp
import asyncio
from aiohttp import ClientConnectorError
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://amdtsmodz.onrender.com/like"

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng lệnh:\n`/like <uid> [region]`\n\nVí dụ: `/like 7534574512 VN`", parse_mode="Markdown")
        return

    uid = context.args[0]
    region = context.args[1].upper() if len(context.args) > 1 else "VN"

    params = {
        "uid": uid,
        "server_name": region
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    await update.message.reply_text(f"❌ API trả về HTTP {resp.status}")
                    return

                data = await resp.json()

        if data.get("status") != 1:
            await update.message.reply_text(f"❌ Lỗi: {data.get('error', 'Không xác định')}")
            return

        reply_text = (
            f"👍 **Tăng like thành công!**\n\n"
            f"👤 Nickname: `{data.get('PlayerNickname')}`\n"
            f"🆔 UID: `{data.get('UID')}`\n"
            f"⭐ Level: {data.get('Level')}\n"
            f"🌍 Region: {data.get('Region')}\n\n"
            f"💖 Likes trước: {data.get('LikesbeforeCommand')}\n"
            f"➕ Được cộng: {data.get('LikesGivenByAPI')}\n"
            f"💖 Likes sau: {data.get('LikesafterCommand')}\n\n"
            f"✅ Cảm ơn bạn đã sử dụng Bot của DatTranDev!"
        )

        await update.message.reply_text(reply_text, parse_mode="Markdown")

    except ClientConnectorError:
        await update.message.reply_text("❌ Không kết nối được API.")
    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
    except Exception as e:
        await update.message.reply_text(f"❌ Có lỗi xảy ra: {e}")
