import aiohttp
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime

API_URL = "https://xp-event-api-s1-w12s.vercel.app/event"

def format_time(timestamp: int) -> str:
    """Chuyển timestamp thành ngày giờ VN"""
    try:
        return datetime.utcfromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return "N/A"

async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: `/events <region>`\n\nVí dụ: `/events vn`", parse_mode="Markdown")
        return

    region = context.args[0].lower()
    params = {"region": region}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    await update.message.reply_text(f"❌ API trả về lỗi HTTP {resp.status}")
                    return
                data = await resp.json()

        if not data.get("success"):
            await update.message.reply_text("❌ API không trả về dữ liệu hợp lệ.")
            return

        events = data.get("events", [])
        if not events:
            await update.message.reply_text("📭 Không có sự kiện nào trong khu vực này.")
            return

        text_lines = [f"📌 **Danh sách sự kiện [{region.upper()}]:**\n"]
        buttons = []

        for i, event in enumerate(events[:10], start=1):  # Giới hạn 10 sự kiện cho gọn
            title = event.get("Title", "Không có tên")
            start = format_time(event.get("Start", 0))
            end = format_time(event.get("End", 0))
            link = event.get("link", None)
            banner = event.get("Banner", None)

            text_lines.append(f"🎉 {i}. *{title}*")
            text_lines.append(f"   🕒 {start} → {end}")

            if link:
                buttons.append([InlineKeyboardButton(f"🔗 {title}", url=link)])
            elif banner:
                buttons.append([InlineKeyboardButton(f"🖼 {title}", url=banner)])

        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
        await update.message.reply_text("\n".join(text_lines), parse_mode="Markdown", reply_markup=reply_markup)

    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")
