from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.stand import Stand
from app.models.car import Car
from datetime import datetime

stands_bp = Blueprint('stands', __name__)

@stands_bp.route('/')
@login_required
def index():
    stands = Stand.query.all()
    return render_template('stands/index.html', stands=stands)

@stands_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        stand_name = request.form.get('stand_name')
        location = request.form.get('location')
        capacity = request.form.get('capacity', type=int, default=10)
        additional_info = request.form.get('additional_info')
        
        # Validate required fields
        if not stand_name or not location:
            flash('Stand name and location are required.', 'danger')
            return render_template('stands/create.html')
        
        try:
            stand = Stand(
                stand_name=stand_name,
                location=location,
                capacity=capacity,
                additional_info=additional_info
            )
            db.session.add(stand)
            db.session.commit()
            flash('Stand created successfully!', 'success')
            return redirect(url_for('stands.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating stand: {str(e)}', 'danger')
    
    return render_template('stands/create.html')

@stands_bp.route('/<int:stand_id>')
@login_required
def view(stand_id):
    stand = Stand.query.get_or_404(stand_id)
    cars = Car.query.filter_by(stand_id=stand_id, date_sold=None).all()
    
    # Calculate performance metrics
    metrics = {
        'current_car_count': stand.current_car_count,
        'occupancy_rate': stand.occupancy_rate,
        'cars_sold_count': stand.cars_sold_count,
        'avg_days_on_stand': stand.avg_days_on_stand,
        'total_profit': stand.total_profit
    }
    
    # Add today's date for calculating days on stand
    today = datetime.now().date()
    
    return render_template('stands/view.html', stand=stand, cars=cars, metrics=metrics, today=today)

@stands_bp.route('/<int:stand_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(stand_id):
    stand = Stand.query.get_or_404(stand_id)
    
    if request.method == 'POST':
        stand_name = request.form.get('stand_name')
        location = request.form.get('location')
        capacity = request.form.get('capacity', type=int)
        additional_info = request.form.get('additional_info')
        
        # Validate required fields
        if not stand_name or not location:
            flash('Stand name and location are required.', 'danger')
            return render_template('stands/edit.html', stand=stand)
        
        try:
            stand.stand_name = stand_name
            stand.location = location
            stand.capacity = capacity
            stand.additional_info = additional_info
            stand.last_updated = datetime.now()
            
            db.session.commit()
            flash('Stand updated successfully!', 'success')
            return redirect(url_for('stands.view', stand_id=stand.stand_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating stand: {str(e)}', 'danger')
    
    return render_template('stands/edit.html', stand=stand)

@stands_bp.route('/<int:stand_id>/delete', methods=['POST'])
@login_required
def delete(stand_id):
    stand = Stand.query.get_or_404(stand_id)
    
    # Check if there are cars associated with this stand
    cars_on_stand = Car.query.filter_by(stand_id=stand_id).count()
    if cars_on_stand > 0:
        flash(f'Cannot delete stand as it has {cars_on_stand} cars associated with it.', 'danger')
        return redirect(url_for('stands.index'))
    
    try:
        db.session.delete(stand)
        db.session.commit()
        flash('Stand deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting stand: {str(e)}', 'danger')
    
    return redirect(url_for('stands.index')) 