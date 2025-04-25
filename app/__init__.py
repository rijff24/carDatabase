"""
Application package for Car Repair and Sales Tracking Web Application.

This module:
1. Initializes Flask extensions
2. Provides the application factory function
3. Registers blueprints for different application components
4. Sets up Jinja2 filters and context processors
"""

from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config
import datetime
import jinja2
import markupsafe
import os
from app.utils.errors import register_error_handlers
import logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
csrf = CSRFProtect()

def create_app(config_name='default'):
    """
    Application factory function that creates and configures the Flask app.
    
    Args:
        config_name (str): Configuration environment to use (default, development, 
                          testing, or production)
                          
    Returns:
        Flask: The configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Ensure secret key is set
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.urandom(24)
    
    # Configure CSRF protection
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow CSRF token on http
    
    # Configure logging
    if not app.debug:
        # Set up logging for production
        app.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] in %(module)s: %(message)s'
        ))
        app.logger.addHandler(handler)
    else:
        # Set up more verbose logging for development
        app.logger.setLevel(logging.DEBUG)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Custom unauthorized handler for login_manager
    @login_manager.unauthorized_handler
    def unauthorized():
        # Check if request is expecting JSON or is an API request
        if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
            return jsonify(message="Authentication required", status_code=401), 401
        # For standard requests, redirect to login page
        return redirect(url_for(login_manager.login_view, next=request.path))
    
    # Register error handlers
    register_error_handlers(app, db)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.cars import cars_bp
    from app.routes.repairs import repairs_bp
    from app.routes.parts import parts_bp
    from app.routes.providers import providers_bp
    from app.routes.stands import stands_bp
    from app.routes.dealers import dealers_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp
    from app.routes.vehicle_data import vehicle_data
    from app.routes.api import api_bp
    from app.routes.import_routes import import_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(cars_bp, url_prefix='/cars')
    app.register_blueprint(repairs_bp, url_prefix='/repairs')
    app.register_blueprint(parts_bp, url_prefix='/parts')
    app.register_blueprint(providers_bp, url_prefix='/providers')
    app.register_blueprint(stands_bp, url_prefix='/stands')
    app.register_blueprint(dealers_bp, url_prefix='/dealers')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(vehicle_data, url_prefix='/vehicle-data')
    app.register_blueprint(api_bp)
    app.register_blueprint(import_bp, url_prefix='/import')
    
    # Temporarily disable CSRF for import routes to debug issues
    csrf.exempt(import_bp)
    
    # Register Jinja2 filters
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_price'] = format_price
    app.jinja_env.filters['format_percentage'] = format_percentage
    app.jinja_env.filters['format_number'] = format_number
    
    # Register context processors
    @app.context_processor
    def utility_processor():
        return {
            'datetime': datetime
        }
    
    # Dark mode context processor
    @app.context_processor
    def dark_mode_processor():
        # Import here to avoid circular import
        from app.models.setting import Setting
        
        # Get dark mode setting or default to False
        dark_mode_enabled = False
        try:
            dark_mode_enabled = Setting.get_setting('enable_dark_mode', False)
        except:
            # If Setting model isn't available yet (e.g., during migrations)
            pass
        
        return {
            'dark_mode_enabled': dark_mode_enabled
        }
    
    return app

# Jinja2 filters
def format_date(value, format='%Y-%m-%d'):
    """Format a date value"""
    if value is None:
        return ''
    return value.strftime(format)

def format_price(value):
    """Format a price value"""
    if value is None:
        return '-'
    return f"${value:,.2f}"

def format_percentage(value):
    """Format a percentage value"""
    if value is None:
        return '-'
    return f"{value:.1f}%"

def format_number(value):
    """Format a number with thousands separators"""
    if value is None:
        return ""
    return "{:,.2f}".format(float(value)) 