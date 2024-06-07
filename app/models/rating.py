from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from . import models


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def get_db():
    from app import db
    return db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    ratings_given = db.relationship('Rating', foreign_keys='Rating.rated_by_id', backref='rater', lazy=True)
    ratings_received = db.relationship('Rating', foreign_keys='Rating.rated_user_id', backref='rated_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)
    rated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rated_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

