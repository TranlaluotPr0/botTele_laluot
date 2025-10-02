# 2fa_command.py

from aiogram import types
from aiogram.dispatcher import Dispatcher
import pyotp

user_keys = {}

async def cmd_2fa(message: types.Message):
    markup = types.ForceReply()
    await message.reply("Nhập key 2FA:", reply_markup=markup)

async def receive_key(message: types.Message):
    key = message.text.strip()
    user_keys[message.from_user.id] = key
    totp = pyotp.TOTP(key)
    otp = totp.now()
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Làm mới OTP", callback_data="refresh_otp")
    )
    await message.reply(f"Mã OTP hiện tại: `{otp}`", reply_markup=markup, parse_mode="Markdown")

async def refresh_otp(callback_query: types.CallbackQuery):
    key = user_keys.get(callback_query.from_user.id)
    totp = pyotp.TOTP(key)
    otp = totp.now()
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Làm mới OTP", callback_data="refresh_otp")
    )
    await callback_query.message.edit_text(f"Mã OTP hiện tại: `{otp}`", reply_markup=markup, parse_mode="Markdown")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_2fa, commands=['2fa'])
    dp.register_message_handler(receive_key, lambda message: message.reply_to_message and 'Nhập key 2FA' in message.reply_to_message.text)
    dp.register_callback_query_handler(refresh_otp, lambda c: c.data == "refresh_otp")
