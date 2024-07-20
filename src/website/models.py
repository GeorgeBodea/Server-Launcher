from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    user_name = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    creation_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))