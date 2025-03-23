"""
Main application file for the Car Repair and Sales Tracking Web Application.

This file:
1. Creates the Flask application
2. Registers CLI commands for database management
3. Sets up the Python shell context

The application can be run directly with:
    python app.py

Or through Flask:
    flask run
"""

import os
from app import create_app, db
from app.models.car import Car
from app.models.repair import Repair
from app.models.part import Part, RepairPart
from app.models.repair_provider import RepairProvider
from app.models.stand import Stand
from app.models.dealer import Dealer
from app.models.user import User
from flask_migrate import Migrate

# Create app instance based on environment setting from .env file
app = create_app(os.getenv('FLASK_ENV') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """
    Make additional objects available in the shell context.
    Allows for easy database queries and manipulation in the Flask shell.
    """
    return dict(
        db=db, 
        Car=Car, 
        Repair=Repair, 
        Part=Part, 
        RepairPart=RepairPart,
        RepairProvider=RepairProvider, 
        Stand=Stand, 
        Dealer=Dealer, 
        User=User
    )

@app.cli.command("create-db")
def create_db():
    """
    Create all database tables.
    Usage: flask create-db
    """
    db.create_all()
    print("Database tables created")

@app.cli.command("drop-db")
def drop_db():
    """
    Drop all database tables.
    Usage: flask drop-db
    """
    db.drop_all()
    print("Database tables dropped")

@app.cli.command("create-admin")
def create_admin():
    """
    Create admin user with default credentials.
    Username: admin
    Password: admin123
    Usage: flask create-admin
    """
    admin = User(
        username='admin',
        full_name='Administrator',
        role='admin'
    )
    admin.password = 'admin123'  # Password will be hashed by the model
    db.session.add(admin)
    db.session.commit()
    print("Admin user created")

if __name__ == '__main__':
    app.run(debug=True) 