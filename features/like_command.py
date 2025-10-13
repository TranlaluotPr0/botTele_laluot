# features/like_command.py
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "http://47.84.86.76:1304/likes"

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng lệnh: /like <uid>\nVí dụ: /like 1048702328")
        return

    uid = context.args[0]
    if not uid.isdigit():
        await update.message.reply_text("⚠️ UID phải là số, ví dụ: /like 123456789")
        return

    params = {"uid": uid, "keys": "gaycow"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=15) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    await update.message.reply_text(
                        f"❌ API trả về HTTP {resp.status}\n📦 Nội dung: {text[:500]}"
                    )
                    return

                data = await resp.json(content_type=None)

        # --- Kiểm tra cấu trúc ---
        if not isinstance(data, dict) or "result" not in data:
            await update.message.reply_text(f"⚠️ API trả về JSON không hợp lệ:\n{data}")
            return

        result = data["result"]
        acc = result.get("ACCOUNT_INFO", {})
        likes = result.get("LIKES_DETAIL", {})
        api = result.get("API", {})

        # --- Lấy thông tin ---
        name = acc.get("Account Name", "Unknown")
        uid = acc.get("Account UID", uid)
        region = acc.get("Account Region", "N/A")
        likes_before = likes.get("Likes Before", "?")
        likes_after = likes.get("Likes After", "?")
        likes_added = likes.get("Likes Added", 0)
        speed = api.get("speeds", "?")

        # --- Format phản hồi ---
        if not api.get("success", False):
            reply = f"❌ API báo lỗi.\nTốc độ phản hồi: {speed}"
        elif likes_added == 0:
            reply = (
                f"👤 Nickname: {name}\n"
                f"🆔 UID: {uid}\n"
                f"🌍 Region: {region}\n\n"
                "❌ Hôm nay đã đạt giới hạn like hoặc không thể thêm like."
            )
        else:
            reply = (
                f"✅ Like thành công!\n\n"
                f"👤 Nickname: {name}\n"
                f"🆔 UID: {uid}\n"
                f"🌍 Region: {region}\n"
                f"❤️ Likes trước: {likes_before}\n"
                f"➕ Likes thêm: {likes_added}\n"
                f"📈 Likes sau: {likes_after}\n"
                f"⚡ Tốc độ API: {speed}\n\n"
                f"Cảm ơn bạn đã sử dụng Bot của TranDatDev 🙏"
            )

        await update.message.reply_text(reply)

    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu (timeout).")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {type(e).__name__}: {e}")
