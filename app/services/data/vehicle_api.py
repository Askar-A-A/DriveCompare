import requests
from typing import Dict, List, Optional, Tuple

class EPAFuelEconomyService:
    """Service for interacting with the EPA FuelEconomy.gov API"""
    BASE_URL = "https://www.fueleconomy.gov/ws/rest"
    
    @staticmethod
    def get_years() -> List[Tuple[int, int]]:
        """Get all available model years"""
        endpoint = "vehicle/menu/year"
        response = EPAFuelEconomyService._make_request(endpoint)
        
        if not response:
            current_year = 2023
            years = [(year, year) for year in range(current_year, current_year-20, -1)]
            return years
        
        years = []
        menu_items = response.get('menuItem', [])
        
        if isinstance(menu_items, list):
            for item in menu_items:
                if isinstance(item, dict):
                    year = item.get('value')
                    if year and year.isdigit():
                        year_int = int(year)
                        years.append((year_int, year_int))
                elif isinstance(item, str) and item.isdigit():
                    year_int = int(item)
                    years.append((year_int, year_int))
        elif isinstance(menu_items, dict):
            year = menu_items.get('value')
            if year and year.isdigit():
                year_int = int(year)
                years.append((year_int, year_int))
        
        years.sort(reverse=True)
        return years
    
    @staticmethod
    def get_makes(year: Optional[int] = None) -> List[Tuple[str, str]]:
        """Get all makes, optionally filtered by year"""
        if year:
            endpoint = f"vehicle/menu/make?year={year}"
        else:
            years = EPAFuelEconomyService.get_years()
            if years:
                year = years[0][0]
                endpoint = f"vehicle/menu/make?year={year}"
            else:
                return []
        
        response = EPAFuelEconomyService._make_request(endpoint)
        
        if not response:
            return []
        
        makes = []
        menu_items = response.get('menuItem', [])
        
        if isinstance(menu_items, list):
            for item in menu_items:
                if isinstance(item, dict):
                    make = item.get('value')
                    if make:
                        makes.append((make, make))
                elif isinstance(item, str):
                    makes.append((item, item))
        elif isinstance(menu_items, dict):
            make = menu_items.get('value')
            if make:
                makes.append((make, make))
        
        makes.sort()
        return makes
    
    @staticmethod
    def get_models(make: str, year: int) -> List[Tuple[str, str]]:
        """Get all models for a specific make and year"""
        endpoint = f"vehicle/menu/model?year={year}&make={make}"
        response = EPAFuelEconomyService._make_request(endpoint)
        
        if not response:
            return []
        
        models = []
        menu_items = response.get('menuItem', [])
        
        if isinstance(menu_items, list):
            for item in menu_items:
                if isinstance(item, dict):
                    model = item.get('value')
                    if model:
                        models.append((model, model))
                elif isinstance(item, str):
                    models.append((item, item))
        elif isinstance(menu_items, dict):
            model = menu_items.get('value')
            if model:
                models.append((model, model))
        
        models.sort()
        return models
    
    @staticmethod
    def get_vehicle_types(make: str) -> List[Dict]:
        """
        EPA doesn't have a direct vehicle type endpoint like NHTSA.
        For compatibility, we'll return a simplified list of common vehicle types.
        """
        vehicle_types = [
            {"Name": "Sedan", "VehicleTypeId": "Sedan"},
            {"Name": "SUV", "VehicleTypeId": "SUV"},
            {"Name": "Truck", "VehicleTypeId": "Truck"},
            {"Name": "Van", "VehicleTypeId": "Van"},
            {"Name": "Wagon", "VehicleTypeId": "Wagon"},
            {"Name": "Coupe", "VehicleTypeId": "Coupe"},
            {"Name": "Convertible", "VehicleTypeId": "Convertible"},
            {"Name": "Hatchback", "VehicleTypeId": "Hatchback"}
        ]
        return vehicle_types
    
    @staticmethod
    def get_fuel_types(make: str, model: str, year: int) -> List[Tuple[str, str]]:
        """Get available fuel types for a specific make/model/year"""
        options_endpoint = f"vehicle/menu/options?year={year}&make={make}&model={model}"
        options_response = EPAFuelEconomyService._make_request(options_endpoint)
        
        if not options_response:
            return EPAFuelEconomyService.default_fuel_types()
        
        vehicle_ids = []
        menu_items = options_response.get('menuItem', [])
        
        if isinstance(menu_items, list):
            for item in menu_items:
                if isinstance(item, dict):
                    vehicle_id = item.get('value')
                    if vehicle_id:
                        vehicle_ids.append(vehicle_id)
                elif isinstance(item, str) and item.isdigit():
                    vehicle_ids.append(item)
        elif isinstance(menu_items, dict):
            vehicle_id = menu_items.get('value')
            if vehicle_id:
                vehicle_ids.append(vehicle_id)
        
        if not vehicle_ids:
            return EPAFuelEconomyService.default_fuel_types()
        
        fuel_types = set()
        
        for vehicle_id in vehicle_ids[:5]:
            vehicle_endpoint = f"vehicle/{vehicle_id}"
            vehicle_response = EPAFuelEconomyService._make_request(vehicle_endpoint)
            
            if vehicle_response:
                fuel_type = vehicle_response.get('fuelType')
                if fuel_type:
                    if fuel_type == 'Regular Gasoline' or fuel_type == 'Regular':
                        display_name = 'Gasoline (Regular 87 octane)'
                    elif fuel_type == 'Premium Gasoline' or fuel_type == 'Premium':
                        display_name = 'Gasoline (Premium 91-93 octane)'
                    elif fuel_type == 'Midgrade Gasoline' or fuel_type == 'Midgrade':
                        display_name = 'Gasoline (Midgrade 89 octane)'
                    elif 'Electricity' in fuel_type:
                        if 'and' in fuel_type:
                            if 'Premium' in fuel_type:
                                display_name = 'Plug-in Hybrid (Premium Gas + Electric)'
                            else:
                                display_name = 'Plug-in Hybrid (Regular Gas + Electric)'
                        else:
                            display_name = 'Electric Vehicle (Battery Only)'
                    elif 'Hybrid' in fuel_type:
                        display_name = 'Hybrid (Gasoline + Electric, Non Plug-in)'
                    elif 'Diesel' in fuel_type:
                        display_name = 'Diesel Fuel'
                    elif 'E85' in fuel_type or 'Flex' in fuel_type:
                        display_name = 'Flex Fuel (E85 Ethanol/Gasoline)'
                    elif 'Natural Gas' in fuel_type or 'CNG' in fuel_type:
                        display_name = 'Compressed Natural Gas (CNG)'
                    else:
                        display_name = f'{fuel_type} (See vehicle manual)'
                    
                    fuel_types.add((fuel_type, display_name))
        
        fuel_types = sorted(list(fuel_types))
        
        if not fuel_types:
            return EPAFuelEconomyService.default_fuel_types()
        
        return fuel_types
    
    @staticmethod
    def get_vehicle_details(vehicle_id: str) -> Optional[Dict]:
        """Get detailed information for a specific vehicle"""
        endpoint = f"vehicle/{vehicle_id}"
        return EPAFuelEconomyService._make_request(endpoint)
    
    @staticmethod
    def default_fuel_types() -> List[Tuple[str, str]]:
        """Return default fuel types with clear descriptions if API fails"""
        return [
            ('Regular Gasoline', 'Gasoline (Regular 87 octane)'),
            ('Premium Gasoline', 'Gasoline (Premium 91-93 octane)'),
            ('Midgrade Gasoline', 'Gasoline (Midgrade 89 octane)'),
            ('Diesel', 'Diesel Fuel'),
            ('Electricity', 'Electric Vehicle (Battery Only)'),
            ('Regular Gasoline and Electricity', 'Plug-in Hybrid (Regular Gas + Electric)'),
            ('Premium Gasoline and Electricity', 'Plug-in Hybrid (Premium Gas + Electric)'),
            ('Hybrid', 'Hybrid (Gasoline + Electric, Non Plug-in)'),
            ('E85', 'Flex Fuel (E85 Ethanol/Gasoline)')
        ]
    
    @staticmethod
    def _make_request(endpoint: str) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            url = f"{EPAFuelEconomyService.BASE_URL}/{endpoint}"
            headers = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return data
                except ValueError as e:
                    return None
            else:
                return None
                
        except requests.RequestException as e:
            return None


# Keep NHTSA service as a fallback or for specific data not available in EPA
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
    def get_vin_variables() -> List[Dict]:
        """Get all possible VIN variables"""
        endpoint = f"vehicles/GetVehicleVariableList?format=json"
        response = NHTSAService._make_request(endpoint)
        results = response.get('Results', []) if response else []
        return results
    
    @staticmethod
    def decode_vin(vin: str) -> List[Dict]:
        """Decode a VIN to get vehicle details"""
        endpoint = f"vehicles/DecodeVin/{vin}?format=json"
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