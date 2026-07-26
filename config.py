import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-default'
    # Add other configuration variables here
