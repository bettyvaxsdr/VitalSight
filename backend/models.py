from backend import db
from datetime import datetime

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pulse = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    state = db.Column(db.String(50))
    