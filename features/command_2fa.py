# command_2fa.py
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

import pyotp

# logging để debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_keys = {}

async def cmd_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Nhập key 2FA của bạn:",
        reply_markup=None
    )
    return

async def receive_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.message.text.strip()
    user_id = update.effective_user.id
    user_keys[user_id] = key
    totp = pyotp.TOTP(key)
    otp = totp.now()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Làm mới OTP", callback_data="refresh_otp")]
    ])
    await update.message.reply_text(
        f"Mã OTP hiện tại: `{otp}`",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def refresh_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    key = user_keys.get(user_id)
    if not key:
        await query.edit_message_text("❗ Chưa có key 2FA. Vui lòng nhập lại lệnh /2fa")
        return

    totp = pyotp.TOTP(key)
    otp = totp.now()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Làm mới OTP", callback_data="refresh_otp")]
    ])

    await query.edit_message_text(
        f"Mã OTP hiện tại: `{otp}`",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

def register_handlers(application):
    from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler

    application.add_handler(CommandHandler("2fa", cmd_2fa))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Filters.reply, receive_key))
    application.add_handler(CallbackQueryHandler(refresh_otp, pattern="refresh_otp"))
