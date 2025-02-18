import requests
from typing import Dict, List, Optional

class NHTSAService:
    BASE_URL = "https://vpic.nhtsa.dot.gov/api"
    
    @staticmethod
    def _make_request(endpoint: str) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            url = f"{NHTSAService.BASE_URL}/{endpoint}"
            response = requests.get(url)
            
            print(f"Requesting URL: {url}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: Status Code {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    @staticmethod
    def get_makes() -> List[Dict]:
        """Get all vehicle makes"""
        endpoint = "vehicles/GetMakes?format=json"
        response = NHTSAService._make_request(endpoint)
        return response.get('Results', []) if response else []
    
    @staticmethod
    def get_models(make: str) -> List[Dict]:
        """Get all models for a specific make"""
        endpoint = f"vehicles/GetModelsForMake/{make}?format=json"
        response = NHTSAService._make_request(endpoint)
        return response.get('Results', []) if response else []

    @staticmethod
    def test_connection() -> bool:
        """Test API connection"""
        response = NHTSAService._make_request("vehicles/GetMakes?format=json")
        return response is not None

    @staticmethod
    def get_vehicle_info(vin: str) -> Optional[Dict]:
        """Get detailed vehicle information by VIN"""
        url = f"{NHTSAService.BASE_URL}/DecodeVin/{vin}?format=json"
        response = requests.get(url)
        data = response.json()
        return data.get('Results', [{}])[0] if data.get('Results') else None
