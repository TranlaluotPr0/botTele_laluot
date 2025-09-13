import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://like-dev-xzza.vercel.app/like"
API_KEY = "xza"   # ✅ Key cố định

# Lệnh /likes <uid> [region]
async def likes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng lệnh: /likes <uid> [region]")
        return

    uid = context.args[0]
    region = context.args[1] if len(context.args) > 1 else "VN"   # mặc định VN

    params = {
        "uid": uid,
        "server_name": region,
        "key": API_KEY
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    await update.message.reply_text(f"❌ API trả về HTTP {resp.status}\n📦 Nội dung: {text}")
                    return

                try:
                    data = await resp.json()
                except Exception:
                    text = await resp.text()
                    await update.message.reply_text(f"📦 Raw response:\n{text}")
                    return

        # Parse JSON an toàn (tùy response)
        likes_before = data.get("LikesbeforeCommand") or data.get("Likes Before Command", "❓")
        likes_after = data.get("LikesafterCommand") or data.get("Likes after", "❓")
        likes_given = data.get("LikesGivenByAPI") or data.get("Likes Added", "❓")
        nickname = data.get("PlayerNickname") or data.get("Player Name", "Không rõ")
        uid_resp = data.get("UID") or data.get("Player UID", uid)
        status = data.get("status") or data.get("Status", "❓")

        status_text = "✅ Thành công" if str(status).lower() in ["1", "success", "true"] else "❌ Thất bại"

        reply = (
            f"✨ *Kết quả Like*\n\n"
            f"👤 Nickname: `{nickname}`\n"
            f"🆔 UID: `{uid_resp}`\n"
            f"🌍 Server: {region.upper()}\n\n"
            f"👍 Likes Trước: {likes_before}\n"
            f"➕ Likes Được Cộng: {likes_given}\n"
            f"✨ Likes Sau: {likes_after}\n\n"
            f"📌 Trạng thái: {status_text}\n\n"
            f"🙏 Cảm ơn bạn đã sử dụng Bot của DatTranDev"
        )

        await update.message.reply_text(reply, parse_mode="Markdown")

    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")
