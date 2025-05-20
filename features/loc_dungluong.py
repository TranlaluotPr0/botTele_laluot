# features/loc_dungluong.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Danh sách user đang chờ nhập khoảng dung lượng
waiting_dungluong = set()

def get_waiting_set():
    return waiting_dungluong

def set_received_files(data):
    global received_files
    received_files = data

# Khi người dùng bấm menu lọc dung lượng
async def loc_dungluong_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    waiting_dungluong.add(query.from_user.id)
    await query.message.reply_text("✍️ Nhập khoảng dung lượng cần lọc (MB), ví dụ: 0.5 5")

# Khi người dùng nhập khoảng dung lượng
async def handle_dungluong_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id in waiting_dungluong:
        try:
            min_mb, max_mb = map(float, text.split())
            matched = [
                f"📄 {f['name']} — {round(f['size'] / 1024 / 1024, 2)} MB"
                for f in received_files
                if min_mb <= f['size'] / (1024 * 1024) <= max_mb
            ]
            if matched:
                await update.message.reply_text("\n".join(matched))
            else:
                await update.message.reply_text("❌ Không tìm thấy file nào trong khoảng dung lượng.")
        except ValueError:
            await update.message.reply_text("⚠️ Sai định dạng. Nhập đúng như: 0.5 5")
        waiting_dungluong.discard(user_id)
