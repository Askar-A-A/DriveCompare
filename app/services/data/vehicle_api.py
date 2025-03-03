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
            # Fallback to a reasonable range of years
            current_year = 2023  # You might want to calculate this dynamically
            years = [(year, year) for year in range(current_year, current_year-20, -1)]
            return years
        
        # Extract years from the response
        years = []
        menu_items = response.get('menuItem', [])
        
        # Handle both list and dictionary responses
        if isinstance(menu_items, list):
            for item in menu_items:
                if isinstance(item, dict):
                    year = item.get('value')
                    if year and year.isdigit():
                        year_int = int(year)
                        years.append((year_int, year_int))
                elif isinstance(item, str) and item.isdigit():
                    # If it's a string and a digit, use it directly as the year
                    year_int = int(item)
                    years.append((year_int, year_int))
        elif isinstance(menu_items, dict):
            year = menu_items.get('value')
            if year and year.isdigit():
                year_int = int(year)
                years.append((year_int, year_int))
        
        # Sort years in descending order (newest first)
        years.sort(reverse=True)
        return years
    
    @staticmethod
    def get_makes(year: Optional[int] = None) -> List[Tuple[str, str]]:
        """Get all makes, optionally filtered by year"""
        if year:
            endpoint = f"vehicle/menu/make?year={year}"
        else:
            # If no year provided, we'll use the most recent year
            years = EPAFuelEconomyService.get_years()
            if years:
                year = years[0][0]  # Get the first (most recent) year
                endpoint = f"vehicle/menu/make?year={year}"
            else:
                return []  # No years available
        
        response = EPAFuelEconomyService._make_request(endpoint)
        
        if not response:
            return []
        
        # Extract makes from the response
        makes = []
        menu_items = response.get('menuItem', [])
        
        # Handle both list and dictionary responses
        if isinstance(menu_items, list):
            for item in menu_items:
                if isinstance(item, dict):
                    make = item.get('value')
                    if make:
                        makes.append((make, make))
                elif isinstance(item, str):
                    # If it's a string, use it directly as the make
                    makes.append((item, item))
        elif isinstance(menu_items, dict):
            make = menu_items.get('value')
            if make:
                makes.append((make, make))
        
        # Sort makes alphabetically
        makes.sort()
        return makes
    
    @staticmethod
    def get_models(make: str, year: int) -> List[Tuple[str, str]]:
        """Get all models for a specific make and year"""
        endpoint = f"vehicle/menu/model?year={year}&make={make}"
        response = EPAFuelEconomyService._make_request(endpoint)
        
        if not response:
            return []
        
        # Extract models from the response
        models = []
        menu_items = response.get('menuItem', [])
        
        # Handle both list and dictionary responses
        if isinstance(menu_items, list):
            for item in menu_items:
                if isinstance(item, dict):
                    model = item.get('value')
                    if model:
                        models.append((model, model))
                elif isinstance(item, str):
                    # If it's a string, use it directly as the model
                    models.append((item, item))
        elif isinstance(menu_items, dict):
            model = menu_items.get('value')
            if model:
                models.append((model, model))
        
        # Sort models alphabetically
        models.sort()
        return models
    
    @staticmethod
    def get_vehicle_types(make: str) -> List[Dict]:
        """
        EPA doesn't have a direct vehicle type endpoint like NHTSA.
        For compatibility, we'll return a simplified list of common vehicle types.
        """
        # Common vehicle types
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
        # First get the vehicle options to find vehicle IDs
        options_endpoint = f"vehicle/menu/options?year={year}&make={make}&model={model}"
        options_response = EPAFuelEconomyService._make_request(options_endpoint)
        
        if not options_response:
            print(f"No options response for: {make} {model} {year}")
            return EPAFuelEconomyService.default_fuel_types()
        
        # Extract vehicle IDs from options
        vehicle_ids = []
        menu_items = options_response.get('menuItem', [])
        
        # Handle both list and dictionary responses
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
            print(f"No vehicle IDs found for: {make} {model} {year}")
            return EPAFuelEconomyService.default_fuel_types()
        
        # Get fuel types from vehicle details
        fuel_types = set()
        
        # Limit to first 3 vehicle IDs to avoid too many API calls
        for vehicle_id in vehicle_ids[:3]:
            vehicle_endpoint = f"vehicle/{vehicle_id}"
            vehicle_response = EPAFuelEconomyService._make_request(vehicle_endpoint)
            
            if vehicle_response:
                # Extract fuel type from vehicle details
                fuel_type = vehicle_response.get('fuelType')
                if fuel_type:
                    fuel_types.add((fuel_type, fuel_type))
        
        # Convert to list and sort
        fuel_types = sorted(list(fuel_types))
        
        # If no fuel types found, use default list
        if not fuel_types:
            print(f"No fuel types found for: {make} {model} {year}, using defaults")
            return EPAFuelEconomyService.default_fuel_types()
        
        return fuel_types
    
    @staticmethod
    def get_vehicle_details(vehicle_id: str) -> Optional[Dict]:
        """Get detailed information for a specific vehicle"""
        endpoint = f"vehicle/{vehicle_id}"
        return EPAFuelEconomyService._make_request(endpoint)
    
    @staticmethod
    def default_fuel_types() -> List[Tuple[str, str]]:
        """Return default fuel types if API fails"""
        return [
            ('Gasoline', 'Gasoline'),
            ('Diesel', 'Diesel'),
            ('Hybrid', 'Hybrid'),
            ('Plug-in Hybrid', 'Plug-in Hybrid'),
            ('Electric', 'Electric'),
            ('Flex-Fuel', 'Flex-Fuel')
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
                    # Print the response structure for debugging
                    if 'model' in endpoint or 'make' in endpoint or 'year' in endpoint or 'options' in endpoint:
                        print(f"API Response for {url}: {str(data)[:200]}...")
                        if data is not None:  # Check if data is not None
                            print(f"Type of menuItem: {type(data.get('menuItem'))}")
                            if isinstance(data.get('menuItem'), list) and data.get('menuItem'):
                                print(f"Type of first item in menuItem: {type(data['menuItem'][0])}")
                    return data
                except ValueError as e:
                    print(f"EPA API JSON parsing error: {e}")
                    return None
            else:
                print(f"EPA API error: {response.status_code} for URL: {url}")
                return None
                
        except requests.RequestException as e:
            print(f"EPA API request exception: {e}")
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