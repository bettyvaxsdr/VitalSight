from flask import jsonify, render_template, request, Response
from flask_login import login_required, current_user
from website import create_app, db
from website.models import HealthData
import requests

app = create_app()

ESP32_IP = "192.168.8.75"
ESP32_STREAM_URL = "http://192.168.8.77:81/stream"

@app.route('/critical')
def critical():
    return render_template("critical.html")

def generate():
    with requests.get(ESP32_STREAM_URL, stream=True) as stream:
        for chunk in stream.iter_content(chunk_size=1024):
            if chunk:
                yield chunk

@app.route('/video')
def video():
    return Response(generate(),
                    content_type='multipart/x-mixed-replace; boundary=frame')


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
        data = HealthData.query.order_by(HealthData.id.desc()).first()

        if not data:
            return jsonify({"error": "No data"}), 404

        # 🔥 ЛОГИКА ЗА СТАТУС
        status = "OK"

        if data.temperature and data.temperature > 38:
            status = "HIGH TEMP"

        if data.pulse and (data.pulse > 120 or data.pulse < 50):
            status = "ABNORMAL PULSE"

        if (
            data.temperature and data.temperature > 38 and
            data.pulse and (data.pulse > 120 or data.pulse < 50)
        ):
            status = "CRITICAL"

        return jsonify({
            "pulse": data.pulse,
            "temperature": data.temperature,
            "movement": data.movement,
            "state": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)