from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from website import create_app, db
from website.models import HealthData

app = create_app()

ESP32_IP = "192.168.8.75"

@app.route('/')
@login_required                      
def index():
    return render_template('home.html', user=current_user)

@app.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

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

        record = HealthData(
            pulse       = pulse,
            temperature = temperature,
            movement    = movement,
            state       = state,
            device_id   = current_user.device_id
        )
        db.session.add(record)
        db.session.commit()

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
    app.run(debug=True, port=5000)