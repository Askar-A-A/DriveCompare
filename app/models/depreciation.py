from app.database import db

class DepreciationRate(db.Model):
    __tablename__ = 'depreciation_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(50), nullable=False)  # EV, ICE, Hybrid
    year_1 = db.Column(db.Float, nullable=False)
    year_2 = db.Column(db.Float, nullable=False)
    year_3 = db.Column(db.Float, nullable=False)
    year_4 = db.Column(db.Float, nullable=False)
    year_5 = db.Column(db.Float, nullable=False)
    
    # Mileage impact per 1000 miles (percentage)
    mileage_impact = db.Column(db.Float, default=0.002)
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<DepreciationRate {self.vehicle_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_type': self.vehicle_type,
            'year_1': self.year_1,
            'year_2': self.year_2,
            'year_3': self.year_3,
            'year_4': self.year_4,
            'year_5': self.year_5,
            'mileage_impact': self.mileage_impact
        }
