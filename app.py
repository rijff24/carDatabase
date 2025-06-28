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
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

# Create the Flask application instance
app = Flask(__name__)

# Load the appropriate configuration
environment = os.environ.get('FLASK_ENV', 'development')
if environment == 'production':
    app.config.from_object('config.ProductionConfig')
elif environment == 'testing':
    app.config.from_object('config.TestingConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

# Initialize the database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import the models and routes after initializing the app and db
from app.models.setting import Setting
from app import routes

# Register blueprints
from app.routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.routes.cars import cars_bp
app.register_blueprint(cars_bp, url_prefix='/cars')

from app.routes.stands import stands_bp
app.register_blueprint(stands_bp, url_prefix='/stands')

from app.routes.dealers import dealers_bp
app.register_blueprint(dealers_bp, url_prefix='/dealers')

from app.routes.repairs import repairs_bp
app.register_blueprint(repairs_bp, url_prefix='/repairs')

from app.routes.providers import providers_bp
app.register_blueprint(providers_bp, url_prefix='/providers')

from app.routes.parts import parts_bp
app.register_blueprint(parts_bp, url_prefix='/parts')

from app.routes.settings import settings_bp
app.register_blueprint(settings_bp, url_prefix='/settings')

from app.routes.reports import reports_bp
app.register_blueprint(reports_bp, url_prefix='/reports')

from app.routes.import_routes import import_bp
app.register_blueprint(import_bp, url_prefix='/import')

from app.routes.vehicle_data import vehicle_data_bp
app.register_blueprint(vehicle_data_bp, url_prefix='/vehicle-data')

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add context processor to make settings available in all templates
@app.context_processor
def inject_settings():
    return dict(settings=Setting)

# Add dark mode setting to all templates
@app.context_processor
def inject_dark_mode():
    # Check if dark mode is enabled in settings
    dark_mode_enabled = Setting.get_setting('enable_dark_mode', False)
    return dict(dark_mode_enabled=dark_mode_enabled)

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
    Password: admin
    Usage: flask create-admin
    """
    admin = User(
        username='admin',
        full_name='Administrator',
        role='admin'
    )
    # Directly set password hash to bypass validation
    admin.password_hash = generate_password_hash('admin')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created with username: admin, password: admin")

if __name__ == '__main__':
    app.run(debug=True) 