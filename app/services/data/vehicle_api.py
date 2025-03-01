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
    def get_vehicle_types(make: str) -> List[Dict]:
        """Get all vehicle_types for a specific make"""
        endpoint = f"vehicles/GetVehicleTypesForMake/{make}?format=json"
        response = NHTSAService._make_request(endpoint)
        if response:
            results = response.get('Results', [])
            return results
        return []

    @staticmethod
    def get_models(make: str, year: int, vehicle_type: str) -> List[Dict]:
        """Get all models for a specific make and year"""
        endpoint = f"vehicles/GetModelsForMakeYear/make/{make}/modelyear/{year}/vehicletype/{vehicle_type}?format=json"
        response = NHTSAService._make_request(endpoint)
        return response.get('Results', []) if response else []
    
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