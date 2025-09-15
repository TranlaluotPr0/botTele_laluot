# features/zw_menu.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

ZERO_WIDTH_SPACE = "\u200b"

# Biến trạng thái: user nào đang chờ nhập text để zw
waiting_zw_users = set()

def get_waiting_zw_set():
    return waiting_zw_users

# Menu thêm lựa chọn ZW
def zw_menu():
    return [InlineKeyboardButton("🌀 Chèn ký tự vô hình (ZW)", callback_data="cmd_zw")]

# Callback khi bấm menu
async def handle_zw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    waiting_zw_users.add(user_id)
    await query.edit_message_text(
        "✍️ Nhập chuỗi văn bản mà bạn muốn chèn **ký tự vô hình U+200B** vào giữa các ký tự."
    )

# Khi user gửi text sau khi chọn menu
async def handle_zw_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in waiting_zw_users:
        return  # Không phải đang trong chế độ nhập ZW

    original_text = update.message.text.strip()
    zw_text = ZERO_WIDTH_SPACE.join(list(original_text))

    waiting_zw_users.remove(user_id)
    await update.message.reply_text(
        f"✅ Kết quả:\n{zw_text}"
    )
