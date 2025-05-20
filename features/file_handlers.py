# features/file_handlers.py
import os
from datetime import datetime
import pytz
import csv

vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")

def parse_size(bytes_size):
    return f"{bytes_size/1024:.2f} KB" if bytes_size < 1024*1024 else f"{bytes_size/1024/1024:.2f} MB"

def parse_time(dt):
    return dt.astimezone(vn_tz).strftime("%H:%M:%S %d-%m-%Y")

def handle_received_file(message, file_id, name, size):
    msg_id = message.message_id
    time_str = parse_time(message.date)
    size_text = parse_size(size)
    data = {
        "id": msg_id,
        "name": name,
        "size": size_text,
        "time": time_str,
        "file_id": file_id
    }
    return data

def load_from_csv(received_files):
    if not os.path.exists("log.csv"):
        return
    with open("log.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 4:
                file_data = {
                    "id": int(row[0]),
                    "name": row[1],
                    "size": row[2],
                    "time": row[3]
                }
                if len(row) >= 5:
                    file_data["file_id"] = row[4]
                received_files.append(file_data)

def append_to_csv(data):
    with open("log.csv", "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([data["id"], data["name"], data["size"], data["time"], data.get("file_id", "")])
