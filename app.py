from flask import Flask, request, jsonify, render_template
from backend import db
from backend.database import init_db
from backend.models import HealthData
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

ESP32_IP = "http://192.168.8.75"


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/get-sensor-data', methods=['GET'])
def get_data():
    try:
        # We send a GET request to the ESP32's '/data' endpoint
        response = request.get(f"{ESP32_IP}/data", timeout=5)
        
        if response.status_code == 200:
            # The ESP32 returns a JSON or string; we pass it along
            sensor_payload = response.json()
            return jsonify({
                "status": "success",
                "device": "ESP32_Node_01",
                "data": sensor_payload
            }), 200
        else:
            return jsonify({"error": "ESP32 returned an error"}), 502
            
    except request.exceptions.RequestException as e:
        return jsonify({"error": f"Could not connect to ESP32: {str(e)}"}), 504

@app.route('/history/<id>', methods=['GET'])
def history(id):
    data = HealthData.query.filter_by(id=id).first()
    if not data:
        return jsonify({"error": "Data not found"}), 404
    
    return render_template('history.html', data=data)    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    pulse = data.get('pulse')
    temperature = data.get('temperature')
    state = data.get('state')

    entry = HealthData(
        pulse = pulse,
        temperature = temperature,
        state = state,
    )

    db.session.add(entry)
    db.session.commit()

    socketio.emit('new_data',
                  {
                    'pulse': pulse,
                    'temperature': temperature,
                    'state': state
                  })

    return {"status": "success"}

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)