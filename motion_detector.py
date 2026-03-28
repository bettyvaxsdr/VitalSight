import cv2
import numpy as np
import time

STREAM_URL = "http://192.168.8.77/stream"  # или :81/stream

cap = cv2.VideoCapture(STREAM_URL)

prev_frame = None
no_motion_start = None
NO_MOTION_THRESHOLD = 15  # секунди без движение

while True:
    ret, frame = cap.read()
    if not ret:
        print("Не може да чете stream-а, проверете URL-а")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if prev_frame is None:
        prev_frame = gray
        continue

    diff = cv2.absdiff(prev_frame, gray)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
    motion_score = np.sum(thresh)

    if motion_score < 5000:
        if no_motion_start is None:
            no_motion_start = time.time()
        else:
            elapsed = time.time() - no_motion_start
            print(f"Няма движение: {int(elapsed)} сек.")
            if elapsed >= NO_MOTION_THRESHOLD:
                print("ALERT! Няма движение 15 секунди!")
                # тук после добавяме връзка с гривната
    else:
        no_motion_start = None  # reset п