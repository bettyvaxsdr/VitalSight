from flask import Flask, request, jsonify, render_template
from backend import db, socketio
from backend.database import init_db
from backend.models import HealthData
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)
socketio.init_app(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    pulse = data.get('pulse')
    temperature = data.get('temperature')
    state = data.get('state')
    timestamp = datetime.now()

    entry = HealthData(
        heart_rate=pulse,
        temperature=temperature,
        state=state,
        timestamp=timestamp
    )

    db.session.add(entry)
    db.session.commit()

    socketio.emit('new_data',
                  {
                    'heart_rate': pulse,
                    'temperature': temperature,
                    'state': state,
                    'timestamp': str(datetime.utcnow())
                  })

    return {"status": "success"}

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)