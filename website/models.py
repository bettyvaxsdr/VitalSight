from website import db
from datetime import datetime
from flask_login import UserMixin

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pulse = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    movement    = db.Column(db.Boolean, default=False)
    state = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    device_id = db.Column(db.String(50),  nullable=True)

