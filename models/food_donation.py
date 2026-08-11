from models import db
from datetime import datetime

class FoodDonation(db.Model):
    # The table name in the database
    __tablename__ = 'food_donation'

    # Primary key for the food donation table, unique identifier
    id = db.Column(db.Integer, primary_key=True)
    
    # Name of the food item being donated, required
    food_name = db.Column(db.String(150), nullable=False)
    
    # Quantity of the food (e.g., number of portions or meals), required
    quantity = db.Column(db.Integer, nullable=False)
    
    # Expiration or best-before time of the food, required
    expiry_time = db.Column(db.DateTime, nullable=False)
    
    # Additional details about the food, optional
    description = db.Column(db.Text, nullable=True)
    
    # Status of the donation (e.g., 'available', 'claimed', 'picked_up'), default is 'available'
    status = db.Column(db.String(50), nullable=False, default='available')
    
    # Foreign key linking the donation to the restaurant (user) that posted it
    restaurant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Optional field for the NGO that claimed the donation
    ngo_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationship to easily access the restaurant user from a donation, and vice versa
    restaurant = db.relationship('User', foreign_keys=[restaurant_id], backref=db.backref('donations', lazy=True))
    
    # Relationship to easily access the NGO user that claimed the donation
    claimed_by = db.relationship('User', foreign_keys=[ngo_id], backref=db.backref('claimed_donations', lazy=True))

    def __repr__(self):
        # A helpful representation of the FoodDonation object for debugging
        return f'<FoodDonation {self.food_name} ({self.status})>'
