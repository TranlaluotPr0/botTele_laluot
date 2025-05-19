import os
import json
from telegram import Update
from telegram.ext import ContextTypes

TAGS_FILE = "tags.json"

# === Load tags từ file JSON ===
def load_tags():
    if not os.path.exists(TAGS_FILE):
        return {}
    with open(TAGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# === Ghi tags vào file JSON ===
def save_tags(tags_data):
    with open(TAGS_FILE, "w", encoding="utf-8") as f:
        json.dump(tags_data, f, ensure_ascii=False, indent=2)

# === /addtag <id> <tag>: gắn tag cho file
async def add_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❗ Dùng: /addtag <id> <ten_tag>")
        return

    file_id_str, tag = context.args[0], context.args[1].strip().lower()

    if not file_id_str.isdigit():
        await update.message.reply_text("❗ ID không hợp lệ.")
        return

    tags_data = load_tags()
    tags = tags_data.get(file_id_str, [])
    if tag in tags:
        await update.message.reply_text("ℹ️ Tag đã tồn tại với file này.")
        return

    tags.append(tag)
    tags_data[file_id_str] = tags
    save_tags(tags_data)

    await update.message.reply_text(f"✅ Đã gắn tag '{tag}' cho file ID {file_id_str}.")

# === /tag <tag>: xem các file có tag tương ứng
async def filter_by_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Dùng: /tag <ten_tag>")
        return

    search_tag = context.args[0].strip().lower()
    tags_data = load_tags()

    matched_ids = [fid for fid, tags in tags_data.items() if search_tag in tags]
    if not matched_ids:
        await update.message.reply_text(f"❌ Không có file nào với tag '{search_tag}'.")
        return

    received_files = context.bot_data.get("received_files", [])
    username = context.bot.username
    matched = [f for f in received_files if str(f["id"]) in matched_ids]

    if not matched:
        await update.message.reply_text("⚠️ Có tag nhưng không tìm thấy file tương ứng.")
        return

    text = f"📂 File có tag '{search_tag}':\n\n"
    for f in matched:
        text += (
            f"🆔 <b>ID:</b> <a href='tg://resolve?domain={username}&message_id={f['id']}'>{f['id']}</a>\n"
            f"📄 <b>Tên:</b> {f['name']}\n"
            f"📦 <b>Dung lượng:</b> {f['size']}\n"
            f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
        )
    await update.message.reply_html(text, disable_web_page_preview=True)
