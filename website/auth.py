from flask import Blueprint, jsonify, request
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db
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


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Please fill in all fields.'}), 400

    user = User.query.filter_by(email=username).first()
    if not user:
        return jsonify({'message': 'User does not exist.'}), 401

    if not check_password_hash(user.password, password):
        return jsonify({'message': 'Incorrect password.'}), 401

    login_user(user, remember=True)
    token = make_token(user.id)
    return jsonify({'token': token, 'message': 'Logged in successfully.'}), 200


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

    existing = User.query.filter_by(email=username).first()
    if existing:
        return jsonify({'message': 'Username already exists.'}), 409

    new_user = User(
        email=username,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        device_id=device_id
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Account created successfully.'}), 201