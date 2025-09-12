import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://freefirev1.vercel.app/like"
API_KEY = "FreeKey"  # Key cố định

# Lệnh /likes <uid>
async def likes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng lệnh: /likes <uid>")
        return

    uid = context.args[0]

    params = {
        "uid": uid,
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

        # Vì response là 1 list JSON, lấy phần tử thứ 2 (thông tin like)
        if len(data) < 2:
            await update.message.reply_text(f"⚠️ API không trả về dữ liệu hợp lệ:\n{data}")
            return

        info = data[1]  # phần tử thứ 2 chứa thông tin like
        key_info = data[0]  # phần tử đầu tiên chứa thông tin key

        # Lấy dữ liệu
        likes_before = info.get("Likes Before Command", "❓")
        likes_after = info.get("Likes after", "❓")
        likes_added = info.get("Likes Added", "❓")
        nickname = info.get("Player Name", "Không rõ")
        uid_resp = info.get("Player UID", uid)
        status = info.get("Status", "❌")

        reply = (
            f"✨ *Kết quả Like (API V1)*\n\n"
            f"👤 Nickname: `{nickname}`\n"
            f"🆔 UID: `{uid_resp}`\n\n"
            f"👍 Likes Trước: {likes_before}\n"
            f"➕ Likes Được Cộng: {likes_added}\n"
            f"✨ Likes Sau: {likes_after}\n\n"
            f"📌 Trạng thái: {status}\n\n"
            f"🔑 Key Expire: {key_info.get('key expire', '❓')}\n"
            f"⏳ Remaining Limit: {key_info.get('remaining limit', '❓')}\n"
            f"✅ Verify: {key_info.get('verify', '❓')}\n\n"
            f"🙏 Cảm ơn bạn đã sử dụng Bot của DatTranDev"
        )

        await update.message.reply_text(reply, parse_mode="Markdown")

    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")
