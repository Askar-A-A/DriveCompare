import requests
from typing import Dict, List, Optional

class NHTSAService:
    BASE_URL = "https://vpic.nhtsa.dot.gov/api"
    
    @staticmethod
    def get_makes() -> List[Dict]:
        """Get all makes without year filtering"""
        print("5. Starting get_makes in NHTSAService")
        endpoint = f"vehicles/GetAllMakes?format=json"
        print(f"6. Calling NHTSA API endpoint: {endpoint}")
        response = NHTSAService._make_request(endpoint)
        print("6a. Received NHTSA API response:", response is not None)
        results = response.get('Results', []) if response else []
        print("6b. Extracted results:", len(results), "makes found")
        return results
    
    @staticmethod
    def get_years_for_make(make: str) -> List[int]:
        """Get available years for a specific make"""
        endpoint = f"vehicles/GetModelsForMake/{make}?format=json"
        response = NHTSAService._make_request(endpoint)
        models = response.get('Results', []) if response else []
        years = set(int(model.get('Model_Year', 0)) for model in models if model.get('Model_Year'))
        return sorted(list(years), reverse=True)
    
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
            print(f"6c. Making request to: {url}")
            response = requests.get(url)
            print(f"6d. Response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("6e. Successfully parsed JSON response")
                return data
            else:
                print(f"6f. API Error: Status Code {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"6g. Request failed: {e}")
            return None