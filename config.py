import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-default'
    
    # Configure the SQLite database URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///greenplate.db'
    
    # Disable modification tracking to save resources (best practice)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
