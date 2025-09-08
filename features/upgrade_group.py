from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def upgrade_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    # Chỉ cho phép chạy trong nhóm
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("⚠️ Lệnh này chỉ dùng trong group hoặc supergroup thôi nha.")
        return

    try:
        # Chạy API promote group → supergroup
        await context.bot.migrate_chat(chat.id)
        await update.message.reply_text("✅ Nhóm đã được nâng cấp thành supergroup thành công!")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi nâng cấp nhóm: {e}")

# Handler để add vào main bot
upgrade_group_handler = CommandHandler("upgradegroup", upgrade_group)
