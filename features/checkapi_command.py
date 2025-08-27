# features/checkapi_command.py
import aiohttp
from aiohttp import ClientConnectorError
from telegram import Update
from telegram.ext import ContextTypes
import asyncio

API_URL = "http://103.149.253.241:2010/like"
KEY = "conbo"

async def checkapi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        params = {"key": KEY, "uid": "447582027", "region": "sg"}  # test với UID mẫu

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(API_URL, params=params, ssl=False, timeout=5) as resp:
                    if resp.status == 200:
                        await update.message.reply_text("✅ API online và phản hồi OK!")
                    else:
                        await update.message.reply_text(f"⚠️ API phản hồi nhưng status {resp.status}")
            except ClientConnectorError:
                await update.message.reply_text("❌ Không kết nối được API (server offline hoặc chặn IP).")
            except asyncio.TimeoutError:
                await update.message.reply_text("⏰ API phản hồi quá lâu, có thể đang lag.")

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi check API: {str(e)}")
