# features/like_command.py
import aiohttp
import asyncio
import re
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://api-likes-alli-ff.vercel.app/like"

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng lệnh: /ok <uid>\nVí dụ: /ok 1048702328")
        return

    uid = context.args[0]

    if not uid.isdigit():
        await update.message.reply_text("⚠️ UID phải là số, ví dụ: /ok 123456789")
        return

    params = {"uid": uid}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=15) as resp:
                text = await resp.text()

                if resp.status != 200:
                    await update.message.reply_text(
                        f"❌ API trả về HTTP {resp.status}\n📦 Nội dung: {text[:500]}"
                    )
                    return

        # --- Parse dữ liệu từ plain text ---
        name_match = re.search(r"Name:\s*(.+)", text)
        before_match = re.search(r"Likes Before:\s*(\d+)", text)
        after_match = re.search(r"Likes After:\s*(\d+)", text)
        added_match = re.search(r"Likes Added:\s*(\d+)", text)
        uid_match = re.search(r"UID:\s*(\d+)", text)

        if not added_match:  # ❌ Không parse được -> gửi toàn bộ nội dung về user
            await update.message.reply_text(
                f"⚠️ API trả về nhưng không parse được dữ liệu:\n\n{text[:1500]}"
            )
            return

        # Nếu parse thành công
        name = name_match.group(1).strip() if name_match else "Unknown"
        likes_before = before_match.group(1) if before_match else "?"
        likes_after = after_match.group(1) if after_match else "?"
        likes_added = int(added_match.group(1)) if added_match else 0
        uid = uid_match.group(1) if uid_match else uid

        # --- Format tin nhắn trả về ---
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
        await update.message.reply_text(f"❌ Lỗi: {e}")
