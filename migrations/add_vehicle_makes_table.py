from app import db
from app.models.car import VehicleMake, Car
from sqlalchemy import text
import logging

def up():
    """Create the vehicle_makes table and populate it with existing makes"""
    try:
        # Check if the table already exists
        inspector = db.inspect(db.engine)
        if 'vehicle_makes' not in inspector.get_table_names():
            logging.info("Creating vehicle_makes table...")
            
            # Create the table
            VehicleMake.__table__.create(db.engine)
            
            # Populate the table with existing unique makes from cars table
            with db.engine.connect() as conn:
                # Get all unique makes from the cars table
                result = conn.execute(text("SELECT DISTINCT vehicle_make FROM cars WHERE vehicle_make IS NOT NULL"))
                makes = [row[0] for row in result]
                
                # Insert each make (sanitized) into the new table
                for make in makes:
                    sanitized_make = VehicleMake.sanitize_name(make)
                    # Check if it already exists
                    exists = conn.execute(
                        text("SELECT COUNT(*) FROM vehicle_makes WHERE lower(name) = lower(:name)"),
                        {"name": sanitized_make}
                    ).scalar()
                    
                    if not exists:
                        conn.execute(
                            text("INSERT INTO vehicle_makes (name) VALUES (:name)"),
                            {"name": sanitized_make}
                        )
                        
            logging.info(f"Successfully populated vehicle_makes table with {len(makes)} unique values")
        else:
            logging.info("vehicle_makes table already exists")
            
        return True
    except Exception as e:
        logging.error(f"Error creating vehicle_makes table: {str(e)}")
        return False
        
def down():
    """Drop the vehicle_makes table"""
    try:
        inspector = db.inspect(db.engine)
        if 'vehicle_makes' in inspector.get_table_names():
            logging.info("Dropping vehicle_makes table...")
            VehicleMake.__table__.drop(db.engine)
            logging.info("Successfully dropped vehicle_makes table")
        else:
            logging.info("vehicle_makes table does not exist")
            
        return True
    except Exception as e:
        logging.error(f"Error dropping vehicle_makes table: {str(e)}")
        return False 