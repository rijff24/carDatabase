"""Script to update vehicle models with their correct makes based on cars in the database"""
import sys
import os
from app import create_app, db
from app.models.car import VehicleMake, VehicleModel, Car
from sqlalchemy import distinct, func

def update_model_make_relationships():
    """Update vehicle models with their correct makes based on cars in the database"""
    app = create_app(os.getenv('FLASK_ENV') or 'default')
    
    with app.app_context():
        try:
            # Get all unique make-model combinations from cars
            make_model_pairs = db.session.query(
                Car.vehicle_make,
                Car.vehicle_model
            ).distinct().all()
            
            # Create a dictionary to store make-model relationships
            make_model_map = {}
            
            # Process each make-model pair
            for make_name, model_name in make_model_pairs:
                # Get or create the make
                make = VehicleMake.get_or_create(make_name)
                if not make:
                    print(f"Could not create make: {make_name}")
                    continue
                
                # Get or create the model with the correct make_id
                model = VehicleModel.get_or_create(model_name, make.id)
                if not model:
                    print(f"Could not create model: {model_name} for make: {make_name}")
                    continue
                
                # Update model's make_id if it doesn't match
                if model.make_id != make.id:
                    model.make_id = make.id
                    db.session.commit()
                    print(f"Updated model {model.name} to be associated with make {make.name}")
            
            print("Successfully updated model-make relationships")
            return True
            
        except Exception as e:
            print(f"Error updating model-make relationships: {str(e)}")
            return False

if __name__ == '__main__':
    update_model_make_relationships() 