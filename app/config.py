#!/usr/bin/env python3
"""
Configurations
"""


class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql://root:your_mysql_password@localhost/flask_app_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'Workfee_dev'

