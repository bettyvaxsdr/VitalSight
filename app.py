from flask import Flask, request, jsonify
from flask_cors import CORS
import database as db
from datetime import datetime
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    pulse = data.get('pulse')
    temperature = data.get('temperature')
    state = data.get('state')
    timestamp = datetime.now()

    db.execute('INSERT INTO health_data (heart_rate, temperature, state, timestamp) VALUES (%s, %s, %s, %s)', (pulse, temperature, state, timestamp))
    db.commit()

    socketio.emit('new data',
                  {
                    'heart_rate': pulse,
                    'temperature': temperature,
                    'state': state,
                    'timestamp': timestamp.strftime('%d-%m-%Y %H:%M:%S')
                  })

    return {"status": "success"}

@socketio.on('connect')
def handle_connect():
    print("Client connected")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)