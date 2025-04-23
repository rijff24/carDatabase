"""Script to add make_id to vehicle_models table"""
import sys
import os
from app import create_app, db
from app.models.car import VehicleMake, VehicleModel
from sqlalchemy import Column, Integer, ForeignKey, MetaData, Table, select

def update_vehicle_models():
    """Add make_id column to vehicle_models table and set default relationships"""
    app = create_app(os.getenv('FLASK_ENV') or 'default')
    
    with app.app_context():
        try:
            # Get metadata from engine
            metadata = MetaData()
            metadata.reflect(bind=db.engine)
            
            # Check if the table exists
            if 'vehicle_models' not in metadata.tables:
                print("vehicle_models table doesn't exist!")
                return False
                
            vehicle_models = metadata.tables['vehicle_models']
            
            # Check if make_id column exists
            if 'make_id' not in vehicle_models.c:
                # Create make_id column
                # Get a connection
                conn = db.engine.connect()
                
                # Execute alter table statement
                conn.execute("ALTER TABLE vehicle_models ADD COLUMN make_id INTEGER REFERENCES vehicle_makes(id)")
                conn.commit()
                conn.close()
                
                print("Added make_id column to vehicle_models table")
                
                # Get default make or create one
                default_make = VehicleMake.query.filter_by(name='Unknown').first()
                if not default_make:
                    default_make = VehicleMake(name='Unknown')
                    db.session.add(default_make)
                    db.session.commit()
                    
                # Set all existing models to use the default make
                conn = db.engine.connect()
                conn.execute(f"UPDATE vehicle_models SET make_id = {default_make.id}")
                conn.commit()
                conn.close()
                
                # Now set make_id to not nullable
                conn = db.engine.connect()
                
                # SQLite doesn't support ALTER COLUMN, so we need to create a new table with the constraint
                conn.execute("""
                    PRAGMA foreign_keys=off;
                    
                    CREATE TABLE vehicle_models_new (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name VARCHAR(50) NOT NULL,
                      make_id INTEGER NOT NULL REFERENCES vehicle_makes(id)
                    );
                    
                    INSERT INTO vehicle_models_new SELECT id, name, make_id FROM vehicle_models;
                    
                    DROP TABLE vehicle_models;
                    
                    ALTER TABLE vehicle_models_new RENAME TO vehicle_models;
                    
                    PRAGMA foreign_keys=on;
                """)
                conn.commit()
                conn.close()
                
                print("Updated vehicle_models table schema to make make_id NOT NULL")
                
                return True
            else:
                print("make_id column already exists in vehicle_models table")
                return True
                
        except Exception as e:
            print(f"Error updating vehicle_models table: {str(e)}")
            return False

if __name__ == "__main__":
    print("Updating vehicle_models table...")
    success = update_vehicle_models()
    if success:
        print("Successfully updated vehicle_models table")
        sys.exit(0)
    else:
        print("Failed to update vehicle_models table")
        sys.exit(1) 