import os
import cv2
import asyncio
import threading
from telegram import Bot
from ultralytics import YOLO

# ---------------- CONFIG ----------------
MODEL_PATH = "features/fall_detection/models/yolov8n-pose.pt"

# Thêm nhiều camera nếu cần
CAMERAS = {
    "Cam1": 0,  # webcam
    "Cam2": "rtsp://admin:pass@192.168.1.2:554/stream"
}
# ----------------------------------------

# Kiểm tra model local
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Không tìm thấy model tại: {MODEL_PATH}\n"
                            f"👉 Hãy chắc rằng file .pt nằm đúng vị trí này.")

print("🚀 Đang tải model YOLO từ local...")
model = YOLO(MODEL_PATH)
print("✅ Model YOLO đã sẵn sàng!")

fall_detection_running = False


async def send_fall_alert(bot: Bot, chat_id: int, frame, cam_name: str):
    """Gửi ảnh cảnh báo ngã đến Telegram"""
    try:
        _, buffer = cv2.imencode(".jpg", frame)
        await bot.send_photo(
            chat_id=chat_id,
            photo=buffer.tobytes(),
            caption=f"🚨 Phát hiện NGÃ từ **{cam_name}**"
        )
    except Exception as e:
        print(f"⚠️ Lỗi gửi ảnh Telegram: {e}")


def detect_fall_pose(keypoints):
    """
    Hàm đơn giản kiểm tra ngã dựa trên tư thế.
    Trả về True nếu phát hiện ngã.
    """
    try:
        y = [kp[1] for kp in keypoints if kp[1] > 0]
        if not y:
            return False
        y_range = max(y) - min(y)
        return y_range < 80  # nhỏ → người đang nằm
    except Exception:
        return False


def process_camera(cam_name, cam_url, bot, chat_id):
    """Luồng xử lý từng camera"""
    cap = cv2.VideoCapture(cam_url)
    if not cap.isOpened():
        print(f"❌ Không thể mở camera {cam_name}")
        return

    print(f"✅ Bắt đầu phát hiện ngã: {cam_name}")

    while fall_detection_running:
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️ Không đọc được khung hình từ {cam_name}")
            break

        # Dự đoán tư thế
        results = model(frame, verbose=False)
        for r in results:
            if r.keypoints is not None:
                keypoints = r.keypoints.xy.cpu().numpy()[0]
                if detect_fall_pose(keypoints):
                    print(f"🚨 Phát hiện ngã từ {cam_name}")
                    asyncio.run(send_fall_alert(bot, chat_id, frame, cam_name))

    cap.release()
    cv2.destroyAllWindows()
    print(f"🛑 Dừng camera: {cam_name}")


def start_fall_detection(bot: Bot, chat_id: int):
    """Bắt đầu phát hiện ngã"""
    global fall_detection_running
    if fall_detection_running:
        return "⚠️ Hệ thống phát hiện ngã đang chạy!"
    fall_detection_running = True
    for cam_name, cam_url in CAMERAS.items():
        threading.Thread(
            target=process_camera,
            args=(cam_name, cam_url, bot, chat_id),
            daemon=True
        ).start()
    return "✅ Đã bật phát hiện ngã!"


def stop_fall_detection():
    """Dừng phát hiện ngã"""
    global fall_detection_running
    fall_detection_running = False
    cv2.destroyAllWindows()
    return "🛑 Đã dừng phát hiện ngã!"
