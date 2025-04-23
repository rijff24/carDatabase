from app import db
from app.models.car import VehicleModel, Car
from sqlalchemy import text
import logging

def up():
    """Create the vehicle_models table and populate it with existing models"""
    try:
        # Check if the table already exists
        inspector = db.inspect(db.engine)
        if 'vehicle_models' not in inspector.get_table_names():
            logging.info("Creating vehicle_models table...")
            
            # Create the table
            VehicleModel.__table__.create(db.engine)
            
            # Populate the table with existing unique models from cars table
            with db.engine.connect() as conn:
                # Get all unique models from the cars table
                result = conn.execute(text("SELECT DISTINCT vehicle_model FROM cars WHERE vehicle_model IS NOT NULL"))
                models = [row[0] for row in result]
                
                # Insert each model (sanitized) into the new table
                for model_name in models:
                    sanitized_model = VehicleModel.sanitize_name(model_name)
                    # Check if it already exists
                    exists = conn.execute(
                        text("SELECT COUNT(*) FROM vehicle_models WHERE lower(name) = lower(:name)"),
                        {"name": sanitized_model}
                    ).scalar()
                    
                    if not exists:
                        conn.execute(
                            text("INSERT INTO vehicle_models (name) VALUES (:name)"),
                            {"name": sanitized_model}
                        )
                        
            logging.info(f"Successfully populated vehicle_models table with {len(models)} unique values")
        else:
            logging.info("vehicle_models table already exists")
            
        return True
    except Exception as e:
        logging.error(f"Error creating vehicle_models table: {str(e)}")
        return False
        
def down():
    """Drop the vehicle_models table"""
    try:
        inspector = db.inspect(db.engine)
        if 'vehicle_models' in inspector.get_table_names():
            logging.info("Dropping vehicle_models table...")
            VehicleModel.__table__.drop(db.engine)
            logging.info("Successfully dropped vehicle_models table")
        else:
            logging.info("vehicle_models table does not exist")
            
        return True
    except Exception as e:
        logging.error(f"Error dropping vehicle_models table: {str(e)}")
        return False 