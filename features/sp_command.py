import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

# Định nghĩa URL API
API_URL = "http://160.30.21.71:5000/api/spam"

async def sp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kiểm tra tham số đầu vào
    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Sử dụng lệnh: /sp <phone> <count>")
        return
    
    phone = context.args[0]
    try:
        count = int(context.args[1])
        if count <= 0:
            await update.message.reply_text("⚠️ Count phải là số nguyên dương!")
            return
    except ValueError:
        await update.message.reply_text("⚠️ Count phải là số nguyên!")
        return
    
    # Tạo tham số cho API
    params = {
        "phone": phone,
        "count": count
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    await update.message.reply_text(f"❌ API trả về HTTP {resp.status}")
                    return
                try:
                    data = await resp.json()
                except aiohttp.ContentTypeError:
                    await update.message.reply_text("❌ Dữ liệu API không phải JSON hợp lệ.")
                    return
                
                # Định dạng phản hồi từ API (giả sử API trả về các trường như nickname, stats, v.v.)
                response_text = (
                    f"📦 Thông tin:đã gửi lệnh thành công\n"
                    
                )
                await update.message.reply_text(response_text)
    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ API phản hồi quá lâu.")
    except aiohttp.ClientConnectionError:
        await update.message.reply_text("❌ Không thể kết nối đến API.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")
