from models import db
from datetime import datetime

class User(db.Model):
    # The table name is typically derived from the class name by default, but we can be explicit
    __tablename__ = 'user'

    # Primary key for the user table, unique identifier
    id = db.Column(db.Integer, primary_key=True)
    
    # User's full name, required
    full_name = db.Column(db.String(100), nullable=False)
    
    # User's email address, must be unique and is required
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Stores the hashed version of the password for security
    password_hash = db.Column(db.String(256), nullable=False)
    
    # User role (e.g., 'admin', 'user', 'customer')
    role = db.Column(db.String(50), nullable=False, default='user')
    
    # Timestamp when the user was created, automatically set to the current UTC time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        # A helpful representation of the User object for debugging
        return f'<User {self.email}>'
