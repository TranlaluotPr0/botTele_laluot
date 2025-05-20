from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/menu", "/chuc_nang"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Chào bạn! Dùng /menu để xem chức năng.", reply_markup=markup)

# === /ping ===
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot đang hoạt động bình thường.")

# === /help ===
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 <b>Hướng dẫn sử dụng bot:</b>\n\n"

        "🟢 <b>Cơ bản:</b>\n"
        "/start – Bắt đầu bot\n"
        "/ping – Kiểm tra bot\n"
        "/help – Hiển thị hướng dẫn\n"
        "/chuc_nang – Hiện các chức năng nâng cao\n\n"

        "📁 <b>Quản lý file:</b>\n"
        "/list – Danh sách tất cả file đã gửi\n"
        "/filter_size <min> <max> – Lọc theo dung lượng (MB)\n"
        "/export – Xuất file log.csv\n"
        "/import – Nhập file log.csv\n\n"

        "📅 <b>Quản lý theo ngày:</b>\n"
        "/list_ngay dd-mm-yyyy – Lọc file theo ngày\n"
        "/chon_ngay – Chọn ngày bằng nút hoặc nhập tay (VD: 19/5)\n\n"

        "🏷 <b>Gắn tag & lọc:</b>\n"
        "/addtag <id> <tag> – Gắn tag cho file\n"
        "/tag <tag> – Lọc file theo tag\n"
        "/removetag <id> <tag> – Gỡ 1 tag khỏi file\n"
        "/cleartags <id> – Xoá toàn bộ tag của file\n"
        "/renametag <tag_cu> <tag_moi> – Đổi tên tag\n\n"

        "📌 <b>Lưu ý:</b>\n"
        "– ID là số hiển thị khi gửi file hoặc xem trong /list\n"
        "– Bạn có thể nhập ngày dưới dạng: 19/5, 19-05-2025,...\n\n"
        "🧑‍💻 Bot đang được nâng cấp thêm tính năng mới!",
        parse_mode="HTML"
    )

# === /menu (inline) ===
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Quản lý file", callback_data="menu_file")],
        [InlineKeyboardButton("📅 Quản lý theo ngày", callback_data="menu_date")],
        [InlineKeyboardButton("🏷 Gắn tag & lọc", callback_data="menu_tag")],
        [InlineKeyboardButton("📖 Hướng dẫn sử dụng", callback_data="menu_help")]
    ])
    await update.message.reply_text("📋 <b>Menu lệnh chính:</b>", reply_markup=keyboard, parse_mode="HTML")

# === Xử lý khi người dùng bấm inline nút ===
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_file":
        text = (
            "📁 <b>Quản lý file:</b>\n"
            "/list – Danh sách tất cả file đã gửi\n"
            "/filter_size <min> <max> – Lọc theo dung lượng (MB)\n"
            "/export – Xuất file log.csv\n"
            "/import – Nhập file log.csv"
        )
    elif query.data == "menu_date":
        text = (
            "📅 <b>Quản lý theo ngày:</b>\n"
            "/list_ngay dd-mm-yyyy – Lọc file theo ngày\n"
            "/chon_ngay – Chọn ngày bằng nút hoặc nhập tay (VD: 19/5)"
        )
    elif query.data == "menu_tag":
        text = (
            "🏷 <b>Gắn tag & lọc:</b>\n"
            "/addtag <id> <tag> – Gắn tag cho file\n"
            "/tag <tag> – Lọc file theo tag\n"
            "/removetag <id> <tag> – Gỡ 1 tag khỏi file\n"
            "/cleartags <id> – Xoá toàn bộ tag của file\n"
            "/renametag <tag_cu> <tag_moi> – Đổi tên tag"
        )
    elif query.data == "menu_help":
        text = (
            "📚 <b>Hướng dẫn sử dụng bot:</b>\n"
            "/start – Bắt đầu bot\n"
            "/ping – Kiểm tra bot\n"
            "/help – Hướng dẫn sử dụng\n"
            "/chuc_nang – Hiện chức năng nâng cao\n\n"
            "🧑‍💻 Bot đang được nâng cấp thêm tính năng mới!"
        )
    else:
        text = "❓ Không rõ lựa chọn."

    await query.edit_message_text(text=text, parse_mode="HTML")
