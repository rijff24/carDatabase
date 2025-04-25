from flask import current_app
import logging
import importlib
import os
import sys

# Import all migration modules
from migrations import create_tables
from migrations import make_provider_fields_optional
from migrations import normalize_provider_service_types
from migrations.versions import update_part_model

# List of migrations in order of execution
MIGRATIONS = [
    create_tables,
    make_provider_fields_optional,
    normalize_provider_service_types,
    update_part_model
]

def run_migrations():
    """Run all pending migrations"""
    logging.info("Starting migrations...")
    
    for migration in MIGRATIONS:
        migration_name = migration.__name__.split('.')[-1]
        logging.info(f"Running migration: {migration_name}")
        
        success = migration.run_migration()
        if success:
            logging.info(f"Migration {migration_name} completed successfully")
        else:
            logging.error(f"Migration {migration_name} failed")
            return False
    
    logging.info("All migrations completed successfully")
    return True

if __name__ == "__main__":
    # This allows running migrations directly
    from flask import Flask
    from app import db
    
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')
    
    with app.app_context():
        run_migrations() 