from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.dealer import Dealer
from app.models.car import Car
from app.utils.forms import DealerForm
from app.utils.validators import validate_params, validate_form
from app.utils.helpers import safe_get_or_404
from datetime import datetime

dealers_bp = Blueprint('dealers', __name__)

VALID_SORT_FIELDS = ['dealer_name', 'date_joined', 'cars_supplied', 'total_revenue']
VALID_SORT_DIRS = ['asc', 'desc']

@dealers_bp.route('/')
@login_required
@validate_params(
    search=(str, False, None),
    min_cars=(int, False, None, lambda x: x >= 0),
    min_revenue=(float, False, None, lambda x: x >= 0),
    sort_by=(str, False, 'dealer_name', lambda x: x in VALID_SORT_FIELDS),
    sort_dir=(str, False, 'asc', lambda x: x in VALID_SORT_DIRS)
)
def index():
    # Get validated parameters
    params = request.validated_params
    search = params.get('search')
    min_cars = params.get('min_cars')
    min_revenue = params.get('min_revenue')
    sort_by = params.get('sort_by', 'dealer_name')
    sort_dir = params.get('sort_dir', 'asc')
    
    # Get all dealers
    dealers = Dealer.query.all()
    
    # Update metrics
    for dealer in dealers:
        dealer.update_performance_metrics()
    db.session.commit()
    
    # Apply search filter if provided
    if search:
        search_term = search.lower()
        dealers = [d for d in dealers if 
                  search_term in d.dealer_name.lower() or
                  (d.contact_info and search_term in d.contact_info.lower()) or
                  (d.address and search_term in d.address.lower())]
    
    # Apply filters
    if min_cars is not None:
        dealers = [d for d in dealers if d.cars_supplied >= min_cars]
        
    if min_revenue is not None:
        dealers = [d for d in dealers if d.total_revenue >= min_revenue]
    
    # Apply sorting
    reverse = sort_dir == 'desc'
    dealers = sorted(dealers, key=lambda x: getattr(x, sort_by) or 0, reverse=reverse)
    
    return render_template(
        'dealers/index.html', 
        dealers=dealers,
        current_search=search,
        current_min_cars=min_cars,
        current_min_revenue=min_revenue,
        current_sort=sort_by,
        current_sort_dir=sort_dir
    )

@dealers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        form = DealerForm(formdata=request.form)
        
        if form.validate_on_submit():
            # Check if a dealer with the same name already exists
            existing_dealer = Dealer.query.filter_by(dealer_name=form.dealer_name.data).first()
            if existing_dealer:
                flash(f'Dealer with name "{form.dealer_name.data}" already exists', 'danger')
                return render_template('dealers/create.html', form=form)
            
            dealer = Dealer(
                dealer_name=form.dealer_name.data,
                contact_info=form.contact_info.data,
                address=form.address.data,
                date_joined=datetime.utcnow()
            )
            
            try:
                db.session.add(dealer)
                db.session.commit()
                flash('Dealer added successfully', 'success')
                return redirect(url_for('dealers.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding dealer: {str(e)}', 'danger')
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        form = DealerForm()
    
    return render_template('dealers/create.html', form=form)

@dealers_bp.route('/<int:dealer_id>')
@login_required
@validate_params(dealer_id=(int, True))
def view(dealer_id):
    dealer = safe_get_or_404(Dealer, dealer_id, f"Dealer with ID {dealer_id} not found")
    dealer.update_performance_metrics()
    db.session.commit()
    
    # Get dealer's cars
    cars = Car.query.filter_by(dealer_id=dealer_id).all()
    
    # Get sales history (only sold cars)
    sales_history = Car.query.filter_by(
        dealer_id=dealer_id, 
        repair_status='Sold'
    ).order_by(Car.date_sold.desc()).all()
    
    return render_template('dealers/view.html', 
                          dealer=dealer, 
                          cars=cars, 
                          sales_history=sales_history)

@dealers_bp.route('/<int:dealer_id>/edit', methods=['GET', 'POST'])
@login_required
@validate_params(dealer_id=(int, True))
def edit(dealer_id):
    dealer = safe_get_or_404(Dealer, dealer_id, f"Dealer with ID {dealer_id} not found")
    
    if request.method == 'POST':
        form = DealerForm(formdata=request.form, obj=dealer)
        
        if form.validate_on_submit():
            # Check if another dealer with the same name exists
            if form.dealer_name.data != dealer.dealer_name:
                existing_dealer = Dealer.query.filter_by(dealer_name=form.dealer_name.data).first()
                if existing_dealer:
                    flash(f'Dealer with name "{form.dealer_name.data}" already exists', 'danger')
                    return render_template('dealers/edit.html', form=form, dealer=dealer)
            
            dealer.dealer_name = form.dealer_name.data
            dealer.contact_info = form.contact_info.data
            dealer.address = form.address.data
            
            try:
                db.session.commit()
                flash('Dealer updated successfully', 'success')
                return redirect(url_for('dealers.view', dealer_id=dealer.dealer_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating dealer: {str(e)}', 'danger')
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        form = DealerForm(obj=dealer)
    
    return render_template('dealers/edit.html', form=form, dealer=dealer)

@dealers_bp.route('/<int:dealer_id>/delete', methods=['POST'])
@login_required
@validate_params(dealer_id=(int, True))
def delete(dealer_id):
    dealer = safe_get_or_404(Dealer, dealer_id, f"Dealer with ID {dealer_id} not found")
    
    # Check if dealer has cars associated
    car_count = Car.query.filter_by(dealer_id=dealer_id).count()
    if car_count > 0:
        flash(f'Cannot delete dealer with {car_count} associated cars', 'danger')
        return redirect(url_for('dealers.view', dealer_id=dealer_id))
    
    try:
        db.session.delete(dealer)
        db.session.commit()
        flash('Dealer deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting dealer: {str(e)}', 'danger')
    
    return redirect(url_for('dealers.index'))

@dealers_bp.route('/<int:dealer_id>/performance')
@login_required
@validate_params(dealer_id=(int, True))
def performance(dealer_id):
    dealer = safe_get_or_404(Dealer, dealer_id, f"Dealer with ID {dealer_id} not found")
    dealer.update_performance_metrics()
    db.session.commit()
    
    # Get sales by month (last 12 months)
    sales_by_month = db.session.query(
        db.func.strftime('%Y-%m', Car.date_sold).label('month'),
        db.func.count().label('count'),
        db.func.sum(Car.sale_price).label('revenue')
    ).filter(
        Car.dealer_id == dealer_id,
        Car.repair_status == 'Sold'
    ).group_by('month').order_by('month').all()
    
    performance_data = {
        'labels': [row.month for row in sales_by_month],
        'sales': [row.count for row in sales_by_month],
        'revenue': [float(row.revenue or 0) for row in sales_by_month]
    }
    
    return jsonify(performance_data) 