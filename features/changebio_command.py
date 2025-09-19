# features/changebio_command.py
import aiohttp
import asyncio
from aiohttp import ClientConnectorError
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://black-change-bio.vercel.app/get"

async def changebio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kiểm tra tham số
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Dùng lệnh:\n`/changebio <jwt_token> <new_bio>`\n\n👉 Dùng `\\n` để xuống dòng.",
            parse_mode="Markdown"
        )
        return
    
    jwt_token = context.args[0]
    bio_text = " ".join(context.args[1:]).strip()
    bio_text = bio_text.replace("\\n", "\n")  # Hỗ trợ xuống dòng

    if not bio_text:
        await update.message.reply_text("⚠️ Bio trống, nhập lại cho chuẩn nha.")
        return

    params = {"access": jwt_token, "text": bio_text}

    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(API_URL, params=params, timeout=10) as resp:
                    content_type = resp.headers.get("Content-Type", "")
                    
                    # Nếu trả JSON
                    if "application/json" in content_type.lower():
                        data = await resp.json(content_type=None)
                        status_api = data.get("status") or data.get("Status api", "")
                        msg = data.get("message") or data.get("msg") or ""

                        if status_api.lower() == "error" or resp.status != 200:
                            response_text = (
                                "❌ Thay đổi tiểu sử thất bại!\n"
                                f"Lý do: {msg or 'Không rõ'}"
                            )
                        else:
                            response_text = (
                                "✅ Tiểu sử đã được thay đổi thành công!\n\n"
                                f"📝 Tiểu sử mới:\n{bio_text}\n\n"
                                "Cảm ơn bạn đã dùng bot của TranDatDev"
                            )
                    
                    # Nếu trả về plain text
                    else:
                        raw_text = await resp.text()
                        if resp.status != 200 or "error" in raw_text.lower():
                            response_text = (
                                "❌ Thay đổi tiểu sử thất bại!\n"
                                f"Lý do từ API: {raw_text.strip()}"
                            )
                        else:
                            response_text = (
                                f"{raw_text.strip()}\n\n"
                                "Cảm ơn bạn đã dùng bot của TranDatDev"
                            )

                    await update.message.reply_text(response_text)

            except ClientConnectorError:
                await update.message.reply_text("❌ Không kết nối được API.")
            except asyncio.TimeoutError:
                await update.message.reply_text("⏰ API phản hồi quá lâu.")

    except Exception as e:
        await update.message.reply_text(f"❌ Có lỗi xảy ra: {e}")
