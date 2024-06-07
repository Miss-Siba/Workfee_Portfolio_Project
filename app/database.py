#!/usr/bin/env python3
"""
Manages the database of the app
"""


from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

db = SQLAlchemy()

