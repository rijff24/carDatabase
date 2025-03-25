from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.car import Car
from app.models.stand import Stand
from app.models.dealer import Dealer
from app.models.repair_provider import RepairProvider
from app.utils.forms import CarForm, CarSaleForm
from app.utils.validators import validate_params, validate_form
from app.utils.helpers import safe_get_or_404
from app import db
from datetime import datetime

cars_bp = Blueprint('cars', __name__)

VALID_STATUSES = ['All', 'Purchased', 'Waiting for Repairs', 'In Repair', 'On Display', 'Waiting for Payment', 'Sold']
VALID_SORT_FIELDS = ['date_bought', 'vehicle_name', 'vehicle_make', 'vehicle_model', 'year', 'purchase_price', 'repair_status']
VALID_SORT_DIRS = ['asc', 'desc']

@cars_bp.route('/')
@login_required
@validate_params(
    status=(str, False, 'All', lambda x: x in VALID_STATUSES),
    search=(str, False, ''),
    sort_by=(str, False, 'date_bought', lambda x: x in VALID_SORT_FIELDS),
    sort_dir=(str, False, 'desc', lambda x: x in VALID_SORT_DIRS)
)
def index():
    """List all cars"""
    # Get validated parameters
    params = request.validated_params
    status = params['status']
    search = params['search']
    sort_by = params['sort_by']
    sort_dir = params['sort_dir']
    
    # Base query
    query = Car.query
    
    # Apply search filter
    if search:
        query = query.filter(
            (Car.vehicle_name.ilike(f'%{search}%')) |
            (Car.vehicle_make.ilike(f'%{search}%')) |
            (Car.vehicle_model.ilike(f'%{search}%')) |
            (Car.colour.ilike(f'%{search}%')) |
            (Car.licence_number.ilike(f'%{search}%')) |
            (Car.registration_number.ilike(f'%{search}%'))
        )
    
    # Apply status filter
    if status != 'All':
        query = query.filter(Car.repair_status == status)
    
    # Apply sorting
    if sort_dir == 'desc':
        query = query.order_by(getattr(Car, sort_by).desc())
    else:
        query = query.order_by(getattr(Car, sort_by))
    
    cars = query.all()
    
    return render_template(
        'cars/index.html',
        cars=cars,
        current_status=status,
        current_sort=sort_by,
        current_sort_dir=sort_dir
    )

@cars_bp.route('/create', methods=['GET', 'POST'])
@login_required
@validate_form(CarForm)
def create():
    """Create a new car"""
    form = request.validated_form if request.method == 'POST' else CarForm()
    
    # Populate the source field with dealers
    dealers = Dealer.query.all()
    form.source.choices = [(d.dealer_id, d.dealer_name) for d in dealers]
    
    if request.method == 'POST':
        # Set the current location based on repair status
        current_location = form.current_location.data
        if form.repair_status.data == 'Purchased':
            current_location = "Dealer's Lot"
        elif form.repair_status.data == 'Waiting for Repairs':
            current_location = 'Base (Awaiting Repairs)'
        elif form.repair_status.data == 'In Repair':
            provider = RepairProvider.query.first()
            current_location = f"Repair: {provider.location if provider else 'Unknown'}"
        elif form.repair_status.data == 'On Display':
            # Get all stands and use the first one found
            stand = Stand.query.first()
            current_location = f"On Display at {stand.stand_name if stand else 'Stand'}"
        
        # Create new car
        dealer = Dealer.query.get(form.source.data)
        car = Car(
            vehicle_name=form.vehicle_name.data,
            vehicle_make=form.vehicle_make.data,
            vehicle_model=form.vehicle_model.data,
            year=form.year.data,
            colour=form.colour.data,
            date_bought=form.date_bought.data,
            purchase_price=form.purchase_price.data,
            repair_status=form.repair_status.data,
            current_location=current_location,
            licence_number=form.licence_number.data,
            registration_number=form.registration_number.data,
            mileage=form.mileage.data,
            fuel_type=form.fuel_type.data,
            engine_size=form.engine_size.data,
            transmission=form.transmission.data,
            body_style=form.body_style.data,
            additional_info=form.additional_info.data,
            source=dealer.dealer_name if dealer else 'Unknown Dealer',
            dealer_id=form.source.data
        )
        
        db.session.add(car)
        db.session.commit()
        
        flash('Car added successfully', 'success')
        return redirect(url_for('cars.view', car_id=car.car_id))
    
    return render_template('cars/create.html', form=form)

@cars_bp.route('/<int:car_id>')
@login_required
@validate_params(car_id=(int, True))
def view(car_id):
    """View car details"""
    car = safe_get_or_404(Car, car_id, f"Car with ID {car_id} not found")
    sale_form = None
    
    # Get all stands for the dropdown
    stands = Stand.query.all()
    
    # If car is on display but not sold, prepare sale form
    if car.repair_status == 'On Display' and not car.date_sold:
        sale_form = CarSaleForm(car_id=car.car_id)
    
    return render_template('cars/view.html', car=car, sale_form=sale_form, stands=stands)

@cars_bp.route('/<int:car_id>/edit', methods=['GET', 'POST'])
@login_required
@validate_params(car_id=(int, True))
def edit(car_id):
    """Edit car details"""
    car = safe_get_or_404(Car, car_id, f"Car with ID {car_id} not found")
    
    # Handle form submission directly without the decorator
    if request.method == 'POST':
        form = CarForm(formdata=request.form, obj=car)
        
        # Populate the source field with dealers
        dealers = Dealer.query.all()
        form.source.choices = [(d.dealer_id, d.dealer_name) for d in dealers]
        
        if form.validate_on_submit():
            # First populate the car object with form data
            form.populate_obj(car)
            
            # Set fields that are not directly mapped
            dealer = safe_get_or_404(Dealer, form.source.data, f"Dealer with ID {form.source.data} not found")
            car.source = dealer.dealer_name
            car.dealer_id = form.source.data
            
            # Set the current location based on repair status - do this AFTER populate_obj
            if car.repair_status == 'Purchased':
                car.current_location = "Dealer's Lot"
            elif car.repair_status == 'Waiting for Repairs':
                car.current_location = 'Base (Awaiting Repairs)'
            elif car.repair_status == 'In Repair':
                provider = RepairProvider.query.first()
                car.current_location = f"Repair: {provider.location if provider else 'Unknown'}"
            elif car.repair_status == 'On Display':
                # If car is already on a stand, keep it there
                if car.stand_id:
                    stand = Stand.query.get(car.stand_id)
                    car.current_location = f"Stand: {stand.stand_name if stand else 'Stand'}"
                else:
                    # Get all stands and use the first one found
                    stand = Stand.query.first()
                    car.current_location = f"On Display at {stand.stand_name if stand else 'Stand'}"
            
            db.session.commit()
            
            flash('Car updated successfully', 'success')
            return redirect(url_for('cars.view', car_id=car.car_id))
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        # GET request - create and populate form
        form = CarForm(obj=car)
        # Populate the source field with dealers
        dealers = Dealer.query.all()
        form.source.choices = [(d.dealer_id, d.dealer_name) for d in dealers]
        
        # Set the current dealer as selected
        if car.dealer_id:
            form.source.data = car.dealer_id
    
    return render_template('cars/edit.html', form=form, car=car)

@cars_bp.route('/<int:car_id>/delete', methods=['POST'])
@login_required
@validate_params(car_id=(int, True))
def delete(car_id):
    """Delete a car"""
    car = safe_get_or_404(Car, car_id, f"Car with ID {car_id} not found")
    
    db.session.delete(car)
    db.session.commit()
    
    flash('Car deleted successfully', 'success')
    return redirect(url_for('cars.index'))

@cars_bp.route('/<int:car_id>/move-to-stand', methods=['POST'])
@login_required
@validate_params(
    car_id=(int, True),
    stand_id=(int, False, None)
)
def move_to_stand(car_id):
    """Move a car to a stand"""
    car = safe_get_or_404(Car, car_id, f"Car with ID {car_id} not found")
    params = request.validated_params
    stand_id = params.get('stand_id')
    
    # Check if a stand_id is provided either in the form data or URL parameter
    if not stand_id and 'stand_id' in request.form:
        try:
            stand_id = int(request.form.get('stand_id'))
        except (ValueError, TypeError):
            flash('Invalid stand ID format', 'danger')
            return redirect(url_for('cars.view', car_id=car_id))
    
    if not stand_id:
        # Try to get the first stand if none selected
        first_stand = Stand.query.first()
        if first_stand:
            stand_id = first_stand.stand_id
        else:
            flash('Please select a stand. If no stands exist, please create one first.', 'danger')
            return redirect(url_for('cars.view', car_id=car_id))
    
    stand = safe_get_or_404(Stand, stand_id, f"Stand with ID {stand_id} not found")
    
    car.stand_id = stand_id
    car.date_added_to_stand = datetime.now().date()
    car.repair_status = 'On Display'
    car.current_location = f"Stand: {stand.stand_name}"
    
    db.session.commit()
    
    flash(f'Car moved to {stand.stand_name} stand', 'success')
    return redirect(url_for('cars.view', car_id=car_id))

@cars_bp.route('/<int:car_id>/record-sale', methods=['POST'])
@login_required
@validate_params(car_id=(int, True))
def record_sale(car_id):
    """Record a car sale"""
    car = safe_get_or_404(Car, car_id, f"Car with ID {car_id} not found")
    
    form = CarSaleForm(formdata=request.form)
    
    if form.validate_on_submit():
        car.date_sold = form.date_sold.data
        car.sale_price = form.sale_price.data
        # Keep the existing dealer_id that was set when the car was added
        car.repair_status = 'Sold'
        
        # Calculate final costs
        car.final_cost_price = car.purchase_price + car.total_repair_cost + car.refuel_cost
        
        db.session.commit()
        
        flash('Sale recorded successfully', 'success')
    else:
        # Show what validation errors occurred
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")
        flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    
    return redirect(url_for('cars.view', car_id=car_id)) 