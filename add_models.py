from app import db, create_app
from app.models.car import VehicleMake, VehicleModel
from sqlalchemy.exc import IntegrityError

def add_models():
    app = create_app()
    with app.app_context():
        try:
            # Get all makes and print them
            makes = VehicleMake.query.all()
            print('Makes:', [(make.id, make.name) for make in makes])
            
            # Add Toyota models
            toyota = VehicleMake.query.filter_by(name='Toyota').first()
            if toyota:
                toyota_models = ['Camry', 'Corolla', 'RAV4', 'Highlander', 'Tacoma', 'Prius']
                for model_name in toyota_models:
                    # Use case-insensitive check
                    existing_model = VehicleModel.query.filter(
                        db.func.lower(VehicleModel.name) == db.func.lower(model_name)
                    ).first()
                    
                    if not existing_model:
                        try:
                            model = VehicleModel(name=model_name, make_id=toyota.id)
                            db.session.add(model)
                            db.session.commit()
                            print(f'Added {model_name} to Toyota')
                        except IntegrityError:
                            db.session.rollback()
                            print(f'Error adding {model_name} to Toyota - already exists')
            
            # Add Volkswagen models
            volkswagen = VehicleMake.query.filter_by(name='Volkswagen').first()
            if volkswagen:
                vw_models = ['Golf', 'Jetta', 'Passat', 'Tiguan', 'Atlas', 'Polo', 'Arteon']
                for model_name in vw_models:
                    # Use case-insensitive check
                    existing_model = VehicleModel.query.filter(
                        db.func.lower(VehicleModel.name) == db.func.lower(model_name)
                    ).first()
                    
                    if not existing_model:
                        try:
                            model = VehicleModel(name=model_name, make_id=volkswagen.id)
                            db.session.add(model)
                            db.session.commit()
                            print(f'Added {model_name} to Volkswagen')
                        except IntegrityError:
                            db.session.rollback()
                            print(f'Error adding {model_name} to Volkswagen - already exists')
            
            # Add VW models (if different from Volkswagen)
            vw = VehicleMake.query.filter_by(name='Vw').first()
            if vw and vw.id != getattr(volkswagen, 'id', None):
                vw_models = ['Golf', 'Jetta', 'Passat', 'Tiguan', 'Atlas', 'Polo', 'Arteon']
                for model_name in vw_models:
                    # Use case-insensitive check
                    existing_model = VehicleModel.query.filter(
                        db.func.lower(VehicleModel.name) == db.func.lower(model_name)
                    ).first()
                    
                    if not existing_model:
                        try:
                            model = VehicleModel(name=model_name, make_id=vw.id)
                            db.session.add(model)
                            db.session.commit()
                            print(f'Added {model_name} to VW')
                        except IntegrityError:
                            db.session.rollback()
                            print(f'Error adding {model_name} to VW - already exists')
            
            # Print all models
            models = VehicleModel.query.all()
            print('All Models:')
            for model in models:
                make_name = model.make.name if hasattr(model, 'make') and model.make else 'Unknown Make'
                print(f'  ID: {model.id}, Name: {model.name}, Make: {make_name}')
        
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == '__main__':
    add_models() 