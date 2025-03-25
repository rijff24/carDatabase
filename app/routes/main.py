from flask import Blueprint, render_template, current_app, jsonify, request
from flask_login import login_required
from app.models.car import Car
from app.models.repair import Repair
from app.models.stand import Stand
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta
from app.utils.errors import (
    ValidationError, DatabaseError, AuthenticationError,
    AuthorizationError, NotFoundError
)
from app.utils.validators import validate_params, validate_json, validate_email, validate_price

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page route"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page with key metrics"""
    # Current inventory
    total_cars = Car.query.count()
    unsold_cars = Car.query.filter(Car.date_sold == None).count()
    cars_in_repair = Car.query.filter(Car.repair_status == 'In Repair').count()
    cars_on_stand = Car.query.filter(Car.repair_status == 'On Display').count()
    
    # Recent sales (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_sales = Car.query.filter(Car.date_sold >= thirty_days_ago).count()
    
    # Recent sales total value
    recent_sales_value = db.session.query(func.sum(Car.sale_price)).\
        filter(Car.date_sold >= thirty_days_ago).scalar() or 0
    
    # Average profit for recent sales
    recent_profits = [car.profit for car in 
                     Car.query.filter(Car.date_sold >= thirty_days_ago).all() 
                     if car.profit is not None]
    avg_profit = sum(recent_profits) / len(recent_profits) if recent_profits else 0
    
    # Top 5 cars waiting longest for repair
    cars_waiting_repair = Car.query.filter(
        Car.repair_status == 'Waiting for Repairs'
    ).order_by(Car.date_bought).limit(5).all()
    
    # Top 5 cars on stand the longest
    cars_on_stand_longest = Car.query.filter(
        Car.repair_status == 'On Display', 
        Car.date_sold == None
    ).order_by(Car.date_added_to_stand).limit(5).all()
    
    # Recent activity - last 10 repairs completed
    recent_repairs = Repair.query.filter(
        Repair.end_date != None
    ).order_by(Repair.end_date.desc()).limit(10).all()
    
    return render_template(
        'dashboard.html',
        total_cars=total_cars,
        unsold_cars=unsold_cars,
        cars_in_repair=cars_in_repair,
        cars_on_stand=cars_on_stand,
        recent_sales=recent_sales,
        recent_sales_value=recent_sales_value,
        avg_profit=avg_profit,
        cars_waiting_repair=cars_waiting_repair,
        cars_on_stand_longest=cars_on_stand_longest,
        recent_repairs=recent_repairs,
        now=datetime.now()
    )

# Test routes for error handling
@main_bp.route('/test/validation-error')
def test_validation_error():
    """Test route that raises a validation error"""
    raise ValidationError("Invalid input provided", field="price")

@main_bp.route('/test/database-error')
def test_database_error():
    """Test route that raises a database error"""
    raise DatabaseError("Failed to connect to database")

@main_bp.route('/test/authentication-error')
def test_authentication_error():
    """Test route that raises an authentication error"""
    raise AuthenticationError("Invalid credentials")

@main_bp.route('/test/authorization-error')
def test_authorization_error():
    """Test route that raises an authorization error"""
    raise AuthorizationError("Insufficient permissions")

@main_bp.route('/test/not-found-error')
def test_not_found_error():
    """Test route that raises a not found error"""
    raise NotFoundError("Resource not found")

@main_bp.route('/test/unexpected-error')
def test_unexpected_error():
    """Test route that raises an unexpected error"""
    raise ValueError("Unexpected error occurred")

# Test routes for parameter validation
@main_bp.route('/test/validate-params')
@validate_params(
    year=(int, True, None),
    month=(int, False, None),
    period=(str, False, 'monthly'),
    email=(str, False, None)
)
def test_validate_params():
    """Test route that demonstrates parameter validation"""
    return jsonify({
        'message': 'Parameters validated successfully',
        'params': request.validated_params
    })

@main_bp.route('/test/validate-json', methods=['POST'])
@validate_json({
    'name': (str, True),
    'price': (float, True),
    'email': (str, False),
    'is_active': (bool, False)
})
def test_validate_json():
    """Test route that demonstrates JSON validation"""
    return jsonify({
        'message': 'JSON validated successfully',
        'data': request.validated_data
    })

@main_bp.route('/test/validate-custom')
@validate_params(
    email=validate_email,
    price=validate_price
)
def test_validate_custom():
    """Test route that demonstrates custom validation functions"""
    return jsonify({
        'message': 'Custom validation successful',
        'params': request.validated_params
    }) 