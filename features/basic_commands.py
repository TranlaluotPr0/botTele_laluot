from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/menu", "/chuc_nang"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Dùng /menu để xem chức năng.", reply_markup=markup)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot đang hoạt động bình thường.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>Hướng dẫn sử dụng bot:</b>\n\n"
        "🟢 <b>Cơ bản:</b>\n"
        "/start – Bắt đầu bot\n"
        "/ping – Kiểm tra bot\n"
        "/help – Hiển thị hướng dẫn\n"
        "/chuc_nang – Hiện các chức năng nâng cao\n\n"

        "📁 <b>Quản lý file:</b>\n"
        "/list – Danh sách tất cả file đã gửi\n"
        "/filter_size &lt;min&gt; &lt;max&gt; – Lọc theo dung lượng (MB)\n"
        "/export – Xuất file log.csv\n"
        "/import – Nhập file log.csv\n\n"

        "📅 <b>Quản lý theo ngày:</b>\n"
        "/list_ngay dd-mm-yyyy – Lọc file theo ngày\n"
        "/chon_ngay – Chọn ngày bằng nút hoặc nhập tay (VD: 19/5)\n\n"

        "🏷 <b>Gắn tag & lọc:</b>\n"
        "/addtag &lt;id&gt; &lt;tag&gt; – Gắn tag cho file\n"
        "/tag &lt;tag&gt; – Lọc file theo tag\n"
        "/removetag &lt;id&gt; &lt;tag&gt; – Gỡ 1 tag khỏi file\n"
        "/cleartags &lt;id&gt; – Xoá toàn bộ tag của file\n"
        "/renametag &lt;tag_cu&gt; &lt;tag_moi&gt; – Đổi tên tag\n\n"
        
        "📌 <b>Lưu ý:</b>\n"
        "– ID là số hiển thị khi gửi file hoặc xem trong /list\n"
        "– Bạn có thể nhập ngày dưới dạng: 19/5, 19-05-2025,...\n\n"
        "🧑‍💻 Dùng đỡ đi, mốt Gia Đạt update thêm tính năng sau... hehe!",
        parse_mode="HTML"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 <b>Menu lệnh chính:</b>\n\n"
        "🟢 <b>Cơ bản:</b>\n"
        "/start – Bắt đầu bot\n"
        "/ping – Kiểm tra bot\n"
        "/help – Hướng dẫn sử dụng\n"
        "/chuc_nang – Xem chức năng nâng cao",
        parse_mode="HTML"
    )
