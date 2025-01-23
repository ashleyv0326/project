from flask_login import UserMixin
from . import db

# user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True, nullable = False)
    password = db.Column(db.String(150), nullable = False)
    first_name = db.Column(db.String(150), nullable = False)
    last_name = db.Column(db.String(150), nullable = False)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    role = db.Column(db.String(50), nullable = False)
    work_hours = db.relationship('Workhours', backref='employee', lazy=True)
# project
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    work_hours = db.relationship('Workhours', backref='project', lazy=True)

# work hours
class Workhours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    hours = db.Column(db.Float, nullable=False) 