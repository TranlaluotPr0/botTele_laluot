# features/changebio_command.py
import aiohttp
import asyncio
import json
from aiohttp import ClientConnectorError
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://black-change-bio.vercel.app/get"

async def changebio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ghép các argument lại
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Dùng lệnh:\n`/changebio <jwt_token> <new_bio>`", parse_mode="Markdown")
        return

    jwt_token = context.args[0]
    bio_text = " ".join(context.args[1:]).strip()

    if not bio_text:
        await update.message.reply_text("⚠️ Bio trống, nhập lại cho chuẩn nha.")
        return

    params = {
        "access": jwt_token,
        "text": bio_text
    }

    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(API_URL, params=params, timeout=10) as resp:
                    if resp.status != 200:
                        await update.message.reply_text(f"❌ API trả về HTTP {resp.status}")
                        return

                    content_type = resp.headers.get("Content-Type", "")
                    if "application/json" in content_type.lower():
                        data = await resp.json(content_type=None)
                    else:
                        text = await resp.text()
                        data = {"raw": text}
            except ClientConnectorError:
                await update.message.reply_text("❌ Không kết nối được API.")
                return
            except asyncio.TimeoutError:
                await update.message.reply_text("⏰ API phản hồi quá lâu.")
                return

        # Format kết quả
        if isinstance(data, dict):
            ok = bool(data.get("ok") or data.get("success") or data.get("status") in [1, "ok", True])
            msg = data.get("message") or data.get("msg")

            if ok or msg:
                await update.message.reply_text(
                    f"✅ Bio changed successfully!\n\n📝 New bio: {bio_text}\n"
                    f"{'ℹ️ ' + msg if msg else ''}"
                )
            else:
                data.pop("DEV", None)
                data.pop("channel", None)
                await update.message.reply_text("📦 Response:\n" + json.dumps(data, ensure_ascii=False, indent=2))
        else:
            await update.message.reply_text("📦 Response:\n" + str(data))

    except Exception as e:
        await update.message.reply_text(f"❌ Có lỗi xảy ra: {e}")
