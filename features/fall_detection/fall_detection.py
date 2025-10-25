
import cv2
import torch
import asyncio
import threading
from telegram import Bot

# ---------------- CONFIG ----------------
MODEL_PATH = "yolov8n-pose.pt"
DRIVE_FILE_ID = "1TZFbiO_shTa7yPKHkkm6KiQ9j9-YYNfn"
MODEL_URL = f"https://drive.google.com/uc?export=download&id={DRIVE_FILE_ID}"
# Nếu có nhiều camera, bạn thêm ở đây
CAMERAS = {
    "Cam1": "rtsp://admin:admin@192.168.1.2:554/stream1",
    # "Cam2": 0,  # ví dụ webcam
}

# ----------------------------------------
model = torch.hub.load('ultralytics/yolov8', 'custom', path=MODEL_PATH)
fall_detection_running = False

def download_model():
    """Tự động tải model YOLO nếu chưa có."""
    if not os.path.exists(MODEL_PATH):
        print("⬇️ Đang tải model YOLO từ Google Drive...")
        response = requests.get(MODEL_URL, stream=True)
        total = int(response.headers.get("content-length", 0))
        with open(MODEL_PATH, "wb") as f:
            downloaded = 0
            for data in response.iter_content(1024 * 1024):
                f.write(data)
                downloaded += len(data)
                percent = downloaded * 100 / total if total > 0 else 0
                print(f"\r   ➜ {percent:.1f}%...", end="")
        print("\n✅ Đã tải xong model YOLO.")

download_model()
model = torch.hub.load('ultralytics/yolov8', 'custom', path=MODEL_PATH)

async def send_fall_alert(bot: Bot, chat_id: int, frame, cam_name: str):
    """Gửi ảnh cảnh báo ngã đến Telegram"""
    _, buffer = cv2.imencode(".jpg", frame)
    await bot.send_photo(
        chat_id=chat_id,
        photo=buffer.tobytes(),
        caption=f"🚨 Phát hiện NGÃ từ **{cam_name}**"
    )


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
        return y_range < 80  # khoảng cách nhỏ => ngã
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
            break

        results = model(frame)
        for person in results:
            try:
                keypoints = person['keypoints']
                if detect_fall_pose(keypoints):
                    asyncio.run(send_fall_alert(bot, chat_id, frame, cam_name))
            except Exception:
                continue

        # Nếu muốn hiển thị xem trực tiếp
        cv2.imshow(f"{cam_name}", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"🛑 Dừng camera: {cam_name}")


def start_fall_detection(bot: Bot, chat_id: int):
    """Hàm khởi động"""
    global fall_detection_running
    if fall_detection_running:
        return "⚠️ Hệ thống phát hiện ngã đang chạy!"
    fall_detection_running = True
    for cam_name, cam_url in CAMERAS.items():
        threading.Thread(target=process_camera, args=(cam_name, cam_url, bot, chat_id), daemon=True).start()
    return "✅ Đã bật phát hiện ngã!"


def stop_fall_detection():
    """Hàm dừng"""
    global fall_detection_running
    fall_detection_running = False
    cv2.destroyAllWindows()
    return "🛑 Đã dừng phát hiện ngã!"
