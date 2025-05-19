from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# === Giao diện chọn ngày từ danh sách file đã lưu ===
async def chon_ngay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    received_files = context.bot_data.get("received_files", [])
    dates = sorted({f['time'].split()[-1] for f in received_files})
    if not dates:
        await update.message.reply_text("📭 Không có dữ liệu ngày nào.")
        return

    keyboard = []
    row = []
    for i, date in enumerate(dates, 1):
        row.append(InlineKeyboardButton(date, callback_data=f"chon_ngay_{date}"))
        if i % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📅 Chọn ngày để tải lại file:", reply_markup=markup)

# === Xử lý khi người dùng bấm vào nút chọn ngày ===
async def handle_ngay_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("chon_ngay_"):
        return

    date_str = query.data.replace("chon_ngay_", "")
    received_files = context.bot_data.get("received_files", [])
    matched = [f for f in received_files if f["time"].endswith(date_str)]

    if not matched:
        await query.edit_message_text(f"❌ Không có file nào trong ngày {date_str}.")
        return

    await query.edit_message_text(f"📤 Đang gửi {len(matched)} file từ ngày {date_str}...")

    for f in matched:
        try:
            # Nếu có file_id thì gửi lại bằng send_document
            if "file_id" in f:
                await context.bot.send_document(
                    chat_id=update.effective_user.id,
                    document=f["file_id"],
                    caption=f"📄 {f['name']}\n📦 {f['size']}\n⏰ {f['time']}"
                )
            else:
                # Nếu không có file_id, gửi thông báo hỗ trợ
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=(
                        f"⚠️ File ID: {f['id']} không thể gửi lại tự động.\n"
                        f"📄 Tên: {f['name']}\n📦 Dung lượng: {f['size']}\n"
                        f"⏰ Thời gian: {f['time']}"
                    )
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"🚫 Lỗi gửi file ID {f['id']}: {str(e)}"
            )
