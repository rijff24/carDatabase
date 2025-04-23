"""
Script to create both the vehicle_makes and vehicle_models tables
"""
from create_vehicle_makes_table import create_vehicle_makes
from create_vehicle_models_table import create_vehicle_models
import sys

if __name__ == "__main__":
    print("Setting up vehicle tables...")
    
    # Create vehicle_makes table
    print("\n1. Creating vehicle_makes table...")
    makes_result = create_vehicle_makes()
    
    # Create vehicle_models table
    print("\n2. Creating vehicle_models table...")
    models_result = create_vehicle_models()
    
    if makes_result and models_result:
        print("\nSetup completed successfully!")
        sys.exit(0)
    else:
        print("\nSetup failed. Check the logs for details.")
        sys.exit(1) 