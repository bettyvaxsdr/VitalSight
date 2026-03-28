from flask import jsonify, render_template, request
from flask_login import login_required, current_user
from website import create_app, db
from website.models import HealthData
import requests

app = create_app()

ESP32_IP = "192.168.8.75"

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

        return jsonify({
            "pulse": data.pulse,
            "temperature": data.temperature,
            "movement": data.movement,
            "state": data.state
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)