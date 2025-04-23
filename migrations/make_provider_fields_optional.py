"""
Migration: Make contact_info and location fields optional for repair providers

This migration alters the repair_providers table to make the contact_info and location
fields nullable (optional), allowing providers to be created with just name and service type.
"""

from app import db
from flask import current_app
import sqlite3
import logging

def run_migration():
    """Run the migration to make contact_info and location nullable in the repair_providers table"""
    try:
        # Get database path
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Step 1: Rename existing table to temporary table
        cursor.execute('''
        ALTER TABLE repair_providers RENAME TO repair_providers_old;
        ''')
        
        # Step 2: Create new table with updated schema
        cursor.execute('''
        CREATE TABLE repair_providers (
            provider_id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_name VARCHAR(100) NOT NULL,
            service_type VARCHAR(50) NOT NULL,
            contact_info VARCHAR(150),
            location VARCHAR(100),
            notes TEXT,
            date_added DATETIME NOT NULL,
            rating INTEGER
        );
        ''')
        
        # Step 3: Copy data from old table to new table
        cursor.execute('''
        INSERT INTO repair_providers (
            provider_id, provider_name, service_type, contact_info, location, notes, date_added, rating
        )
        SELECT provider_id, provider_name, service_type, contact_info, location, notes, date_added, rating
        FROM repair_providers_old;
        ''')
        
        # Step 4: Drop old table
        cursor.execute('''
        DROP TABLE repair_providers_old;
        ''')
        
        # Commit changes
        conn.commit()
        conn.close()
        
        logging.info("Successfully made contact_info and location nullable in repair_providers table")
        return True
    except Exception as e:
        logging.error(f"Error during migration: {str(e)}")
        # If there was an error, rollback
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    # This allows running the migration directly
    from flask import Flask
    from app import db
    
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')
    
    with app.app_context():
        if run_migration():
            print("Migration completed successfully")
        else:
            print("Migration failed") 