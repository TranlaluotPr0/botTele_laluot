# features/additem_command.py
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://add-item-profile.vercel.app/"

async def additem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Lệnh: /additem <access_token> <item1> <item2> ... <item15>
    - access_token: token người dùng
    - item1..item15: tối đa 15 itemid
    """
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Dùng lệnh: /additem <access_token> <item1> <item2> ... (tối đa 15 item)"
        )
        return

    access_token = context.args[0]
    items = context.args[1:16]  # chỉ lấy tối đa 15 item
    params = {"access_token": access_token}

    # map itemid1...itemid15
    for i, item in enumerate(items, start=1):
        params[f"itemid{i}"] = item

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=15) as resp:
                if resp.status != 200:
                    await update.message.reply_text(f"❌ API trả về HTTP {resp.status}")
                    return
                data = await resp.text()

        await update.message.reply_text(f"✅ Kết quả API:\n{data}")

    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")
