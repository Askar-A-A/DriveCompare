from app.database import db
from datetime import datetime

class Vehicle(db.Model):
    __tablename__ = 'vehicles'  # Explicitly name the table
    
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20))  # EV, ICE, or Hybrid
    
    # New fields for EV/ICE comparison
    purchase_price = db.Column(db.Float)
    fuel_efficiency = db.Column(db.Float)  # MPG for ICE, MPGe for EV
    battery_capacity = db.Column(db.Float)  # kWh for EV
    range = db.Column(db.Float)  # miles
    real_world_range = db.Column(db.Float)  # miles
    
    # NHTSA specific fields
    nhtsa_vehicle_id = db.Column(db.String(50))
    fuel_type = db.Column(db.String(50))
    drive_type = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Vehicle {self.year} {self.make} {self.model}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'type': self.type
        }