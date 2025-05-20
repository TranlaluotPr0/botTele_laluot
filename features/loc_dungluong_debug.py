from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import re
import traceback

# Bộ nhớ lưu user đang lọc
waiting_dungluong = set()

def get_waiting_set():
    return waiting_dungluong

def set_received_files(data):
    # Không còn cần nếu đã dùng context.application.bot_data
    pass

def convert_to_mb(value_str):
    pattern = r"^([\d.]+)\s*(KB|MB|GB)?$"
    match = re.fullmatch(pattern, value_str.strip().upper())
    if not match:
        raise ValueError(f"Không đúng định dạng đơn vị: {value_str!r}")
    value, unit = match.groups()
    value = float(value)
    if unit == "KB":
        return value / 1024
    elif unit == "GB":
        return value * 1024
    return value  # Mặc định MB

# --- Gọi khi nhấn "📏 Lọc dung lượng"
async def loc_dungluong_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔢 Lọc trong khoảng", callback_data="loc_khoang"),
            InlineKeyboardButton("🔼 Lọc > hoặc <", callback_data="loc_toan_tu")
        ],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="menu_file")]
    ])
    message = "📏 Chọn cách lọc dung lượng:"
    if update.callback_query:
        await update.callback_query.message.reply_text(message, reply_markup=keyboard)
    elif update.message:
        await update.message.reply_text(message, reply_markup=keyboard)

# --- Người dùng chọn lọc trong khoảng
async def loc_khoang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    waiting_dungluong.add(user_id)
    await update.callback_query.message.reply_text(
        "🔢 Nhập khoảng dung lượng cần lọc, ví dụ: <code>100KB 1GB</code>",
        parse_mode="HTML"
    )

# --- Người dùng chọn lọc > hoặc <
async def loc_toan_tu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    waiting_dungluong.add(user_id)
    await update.callback_query.message.reply_text(
        "🔼 Nhập điều kiện, ví dụ: <code>&gt;10MB</code> hoặc <code>&lt;500MB</code>",
        parse_mode="HTML"
    )

# --- Xử lý nội dung nhập từ người dùng
async def handle_dungluong_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().upper()

    if user_id not in waiting_dungluong:
        return

    try:
        files = context.application.bot_data.get("received_files", [])
        print("[DEBUG] Tổng số file:", len(files))

        # Trường hợp toán tử > hoặc <
        if text.startswith(">") or text.startswith("<"):
            op = text[0]
            value = convert_to_mb(text[1:])
            matched = [
                f for f in files
                if (int(f['size']) / 1024 / 1024 > value if op == ">" else int(f['size']) / 1024 / 1024 < value)
            ]
        else:
            # Trường hợp khoảng
            parts = text.split()
            if len(parts) != 2:
                raise ValueError("Cần nhập đúng định dạng khoảng: <min> <max>")
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

    except Exception as e:
        print("❌ Lỗi lọc:", e)
        traceback.print_exc()
        await update.message.reply_text(
            "⚠️ Sai định dạng. Nhập như:\n<code>100KB 1GB</code> hoặc <code>>50MB</code>",
            parse_mode="HTML"
        )
