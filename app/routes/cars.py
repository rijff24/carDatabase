from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app.models.car import Car, VehicleMake, VehicleModel, VehicleYear, VehicleColor
from app.models.stand import Stand
from app.models.dealer import Dealer
from app.models.repair_provider import RepairProvider
from app.models.sale import Sale
from app.utils.forms import CarForm, CarSaleForm, MoveToStandForm, StandForm
from app.utils.validators import validate_params, validate_form
from app.utils.helpers import safe_get_or_404
from app import db
from datetime import datetime
from sqlalchemy import extract
from app.models.setting import Setting

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
def create():
    """Add a new car route"""
    if request.method == 'POST':
        try:
            # Get form data
            data = request.form
            
            # Get or create make
            make_name = data.get('vehicle_make', '').strip()
            if not make_name:
                flash('Make is required', 'danger')
                return redirect(url_for('cars.create'))
                
            make = VehicleMake.get_or_create(make_name)
            if not make:
                flash('Invalid make name', 'danger')
                return redirect(url_for('cars.create'))
            
            # Get or create model with relationship to make
            model_name = data.get('vehicle_model', '').strip()
            if not model_name:
                flash('Model is required', 'danger')
                return redirect(url_for('cars.create'))
                
            model = VehicleModel.get_or_create(model_name, make_id=make.id)
            if not model:
                flash('Invalid model name', 'danger')
                return redirect(url_for('cars.create'))
            
            # Get dealer info
            dealer_id = data.get('source')
            if not dealer_id:
                flash('Source (Dealer) is required', 'danger')
                return redirect(url_for('cars.create'))
                
            dealer = Dealer.query.get(dealer_id)
            if not dealer:
                flash('Invalid dealer selected', 'danger')
                return redirect(url_for('cars.create'))
            
            # Create new car
            car = Car(
                vehicle_name=data.get('vehicle_name', '').strip(),
                vehicle_make=make.name,
                vehicle_model=model.name,
                year=int(data.get('year')),
                colour=data.get('colour', '').strip(),
                dekra_condition=data.get('dekra_condition'),
                licence_number=data.get('licence_number', '').strip(),
                registration_number=data.get('registration_number', '').strip(),
                purchase_price=float(data.get('purchase_price')),
                source=dealer.dealer_name,
                dealer_id=dealer.dealer_id,
                date_bought=datetime.now().date(),
                repair_status=data.get('repair_status')
            )
            
            # Set the current location based on repair status
            if car.repair_status == 'Purchased':
                car.current_location = "Dealer's Lot"
            elif car.repair_status == 'Waiting for Repairs':
                car.current_location = 'Base (Awaiting Repairs)'
            elif car.repair_status == 'In Repair':
                provider = RepairProvider.query.first()
                car.current_location = f"Repair: {provider.location if provider else 'Unknown'}"
            elif car.repair_status == 'On Display':
                stand = Stand.query.first()
                car.current_location = f"On Display at {stand.stand_name if stand else 'Stand'}"
            else:
                car.current_location = data.get('current_location', '').strip()
            
            db.session.add(car)
            db.session.commit()
            
            flash(f'Car {car.full_name} added successfully', 'success')
            return redirect(url_for('cars.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding car: {str(e)}', 'danger')
            return redirect(url_for('cars.create'))
    
    # GET request - fetch dealers for dropdown
    dealers = Dealer.query.all()
    return render_template('cars/create.html', dealers=dealers)

@cars_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_car():
    """Add a new car"""
    if request.method == 'POST':
        try:
            # Get form data
            data = request.form
            
            # Handle make (either existing or new)
            make_id = data.get('make_id')
            new_make = data.get('new_make', '').strip()
            if new_make:
                make = VehicleMake.get_or_create(new_make)
                if not make:
                    flash('Invalid make name', 'danger')
                    return redirect(url_for('cars.add_car'))
                make_id = make.id
            elif not make_id:
                flash('Make is required', 'danger')
                return redirect(url_for('cars.add_car'))
            
            # Handle model (either existing or new)
            model_id = data.get('model_id')
            new_model = data.get('new_model', '').strip()
            if new_model:
                model = VehicleModel.get_or_create(new_model, make_id=make_id)
                if not model:
                    flash('Invalid model name', 'danger')
                    return redirect(url_for('cars.add_car'))
                model_id = model.id
            elif not model_id:
                flash('Model is required', 'danger')
                return redirect(url_for('cars.add_car'))
            
            # Create new car
            car = Car(
                vin=data['vin'],
                year=int(data['year']),
                vehicle_make_id=make_id,
                vehicle_model_id=model_id,
                color=data.get('color'),
                mileage=int(data['mileage']) if data.get('mileage') else None,
                price=float(data['price']) if data.get('price') else None,
                status=data.get('status', 'available'),
                notes=data.get('notes')
            )
            
            db.session.add(car)
            db.session.commit()
            
            flash(f'Car {car.full_name} added successfully', 'success')
            return redirect(url_for('cars.list_cars'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding car: {str(e)}', 'danger')
            return redirect(url_for('cars.add_car'))
    
    # GET request - show form
    makes = VehicleMake.query.order_by(VehicleMake.name).all()
    return render_template('cars/form.html', makes=makes, current_year=datetime.now().year)

@cars_bp.route('/edit/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    """Edit an existing car"""
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            data = request.form
            
            # Handle make (either existing or new)
            make_id = data.get('make_id')
            new_make = data.get('new_make', '').strip()
            if new_make:
                make = VehicleMake.get_or_create(new_make)
                if not make:
                    flash('Invalid make name', 'danger')
                    return redirect(url_for('cars.edit_car', car_id=car.id))
                make_id = make.id
            elif not make_id:
                flash('Make is required', 'danger')
                return redirect(url_for('cars.edit_car', car_id=car.id))
            
            # Handle model (either existing or new)
            model_id = data.get('model_id')
            new_model = data.get('new_model', '').strip()
            if new_model:
                model = VehicleModel.get_or_create(new_model, make_id=make_id)
                if not model:
                    flash('Invalid model name', 'danger')
                    return redirect(url_for('cars.edit_car', car_id=car.id))
                model_id = model.id
            elif not model_id:
                flash('Model is required', 'danger')
                return redirect(url_for('cars.edit_car', car_id=car.id))
            
            # Update car
            car.vin = data['vin']
            car.year = int(data['year'])
            car.vehicle_make_id = make_id
            car.vehicle_model_id = model_id
            car.color = data.get('color')
            car.mileage = int(data['mileage']) if data.get('mileage') else None
            car.price = float(data['price']) if data.get('price') else None
            car.status = data.get('status', 'available')
            car.notes = data.get('notes')
            
            db.session.commit()
            
            flash(f'Car {car.full_name} updated successfully', 'success')
            return redirect(url_for('cars.list_cars'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating car: {str(e)}', 'danger')
            return redirect(url_for('cars.edit_car', car_id=car.id))
    
    # GET request - show form
    makes = VehicleMake.query.order_by(VehicleMake.name).all()
    return render_template('cars/form.html', car=car, makes=makes, current_year=datetime.now().year)

@cars_bp.route('/<int:car_id>')
@login_required
@validate_params(car_id=(int, True))
def view(car_id):
    """View car details"""
    car = safe_get_or_404(Car, car_id, f"Car with ID {car_id} not found")
    sale_form = None
    move_to_stand_form = None
    
    # Get all stands for the dropdown
    stands = Stand.query.all()
    
    # If car is waiting for repairs or in repair, create move to stand form
    if car.repair_status in ['Waiting for Repairs', 'In Repair']:
        move_to_stand_form = MoveToStandForm()
        # Populate stand choices
        move_to_stand_form.stand_id.choices = [(s.stand_id, s.stand_name) for s in stands]
    
    # If car is on display but not sold, prepare sale form
    if car.repair_status == 'On Display' and not car.date_sold:
        sale_form = CarSaleForm(car_id=car.car_id)
    
    # Create stand form for the modal
    stand_form = StandForm()
    
    return render_template('cars/view.html', 
                          car=car, 
                          sale_form=sale_form, 
                          move_to_stand_form=move_to_stand_form, 
                          stands=stands,
                          stand_form=stand_form,
                          settings=Setting)

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
            # Handle the make field - get or create
            make_name = form.vehicle_make.data
            make = VehicleMake.get_or_create(make_name)
            
            # Handle the model field - get or create
            model_name = form.vehicle_model.data
            VehicleModel.get_or_create(model_name, make_id=make.id)
            
            # First populate the car object with form data
            form.populate_obj(car)
            
            # Sanitize the make field
            car.vehicle_make = VehicleMake.sanitize_name(car.vehicle_make)
            
            # Sanitize the model field
            car.vehicle_model = VehicleModel.sanitize_name(car.vehicle_model)
            
            # Sanitize the color field
            if form.colour.data:
                form.colour.data = VehicleColor.sanitize_name(form.colour.data)
            
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
    
    # Check if car has related sales
    if car.sale:
        # Delete the related sale first
        db.session.delete(car.sale)
        db.session.flush()  # Apply the deletion before moving on
    
    # Now delete the car
    db.session.delete(car)
    db.session.commit()
    
    flash('Car deleted successfully', 'success')
    return redirect(url_for('cars.index'))

@cars_bp.route('/<int:car_id>/move-to-stand', methods=['POST'])
@login_required
@validate_params(car_id=(int, True))
def move_to_stand(car_id):
    """Move a car to a stand or change stands"""
    car = safe_get_or_404(Car, car_id, f"Car with ID {car_id} not found")
    
    # Get stand_id from form
    stand_id = request.form.get('stand_id')
    if not stand_id:
        flash('Please select a stand', 'danger')
        return redirect(url_for('cars.view', car_id=car_id))
    
    # Validate if it's a valid stand_id
    try:
        stand_id = int(stand_id)
    except ValueError:
        flash('Invalid stand selection', 'danger')
        return redirect(url_for('cars.view', car_id=car_id))
    
    try:
        stand = safe_get_or_404(Stand, stand_id, f"Stand with ID {stand_id} not found")
        
        # Check if we're changing stands or moving to a stand for the first time
        is_changing_stands = car.stand_id is not None
        
        # Update car's stand information
        car.stand_id = stand_id
        
        # Only update date_added_to_stand if the car was not already on a stand
        if not is_changing_stands:
            car.date_added_to_stand = datetime.now().date()
        
        # Update repair status if car wasn't already on display
        if car.repair_status != 'On Display':
            car.repair_status = 'On Display'
        
        # Update current location
        car.current_location = f"Stand: {stand.stand_name}"
        
        db.session.commit()
        
        flash(f'Car moved to {stand.stand_name} stand', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error changing stand: {str(e)}', 'danger')
    
    return redirect(url_for('cars.view', car_id=car_id))

@cars_bp.route('/<int:car_id>/record-sale', methods=['POST'])
@login_required
@validate_params(car_id=(int, True))
def record_sale(car_id):
    """Record a car sale"""
    car = safe_get_or_404(Car, car_id, f"Car with ID {car_id} not found")
    
    form = CarSaleForm(formdata=request.form)
    
    if form.validate_on_submit():
        # Update car fields
        car.date_sold = form.date_sold.data
        car.sale_price = form.sale_price.data
        car.repair_status = 'Sold'
        
        # Calculate final costs
        car.final_cost_price = car.purchase_price + car.total_repair_cost + car.refuel_cost
        
        # Create a new Sale record - this is the key addition
        # Use the dealer_id from the car if available
        dealer_id = car.dealer_id if car.dealer_id else 1  # Default to first dealer if none set
        
        # Check if a sale record already exists for this car
        existing_sale = Sale.query.filter_by(car_id=car.car_id).first()
        
        if existing_sale:
            # Update existing sale record
            existing_sale.sale_date = form.date_sold.data
            existing_sale.sale_price = form.sale_price.data
            existing_sale.dealer_id = dealer_id
            # Generate a default customer name if none exists
            if not existing_sale.customer_name:
                existing_sale.customer_name = f"Customer {form.date_sold.data.year}-{len(Sale.query.filter(extract('year', Sale.sale_date) == form.date_sold.data.year).all()) + 1}"
        else:
            # Create new sale record
            sale = Sale(
                car_id=car.car_id,
                dealer_id=dealer_id,
                sale_price=form.sale_price.data,
                sale_date=form.date_sold.data,
                # Generate a default customer name
                customer_name=f"Customer {form.date_sold.data.year}-{len(Sale.query.filter(extract('year', Sale.sale_date) == form.date_sold.data.year).all()) + 1}"
            )
            db.session.add(sale)
        
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

@cars_bp.route('/<int:car_id>/unsell', methods=['POST'])
@login_required
@validate_params(car_id=(int, True))
def unsell_car(car_id):
    """Unsell a car - remove sale record and return to inventory"""
    car = safe_get_or_404(Car, car_id, f"Car with ID {car_id} not found")
    
    # Check if the car is actually sold
    if not car.date_sold and not car.sale:
        flash('This car is not currently marked as sold.', 'warning')
        return redirect(url_for('cars.view', car_id=car_id))
    
    try:
        # Delete ALL related sale records - fix for multiple sale records issue
        sale_records = Sale.query.filter_by(car_id=car.car_id).all()
        
        if sale_records:
            for sale in sale_records:
                db.session.delete(sale)
            db.session.flush()  # Apply the deletion before moving on
            flash(f'Removed {len(sale_records)} sale records.', 'info')
        else:
            flash('No sale records found to remove.', 'info')
        
        # Reset car status
        car.date_sold = None
        car.sale_price = None
        
        # Determine what stand to put the car back on
        if car.stand_id:
            stand = Stand.query.get(car.stand_id)
            car.repair_status = 'On Display'
            car.current_location = f"Stand: {stand.stand_name if stand else 'Stand'}"
        else:
            # No stand assigned, so put it in waiting status
            car.repair_status = 'Waiting for Repairs'
            car.current_location = 'Base (Awaiting Repairs)'
            
        # Save changes
        db.session.commit()
        
        flash('Car has been unsold and returned to inventory.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error unselling car: {str(e)}', 'danger')
    
    return redirect(url_for('cars.view', car_id=car_id))

@cars_bp.route('/create-stand-ajax', methods=['POST'])
@login_required
def create_stand_ajax():
    """Create a stand from modal and return JSON response"""
    form = StandForm(formdata=request.form)
    
    if form.validate_on_submit():
        try:
            # Create the new stand
            stand = Stand(
                stand_name=form.stand_name.data,
                location=form.location.data,
                capacity=form.capacity.data,
                additional_info=form.additional_info.data,
                date_created=datetime.now(),
                last_updated=datetime.now()
            )
            
            db.session.add(stand)
            db.session.commit()
            
            # Return success with the new stand info
            return jsonify({
                'success': True,
                'stand_id': stand.stand_id,
                'stand_name': stand.stand_name,
                'message': 'Stand created successfully!'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error creating stand: {str(e)}'
            })
    else:
        # Return validation errors
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")
        
        return jsonify({
            'success': False,
            'message': f"Form validation failed: {', '.join(error_messages)}"
        }) 