# Import the SQLAlchemy class from flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy

# Initialize the database instance.
# We do not pass the app here so that we can initialize it later in app.py
# This is a common pattern to avoid circular imports.
db = SQLAlchemy()
