import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://like-api-by-jobayar.vercel.app/like"
API_KEY = "@JOBAYAR_AHMED"   # ✅ khóa cố định trong API

# Lệnh /likes <uid> [region]
async def likes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng lệnh: /likes <uid> [region]")
        return

    uid = context.args[0]
    region = context.args[1] if len(context.args) > 1 else "vn"   # mặc định VN

    params = {
        "uid": uid,
        "server_name": region,   # ✅ API yêu cầu server_name
        "key": API_KEY           # ✅ thêm key
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

        # Lấy dữ liệu từ JSON (theo format bạn test trước đó)
        likes_before = data.get("LikesbeforeCommand", "❓")
        likes_after = data.get("LikesafterCommand", "❓")
        likes_given = data.get("LikesGivenByAPI", "❓")
        nickname = data.get("PlayerNickname", "Không rõ")
        status = data.get("status", "❓")

        status_text = "✅ Thành công" if status == 1 else "❌ Thất bại"

        reply = (
            f"✨ *Kết quả Like*\n\n"
            f"👤 Nickname: `{nickname}`\n"
            f"🆔 UID: `{uid}`\n"
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
