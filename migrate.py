from migrations.add_vehicle_makes_table import up as create_vehicle_makes_table
import logging
from app import app, db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info("Starting migration: Creating vehicle_makes table")
    
    with app.app_context():
        result = create_vehicle_makes_table()
    
        if result:
            logging.info("Migration completed successfully")
        else:
            logging.error("Migration failed") 