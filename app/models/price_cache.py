from app.database import db
from datetime import datetime

class PriceCache(db.Model):
    __tablename__ = 'price_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<PriceCache {self.cache_key}>'
