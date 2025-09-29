# features/jwt_command.py
import aiohttp
import asyncio
from aiohttp import ClientConnectorError
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://ff-community-api.vercel.app/oauth/guest:token"

async def jwt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kiểm tra tham số
    if not context.args:
        await update.message.reply_text(
            "⚠️ Dùng lệnh:\n`/jwt <data>`\n\n"
            "👉 Ví dụ:\n`/jwt 4193715627:2038FBA3D5FC73D5E72AFE32BA8FAB10B214533AD091DB5A9349B7BA089D569E`",
            parse_mode="Markdown"
        )
        return

    data_param = context.args[0]

    params = {"data": data_param}

    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(API_URL, params=params, timeout=10) as resp:
                    content_type = resp.headers.get("Content-Type", "")

                    # Nếu trả JSON
                    if "application/json" in content_type.lower():
                        data = await resp.json(content_type=None)
                        jwt_token = data.get("token") or data.get("jwt") or ""
                        msg = data.get("message") or data.get("msg") or ""

                        if not jwt_token:
                            response_text = (
                                "❌ Lấy token thất bại!\n"
                                f"Lý do: {msg or 'Không rõ'}"
                            )
                        else:
                            response_text = (
                                "✅ Lấy token thành công!\n\n"
                                f"🔑 JWT Token:\n`{jwt_token}`\n\n"
                                "Cảm ơn bạn đã dùng bot của TranDatDev"
                            )

                    # Nếu trả về plain text
                    else:
                        raw_text = await resp.text()
                        if resp.status != 200 or "error" in raw_text.lower():
                            response_text = (
                                "❌ Lấy token thất bại!\n"
                                f"Lý do từ API: {raw_text.strip()}"
                            )
                        else:
                            response_text = (
                                f"✅ Token nhận được:\n`{raw_text.strip()}`\n\n"
                                "Cảm ơn bạn đã dùng bot của TranDatDev"
                            )

                    await update.message.reply_text(response_text, parse_mode="Markdown")

            except ClientConnectorError:
                await update.message.reply_text("❌ Không kết nối được API.")
            except asyncio.TimeoutError:
                await update.message.reply_text("⏰ API phản hồi quá lâu.")

    except Exception as e:
        await update.message.reply_text(f"❌ Có lỗi xảy ra: {e}")
