from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from website import create_app

app = create_app()

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login_page'))
    return render_template('home.html', user=current_user)

@app.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

# ... get_status and history routes stay the same ...

if __name__ == '__main__':
    app.run(debug=True, port=5000)