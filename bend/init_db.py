# backend/init_db.py
from app import app, db # Import your Flask app and db instance

with app.app_context():
    db.create_all()
    print("Database tables created/checked by init_db.py")