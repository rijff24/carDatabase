"""
Script to create and populate all vehicle-related tables
"""
from create_vehicle_makes_table import create_vehicle_makes
from create_vehicle_models_table import create_vehicle_models
from create_vehicle_data_tables import create_vehicle_data
import sys

if __name__ == "__main__":
    print("Setting up all vehicle tables...")
    
    # Create vehicle_makes table
    print("\n1. Creating vehicle_makes table...")
    makes_result = create_vehicle_makes()
    
    # Create vehicle_models table
    print("\n2. Creating vehicle_models table...")
    models_result = create_vehicle_models()
    
    # Create vehicle_years and vehicle_colors tables
    print("\n3. Creating vehicle_years and vehicle_colors tables...")
    created_data_tables = create_vehicle_data()
    
    if makes_result and models_result and created_data_tables is not None:
        print("\nAll tables setup completed successfully!")
        sys.exit(0)
    else:
        print("\nSetup failed. Check the logs for details.")
        sys.exit(1) 