from app.models.depreciation import DepreciationRate
from app.services.data.pricing_api import PricingService
from app.database import db

class DepreciationService:
    @staticmethod
    def calculate_depreciation(vehicle, years=5, annual_mileage=12000):

        # Get initial vehicle price
        initial_price = PricingService.get_vehicle_price(
            vehicle.make, 
            vehicle.model, 
            vehicle.year, 
            vehicle.type  
        )
        
        # Define standard depreciation rates (no longer based on fuel type)
        depreciation_rates = {
            'year_1': 0.15,  # 15% depreciation in first year
            'year_2': 0.13,  # 13% depreciation in second year
            'year_3': 0.11,  # 11% depreciation in third year
            'year_4': 0.09,  # 9% depreciation in fourth year
            'year_5': 0.07,  # 7% depreciation in fifth year
            'mileage_impact': 0.002  # Impact of mileage on depreciation
        }
        
        # Calculate yearly depreciation
        yearly_values = []
        current_value = initial_price
        
        for year in range(1, min(years + 1, 6)):
            # Get the depreciation percentage for this year
            year_attr = f'year_{year}'
            year_depreciation_rate = depreciation_rates.get(year_attr, 0.05)  # Default to 5% if beyond year 5
            
            # Apply mileage impact
            mileage_factor = 1 + (depreciation_rates['mileage_impact'] * (annual_mileage / 1000 - 12))  # Adjust if not standard mileage
            
            # Calculate new value
            depreciation_amount = current_value * year_depreciation_rate * mileage_factor
            new_value = current_value - depreciation_amount
            
            yearly_values.append({
                'year': year,
                'start_value': round(current_value, 2),
                'depreciation_amount': round(depreciation_amount, 2),
                'end_value': round(new_value, 2),
                'depreciation_rate': round(year_depreciation_rate * 100, 1)
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
    
