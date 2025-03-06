from app.database import db
from datetime import datetime
import json

class TCOComparison(db.Model):
    __tablename__ = 'tco_comparisons'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Optional user association
    
    # Vehicle 1 details
    vehicle1_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    vehicle1_make = db.Column(db.String(100), nullable=False)
    vehicle1_model = db.Column(db.String(100), nullable=False)
    vehicle1_year = db.Column(db.Integer, nullable=False)
    vehicle1_fuel_type = db.Column(db.String(50), nullable=False)
    vehicle1_type = db.Column(db.String(50), nullable=False)
    
    # Vehicle 2 details (nullable for single vehicle analysis)
    vehicle2_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    vehicle2_make = db.Column(db.String(100), nullable=True)
    vehicle2_model = db.Column(db.String(100), nullable=True)
    vehicle2_year = db.Column(db.Integer, nullable=True)
    vehicle2_fuel_type = db.Column(db.String(50), nullable=True)
    vehicle2_type = db.Column(db.String(50), nullable=True)
    
    # Analysis parameters
    annual_mileage = db.Column(db.Integer, nullable=False, default=12000)
    ownership_years = db.Column(db.Integer, nullable=False, default=5)
    
    # Results storage (as JSON)
    comparison_data = db.Column(db.Text, nullable=False)  # Stored as JSON
    
    # Charts (stored as base64 encoded images)
    depreciation_chart = db.Column(db.Text, nullable=True)
    retention_chart = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_comparison = db.Column(db.Boolean, default=False)
    
    # Relationships
    vehicle1 = db.relationship('Vehicle', foreign_keys=[vehicle1_id], backref='primary_comparisons')
    vehicle2 = db.relationship('Vehicle', foreign_keys=[vehicle2_id], backref='secondary_comparisons')
    user = db.relationship('User', backref='tco_comparisons')
    
    def get_comparison_data(self):
        """Return the comparison data as a Python dictionary"""
        try:
            if not self.comparison_data:
                return {'vehicle1': {}, 'vehicle2': {}}
            data = json.loads(self.comparison_data)
            # Ensure the expected structure exists
            if 'vehicle1' not in data:
                data['vehicle1'] = {}
            if 'vehicle2' not in data:
                data['vehicle2'] = {}
            return data
        except Exception as e:
            print(f"Error parsing comparison data: {e}")
            return {'vehicle1': {}, 'vehicle2': {}}
    
    def set_comparison_data(self, data):
        """Store the comparison data as JSON"""
        if data:
            self.comparison_data = json.dumps(data)
        else:
            self.comparison_data = json.dumps({'vehicle1': {}, 'vehicle2': {}})
