from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    user_name = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    instances = db.relationship('Instance')

class Instance(db.Model): 
    aws_instance_id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))