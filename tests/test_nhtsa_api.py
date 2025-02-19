import sys
import os
from typing import Dict, List
from datetime import datetime

# Add the application root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vehicle_api import NHTSAService

def print_separator():
    print("\n" + "="*50 + "\n")

def test_get_makes():
    """Test getting vehicle makes for a specific year"""
    print("Testing Get Makes...")
    year = 2024
    
    try:
        makes = NHTSAService.get_makes(year)
        print(f"✓ Found {len(makes)} makes for {year}")
        print("Sample makes:")
        for make in makes[:3]:  # Show first 3 makes
            print(f"  - {make.get('Make_Name', 'N/A')}")
    except Exception as e:
        print(f"✗ Error getting makes: {e}")
    
    print_separator()

def test_get_models():
    """Test getting models for specific makes and year"""
    print("Testing Get Models...")
    test_makes = ["Honda", "Toyota", "Tesla"]
    year = 2024
    
    for make in test_makes:
        try:
            models = NHTSAService.get_models(make, year)
            print(f"✓ Found {len(models)} models for {make} {year}")
            print(f"Sample {make} models:")
            for model in models[:3]:  # Show first 3 models
                print(f"  - {model.get('Model_Name', 'N/A')}")
        except Exception as e:
            print(f"✗ Error getting models for {make}: {e}")
        print()
    
    print_separator()

def test_get_vehicle_info():
    """Test getting vehicle information by VIN"""
    print("Testing Get Vehicle Info...")
    # Test VINs (you can replace these with real VINs)
    test_vins = [
        "1HGCM82633A123456",  # Honda (example)
        "5YJ3E1EA1JF123456",  # Tesla (example)
    ]
    
    for vin in test_vins:
        try:
            vehicle_info = NHTSAService.get_vehicle_info(vin)
            if vehicle_info:
                print(f"✓ Successfully decoded VIN: {vin}")
                print("Vehicle details:")
                print(f"  - Make: {vehicle_info.get('Make', 'N/A')}")
                print(f"  - Model: {vehicle_info.get('Model', 'N/A')}")
                print(f"  - Year: {vehicle_info.get('ModelYear', 'N/A')}")
                print(f"  - Body Style: {vehicle_info.get('BodyClass', 'N/A')}")
            else:
                print(f"✗ No information found for VIN: {vin}")
        except Exception as e:
            print(f"✗ Error decoding VIN {vin}: {e}")
        print()
    
    print_separator()

def run_all_tests():
    """Run all API tests"""
    print(f"Starting NHTSA API Tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    test_get_makes()
    test_get_models()
    test_get_vehicle_info()
    
    print("All tests completed!")

if __name__ == "__main__":
    run_all_tests()
