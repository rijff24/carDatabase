"""Script to create vehicle_makes table and populate it with existing makes"""
import sys
from app import create_app, db
from app.models.car import Car, VehicleMake
import os

def create_vehicle_makes():
    """Create vehicle_makes table and populate it with existing makes"""
    app = create_app(os.getenv('FLASK_ENV') or 'default')
    
    with app.app_context():
        # Check if table exists
        if not VehicleMake.__table__.exists(db.engine):
            # Create table
            VehicleMake.__table__.create(db.engine)
            print("Created vehicle_makes table")
            
            # Get all unique makes from cars
            unique_makes = db.session.query(Car.vehicle_make).distinct().all()
            make_count = 0
            
            # Add each make to the new table
            for make in unique_makes:
                make_name = make[0]
                if make_name:
                    sanitized_name = VehicleMake.sanitize_name(make_name)
                    # Check if already exists (case insensitive)
                    exists = db.session.query(db.func.count(VehicleMake.id)).filter(
                        db.func.lower(VehicleMake.name) == db.func.lower(sanitized_name)
                    ).scalar()
                    
                    if not exists:
                        new_make = VehicleMake(name=sanitized_name)
                        db.session.add(new_make)
                        make_count += 1
            
            db.session.commit()
            print(f"Added {make_count} unique vehicle makes")
            return True
        else:
            print("vehicle_makes table already exists")
            return True

if __name__ == "__main__":
    print("Creating vehicle_makes table...")
    success = create_vehicle_makes()
    if success:
        print("Successfully created vehicle_makes table")
        sys.exit(0)
    else:
        print("Failed to create vehicle_makes table")
        sys.exit(1) 