from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.stand import Stand
from app.models.car import Car
from app.utils.forms import StandForm
from app.utils.validators import validate_params, validate_form
from app.utils.helpers import safe_get_or_404
from datetime import datetime

stands_bp = Blueprint('stands', __name__)

VALID_SORT_FIELDS = ['stand_name', 'location', 'capacity', 'current_car_count', 'cars_sold_count']
VALID_SORT_DIRS = ['asc', 'desc']

@stands_bp.route('/')
@login_required
@validate_params(
    search=(str, False, None),
    min_capacity=(int, False, None, lambda x: x >= 0),
    max_capacity=(int, False, None, lambda x: x >= 0),
    sort_by=(str, False, 'stand_name', lambda x: x in VALID_SORT_FIELDS),
    sort_dir=(str, False, 'asc', lambda x: x in VALID_SORT_DIRS)
)
def index():
    """List all stands with filtering options"""
    # Get validated parameters
    params = request.validated_params
    search = params.get('search')
    min_capacity = params.get('min_capacity') 
    max_capacity = params.get('max_capacity')
    sort_by = params.get('sort_by', 'stand_name')
    sort_dir = params.get('sort_dir', 'asc')
    
    # Start with base query
    query = Stand.query
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Stand.stand_name.ilike(search_term) | 
            Stand.location.ilike(search_term)
        )
    
    if min_capacity is not None:
        query = query.filter(Stand.capacity >= min_capacity)
        
    if max_capacity is not None:
        query = query.filter(Stand.capacity <= max_capacity)
    
    # Apply sorting for model attributes
    if sort_by in ['stand_name', 'location', 'capacity']:
        if sort_dir == 'desc':
            query = query.order_by(getattr(Stand, sort_by).desc())
        else:
            query = query.order_by(getattr(Stand, sort_by))
    
    stands = query.all()
    
    # For computed properties, sort after query
    if sort_by in ['current_car_count', 'cars_sold_count']:
        stands = sorted(stands, 
                       key=lambda x: getattr(x, sort_by),
                       reverse=(sort_dir == 'desc'))
    
    return render_template(
        'stands/index.html', 
        stands=stands,
        current_search=search,
        current_min_capacity=min_capacity,
        current_max_capacity=max_capacity,
        current_sort=sort_by,
        current_sort_dir=sort_dir
    )

@stands_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        form = StandForm(formdata=request.form)
        
        if form.validate_on_submit():
            try:
                stand = Stand(
                    stand_name=form.stand_name.data,
                    location=form.location.data,
                    capacity=form.capacity.data,
                    additional_info=form.additional_info.data
                )
                db.session.add(stand)
                db.session.commit()
                flash('Stand created successfully!', 'success')
                return redirect(url_for('stands.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating stand: {str(e)}', 'danger')
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        form = StandForm()
    
    return render_template('stands/create.html', form=form)

@stands_bp.route('/<int:stand_id>')
@login_required
@validate_params(stand_id=(int, True))
def view(stand_id):
    stand = safe_get_or_404(Stand, stand_id, f"Stand with ID {stand_id} not found")
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
@validate_params(stand_id=(int, True))
def edit(stand_id):
    stand = safe_get_or_404(Stand, stand_id, f"Stand with ID {stand_id} not found")
    
    if request.method == 'POST':
        form = StandForm(formdata=request.form, obj=stand)
        
        if form.validate_on_submit():
            try:
                form.populate_obj(stand)
                stand.last_updated = datetime.now()
                
                db.session.commit()
                flash('Stand updated successfully!', 'success')
                return redirect(url_for('stands.view', stand_id=stand.stand_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating stand: {str(e)}', 'danger')
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        form = StandForm(obj=stand)
    
    return render_template('stands/edit.html', form=form, stand=stand)

@stands_bp.route('/<int:stand_id>/delete', methods=['POST'])
@login_required
@validate_params(stand_id=(int, True))
def delete(stand_id):
    stand = safe_get_or_404(Stand, stand_id, f"Stand with ID {stand_id} not found")
    
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