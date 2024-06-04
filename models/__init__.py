from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads


# Configure file uploads
photos = UploadSet('photos', IMAGES)

def configure_extensions(app):
    # Initialize SQLAlchemy with app context
    db.init_app(app)

    # Configure file uploads with app context
    configure_uploads(app, photos)

# Create SQLAlchemy object
db = SQLAlchemy()

# Import models so they can be accessed as part of the package
from .user import User
from .portfolio import Portfolio
from .job import Job
from .message import Message
from .rating import Rating
