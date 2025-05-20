# features/loc_dungluong.py

from telegram import Update
from telegram.ext import ContextTypes
import re

waiting_dungluong = set()
received_files = []

def get_waiting_set():
    return waiting_dungluong

def set_received_files(data):
    global received_files
    received_files = data


# === Hàm chuyển đơn vị sang MB ===
def convert_to_mb(value_str):
    pattern = r"([\d.]+)\s*(KB|MB|GB)?"
    match = re.fullmatch(pattern, value_str.strip().upper())
    if not match:
        raise ValueError("Không đúng định dạng đơn vị")

    value, unit = match.groups()
    value = float(value)

    if unit == "KB":
        return value / 1024
    elif unit == "GB":
        return value * 1024
    return value  # Mặc định là MB


async def loc_dungluong_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    waiting_dungluong.add(user_id)

    message = (
        "📏 Nhập khoảng dung lượng cần lọc.\n"
        "• Ví dụ: <code>100KB 10MB</code>\n"
        "• Hoặc: <code>>10MB</code> / <code><2GB</code>\n"
        "• Mặc định đơn vị là MB nếu không ghi rõ."
    )

    if update.callback_query:
        await update.callback_query.message.reply_text(message, parse_mode="HTML")
    elif update.message:
        await update.message.reply_text(message, parse_mode="HTML")


async def handle_dungluong_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id in waiting_dungluong:
        try:
            files = received_files

            # === Trường hợp toán tử đơn: >10MB hoặc <2GB
            if text.startswith(">") or text.startswith("<"):
                op = text[0]
                value = convert_to_mb(text[1:])
                if op == ">":
                    matched = [
                        f for f in files
                        if int(f['size']) / 1024 / 1024 > value
                    ]
                else:
                    matched = [
                        f for f in files
                        if int(f['size']) / 1024 / 1024 < value
                    ]
            else:
                # === Trường hợp khoảng: 100KB 10MB
                parts = text.split()
                if len(parts) != 2:
                    raise ValueError("Cần nhập 2 giá trị hoặc dùng > / <")

                min_mb = convert_to_mb(parts[0])
                max_mb = convert_to_mb(parts[1])

                matched = [
                    f for f in files
                    if min_mb <= int(f['size']) / 1024 / 1024 <= max_mb
                ]

            if matched:
                lines = [
                    f"📄 <b>{f['name']}</b>\n"
                    f"📦 {round(int(f['size']) / 1024 / 1024, 2)} MB\n"
                    f"🆔 <code>{f['id']}</code>"
                    for f in matched
                ]
                await update.message.reply_html("🔎 Kết quả tìm thấy:\n\n" + "\n\n".join(lines))
            else:
                await update.message.reply_text("❌ Không tìm thấy file nào phù hợp.")

            waiting_dungluong.discard(user_id)

        except Exception:
            await update.message.reply_text("⚠️ Sai định dạng. Ví dụ: 100KB 10MB hoặc >1GB")
