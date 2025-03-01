import requests
import json
from datetime import datetime, timedelta
from app.database import db
import os
from functools import lru_cache
from app.models.price_cache import PriceCache

class PricingService:
    BASE_URL = "https://api.marketcheck.com/v2"
    API_KEY = os.environ.get('MARKETCHECK_API_KEY', 'your_default_api_key')
    CACHE_EXPIRY_DAYS = 7  # Cache prices for 7 days
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_vehicle_price(make, model, year, trim=None):
        """
        Get the current market price for a vehicle
        Uses caching to reduce API calls
        """
        # Check if we have this in our database cache first
        cache_key = f"{make}_{model}_{year}_{trim}"
        cached_price = PricingService._get_cached_price(cache_key)
        
        if cached_price:
            return cached_price
        
        # If not in cache, call the API
        try:
            url = f"{PricingService.BASE_URL}/search"
            params = {
                'api_key': PricingService.API_KEY,
                'make': make,
                'model': model,
                'year': year,
                'trim': trim,
                'stats': 'true',
                'per_page': 1
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'stats' in data and 'price' in data['stats']:
                    avg_price = data['stats']['price']['mean']
                    # Cache this result
                    PricingService._cache_price(cache_key, avg_price)
                    return avg_price
            
            # Fallback to default estimation if API fails
            return PricingService._estimate_price(make, model, year)
            
        except Exception as e:
            print(f"Error fetching price data: {str(e)}")
            return PricingService._estimate_price(make, model, year)
    
    @staticmethod
    def _get_cached_price(cache_key):
        """Check if we have a cached price in our database"""
        try:
            # Find cache entry
            cache_entry = PriceCache.query.filter_by(cache_key=cache_key).first()
            
            # If found and not expired, return the price
            if cache_entry:
                expiry_date = datetime.now() - timedelta(days=PricingService.CACHE_EXPIRY_DAYS)
                if cache_entry.created_at > expiry_date:
                    return cache_entry.price
                else:
                    # Delete expired cache entry
                    db.session.delete(cache_entry)
                    db.session.commit()
            
            return None
        except Exception as e:
            print(f"Error retrieving cached price: {str(e)}")
            return None
    
    @staticmethod
    def _cache_price(cache_key, price):
        """Store price in cache"""
        try:
            # Check if entry already exists
            existing_cache = PriceCache.query.filter_by(cache_key=cache_key).first()
            
            if existing_cache:
                # Update existing entry
                existing_cache.price = price
                existing_cache.created_at = datetime.now()
            else:
                # Create new entry
                cache_entry = PriceCache(
                    cache_key=cache_key,
                    price=price
                )
                db.session.add(cache_entry)
            
            db.session.commit()
        except Exception as e:
            print(f"Error caching price: {str(e)}")
            db.session.rollback()
    
    @staticmethod
    def _estimate_price(make, model, year):
        """Fallback method to estimate price if API fails"""
        current_year = datetime.now().year
        age = current_year - int(year)
        
        # Very basic estimation logic
        base_price = 30000
        
        # Adjust for premium brands
        premium_brands = ['BMW', 'MERCEDES-BENZ', 'AUDI', 'LEXUS', 'TESLA', 'PORSCHE']
        brand_multiplier = 1.5 if make.upper() in premium_brands else 1.0
        
        # Adjust for age
        age_factor = max(0.5, 1 - (age * 0.08))
        
        estimated_price = base_price * brand_multiplier * age_factor
        
        return round(estimated_price, 2)
