import aiohttp
import asyncio
import json
from aiohttp import ClientConnectorError
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler
)

API_URL = "https://danger-search-nickname.vercel.app/name/{region}?nickname={nickname}&key=DANGER"

async def search_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Lấy tham số từ command
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Usage: /searchplayer <region> <nickname>")
        return
    
    region = context.args[0].lower()
    nickname = " ".join(context.args[1:])

    url = API_URL.format(region=region, nickname=nickname)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    await update.message.reply_text(f"❌ API trả về HTTP {resp.status}")
                    return

                data = await resp.json()

        results = data.get("results", [])
        if not results:
            await update.message.reply_text("🔍 Không tìm thấy người chơi nào.")
            return

        # Format kết quả (chỉ lấy top 5 cho gọn)
        reply_text = f"🕵️ Search results for *{nickname}* in region `{region.upper()}`:\n\n"
        for i, player in enumerate(results[:5], start=1):
            reply_text += (
                f"#{i}\n"
                f"👤 Nickname: `{player.get('nickname')}`\n"
                f"🆔 Account ID: `{player.get('accountId')}`\n"
                f"⭐ Level: {player.get('level')}\n"
                f"⏰ Last Login: {player.get('lastLogin')}\n"
                f"🌍 Region: {player.get('region')}\n\n"
            )

        await update.message.reply_text(reply_text, parse_mode="Markdown")

    except ClientConnectorError:
        await update.message.reply_text("❌ Không kết nối được API.")
    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
    except Exception as e:
        await update.message.reply_text(f"❌ Có lỗi xảy ra: {e}")


# Handler để add vào bot.py
search_player_handler = CommandHandler("searchplayer", search_player)
