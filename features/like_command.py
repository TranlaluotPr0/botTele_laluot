# features/like_command.py
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

# 🔗 API mới
API_URL = "https://ag-team-like-api.vercel.app/like"

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng lệnh: /like <uid>\nVí dụ: /like 1048702328")
        return

    uid = context.args[0]
    if not uid.isdigit():
        await update.message.reply_text("⚠️ UID phải là số, ví dụ: /like 123456789")
        return

    params = {"uid": uid}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=15) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    await update.message.reply_text(
                        f"❌ API trả về HTTP {resp.status}\n📦 Nội dung: {text[:500]}"
                    )
                    return

                data = await resp.json(content_type=None)  # 👈 Parse JSON

        # --- Kiểm tra dữ liệu ---
        if not isinstance(data, dict) or "LikesGivenByAPI" not in data:
            await update.message.reply_text(
                f"⚠️ API trả về nhưng không đúng định dạng JSON:\n\n{data}"
            )
            return

        # --- Lấy dữ liệu ---
        name = data.get("PlayerNickname", "Unknown")
        uid = data.get("UID", uid)
        likes_before = data.get("LikesBefore", "?")
        likes_after = data.get("LikesAfter", "?")
        likes_added = data.get("LikesGivenByAPI", 0)

        # --- Format tin nhắn ---
        if likes_added == 0:
            reply = (
                f"👤 Nickname: {name}\n"
                f"🆔 UID: {uid}\n\n"
                "❌ Hôm nay đã tối đa lượt like hoặc không thể thêm like."
            )
        else:
            reply = (
                f"✅ Like thành công!\n\n"
                f"👤 Nickname: {name}\n"
                f"🆔 UID: {uid}\n"
                f"❤️ Likes trước: {likes_before}\n"
                f"➕ Likes thêm: {likes_added}\n"
                f"📈 Likes sau: {likes_after}\n\n"
                f"Cảm ơn bạn đã sử dụng Bot của TranDatDev 🙏"
            )

        await update.message.reply_text(reply)

    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu (timeout).")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {type(e).__name__}: {e}")
