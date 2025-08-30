# features/changebio_conversation.py
import aiohttp
import asyncio
import json
from aiohttp import ClientConnectorError
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)

API_URL = "https://black-change-bio.vercel.app/get"

# Các bước trong conversation
ASK_JWT, ASK_BIO = range(2)

async def start_changebio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔑 Send your JWT token")
    return ASK_JWT

async def receive_jwt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jwt_token = update.message.text.strip()
    if not jwt_token:
        await update.message.reply_text("⚠️ Token không hợp lệ, nhập lại:")
        return ASK_JWT

    context.user_data["jwt_token"] = jwt_token
    await update.message.reply_text("✏️ Now send your new bio")
    return ASK_BIO

async def receive_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bio_text = update.message.text.strip()
    jwt_token = context.user_data.get("jwt_token")

    if not bio_text:
        await update.message.reply_text("⚠️ Bio trống, nhập lại:")
        return ASK_BIO

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
                        return ConversationHandler.END

                    content_type = resp.headers.get("Content-Type", "")
                    if "application/json" in content_type.lower():
                        data = await resp.json(content_type=None)
                    else:
                        text = await resp.text()
                        data = {"raw": text}
            except ClientConnectorError:
                await update.message.reply_text("❌ Không kết nối được API.")
                return ConversationHandler.END
            except asyncio.TimeoutError:
                await update.message.reply_text("⏰ API phản hồi quá lâu.")
                return ConversationHandler.END

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

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Hủy đổi bio.")
    return ConversationHandler.END
