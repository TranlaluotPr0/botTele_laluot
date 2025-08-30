import aiohttp
import asyncio
from aiohttp import ClientConnectorError
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler
)

API_URL = "https://danger-search-nickname.vercel.app/name/{region}?nickname={nickname}&key=DANGER"

async def search_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kiểm tra đủ tham số
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Usage: /searchplayer <region> <nickname>")
        return
    
    region = context.args[0].lower()
    nickname = " ".join(context.args[1:])  # gộp lại nickname có khoảng trắng

    url = API_URL.format(region=region, nickname=nickname)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    await update.message.reply_text(f"❌ API trả về HTTP {resp.status}")
                    return

                # Parse JSON
                data = await resp.json(content_type=None)

        results = data.get("results", [])
        if not isinstance(results, list) or len(results) == 0:
            await update.message.reply_text("🔍 Không tìm thấy người chơi nào.")
            return

        # Format kết quả (chỉ lấy tối đa 5 người)
        reply_text = (
            f"🕵️ Search results for *{nickname}* "
            f"in region `{region.upper()}`:\n\n"
        )
        for i, player in enumerate(results[:5], start=1):
            reply_text += (
                f"#{i}\n"
                f"👤 Nickname: `{player.get('nickname', 'N/A')}`\n"
                f"🆔 Account ID: `{player.get('accountId', 'N/A')}`\n"
                f"⭐ Level: {player.get('level', 'N/A')}\n"
                f"⏰ Last Login: {player.get('lastLogin', 'N/A')}\n"
                f"🌍 Region: {player.get('region', 'N/A')}\n\n"
            )

        await update.message.reply_text(reply_text, parse_mode="Markdown")

    except ClientConnectorError:
        await update.message.reply_text("❌ Không kết nối được API.")
    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
    except Exception as e:
        # In ra lỗi để debug dễ hơn
        await update.message.reply_text(f"❌ Có lỗi xảy ra: {type(e).__name__} - {e}")


# Handler để add vào bot.py
search_player_handler = CommandHandler("searchplayer", search_player)
