from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    device_id = db.Column(db.String(50), nullable=True)

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    pulse = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    movement = db.Column(db.Boolean, default=False)
    state = db.Column(db.String(50))
    device_id = db.Column(db.String(50))