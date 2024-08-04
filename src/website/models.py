from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

# Initialize the database
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    user_name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __init__(self, email, user_name, password):
        self.email = email
        self.user_name = user_name
        self.password = password

    def __repr__(self):
        return f'<User {self.user_name}>'
