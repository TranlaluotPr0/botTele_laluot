from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

# === Lệnh /chon_ngay: hiển thị nút + cho phép nhập ngày ===
async def chon_ngay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    received_files = context.bot_data.get("received_files", [])
    if not received_files:
        await update.message.reply_text("📭 Chưa có dữ liệu file nào.")
        return

    # Lấy các ngày có trong log
    dates = sorted({f['time'].split()[-1] for f in received_files})
    context.user_data["chon_ngay_mode"] = True  # Đánh dấu đang chờ nhập ngày

    # Giao diện nút chọn ngày
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

    # Gửi hướng dẫn + nút chọn ngày
    await update.message.reply_text(
        f"📅 Bạn có thể **chọn ngày bên dưới** hoặc **nhập ngày bằng tay** (ví dụ: 19/5 hoặc 18-05).\n"
        f"→ Từ ngày: {dates[0]} đến {dates[-1]}",
        reply_markup=markup
    )

# === Khi bấm vào nút chọn ngày ===
async def handle_ngay_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("chon_ngay_"):
        return

    date_str = query.data.replace("chon_ngay_", "")
    await process_date(update, context, date_str, from_callback=True)

# === Khi người dùng nhập ngày bằng tay ===
async def handle_ngay_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("chon_ngay_mode"):
        return  # Bỏ qua nếu không ở trạng thái chờ nhập ngày

    date_input = update.message.text.strip()
    # Chuẩn hoá các kiểu: 19/5, 19-05, 19/05/2025, ...
    for fmt in ["%d/%m", "%d-%m", "%d/%m/%Y", "%d-%m-%Y"]:
        try:
            parsed = datetime.strptime(date_input, fmt)
            date_str = parsed.strftime("%d-%m-%Y")
            await process_date(update, context, date_str)
            return
        except:
            continue
    await update.message.reply_text("❌ Ngày không hợp lệ. Vui lòng nhập lại (ví dụ: 19/5 hoặc 19-05-2025).")

# === Xử lý ngày đã chuẩn hóa (dùng chung cho nút & text) ===
async def process_date(update: Update, context: ContextTypes.DEFAULT_TYPE, date_str: str, from_callback=False):
    received_files = context.bot_data.get("received_files", [])
    matched = [f for f in received_files if f["time"].endswith(date_str)]

    if from_callback:
        await update.callback_query.edit_message_text(
            f"📤 Đang gửi {len(matched)} file từ ngày {date_str}..." if matched
            else f"❌ Không có file nào ngày {date_str}."
        )
    else:
        context.user_data["chon_ngay_mode"] = False  # Reset trạng thái nhập ngày
        await update.message.reply_text(
            f"📤 Đang gửi {len(matched)} file từ ngày {date_str}..." if matched
            else f"❌ Không có file nào ngày {date_str}."
        )

    for f in matched:
        try:
            if "file_id" in f:
                await context.bot.send_document(
                    chat_id=update.effective_user.id,
                    document=f["file_id"],
                    caption=f"📄 {f['name']}\n📦 {f['size']}\n⏰ {f['time']}"
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=(
                        f"📄 {f['name']} ({f['size']})\n⏰ {f['time']}\n"
                        f"⚠️ Không thể gửi lại file vì thiếu file_id."
                    )
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"⚠️ Lỗi gửi file: {f['name']}\n{str(e)}"
            )
