from flask import Blueprint, jsonify, redirect, request, url_for
from website.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import jwt
import datetime
import os

auth = Blueprint('auth', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')

def make_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


# @auth.route('/login', methods=['POST'])
# def login():
#     if request.is_json:
#         data = request.get_json()
#     else:
#         data = request.form
        
#     username = data.get('username')
#     password = data.get('password')

#     if not username or not password:
#         return jsonify({'message': 'Please fill in all fields.'}), 400

#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({'message': 'User does not exist.'}), 401

#     if not check_password_hash(user.password, password):
#         return jsonify({'message': 'Incorrect password.'}), 401

#     login_user(user, remember=True)

#     if request.is_json:
#         token = make_token(user.id)  
#         return jsonify({'token': token, 'message': 'Logged in successfully.'}), 200
#     else:
#         return redirect(url_for('index'))


@auth.route('/login', methods=['POST', 'GET'])
def login():
    # Ако е JSON (AJAX), вземаме данните от request.json
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        # Ако е HTML form, вземаме данните от request.form
        username = request.form.get('username')
        password = request.form.get('password')

    # Проверка за празни полета
    if not username or not password:
        if request.is_json:
            return jsonify({'message': 'Please fill in all fields.'}), 400
        else:
            return 'Please fill in all fields', 400

    # Проверка за съществуващ потребител
    user = User.query.filter_by(username=username).first()
    if not user:
        if request.is_json:
            return jsonify({'message': 'User does not exist.'}), 401
        else:
            return 'User does not exist', 401

    # Проверка на паролата
    if not check_password_hash(user.password, password):
        if request.is_json:
            return jsonify({'message': 'Incorrect password.'}), 401
        else:
            return 'Incorrect password', 401

    # Логваме user с Flask-Login (session cookie)
    login_user(user, remember=True)

    # Ако е JSON (AJAX), връщаме token + message
    if request.is_json:
        # Ако имаш JWT token функция
        token = make_token(user.id)  # твоят JWT токен
        return jsonify({'token': token, 'message': 'Logged in successfully.'}), 200
    else:
        # За класически HTML form redirect към home
        return redirect(url_for('index'))


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully.'}), 200


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    username  = data.get('username', '').strip()
    password  = data.get('password', '')
    device_id = data.get('device_id', '').strip()

    if not username or not password or not device_id:
        return jsonify({'message': 'Please fill in all fields.'}), 400

    if len(username) < 4:
        return jsonify({'message': 'Username must be at least 4 characters.'}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters.'}), 400

    if len(device_id) < 5:
        return jsonify({'message': 'Device ID must be at least 5 characters.'}), 400

    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({'message': 'Username already exists.'}), 409

    new_user = User(
        username=username,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        device_id=device_id
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Account created successfully.'}), 201