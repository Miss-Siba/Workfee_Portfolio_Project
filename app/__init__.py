from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.models import User, Job, Ratings, Messsages

# Application factory
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import parts of our application
        from . import routes
        from .models import User, Job

        # Create tables for our models
        db.create_all()

    return app
