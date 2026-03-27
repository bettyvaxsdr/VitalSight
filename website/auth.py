from flask import Blueprint, jsonify, request, render_template
from website.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Please fill in all fields.'}), 400

    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': 'No such user exists.'}), 404

    if not check_password_hash(user.password, password):
        return jsonify({'message': 'Incorrect password.'}), 401

    login_user(user, remember=True)
    return jsonify({'message': 'Logged in successfully.'}), 200

@auth.route('/signup', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    device_id = data.get('device_id', '').strip()

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists.'}), 409

    new_user = User(
        username=username,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        device_id=device_id
    )
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)
    return jsonify({'message': 'Account created successfully.'}), 201

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out.'}), 200