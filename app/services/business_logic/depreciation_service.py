from app.models.depreciation import DepreciationRate
from app.models import Vehicle
from app.services.data.pricing_api import PricingService
from app.services.data.vehicle_api import EPAFuelEconomyService
from app.database import db
import math
from datetime import datetime

class DepreciationService:
    @staticmethod
    def get_or_create_vehicle(make, model, year, fuel_type, vehicle_type=None):
        """
        Get a vehicle from the database or create it if it doesn't exist
        
        Args:
            make: Vehicle make
            model: Vehicle model
            year: Vehicle year
            fuel_type: Vehicle fuel type
            vehicle_type: Vehicle type (optional, will be determined if not provided)
            
        Returns:
            Vehicle object
        """
        # Determine vehicle type if not provided
        if not vehicle_type:
            # Simple logic to determine vehicle type from model name
            model_lower = model.lower()
            if any(term in model_lower for term in ['truck', 'pickup']):
                vehicle_type = 'Truck'
            elif any(term in model_lower for term in ['suv', 'crossover', '4wd', 'awd']):
                vehicle_type = 'SUV'
            elif any(term in model_lower for term in ['van', 'minivan']):
                vehicle_type = 'Van'
            elif any(term in model_lower for term in ['coupe', 'convertible', 'roadster']):
                vehicle_type = 'Sports Car'
            else:
                vehicle_type = 'Sedan'  # Default to sedan
        
        # Check if vehicle exists in database
        vehicle = Vehicle.query.filter_by(
            make=make,
            model=model,
            year=year,
            fuel_type=fuel_type,
            type=vehicle_type
        ).first()
        
        # If vehicle doesn't exist, create it
        if not vehicle:
            vehicle = Vehicle(
                make=make,
                model=model,
                year=year,
                fuel_type=fuel_type,
                type=vehicle_type,
                created_at=datetime.utcnow()
            )
            db.session.add(vehicle)
            db.session.commit()
            print(f"Created new vehicle: {make} {model} {year} {fuel_type} {vehicle_type}")
        
        return vehicle
    
    @staticmethod
    def calculate_depreciation(vehicle, years=5, annual_mileage=12000):
        """
        Calculate depreciation for a vehicle
        
        Args:
            vehicle: Vehicle object or dict with make, model, year, type
            years: Number of years to calculate (default 5)
            annual_mileage: Annual mileage (default 12000)
            
        Returns:
            Dictionary with depreciation data
        """
        # If vehicle is a dict, get or create the vehicle object
        if isinstance(vehicle, dict):
            vehicle = DepreciationService.get_or_create_vehicle(
                vehicle['make'],
                vehicle['model'],
                vehicle['year'],
                vehicle.get('fuel_type', 'Gasoline'),
                vehicle.get('type')
            )
        
        # Get initial vehicle price
        initial_price = PricingService.get_vehicle_price(
            vehicle.make, 
            vehicle.model, 
            vehicle.year, 
            vehicle.type
        )
        
        # Define depreciation rates (k values) for exponential decay model
        base_depreciation_rates = {
            'year_1': 0.19,  # ~17% depreciation in first year
            'year_2': 0.17,  # ~16% depreciation in second year
            'year_3': 0.14,  # ~13% depreciation in third year
            'year_4': 0.12,  # ~11% depreciation in fourth year
            'year_5': 0.10,  # ~9.5% depreciation in fifth year
            'mileage_impact': 0.00015  # Impact of mileage on depreciation rate
        }
        
        # Adjust depreciation rates based on vehicle type and fuel type
        if vehicle.type == 'Electric':
            # Electric vehicles depreciate faster in early years
            base_depreciation_rates['year_1'] = 0.25
            base_depreciation_rates['year_2'] = 0.20
        elif vehicle.type == 'Luxury':
            # Luxury vehicles depreciate faster
            base_depreciation_rates['year_1'] = 0.22
            base_depreciation_rates['year_2'] = 0.19
        
        if vehicle.fuel_type == 'Electric':
            # Electric vehicles depreciate faster in early years
            base_depreciation_rates['year_1'] = 0.25
            base_depreciation_rates['year_2'] = 0.20
        elif vehicle.fuel_type == 'Hybrid':
            # Hybrids depreciate slightly slower
            base_depreciation_rates['year_1'] = 0.17
            base_depreciation_rates['year_2'] = 0.15
        
        # Calculate yearly depreciation using exponential decay
        yearly_values = []
        current_value = initial_price
        
        for year in range(1, years + 1):
            # Get the base depreciation rate for this year
            year_attr = f'year_{year}'
            base_k = base_depreciation_rates.get(year_attr, 0.08)  # Default to 8% if beyond year 5
            
            # Adjust depreciation rate based on mileage, but ensure it never goes negative
            mileage_adjustment = (annual_mileage - 12000) * base_depreciation_rates['mileage_impact']
            adjusted_k = max(0.02, base_k + mileage_adjustment)  # Ensure minimum 2% depreciation
            
            # Calculate new value using exponential decay
            depreciation_factor = math.exp(-adjusted_k)
            new_value = current_value * depreciation_factor
            
            # Ensure car always depreciates (value never increases)
            new_value = min(current_value, new_value)
            
            depreciation_amount = current_value - new_value
            
            # Calculate effective depreciation rate as a percentage
            effective_rate = (1 - (new_value / current_value)) * 100
            
            yearly_values.append({
                'year': year,
                'start_value': round(current_value, 2),
                'depreciation_amount': round(depreciation_amount, 2),
                'end_value': round(new_value, 2),
                'depreciation_rate': round(effective_rate, 1)
            })
            
            current_value = new_value
        
        return {
            'initial_price': round(initial_price, 2),
            'final_value': round(current_value, 2),
            'total_depreciation': round(initial_price - current_value, 2),
            'depreciation_percentage': round(((initial_price - current_value) / initial_price) * 100, 1),
            'yearly_values': yearly_values
        }
    
    @staticmethod
    def compare_depreciation(vehicle1, vehicle2, years=5, annual_mileage=12000):
        """
        Compare depreciation between two vehicles using exponential decay model
        
        Args:
            vehicle1: First vehicle object or dict
            vehicle2: Second vehicle object or dict
            years: Number of years to calculate (default 5)
            annual_mileage: Annual mileage (default 12000)
            
        Returns:
            Dictionary with comparison data
        """
        vehicle1_depreciation = DepreciationService.calculate_depreciation(
            vehicle1, years, annual_mileage
        )
        
        vehicle2_depreciation = DepreciationService.calculate_depreciation(
            vehicle2, years, annual_mileage
        )
        
        difference = {
            'initial_price_diff': round(vehicle1_depreciation['initial_price'] - vehicle2_depreciation['initial_price'], 2),
            'final_value_diff': round(vehicle1_depreciation['final_value'] - vehicle2_depreciation['final_value'], 2),
            'total_depreciation_diff': round(vehicle1_depreciation['total_depreciation'] - vehicle2_depreciation['total_depreciation'], 2),
            'depreciation_percentage_diff': round(vehicle1_depreciation['depreciation_percentage'] - vehicle2_depreciation['depreciation_percentage'], 1)
        }
        
        return {
            'vehicle1': vehicle1_depreciation,
            'vehicle2': vehicle2_depreciation,
            'difference': difference
        }
    
