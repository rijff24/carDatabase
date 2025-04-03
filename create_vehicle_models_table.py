"""Script to create vehicle_models table and populate it with existing models"""
import sys
from app import create_app, db
from app.models.car import Car, VehicleModel
import os

def create_vehicle_models():
    """Create vehicle_models table and populate it with existing models"""
    app = create_app(os.getenv('FLASK_ENV') or 'default')
    
    with app.app_context():
        # Check if table exists
        if not VehicleModel.__table__.exists(db.engine):
            # Create table
            VehicleModel.__table__.create(db.engine)
            print("Created vehicle_models table")
            
            # Get all unique models from cars
            unique_models = db.session.query(Car.vehicle_model).distinct().all()
            model_count = 0
            
            # Add each model to the new table
            for model in unique_models:
                model_name = model[0]
                if model_name:
                    sanitized_name = VehicleModel.sanitize_name(model_name)
                    # Check if already exists (case insensitive)
                    exists = db.session.query(db.func.count(VehicleModel.id)).filter(
                        db.func.lower(VehicleModel.name) == db.func.lower(sanitized_name)
                    ).scalar()
                    
                    if not exists:
                        new_model = VehicleModel(name=sanitized_name)
                        db.session.add(new_model)
                        model_count += 1
            
            db.session.commit()
            print(f"Added {model_count} unique vehicle models")
            return True
        else:
            print("vehicle_models table already exists")
            return True

if __name__ == "__main__":
    print("Creating vehicle_models table...")
    success = create_vehicle_models()
    if success:
        print("Successfully created vehicle_models table")
        sys.exit(0)
    else:
        print("Failed to create vehicle_models table")
        sys.exit(1) 