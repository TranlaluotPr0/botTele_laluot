# features/loc_dungluong.py

from telegram import Update
from telegram.ext import ContextTypes

# Bộ nhớ tạm thời lưu user đang chờ lọc dung lượng
waiting_dungluong = set()
received_files = []  # Sẽ được gán từ main.py

def get_waiting_set():
    return waiting_dungluong

def set_received_files(data):
    global received_files
    received_files = data


# Gọi khi người dùng nhấn nút "📏 Lọc dung lượng"
async def loc_dungluong_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    waiting_dungluong.add(user_id)

    if update.callback_query:
        await update.callback_query.message.reply_text(
            "📏 Nhập khoảng dung lượng cần lọc (MB), ví dụ: <code>0.5 5</code>",
            parse_mode="HTML"
        )
    elif update.message:
        await update.message.reply_text(
            "📏 Nhập khoảng dung lượng cần lọc (MB), ví dụ: <code>0.5 5</code>",
            parse_mode="HTML"
        )


# Gọi khi người dùng nhập đoạn text (ví dụ: "0.5 5")
async def handle_dungluong_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id in waiting_dungluong:
        try:
            min_mb, max_mb = map(float, text.split())
            matched = [
                f"📄 <b>{f['name']}</b>\n📦 {round(f['size'] / 1024 / 1024, 2)} MB\n🆔 <code>{f['id']}</code>"
                for f in received_files
                if min_mb <= f['size'] / 1024 / 1024 <= max_mb
            ]

            if matched:
                await update.message.reply_html("🔎 Kết quả tìm thấy:\n\n" + "\n\n".join(matched))
            else:
                await update.message.reply_text("❌ Không tìm thấy file nào trong khoảng dung lượng.")
        except ValueError:
            await update.message.reply_text("⚠️ Sai định dạng. Nhập đúng như: 0.5 5")

        waiting_dungluong.discard(user_id)
