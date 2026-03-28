from flask import jsonify, render_template, request
from flask_login import login_required, current_user
from website import create_app, db
from website.models import HealthData
import requests
import cv2
import numpy as np
import threading
import time

app = create_app()
ESP32_IP = "192.168.8.75"
CAMERA_IP = "192.168.8.77"

# --- Motion Detection ---
motion_state = {
    "moving": True,
    "no_motion_seconds": 0
}

def motion_detection_loop():
    cap = cv2.VideoCapture(f"http://{CAMERA_IP}/stream")
    prev_frame = None
    no_motion_start = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Камерата не се чете, опитвам пак...")
            time.sleep(2)
            cap = cv2.VideoCapture(f"http://{CAMERA_IP}/stream")
            continue

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
            elapsed = time.time() - no_motion_start
            motion_state["moving"] = False
            motion_state["no_motion_seconds"] = int(elapsed)
            int(elapsed)
        else:
            no_motion_start = None
            motion_state["moving"] = True
            motion_state["no_motion_seconds"] = 0

        prev_frame = gray

# Стартира motion detection в отделна нишка
t = threading.Thread(target=motion_detection_loop, daemon=True)
t.start()

# --- Routes ---
@app.route('/')
@login_required
def index():
    return render_template('home.html', user=current_user)

@app.route('/sensor-data', methods=['POST'])
def sensor_data():
    res = request.get_json()
    print("Received data:", res)
    try:
        db.session.add(HealthData(
        pulse=res.get("bpm"),
        temperature=res.get("value"),
        movement=res.get("movement", False),
        state=res.get("state", ""),
        device_id=res.get("sensor")
        ))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"status": "data received"}), 200

@app.route('/latest-data', methods=['GET'])
@login_required
def latest_data():
    try:
        res  = requests.get(f"http://{ESP32_IP}/data", timeout=2)
        data = res.json()

        pulse       = data.get("pulse")
        temperature = data.get("temperature")
        movement    = data.get("movement")
        state       = data.get("state")

        alarm = False
        if pulse       is not None and (pulse < 40 or pulse > 120):
            alarm = True
        if temperature is not None and (temperature < 35 or temperature > 38):
            alarm = True
        if movement:
            alarm = True

        return jsonify({
            "pulse":       pulse,
            "temperature": temperature,
            "movement":    movement,
            "state":       state,
            "alarm":       alarm
        })

    except Exception as e:
        return jsonify({
            "error":   "ESP32 not reachable",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)