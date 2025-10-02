import logging
import base64
import pyotp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# logging để debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_keys = {}

# Hàm chuẩn hóa key 2FA
def normalize_key(key: str) -> str:
    k = key.strip().replace(" ", "")

    # Nếu user dán link otpauth://
    if k.lower().startswith("otpauth://"):
        try:
            parsed = pyotp.parse_uri(k)
            return parsed.secret
        except Exception:
            raise ValueError("Không parse được otpauth:// link")

    # Thử decode base32
    try:
        base64.b32decode(k.upper())
        return k.upper()
    except Exception:
        # Nếu không phải base32, encode ASCII sang base32
        return base64.b32encode(k.encode()).decode("utf-8")


async def cmd_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 Nhập key 2FA của bạn:")
    return


async def receive_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.message.text.strip()
    user_id = update.effective_user.id

    try:
        clean_key = normalize_key(key)
        user_keys[user_id] = clean_key

        totp = pyotp.TOTP(clean_key)
        otp = totp.now()

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Làm mới OTP", callback_data="refresh_otp")]
        ])

        await update.message.reply_text(
            f"Mã OTP hiện tại: `{otp}`",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"❗ Key 2FA không hợp lệ!\nChi tiết: {e}")


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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_key))
    application.add_handler(CallbackQueryHandler(refresh_otp, pattern="refresh_otp"))
