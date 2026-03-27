from flask import jsonify, render_template
from flask_login import login_required, current_user
from website import create_app, db
import requests
import motion_detector

app = create_app()
ESP32_IP = "192.168.8.75"

@app.route('/api/status')
@login_required
def get_status():
    try:
        res  = requests.get(f"http://{ESP32_IP}/data", timeout=2)
        data = res.json()

        pulse       = data.get("bpm")
        temperature = data.get("value")
        movement    = motion_detector.get_movement_status()  # ← от OpenCV

        alarm = False
        if pulse is not None and isinstance(pulse, (int, float)):
            if pulse < 40 or pulse > 120:
                alarm = True
        if temperature is not None and (temperature < 35 or temperature > 38):
            alarm = True
        if movement:
            alarm = True  # липса на движение = alarm

        return jsonify({
            "pulse":       pulse,
            "temperature": temperature,
            "movement":    movement,
            "alarm":       alarm
        })

    except Exception as e:
        return jsonify({"error": "ESP32 not reachable", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)