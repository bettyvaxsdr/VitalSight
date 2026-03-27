from flask import jsonify, render_template
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

@app.route('/api/status')
@login_required
def get_status():
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

@app.route('/history/<int:id>', methods=['GET'])
def history(id):
    data = HealthData.query.filter_by(id=id).first()
    if not data:
        return jsonify({"message": "No data found."}), 404
    return jsonify({
        "id":          data.id,
        "timestamp":   data.timestamp.isoformat(),
        "pulse":       data.pulse,
        "temperature": data.temperature,
        "movement":    data.movement,
        "state":       data.state,
        "device_id":   data.device_id
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)