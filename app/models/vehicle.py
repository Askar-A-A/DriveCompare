from app.database import db
from datetime import datetime

class Vehicle(db.Model):
    __tablename__ = 'vehicles'  # Explicitly name the table
    
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    fuel_type = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Vehicle {self.year} {self.make} {self.model}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'type': self.type,
            'fuel_type': self.fuel_type
        }