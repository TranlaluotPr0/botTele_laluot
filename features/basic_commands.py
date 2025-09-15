# features/basic_commands.py
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from features.import_export import export_csv, import_csv

from features.loc_dungluong import get_waiting_set as get_waiting_luong_set
from features.tags import (
    add_tag, filter_by_tag, remove_tag, clear_tags, rename_tag,
    get_waiting_tag_action, set_waiting_tag_action
)

# logging để debug (Render show stdout)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Gửi menu chính qua nút ===
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Quản lý file", callback_data="menu_file")],
        [InlineKeyboardButton("📅 Quản lý theo ngày", callback_data="menu_date")],
        [InlineKeyboardButton("🌐 Chèn ký tự vô hình (ZW)", callback_data="menu_zw")],
    ])

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text="📋 <b>Menu lệnh chính:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    elif update.message:
        await update.message.reply_text(
            "📋 <b>Menu lệnh chính:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )


# === Callback xử lý tất cả menu ===
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Nếu bấm menu chính
    if query.data == "menu_main":
        await menu(update, context)
        return

    # === ZW Menu: bật cờ chờ input vào user_data ===
    if query.data == "menu_zw":
        context.user_data["awaiting_zw"] = True
        logger.info("User %s set awaiting_zw=True", query.from_user.id)
        await query.edit_message_text(
            "✍️ Nhập chuỗi văn bản mà bạn muốn chèn <b>ký tự vô hình U+200B</b> vào giữa các ký tự.",
            parse_mode="HTML"
        )
        return

    # === Quản lý file ===
    if query.data == "menu_file":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Danh sách file", callback_data="cmd_list")],
            [InlineKeyboardButton("📏 Lọc dung lượng", callback_data="cmd_filter_size")],
            [InlineKeyboardButton("⬇️ Xuất log", callback_data="cmd_export")],
            [InlineKeyboardButton("⬆️ Nhập log", callback_data="cmd_import")],
            [InlineKeyboardButton("🔙 Quay lại menu", callback_data="menu_main")]
        ])
        await query.edit_message_text("📁 <b>Quản lý file:</b>", reply_markup=keyboard, parse_mode="HTML")
        return

    elif query.data == "cmd_list":
        await query.message.reply_text("📄 Tính năng danh sách file đã được tạm xoá.")

    elif query.data == "cmd_filter_size":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔢 Lọc trong khoảng", callback_data="loc_khoang"),
                InlineKeyboardButton("🔼 Lọc > hoặc <", callback_data="loc_toan_tu")
            ],
            [InlineKeyboardButton("🔙 Quay lại", callback_data="menu_file")]
        ])
        await query.edit_message_text("📏 Chọn cách lọc dung lượng:", reply_markup=keyboard)

    elif query.data == "loc_khoang":
        get_waiting_luong_set().add(query.from_user.id)
        await query.message.reply_text(
            "🔢 Nhập khoảng dung lượng cần lọc, ví dụ:\n<code>100KB 500MB</code>",
            parse_mode="HTML"
        )

    elif query.data == "loc_toan_tu":
        get_waiting_luong_set().add(query.from_user.id)
        await query.message.reply_text(
            "🔼 Nhập điều kiện lọc, ví dụ:\n<code>&gt;100MB</code> hoặc <code>&lt;1GB</code>",
            parse_mode="HTML"
        )

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
        set_waiting_tag_action(query.from_user.id, "add")
        await query.message.reply_text("➕ Gửi nội dung: <code>ID TAG</code> (ví dụ: <b>123 học_tập</b>)", parse_mode="HTML")

    elif query.data == "cmd_tag":
        set_waiting_tag_action(query.from_user.id, "filter")
        await query.message.reply_text("🔍 Gửi tên tag để lọc, ví dụ: <b>học_tập</b>", parse_mode="HTML")

    elif query.data == "cmd_removetag":
        set_waiting_tag_action(query.from_user.id, "remove")
        await query.message.reply_text("❌ Gửi nội dung: <code>ID TAG</code> để gỡ", parse_mode="HTML")

    elif query.data == "cmd_cleartags":
        set_waiting_tag_action(query.from_user.id, "clear")
        await query.message.reply_text("🧹 Gửi ID file cần xoá toàn bộ tag", parse_mode="HTML")

    elif query.data == "cmd_renametag":
        set_waiting_tag_action(query.from_user.id, "rename")
        await query.message.reply_text("✏️ Gửi: <code>tag_cũ tag_mới</code> để đổi tên", parse_mode="HTML")

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


# === Bắt tin nhắn để xử lý ZW (dùng context.user_data) ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    logger.info("handle_message triggered for user=%s text=%r awaiting=%s",
                user_id, text, context.user_data.get("awaiting_zw"))

    if context.user_data.get("awaiting_zw"):
        zw_text = "\u200b".join(list(text))
        await update.message.reply_text(f"✅ Kết quả:\n{zw_text}")
        logger.info("ZW result for user=%s: %r", user_id, zw_text)
        context.user_data.pop("awaiting_zw", None)
        return

    return


# === Các lệnh cơ bản: /start, /ping, /menu ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xin chào! Tôi là bot hỗ trợ quản lý file.\n"
        "Bạn có thể:\n"
        "• Gửi file tài liệu hoặc ảnh\n"
        "• Dùng lệnh /menu để truy cập các chức năng quản lý."
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot đang hoạt động bình thường.")

async def fallback_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update, context)
