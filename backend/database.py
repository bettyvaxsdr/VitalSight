from backend import db  
from backend.models import HealthData 
  
def init_db(app):  
    db.init_app(app)  
    with app.app_context():  
        db.create_all()