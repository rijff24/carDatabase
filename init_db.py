"""
Database initialization script for the Car Repair and Sales Tracking application.

This script:
1. Creates all database tables
2. Checks if an admin user exists
3. Creates an admin user if one doesn't exist

Run this script directly to initialize the development database:
    python init_db.py
"""

from app import create_app, db
from app.models.user import User

# Create app with development configuration
app = create_app('development')
with app.app_context():
    # Create all database tables
    db.create_all()
    
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # Create admin user with default credentials
        admin = User(
            username='admin',
            full_name='Administrator',
            role='admin'
        )
        admin.password = 'admin123'  # Password will be hashed by the model
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.") 