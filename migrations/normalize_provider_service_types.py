"""
Migration: Normalize provider service types to match repair types

This migration updates all existing repair providers to ensure their service_type
values match exactly with the valid repair types in the RepairForm.
"""

from app import db
from app.models.repair_provider import RepairProvider
from flask import current_app
import logging

# Valid repair types from the RepairForm
VALID_REPAIR_TYPES = [
    'Upholstery', 'Panel Beating', 'Tires/Suspension', 'Workshop Repairs',
    'Car Wash', 'Air Conditioning', 'Brakes/Clutch', 'Windscreen',
    'Covers', 'Diagnostics', 'Other'
]

def find_closest_match(service_type):
    """Find the closest matching repair type for a given service type"""
    service_type = service_type.strip()
    
    # Direct match
    for repair_type in VALID_REPAIR_TYPES:
        if service_type.lower() == repair_type.lower():
            return repair_type
    
    # Contains match (e.g., "auto glass" -> "Windscreen")
    mapping = {
        'upholst': 'Upholstery',
        'panel': 'Panel Beating',
        'body': 'Panel Beating',
        'tir': 'Tires/Suspension',
        'wheel': 'Tires/Suspension',
        'suspension': 'Tires/Suspension',
        'workshop': 'Workshop Repairs',
        'repair': 'Workshop Repairs',
        'mechanic': 'Workshop Repairs',
        'wash': 'Car Wash',
        'clean': 'Car Wash',
        'air': 'Air Conditioning',
        'a/c': 'Air Conditioning',
        'brake': 'Brakes/Clutch',
        'clutch': 'Brakes/Clutch',
        'glass': 'Windscreen',
        'windscreen': 'Windscreen',
        'window': 'Windscreen',
        'cover': 'Covers',
        'diagnos': 'Diagnostics',
        'electric': 'Diagnostics'
    }
    
    for keyword, repair_type in mapping.items():
        if keyword.lower() in service_type.lower():
            return repair_type
    
    # Default case
    return 'Other'

def run_migration():
    """Run the migration to normalize provider service types"""
    try:
        providers = RepairProvider.query.all()
        updates_count = 0
        
        for provider in providers:
            original_type = provider.service_type
            if original_type not in VALID_REPAIR_TYPES:
                provider.service_type = find_closest_match(original_type)
                updates_count += 1
                logging.info(f"Updated provider '{provider.provider_name}' service type from '{original_type}' to '{provider.service_type}'")
        
        if updates_count > 0:
            db.session.commit()
            logging.info(f"Successfully updated {updates_count} provider service types")
        else:
            logging.info("No provider service types needed updating")
            
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error during migration: {str(e)}")
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