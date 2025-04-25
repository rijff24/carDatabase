from flask import Blueprint, render_template, current_app, jsonify, request
from flask_login import login_required
from app.models.car import Car
from app.models.repair import Repair
from app.models.stand import Stand
from app.models.setting import Setting
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
    
    # Count cars ready for display and calculate average recon time
    cars_ready_for_display = Car.query.filter(
        Car.repair_status == 'Ready for Display',
        Car.date_sold == None
    ).all()
    
    ready_for_display_count = len(cars_ready_for_display)
    
    # Calculate average reconditioning time (days from purchase to 'Ready for Display' status)
    recon_times = []
    current_date = datetime.now().date()
    
    for car in cars_ready_for_display:
        if car.date_bought:
            # For cars with date_bought, calculate days to reach 'Ready for Display'
            # In a full implementation, you would use the actual date the status changed
            # Here we're using the current date as an approximation
            recon_time = (current_date - car.date_bought).days
            if recon_time >= 0:  # Ensure we don't include negative values
                recon_times.append(recon_time)
    
    avg_recon_time = sum(recon_times) / len(recon_times) if recon_times else None
    
    # Recent sales (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_sales = Car.query.filter(Car.date_sold >= thirty_days_ago).count()
    
    # Recent sales total value
    recent_sales_value = db.session.query(func.sum(Car.sale_price)).\
        filter(Car.date_sold >= thirty_days_ago).scalar() or 0
    
    # Recent profits and ROI calculations
    recently_sold_cars = Car.query.filter(Car.date_sold >= thirty_days_ago).all()
    
    # Calculate total profit for past 30 days
    total_profit = sum(car.profit for car in recently_sold_cars if car.profit is not None)
    
    # Calculate ROI for each car and then average
    roi_values = []
    for car in recently_sold_cars:
        if car.profit is not None and car.total_investment and float(car.total_investment) > 0:
            # ROI = (profit / total_investment) * 100
            roi = (float(car.profit) / float(car.total_investment)) * 100
            roi_values.append(roi)
    
    # Calculate average ROI
    avg_roi = sum(roi_values) / len(roi_values) if roi_values else 0
    
    # Average profit for recent sales
    recent_profits = [car.profit for car in recently_sold_cars if car.profit is not None]
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
    
    # Get threshold settings
    stand_aging_threshold_days = Setting.get_setting('stand_aging_threshold_days', 180, 'int')
    status_inactivity_threshold_days = Setting.get_setting('status_inactivity_threshold_days', 30, 'int')
    enable_status_warnings = Setting.get_setting('enable_status_warnings', True, 'bool')
    
    # Count vehicles exceeding aging threshold
    current_date = datetime.now().date()
    aging_threshold_date = current_date - timedelta(days=stand_aging_threshold_days)
    aging_warning_date = current_date - timedelta(days=stand_aging_threshold_days / 2)
    
    # Count vehicles exceeding stand aging threshold
    vehicles_exceeding_aging = Car.query.filter(
        Car.date_added_to_stand <= aging_threshold_date,
        Car.date_sold == None,
        Car.repair_status == 'On Display'
    ).count()
    
    # Count vehicles approaching stand aging threshold (over 50%)
    vehicles_approaching_aging = Car.query.filter(
        Car.date_added_to_stand <= aging_warning_date,
        Car.date_added_to_stand > aging_threshold_date,
        Car.date_sold == None,
        Car.repair_status == 'On Display'
    ).count()
    
    # Status inactivity counts - in a real implementation, this would use the actual last status change date
    # For this example, we'll use a placeholder approach
    vehicles_inactive_status = 0
    vehicles_approaching_inactive = 0
    
    if enable_status_warnings:
        # In a real implementation, you would have a last_status_change field to check against
        # This is a placeholder that assumes all unsold cars have relevant status data
        all_unsold_cars = Car.query.filter(Car.date_sold == None).all()
        
        status_inactive_threshold_date = current_date - timedelta(days=status_inactivity_threshold_days)
        status_warning_threshold_date = current_date - timedelta(days=status_inactivity_threshold_days / 2)
        
        # Count vehicles with inactive status (exceeding threshold)
        # In a real implementation, replace this with a check against last_status_change
        for car in all_unsold_cars:
            # Placeholder logic - in a real app you would check the actual last status change date
            # For example: days_since_change = (current_date - car.last_status_change).days
            
            # This example checks if repair_status is "Waiting for Repairs" and days since purchase exceeds threshold
            if car.repair_status == 'Waiting for Repairs' and car.date_bought:
                days_since_bought = (current_date - car.date_bought).days
                
                if days_since_bought > status_inactivity_threshold_days:
                    vehicles_inactive_status += 1
                elif days_since_bought > status_inactivity_threshold_days / 2:
                    vehicles_approaching_inactive += 1
    
    # Get stand statistics (cars per stand and average age)
    stands_with_stats = []
    all_stands = Stand.query.order_by(Stand.stand_name).all()
    
    for stand in all_stands:
        # Get unsold cars on this stand
        cars_on_this_stand = Car.query.filter(
            Car.stand_id == stand.stand_id,
            Car.date_sold == None
        ).all()
        
        total_cars_on_stand = len(cars_on_this_stand)
        
        # Calculate average age (days on stand)
        total_age = 0
        for car in cars_on_this_stand:
            if car.date_added_to_stand:
                days_on_stand = (current_date - car.date_added_to_stand).days
                total_age += days_on_stand
        
        avg_age = round(total_age / total_cars_on_stand if total_cars_on_stand > 0 else 0)
        
        # Add to the list if there are cars on the stand
        if total_cars_on_stand > 0:
            stands_with_stats.append({
                'stand_id': stand.stand_id,
                'stand_name': stand.stand_name,
                'total_cars': total_cars_on_stand,
                'avg_age': avg_age
            })
    
    # Sort stands by those with highest average age first
    stands_with_stats.sort(key=lambda x: x['avg_age'], reverse=True)
    
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
        now=datetime.now(),
        # New variables for aging and status warnings
        stand_aging_threshold_days=stand_aging_threshold_days,
        status_inactivity_threshold_days=status_inactivity_threshold_days,
        enable_status_warnings=enable_status_warnings,
        vehicles_exceeding_aging=vehicles_exceeding_aging,
        vehicles_approaching_aging=vehicles_approaching_aging,
        vehicles_inactive_status=vehicles_inactive_status,
        vehicles_approaching_inactive=vehicles_approaching_inactive,
        # Stand statistics
        stands_with_stats=stands_with_stats,
        # Profitability metrics
        total_profit=total_profit,
        avg_roi=avg_roi,
        # Ready for display cars
        ready_for_display_count=ready_for_display_count,
        avg_recon_time=avg_recon_time
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