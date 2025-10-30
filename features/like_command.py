# features/like_command.py
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://api.freefireservice.dnc.su/sendLikes"
ACCESS_KEY = "@onew_modz"

async def like_single_uid(uid: str) -> str:
    """Xử lý 1 UID duy nhất, trả về chuỗi kết quả."""
    params = {"uid": uid, "access_key": ACCESS_KEY}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=20) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    return f"❌ UID {uid}: HTTP {resp.status}\n📦 Nội dung: {text[:300]}"

                data = await resp.json(content_type=None)
    except asyncio.TimeoutError:
        return f"⏰ UID {uid}: API phản hồi quá lâu (timeout)."
    except Exception as e:
        return f"❌ UID {uid}: {type(e).__name__}: {e}"

    # --- Kiểm tra dữ liệu ---
    if not isinstance(data, dict) or "result" not in data:
        return f"⚠️ UID {uid}: JSON không hợp lệ.\n{data}"

    result = data["result"]
    acc = result.get("ACCOUNT_INFO", {})
    likes = result.get("LIKES_DETAIL", {})
    api = result.get("API", {})

    # --- Trích thông tin ---
    name = acc.get("Account Name", "Unknown")
    region = acc.get("Account Region", "N/A")
    uid = acc.get("Account UID", uid)
    likes_before = likes.get("Likes Before", "?")
    likes_after = likes.get("Likes After", "?")
    likes_added = likes.get("Likes Added", 0)
    speed = api.get("speeds", "?")
    success = api.get("success", False)

    # --- Format kết quả ---
    if not success:
        return f"❌ UID {uid}: API báo lỗi. (Tốc độ {speed})"
    elif likes_added == 0:
        return (
            f"👤 {name}\n🆔 {uid}\n🌍 {region}\n"
            f"❌ Không thể thêm like (đã đạt giới hạn hoặc lỗi)\n⚡ {speed}"
        )
    else:
        return (
            f"✅ Like thành công cho UID {uid}!\n"
            f"👤 {name}\n🌍 {region}\n"
            f"❤️ Trước: {likes_before}\n"
            f"➕ Thêm: {likes_added}\n"
            f"📈 Sau: {likes_after}\n"
            f"⚡ Tốc độ: {speed}"
        )


async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý /like <uid1> <uid2> ... hoặc nhiều UID xuống dòng."""
    if not context.args:
        await update.message.reply_text("⚠️ Dùng lệnh:\n/like <uid1> [uid2 uid3 ...]\nHoặc xuống dòng nhiều UID.")
        return

    # Ghép args lại và tách UID
    text = " ".join(context.args)
    uids = [u.strip() for u in text.replace("\n", " ").split() if u.strip().isdigit()]

    if not uids:
        await update.message.reply_text("⚠️ Không tìm thấy UID hợp lệ. Mỗi UID phải là số.")
        return

    await update.message.reply_text(f"🔄 Đang xử lý {len(uids)} UID... Vui lòng chờ ⏳")

    for i, uid in enumerate(uids, start=1):
        reply = await like_single_uid(uid)
        await update.message.reply_text(f"📍 {i}/{len(uids)}\n{reply}")
        await asyncio.sleep(2)  # nghỉ 2s giữa các request để tránh bị chặn

    await update.message.reply_text("✅ Hoàn tất tất cả UID!")
