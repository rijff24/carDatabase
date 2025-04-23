"""Script to verify vehicle model-make relationships"""
import sys
import os
from app import create_app, db
from app.models.car import VehicleMake, VehicleModel

def verify_relationships():
    """Verify that vehicle models are correctly associated with their makes"""
    app = create_app(os.getenv('FLASK_ENV') or 'default')
    
    with app.app_context():
        try:
            # Get all makes
            makes = VehicleMake.query.all()
            print("\nVerifying make-model relationships:")
            print("-" * 50)
            
            for make in makes:
                print(f"\nMake: {make.name}")
                print("Associated models:")
                models = VehicleModel.query.filter_by(make_id=make.id).all()
                if models:
                    for model in models:
                        print(f"  - {model.name}")
                else:
                    print("  No models associated")
            
            print("\nVerification complete")
            return True
            
        except Exception as e:
            print(f"Error verifying relationships: {str(e)}")
            return False

if __name__ == '__main__':
    verify_relationships() 