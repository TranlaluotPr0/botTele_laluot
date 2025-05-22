import os
import json
from telegram import Update
from telegram.ext import ContextTypes

TAGS_FILE = "tags.json"

def load_tags():
    if not os.path.exists(TAGS_FILE):
        return {}
    with open(TAGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tags(tags_data):
    with open(TAGS_FILE, "w", encoding="utf-8") as f:
        json.dump(tags_data, f, ensure_ascii=False, indent=2)

# === Bộ nhớ tạm: người dùng đang thao tác gì (gắn tag, lọc tag, xóa tag...)
tag_action_state = {}  # user_id -> {"action": "add"/"filter"/..., "args": [...]}

def get_tag_state(user_id):
    return tag_action_state.get(user_id)

def clear_tag_state(user_id):
    tag_action_state.pop(user_id, None)

def set_tag_state(user_id, action, args=None):
    tag_action_state[user_id] = {"action": action, "args": args or []}

# === Gửi nội dung: "ID TAG"
async def add_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if " " not in text:
        await update.message.reply_text("⚠️ Nhập đúng định dạng: <code>ID TAG</code>", parse_mode="HTML")
        return

    file_id_str, tag = text.split(maxsplit=1)
    if not file_id_str.isdigit():
        await update.message.reply_text("⚠️ ID không hợp lệ.")
        return

    tags_data = load_tags()
    tags = tags_data.get(file_id_str, [])
    tag = tag.lower()
    if tag not in tags:
        tags.append(tag)
        tags_data[file_id_str] = tags
        save_tags(tags_data)
        await update.message.reply_text(f"✅ Đã gắn tag <b>{tag}</b> cho file ID {file_id_str}.", parse_mode="HTML")
    else:
        await update.message.reply_text("ℹ️ Tag đã tồn tại.")

    clear_tag_state(user_id)

# === Gửi tag cần lọc
async def filter_by_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    search_tag = update.message.text.strip().lower()
    tags_data = load_tags()
    matched_ids = [fid for fid, tags in tags_data.items() if search_tag in tags]

    if not matched_ids:
        await update.message.reply_text(f"❌ Không có file nào với tag '{search_tag}'.")
        clear_tag_state(user_id)
        return

    received_files = context.application.bot_data.get("received_files", [])
    matched = [f for f in received_files if str(f["id"]) in matched_ids]

    if not matched:
        await update.message.reply_text("⚠️ Có tag nhưng không tìm thấy file tương ứng.")
    else:
        text = f"📂 File có tag '<b>{search_tag}</b>':\n\n"
        for f in matched:
            text += (
                f"📄 <b>{f['name']}</b>\n"
                f"📦 {round(int(f['size']) / 1024 / 1024, 2)} MB\n"
                f"⏰ {f['time']}\n"
                f"🆔 <code>{f['id']}</code>\n───\n"
            )
        await update.message.reply_html(text)

    clear_tag_state(user_id)

# === Gửi ID TAG để gỡ
async def remove_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if " " not in text:
        await update.message.reply_text("⚠️ Nhập đúng định dạng: <code>ID TAG</code>", parse_mode="HTML")
        return

    file_id_str, tag = text.split(maxsplit=1)
    tag = tag.lower()
    tags_data = load_tags()

    if file_id_str not in tags_data or tag not in tags_data[file_id_str]:
        await update.message.reply_text("⚠️ Không tìm thấy tag.")
        return

    tags_data[file_id_str].remove(tag)
    if not tags_data[file_id_str]:
        del tags_data[file_id_str]
    save_tags(tags_data)
    await update.message.reply_text(f"✅ Đã gỡ tag '{tag}' khỏi file ID {file_id_str}.")
    clear_tag_state(user_id)

# === Xoá toàn bộ tag của 1 file
async def clear_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    file_id = update.message.text.strip()
    tags_data = load_tags()

    if not file_id.isdigit() or file_id not in tags_data:
        await update.message.reply_text("⚠️ Không có tag với file ID đó.")
        return

    del tags_data[file_id]
    save_tags(tags_data)
    await update.message.reply_text(f"🧹 Đã xoá toàn bộ tag của file ID {file_id}.")
    clear_tag_state(user_id)

# === Đổi tên tag
async def rename_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if " " not in text:
        await update.message.reply_text("⚠️ Nhập đúng định dạng: <code>tag_cũ tag_mới</code>", parse_mode="HTML")
        return

    old_tag, new_tag = map(str.lower, text.split(maxsplit=1))
    tags_data = load_tags()
    count = 0

    for file_id in list(tags_data):
        tags = tags_data[file_id]
        if old_tag in tags:
            tags.remove(old_tag)
            if new_tag not in tags:
                tags.append(new_tag)
            count += 1

    if count == 0:
        await update.message.reply_text("❌ Không tìm thấy tag cần đổi.")
    else:
        save_tags(tags_data)
        await update.message.reply_text(f"✏️ Đã đổi tên '{old_tag}' thành '{new_tag}' cho {count} file.")
    clear_tag_state(user_id)
