import aiohttp
import asyncio
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

API_URL = "https://xp-event-api-s1-w12s.vercel.app/event?region={region}"

# === Kiểm tra URL hợp lệ cho Telegram ===
def is_valid_url(url: str) -> bool:
    if not url:
        return False
    if not url.startswith("http"):
        return False
    if "<" in url or ">" in url:  # loại bỏ placeholder
        return False
    return True

# === Định dạng timestamp thành ngày giờ dễ đọc (UTC+7 cho VN) ===
def format_time(ts: int) -> str:
    if not ts:
        return "?"
    tz_vn = timezone(timedelta(hours=7))  # múi giờ VN (GMT+7)
    return datetime.fromtimestamp(ts, tz=tz_vn).strftime("%d-%m-%Y %H:%M")

# === Lệnh /events {region} ===
async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng lệnh: `/events vn` hoặc `/events bd`", parse_mode="Markdown")
        return

    region = context.args[0].upper()

    url = API_URL.format(region=region)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    await update.message.reply_text(f"❌ API trả về lỗi HTTP {resp.status}")
                    return
                data = await resp.json()
    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
        return
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi gọi API: {e}")
        return

    events = data.get("events", [])
    if not events:
        await update.message.reply_text("⚠️ Không có sự kiện nào trong khu vực này.")
        return

    text_lines = [f"📅 **Danh sách sự kiện ({region})**:"]
    buttons = []

    for i, event in enumerate(events[:10], start=1):  # giới hạn 10 sự kiện
        title = event.get("Title", "Không có tên")
        start = format_time(event.get("Start", 0))
        end = format_time(event.get("End", 0))
        link = event.get("link", None)
        banner = event.get("Banner", None)

        text_lines.append(f"\n🎉 {i}. *{title}*")
        text_lines.append(f"   🕒 {start} → {end}")

        # Ưu tiên tạo button từ link chính
        if is_valid_url(link):
            buttons.append([InlineKeyboardButton(f"🔗 {title}", url=link)])
        elif is_valid_url(banner):
            buttons.append([InlineKeyboardButton(f"🖼 {title}", url=banner)])
        else:
            # Nếu URL lỗi thì in ra text cho người dùng copy
            if link:
                text_lines.append(f"   🔗 {link}")
            if banner:
                text_lines.append(f"   🖼 {banner}")

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    await update.message.reply_text("\n".join(text_lines), parse_mode="Markdown", reply_markup=reply_markup)
