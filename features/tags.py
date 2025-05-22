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

# === /addtag <id> <tag>
async def add_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message

    if len(context.args) < 2:
        await message.reply_text("❗ Dùng: /addtag <id> <tag>")
        return

    file_id_str, tag = context.args[0], context.args[1].strip().lower()
    if not file_id_str.isdigit():
        await message.reply_text("❗ ID không hợp lệ.")
        return

    tags_data = load_tags()
    tags = tags_data.get(file_id_str, [])
    if tag in tags:
        await message.reply_text("ℹ️ Tag đã tồn tại với file này.")
        return

    tags.append(tag)
    tags_data[file_id_str] = tags
    save_tags(tags_data)

    await message.reply_text(f"✅ Đã gắn tag '{tag}' cho file ID {file_id_str}.")

# === /removetag <id> <tag>
async def remove_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message

    if len(context.args) < 2:
        await message.reply_text("❗ Dùng: /removetag <id> <tag>")
        return

    file_id_str, tag = context.args[0], context.args[1].strip().lower()
    tags_data = load_tags()

    if file_id_str not in tags_data or tag not in tags_data[file_id_str]:
        await message.reply_text("⚠️ Tag không tồn tại với file này.")
        return

    tags_data[file_id_str].remove(tag)
    if not tags_data[file_id_str]:
        del tags_data[file_id_str]
    save_tags(tags_data)

    await message.reply_text(f"✅ Đã xóa tag '{tag}' khỏi file ID {file_id_str}.")

# === /cleartags <id>
async def clear_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message

    if not context.args or not context.args[0].isdigit():
        await message.reply_text("❗ Dùng: /cleartags <id>")
        return

    file_id_str = context.args[0]
    tags_data = load_tags()

    if file_id_str not in tags_data:
        await message.reply_text("⚠️ File này không có tag.")
        return

    del tags_data[file_id_str]
    save_tags(tags_data)

    await message.reply_text(f"🗑 Đã xóa toàn bộ tag của file ID {file_id_str}.")

# === /renametag <old_tag> <new_tag>
async def rename_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message

    if len(context.args) < 2:
        await message.reply_text("❗ Dùng: /renametag <tag_cũ> <tag_mới>")
        return

    old_tag = context.args[0].strip().lower()
    new_tag = context.args[1].strip().lower()
    tags_data = load_tags()
    count = 0

    for file_id, tags in tags_data.items():
        if old_tag in tags:
            tags.remove(old_tag)
            if new_tag not in tags:
                tags.append(new_tag)
            tags_data[file_id] = tags
            count += 1

    if count == 0:
        await message.reply_text("❌ Không tìm thấy tag cần đổi.")
    else:
        save_tags(tags_data)
        await message.reply_text(f"✅ Đã đổi '{old_tag}' → '{new_tag}' cho {count} file.")

# === /tag <tag>
async def filter_by_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message

    if not context.args:
        await message.reply_text("❗ Dùng: /tag <tag>")
        return

    search_tag = context.args[0].strip().lower()
    tags_data = load_tags()
    matched_ids = [fid for fid, tags in tags_data.items() if search_tag in tags]

    if not matched_ids:
        await message.reply_text(f"❌ Không có file nào với tag '{search_tag}'.")
        return

    received_files = context.bot_data.get("received_files", [])
    username = context.bot.username
    matched = [f for f in received_files if str(f["id"]) in matched_ids]

    if not matched:
        await message.reply_text("⚠️ Có tag nhưng không tìm thấy file tương ứng.")
        return

    text = f"📂 File có tag '{search_tag}':\n\n"
    for f in matched:
        text += (
            f"🆔 <b>ID:</b> <a href='tg://resolve?domain={username}&message_id={f['id']}'>{f['id']}</a>\n"
            f"📄 <b>Tên:</b> {f['name']}\n"
            f"📦 <b>Dung lượng:</b> {f['size']}\n"
            f"⏰ <b>Thời gian:</b> {f['time']}\n───\n"
        )
    await message.reply_html(text, disable_web_page_preview=True)

# ==== MENU TAG ACTIONS SUPPORT ====
_waiting_tag_action = {}

def set_waiting_tag_action(user_id, action):
    _waiting_tag_action[user_id] = action

def get_waiting_tag_action(user_id):
    return _waiting_tag_action.get(user_id)

def clear_waiting_tag_action(user_id):
    _waiting_tag_action.pop(user_id, None)

async def handle_tag_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = update.effective_user.id
    action = get_waiting_tag_action(user_id)
    text = message.text.strip()

    if action == "add":
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await message.reply_text("❗ Dùng: <code>ID TAG</code>", parse_mode="HTML")
        else:
            context.args = parts
            await add_tag(update, context)
    elif action == "remove":
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await message.reply_text("❗ Dùng: <code>ID TAG</code> để gỡ", parse_mode="HTML")
        else:
            context.args = parts
            await remove_tag(update, context)
    elif action == "clear":
        context.args = [text]
        await clear_tags(update, context)
    elif action == "rename":
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await message.reply_text("❗ Dùng: <code>tag_cũ tag_mới</code>", parse_mode="HTML")
        else:
            context.args = parts
            await rename_tag(update, context)

    clear_waiting_tag_action(user_id)
