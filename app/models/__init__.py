#!/usr/bin/python3
"""
initialize the models package
"""
import os
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads
from models.user import User
from models.portfolio import Portfolio
from models.job import Job
from models.message import Message
from models.rating import Rating


# Create SQLAlchemy object
db = SQLAlchemy()
# Configure file uploads
photos = UploadSet('photos', IMAGES)

def configure_extensions(app):
    """Initialize SQLAlchemy with app context"""
    db.init_app(app)
    # Configure file uploads with app context
    configure_uploads(app, photos)
