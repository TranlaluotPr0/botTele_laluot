# features/autolike.py
import asyncio
import aiohttp
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+. Nếu không có, cài pytz và thay thế.
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "http://47.84.86.76:1304/likes"
API_KEYS = "gaycow"

TZ = ZoneInfo("Asia/Ho_Chi_Minh")


async def send_like_request(uid: str):
    """Gọi API like và trả về dict kết quả (hoặc raise on error)."""
    params = {"uid": uid, "keys": API_KEYS}
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(API_URL, params=params) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status}: {text[:500]}")
            # parse JSON
            data = await session._response_class.json(resp) if False else None
            # Above is disabled — use resp.json() safely:
            data = await resp.json(content_type=None)
            return data


async def _autolike_job_callback(context: ContextTypes.DEFAULT_TYPE):
    """
    Job callback chạy theo JobQueue.
    context.job.data chứa dictionary:
      {
        "uid": str,
        "remaining": int,
        "chat_id": int,
        "job_name": str
      }
    """
    job_data = context.job.data
    uid = job_data["uid"]
    remaining = job_data["remaining"]
    chat_id = job_data["chat_id"]
    job_name = job_data.get("job_name", "autolike")

    # gọi API (bắt lỗi để job vẫn tiếp tục hoặc huỷ nếu cần)
    try:
        data = await send_like_request(uid)
    except asyncio.TimeoutError:
        await context.bot.send_message(chat_id=chat_id, text=f"⏰ (AutoLike) UID {uid}: timeout khi gọi API.")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ (AutoLike) UID {uid}: Lỗi {type(e).__name__}: {e}")
    else:
        # format thông tin trả về (tùy theo cấu trúc API của bạn)
        try:
            # API trả về { "result": { "ACCOUNT_INFO": {...}, "LIKES_DETAIL": {...}, "API": {...} } }
            result = data.get("result", {}) if isinstance(data, dict) else {}
            acc = result.get("ACCOUNT_INFO", {})
            likes = result.get("LIKES_DETAIL", {})
            api_info = result.get("API", {})

            nick = acc.get("Account Name", "Unknown")
            likes_added = likes.get("Likes Added", 0)
            likes_before = likes.get("Likes Before", "?")
            likes_after = likes.get("Likes After", "?")
            speed = api_info.get("speeds", "?")
            success = api_info.get("success", False)

            if success and likes_added and likes_added > 0:
                text = (
                    f"✅ (AutoLike) UID {uid} — {nick}\n"
                    f"❤️ Likes trước: {likes_before}\n"
                    f"➕ Likes thêm: {likes_added}\n"
                    f"📈 Likes sau: {likes_after}\n"
                    f"⚡ Tốc độ: {speed}\n"
                    f"🔁 Còn lại: {remaining} lần (bao gồm lần này)"
                )
            else:
                text = (
                    f"⚠️ (AutoLike) UID {uid} — {nick}\n"
                    f"Không thêm được like (có thể đã đạt giới hạn). Tốc độ: {speed}\n"
                    f"🔁 Còn lại: {remaining} lần (bao gồm lần này)"
                )
        except Exception:
            text = f"ℹ️ (AutoLike) UID {uid}: phản hồi API: {data}"

        await context.bot.send_message(chat_id=chat_id, text=text)

    # Giảm counter và huỷ job nếu đã xài hết
    job_data["remaining"] = remaining - 1
    if job_data["remaining"] <= 0:
        # huỷ job hiện tại
        current_job = context.job
        current_job.schedule_removal()
        await context.bot.send_message(chat_id=chat_id, text=f"🟢 (AutoLike) Job `{job_name}` đã kết thúc sau đủ số lần yêu cầu.")
    else:
        # cập nhật data job (JobQueue giữ reference đến dict nên thay đổi đủ)
        pass


async def autolike_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /autolike <uid> <HH:MM> <days>
    Ex: /autolike 2141948885 03:00 3
    """
    if len(context.args) < 3:
        await update.message.reply_text("⚠️ Dùng: /autolike <uid> <HH:MM> <days>\nVí dụ: /autolike 2141948885 03:00 3")
        return

    uid = context.args[0].strip()
    hhmm = context.args[1].strip()
    days_str = context.args[2].strip()

    if not uid.isdigit():
        await update.message.reply_text("⚠️ UID phải là số.")
        return

    try:
        hour, minute = map(int, hhmm.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except Exception:
        await update.message.reply_text("⚠️ Thời gian không hợp lệ. Dùng định dạng HH:MM (24h). Ví dụ 03:00")
        return

    try:
        days = int(days_str)
        if days <= 0:
            raise ValueError
    except Exception:
        await update.message.reply_text("⚠️ Số ngày phải là số nguyên dương.")
        return

    chat_id = update.effective_chat.id

    # Tạo tên job duy nhất
    created_at = datetime.now(TZ).strftime("%Y%m%d%H%M%S")
    job_name = f"autolike_{chat_id}_{uid}_{created_at}"

    # Data lưu trong job để dùng trong callback
    job_data = {
        "uid": uid,
        "remaining": days,
        "chat_id": chat_id,
        "job_name": job_name
    }

    # Lấy đối tượng time theo timezone
    sched_time = time(hour=hour, minute=minute, tzinfo=TZ)

    # Đăng ký job với JobQueue (run_daily sẽ tự schedule mỗi ngày tại thời điểm này)
    # context.job_queue.run_daily chấp nhận async callback
    job = context.job_queue.run_daily(
        callback=_autolike_job_callback,
        time=sched_time,
        days=(0,1,2,3,4,5,6),  # mỗi ngày
        context=job_data,
        name=job_name
    )

    await update.message.reply_text(
        f"🟢 AutoLike đã được tạo.\n"
        f"• UID: {uid}\n"
        f"• Giờ (Asia/Ho_Chi_Minh): {hhmm}\n"
        f"• Số ngày: {days}\n"
        f"• Tên job: `{job_name}`\n\n"
        f"Dùng /list_autolike để xem job hoặc /cancel_autolike {job_name} để huỷ."
    )


async def list_autolike_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = context.job_queue.jobs()
    user_chat_id = update.effective_chat.id
    lines = []
    for j in jobs:
        # lọc job tên bắt đầu bằng autolike và chat_id khớp (nếu bạn muốn cho user chỉ xem job mình tạo)
        data = j.data or {}
        if not isinstance(data, dict):
            continue
        if data.get("chat_id") != user_chat_id:
            continue
        name = j.name
        uid = data.get("uid")
        remaining = data.get("remaining")
        # lấy thông tin thời gian tiếp theo
        next_time = j.next_t
        # j.next_t là datetime in UTC (JobQueue internal). Convert to TZ for display if exists.
        try:
            next_local = next_time.astimezone(TZ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            next_local = str(next_time)
        lines.append(f"- {name}\n  UID: {uid} | Còn: {remaining} lần | Lần kế: {next_local}")

    if not lines:
        await update.message.reply_text("ℹ️ Không tìm thấy AutoLike job cho chat này.")
    else:
        text = "📋 Danh sách AutoLike:\n\n" + "\n\n".join(lines)
        await update.message.reply_text(text)


async def cancel_autolike_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /cancel_autolike <job_name>
    """
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Dùng: /cancel_autolike <job_name>\nLấy job_name từ /list_autolike")
        return

    job_name = context.args[0].strip()
    jobs = context.job_queue.get_jobs_named(job_name)
    if not jobs:
        await update.message.reply_text(f"⚠️ Không tìm thấy job tên `{job_name}`.")
        return

    for j in jobs:
        j.schedule_removal()

    await update.message.reply_text(f"🛑 Job `{job_name}` đã được huỷ.")


# Bạn cần đăng ký các handler này vào Application/Dispatcher chính của bot:
# application.add_handler(CommandHandler("autolike", autolike_command))
# application.add_handler(CommandHandler("list_autolike", list_autolike_command))
# application.add_handler(CommandHandler("cancel_autolike", cancel_autolike_command))
#
# Lưu ý: JobQueue được tự động khởi bởi Application khi bạn tạo Application và chạy application.run_polling() / start_polling()
