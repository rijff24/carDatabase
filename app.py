import os
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///car_sales.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Import models (must be after db initialization)
# from app.models import User, Car, Repair, Stand, Provider

# Register blueprints (commented out as they're not created yet)
# from app.auth import auth
# from app.cars import cars
# from app.repairs import repairs
# from app.stands import stands
# from app.providers import providers
# from app.reports import reports
# from app.users import users
# from app.settings import settings
# 
# app.register_blueprint(auth, url_prefix='/auth')
# app.register_blueprint(cars, url_prefix='/cars')
# app.register_blueprint(repairs, url_prefix='/repairs')
# app.register_blueprint(stands, url_prefix='/stands')
# app.register_blueprint(providers, url_prefix='/providers')
# app.register_blueprint(reports, url_prefix='/reports')
# app.register_blueprint(users, url_prefix='/users')
# app.register_blueprint(settings, url_prefix='/settings')

# Main routes
@app.route('/')
def index():
    # Sample data for demonstration
    total_cars = 42
    cars_on_stand = 15
    recent_sales = 7
    avg_profit = 1250.75
    
    # Cars waiting for repair (sample data)
    cars_waiting_repair = [
        {
            'car_id': 1,
            'vehicle_make': 'Toyota',
            'vehicle_model': 'Corolla',
            'year': 2018,
            'date_bought': datetime.now() - timedelta(days=15)
        },
        {
            'car_id': 2,
            'vehicle_make': 'Honda',
            'vehicle_model': 'Civic',
            'year': 2019,
            'date_bought': datetime.now() - timedelta(days=10)
        }
    ]
    
    # Cars on stand the longest (sample data)
    cars_on_stand_longest = [
        {
            'car_id': 3,
            'vehicle_make': 'Ford',
            'vehicle_model': 'Focus',
            'year': 2017,
            'stand': {'stand_name': 'Main Lot'},
            'date_added_to_stand': datetime.now() - timedelta(days=30),
            'date_sold': None
        },
        {
            'car_id': 4,
            'vehicle_make': 'Chevrolet',
            'vehicle_model': 'Malibu',
            'year': 2018,
            'stand': {'stand_name': 'Front Display'},
            'date_added_to_stand': datetime.now() - timedelta(days=25),
            'date_sold': None
        }
    ]
    
    # Recent repairs (sample data)
    recent_repairs = [
        {
            'repair_id': 1,
            'car_id': 5,
            'car': {'vehicle_make': 'Nissan', 'vehicle_model': 'Altima'},
            'repair_type': 'Engine Repair',
            'provider': {'provider_name': 'Auto Fix Shop'},
            'end_date': datetime.now() - timedelta(days=3),
            'repair_cost': 850.00,
            'duration': 5
        },
        {
            'repair_id': 2,
            'car_id': 6,
            'car': {'vehicle_make': 'Hyundai', 'vehicle_model': 'Elantra'},
            'repair_type': 'Transmission Service',
            'provider': {'provider_name': 'Mechanics Inc.'},
            'end_date': datetime.now() - timedelta(days=5),
            'repair_cost': 1200.00,
            'duration': 7
        }
    ]
    
    return render_template('dashboard.html',
                         total_cars=total_cars,
                         cars_on_stand=cars_on_stand,
                         recent_sales=recent_sales,
                         avg_profit=avg_profit,
                         cars_waiting_repair=cars_waiting_repair,
                         cars_on_stand_longest=cars_on_stand_longest,
                         recent_repairs=recent_repairs,
                         now=datetime.now)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True) 