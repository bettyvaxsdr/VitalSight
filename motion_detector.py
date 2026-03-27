import cv2
import time
import threading

STREAM_URL = "http://192.168.8.XX/stream"  # IP на ESP32-CAM
NO_MOTION_THRESHOLD = 10  # секунди без движение = alert

_movement_detected = False
_last_motion_time  = time.time()
_lock = threading.Lock()

def get_movement_status():
    """Извиква се от app.py"""
    with _lock:
        no_motion_for = time.time() - _last_motion_time
        return no_motion_for > NO_MOTION_THRESHOLD

def run_detector():
    global _last_motion_time

    cap = cv2.VideoCapture(STREAM_URL)
    prev_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Stream изгубен, опит за свързване...")
            time.sleep(2)
            cap = cv2.VideoCapture(STREAM_URL)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if prev_frame is None:
            prev_frame = gray
            continue

        delta    = cv2.absdiff(prev_frame, gray)
        thresh   = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh   = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        motion = any(cv2.contourArea(c) > 500 for c in contours)

        if motion:
            with _lock:
                _last_motion_time = time.time()

        prev_frame = gray

# Стартира в background thread
detector_thread = threading.Thread(target=run_detector, daemon=True)
detector_thread.start()