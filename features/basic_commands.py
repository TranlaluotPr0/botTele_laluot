from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from features.file_list import list_files
from features.import_export import export_csv, import_csv
from features.chon_ngay import chon_ngay


# === Gửi menu chính qua nút ===
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Quản lý file", callback_data="menu_file")],
        [InlineKeyboardButton("📅 Quản lý theo ngày", callback_data="menu_date")],
        [InlineKeyboardButton("🏷 Gắn tag & lọc", callback_data="menu_tag")],
        [InlineKeyboardButton("📖 Hướng dẫn sử dụng", callback_data="menu_help")]
    ])
    await update.message.reply_text("📋 <b>Menu lệnh chính:</b>", reply_markup=keyboard, parse_mode="HTML")


# === Callback xử lý tất cả menu ===
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # === Quay lại menu chính ===
    if query.data == "menu_main":
        await menu(update, context)

    # === Quản lý file ===
    elif query.data == "menu_file":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Danh sách file", callback_data="cmd_list")],
            [InlineKeyboardButton("📏 Lọc dung lượng", callback_data="cmd_filter_size")],
            [InlineKeyboardButton("⬇️ Xuất log", callback_data="cmd_export")],
            [InlineKeyboardButton("⬆️ Nhập log", callback_data="cmd_import")],
            [InlineKeyboardButton("🔙 Quay lại menu", callback_data="menu_main")]
        ])
        await query.edit_message_text("📁 <b>Quản lý file:</b>", reply_markup=keyboard, parse_mode="HTML")

    elif query.data == "cmd_list":
        await list_files(update, context)
    elif query.data == "cmd_filter_size":
        await query.message.reply_text("📏 Nhập dung lượng cần lọc, ví dụ: <code>0.5 5</code> (MB)", parse_mode="HTML")
    elif query.data == "cmd_export":
        await export_csv(update, context)
    elif query.data == "cmd_import":
        await import_csv(update, context)

    # === Quản lý theo ngày ===
    elif query.data == "menu_date":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 Lọc theo ngày", callback_data="cmd_list_date")],
            [InlineKeyboardButton("📆 Chọn ngày bằng nút", callback_data="cmd_chon_ngay")],
            [InlineKeyboardButton("🔙 Quay lại menu", callback_data="menu_main")]
        ])
        await query.edit_message_text("📅 <b>Quản lý theo ngày:</b>", reply_markup=keyboard, parse_mode="HTML")

    elif query.data == "cmd_list_date":
        await query.message.reply_text("📅 Nhập ngày cần lọc (dd-mm-yyyy), ví dụ: <b>20-05-2025</b>", parse_mode="HTML")
    elif query.data == "cmd_chon_ngay":
        await chon_ngay(update, context)

    # === Gắn tag & lọc ===
    elif query.data == "menu_tag":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Gắn tag", callback_data="cmd_addtag")],
            [InlineKeyboardButton("🔍 Lọc theo tag", callback_data="cmd_tag")],
            [InlineKeyboardButton("❌ Gỡ tag", callback_data="cmd_removetag")],
            [InlineKeyboardButton("🧹 Xoá toàn bộ tag", callback_data="cmd_cleartags")],
            [InlineKeyboardButton("✏️ Đổi tên tag", callback_data="cmd_renametag")],
            [InlineKeyboardButton("🔙 Quay lại menu", callback_data="menu_main")]
        ])
        await query.edit_message_text("🏷 <b>Gắn tag & lọc:</b>", reply_markup=keyboard, parse_mode="HTML")

    elif query.data == "cmd_addtag":
        await query.message.reply_text("➕ Gửi nội dung: <code>ID TAG</code> (ví dụ: <b>123 học_tập</b>)", parse_mode="HTML")
    elif query.data == "cmd_tag":
        await query.message.reply_text("🔍 Gửi tên tag để lọc, ví dụ: <b>học_tập</b>", parse_mode="HTML")
    elif query.data == "cmd_removetag":
        await query.message.reply_text("❌ Gửi nội dung: <code>ID TAG</code> để gỡ", parse_mode="HTML")
    elif query.data == "cmd_cleartags":
        await query.message.reply_text("🧹 Gửi ID file cần xoá toàn bộ tag", parse_mode="HTML")
    elif query.data == "cmd_renametag":
        await query.message.reply_text("✏️ Gửi: <code>tag_cũ tag_mới</code> để đổi tên", parse_mode="HTML")

    # === Hướng dẫn ===
    elif query.data == "menu_help":
        await query.edit_message_text(
            "📚 <b>Hướng dẫn:</b>\n"
            "Mọi chức năng đều có thể truy cập qua menu nút bấm.\n"
            "Một số chức năng yêu cầu bạn nhập nội dung cụ thể như ngày, tag, ID file...\n\n"
            "🧑‍💻 Bot đang được nâng cấp liên tục!",
            parse_mode="HTML"
        )

    else:
        await query.edit_message_text("❓ Không rõ lựa chọn.", parse_mode="HTML")

