#!/usr/bin/env python3
"""
Initializes app
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .models.user import User
from .models.job import Job
from .models.rating import Rating
from .models.message import Message


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()


# Application factory
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import parts of our application
        from . import routes
        from .models import User, Job, Portfolio

        # Create tables for our models
        db.create_all()

    return app
