from telegram import InlineKeyboardMarkup, InlineKeyboardButton

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # ==== Quản lý file ====
    if query.data == "menu_file":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Danh sách file", callback_data="cmd_list")],
            [InlineKeyboardButton("📏 Lọc dung lượng", callback_data="cmd_filter_size")],
            [InlineKeyboardButton("⬇️ Xuất log", callback_data="cmd_export")],
            [InlineKeyboardButton("⬆️ Nhập log", callback_data="cmd_import")],
            [InlineKeyboardButton("🔙 Quay lại menu", callback_data="menu_main")]
        ])
        await query.edit_message_text("📁 <b>Quản lý file:</b>", parse_mode="HTML", reply_markup=keyboard)

    # ==== Quay lại menu chính ====
    elif query.data == "menu_main":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📁 Quản lý file", callback_data="menu_file")],
            [InlineKeyboardButton("📅 Quản lý theo ngày", callback_data="menu_date")],
            [InlineKeyboardButton("🏷 Gắn tag & lọc", callback_data="menu_tag")],
            [InlineKeyboardButton("📖 Hướng dẫn sử dụng", callback_data="menu_help")]
        ])
        await query.edit_message_text("📋 <b>Menu lệnh chính:</b>", reply_markup=keyboard, parse_mode="HTML")

    # ==== Gọi lệnh tương ứng ====
    elif query.data == "cmd_list":
        await query.message.chat.send_message("/list")
    elif query.data == "cmd_filter_size":
        await query.message.chat.send_message("/filter_size 0.1 5")
    elif query.data == "cmd_export":
        await query.message.chat.send_message("/export")
    elif query.data == "cmd_import":
        await query.message.chat.send_message("/import")

    # ==== Các phần khác giữ nguyên... ====
    elif query.data == "menu_date":
        await query.edit_message_text(
            "📅 <b>Quản lý theo ngày:</b>\n"
            "/list_ngay dd-mm-yyyy – Lọc file theo ngày\n"
            "/chon_ngay – Chọn ngày bằng nút hoặc nhập tay (VD: 19/5)",
            parse_mode="HTML"
        )

    elif query.data == "menu_tag":
        await query.edit_message_text(
            "🏷 <b>Gắn tag & lọc:</b>\n"
            "/addtag <id> <tag> – Gắn tag cho file\n"
            "/tag <tag> – Lọc file theo tag\n"
            "/removetag <id> <tag> – Gỡ 1 tag khỏi file\n"
            "/cleartags <id> – Xoá toàn bộ tag của file\n"
            "/renametag <tag_cu> <tag_moi> – Đổi tên tag",
            parse_mode="HTML"
        )

    elif query.data == "menu_help":
        await query.edit_message_text(
            "📚 <b>Hướng dẫn sử dụng bot:</b>\n"
            "/start – Bắt đầu bot\n"
            "/ping – Kiểm tra bot\n"
            "/help – Hướng dẫn sử dụng\n"
            "/chuc_nang – Hiện chức năng nâng cao\n\n"
            "🧑‍💻 Bot đang được nâng cấp thêm tính năng mới!",
            parse_mode="HTML"
        )

    else:
        await query.edit_message_text("❓ Không rõ lựa chọn.", parse_mode="HTML")
