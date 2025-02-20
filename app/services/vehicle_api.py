import requests
from typing import Dict, List, Optional

class NHTSAService:
    BASE_URL = "https://vpic.nhtsa.dot.gov/api"
    
    @staticmethod
    def get_makes() -> List[Dict]:
        """Get all makes without year filtering"""
        endpoint = f"vehicles/GetAllMakes?format=json"
        response = NHTSAService._make_request(endpoint)
        results = response.get('Results', []) if response else []
        return results
    
    @staticmethod
    def get_years_for_make(make: str) -> List[int]:
        """Get available years for a specific make"""
        endpoint = f"vehicles/GetModelsForMakeYear/make/{make}?format=json"
        response = NHTSAService._make_request(endpoint)
        if response:
            models = response.get('Results', [])
            # Get unique years and filter out invalid years (0 or None)
            years = {
                int(model.get('Model_Year', 0)) 
                for model in models 
                if model.get('Model_Year') and int(model.get('Model_Year', 0)) > 1900
            }
            return sorted(list(years), reverse=True)  # Most recent years first
        return []
    
    @staticmethod
    def get_models(make: str, year: int) -> List[Dict]:
        """Get all models for a specific make and year"""
        endpoint = f"vehicles/GetModelsForMakeYear/make/{make}/modelyear/{year}?format=json"
        response = NHTSAService._make_request(endpoint)
        return response.get('Results', []) if response else []
    
    @staticmethod
    def get_vehicle_info(vin: str) -> Optional[Dict]:
        """Get vehicle details by VIN"""
        endpoint = f"vehicles/DecodeVinValues/{vin}?format=json"
        response = NHTSAService._make_request(endpoint)
        return response.get('Results', [{}])[0] if response else None
    
    @staticmethod
    def get_vehicle_types() -> List[Dict]:
        """Get all vehicle types (car, truck, etc.)"""
        endpoint = "vehicles/GetVehicleTypesForMake/honda?format=json"
        response = NHTSAService._make_request(endpoint)
        return response.get('Results', []) if response else []
    
    @staticmethod
    def get_fuel_types(make: str, model: str, year: int) -> List[str]:
        """Get available fuel types for a specific vehicle"""
        endpoint = f"vehicles/GetModelsForMakeYear/make/{make}/modelYear/{year}?format=json"
        response = NHTSAService._make_request(endpoint)
        return [r.get('FuelTypePrimary') for r in response.get('Results', [])] if response else []
    
    @staticmethod
    def get_ev_details(make: str, model: str, year: int) -> Optional[Dict]:
        """Get EV-specific details if available"""
        endpoint = f"vehicles/GetModelsForMakeYear/make/{make}/modelYear/{year}?format=json"
        response = NHTSAService._make_request(endpoint)
        if response and response.get('Results'):
            for result in response['Results']:
                if result.get('ElectrificationLevel') in ['BEV', 'PHEV']:
                    return result
        return None

    @staticmethod
    def _make_request(endpoint: str) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            url = f"{NHTSAService.BASE_URL}/{endpoint}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return None
                
        except requests.RequestException as e:
            return None