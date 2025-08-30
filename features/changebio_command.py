# features/changebio_command.py
import aiohttp
import asyncio
import json
from aiohttp import ClientConnectorError
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://black-change-bio.vercel.app/get"  # HTTPS, không cần ssl=False

async def changebio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # /changebio <JWT> <bio mới...>
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Dùng: /changebio <JWT> <bio_mới>\n"
                "Ví dụ:\n"
                "   /changebio eyJhbGciOi... Hello anh em 🚀"
            )
            return

        jwt_token = context.args[0]
        bio_text = " ".join(context.args[1:]).strip()
        if not bio_text:
            await update.message.reply_text("⚠️ Bio trống rồi bạn ơi.")
            return

        params = {
            "access": jwt_token,
            "text": bio_text
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(API_URL, params=params, timeout=10) as resp:
                    if resp.status != 200:
                        await update.message.reply_text(f"❌ API trả về HTTP {resp.status}")
                        return

                    # ưu tiên parse JSON; nếu không, trả raw text
                    content_type = resp.headers.get("Content-Type", "")
                    if "application/json" in content_type.lower():
                        data = await resp.json(content_type=None)
                    else:
                        text = await resp.text()
                        data = {"raw": text}
            except ClientConnectorError:
                await update.message.reply_text("❌ Không kết nối được API (server offline hoặc chặn IP).")
                return
            except asyncio.TimeoutError:
                await update.message.reply_text("⏰ API phản hồi quá lâu, vui lòng thử lại sau!")
                return

        # Format kết quả (ẩn DEV/channel nếu có; chỉ show thông tin hữu ích)
        if isinstance(data, dict):
            # vài khóa thường gặp: status/success/msg
            ok = bool(data.get("ok") or data.get("success") or data.get("status") in [1, "ok", True])
            msg = data.get("message") or data.get("msg")

            if ok or msg:
                await update.message.reply_text(
                    f"✅ Đổi bio thành công!\n\n"
                    f"📝 Bio mới: {bio_text}\n"
                    f"{'ℹ️ ' + msg if msg else ''}"
                )
            else:
                # fallback: in gọn JSON để bạn xem server trả gì
                # đồng thời bỏ DEV/channel nếu xuất hiện
                data.pop("DEV", None)
                data.pop("channel", None)
                await update.message.reply_text("📦 Response:\n" + json.dumps(data, ensure_ascii=False, indent=2))
        else:
            await update.message.reply_text(f"📦 Response:\n{data}")

    except Exception:
        await update.message.reply_text("❌ Có lỗi xảy ra, vui lòng thử lại sau!")
