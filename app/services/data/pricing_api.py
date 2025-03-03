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
        
        Returns:
            float: The vehicle price if found
            float: Estimated price if API fails
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
            
            response = requests.get(url, params=params, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if 'stats' in data and 'price' in data['stats']:
                    avg_price = data['stats']['price']['mean']
                    # Cache this result
                    PricingService._cache_price(cache_key, avg_price)
                    return avg_price
            
            # If we couldn't get a price, estimate it
            estimated_price = PricingService._estimate_price(make, model, year)
            return estimated_price
            
        except Exception as e:
            print(f"Error fetching price data: {str(e)}")
            # Fallback to estimation
            return PricingService._estimate_price(make, model, year)
    
    @staticmethod
    def _estimate_price(make, model, year):
        """Estimate vehicle price based on make, model and year"""
        current_year = datetime.now().year
        age = current_year - int(year)
        
        # Base prices by make (very simplified)
        base_prices = {
            'TOYOTA': 30000,
            'HONDA': 28000,
            'FORD': 32000,
            'CHEVROLET': 33000,
            'BMW': 50000,
            'MERCEDES-BENZ': 55000,
            'AUDI': 48000,
            'LEXUS': 45000,
            'TESLA': 60000,
            'VOLKSWAGEN': 28000,
            'SUBARU': 27000,
            'NISSAN': 26000,
            'KIA': 24000,
            'HYUNDAI': 25000,
            'MAZDA': 26000,
            'JEEP': 35000,
            'DODGE': 32000,
            'RAM': 40000,
            'GMC': 38000,
            'CADILLAC': 50000,
            'LINCOLN': 48000,
            'ACURA': 40000,
            'INFINITI': 42000,
            'VOLVO': 45000,
            'PORSCHE': 80000,
            'JAGUAR': 60000,
            'LAND ROVER': 70000,
            'MINI': 30000,
            'MITSUBISHI': 25000,
            'BUICK': 32000,
            'CHRYSLER': 30000,
            'ALFA ROMEO': 45000,
            'GENESIS': 45000,
            'FIAT': 25000,
            'MASERATI': 90000,
            'BENTLEY': 200000,
            'FERRARI': 250000,
            'LAMBORGHINI': 300000,
            'ROLLS-ROYCE': 350000,
            'ASTON MARTIN': 200000,
            'MCLAREN': 250000,
            'BUGATTI': 2000000,
            'LOTUS': 100000,
        }
        
        # Get base price for make or use average
        base_price = base_prices.get(make.upper(), 35000)
        
        # Apply age depreciation (simplified)
        if age <= 1:
            depreciation = 0.1  # 10% first year
        elif age <= 3:
            depreciation = 0.1 + (age - 1) * 0.08  # 8% per year after first
        elif age <= 6:
            depreciation = 0.26 + (age - 3) * 0.06  # 6% per year after third
        elif age <= 10:
            depreciation = 0.44 + (age - 6) * 0.04  # 4% per year after sixth
        else:
            depreciation = 0.6 + (age - 10) * 0.02  # 2% per year after tenth
            
        # Cap depreciation at 90%
        depreciation = min(depreciation, 0.9)
        
        # Apply model adjustments (simplified)
        model_lower = model.lower()
        model_factor = 1.0
        
        # Luxury/premium models
        if any(word in model_lower for word in ['premium', 'luxury', 'sport', 'limited', 'platinum', 'elite']):
            model_factor = 1.2
        
        # Economy models
        if any(word in model_lower for word in ['base', 'standard', 'economy', 'basic']):
            model_factor = 0.9
            
        # Calculate final price
        estimated_price = base_price * model_factor * (1 - depreciation)
        
        return round(estimated_price, 2)
    
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
