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
            
            # Check required fields
            vehicle_name = data.get('vehicle_name', '').strip()
            if not vehicle_name:
                flash('Vehicle name is required', 'danger')
                return redirect(url_for('cars.create'))
            
            try:
                purchase_price = float(data.get('purchase_price', 0))
                if purchase_price < 0:
                    flash('Purchase price cannot be negative', 'danger')
                    return redirect(url_for('cars.create'))
            except ValueError:
                flash('Purchase price must be a valid number', 'danger')
                return redirect(url_for('cars.create'))
            
            # Process make (optional)
            make = None
            make_name = data.get('vehicle_make', '').strip()
            if make_name:
                make = VehicleMake.get_or_create(make_name)
            
            # Process model (optional)
            model = None
            model_name = data.get('vehicle_model', '').strip()
            if make and model_name:
                model = VehicleModel.get_or_create(model_name, make_id=make.id)
            
            # Get dealer (optional)
            dealer = None
            dealer_id = data.get('source')
            if dealer_id:
                dealer = Dealer.query.get(dealer_id)
            else:
                # Use default dealer if available
                dealer = Dealer.query.first()
            
            # Get stand (optional)
            stand = None
            stand_id = data.get('stand_id')
            if stand_id and data.get('repair_status') == 'On Display':
                try:
                    stand_id = int(stand_id)
                    stand = Stand.query.get(stand_id)
                except (ValueError, TypeError):
                    pass
            
            # Set default values for optional fields
            year = None
            try:
                year_value = data.get('year')
                if year_value:
                    year = int(year_value)
            except ValueError:
                pass
            
            # Create car with available data
            car_data = {
                'vehicle_name': vehicle_name,
                'purchase_price': purchase_price,
                'date_bought': datetime.now().date(),
                'repair_status': data.get('repair_status', 'Purchased'),
                'current_location': data.get('current_location', "Dealer's Lot"),
                'refuel_cost': float(data.get('refuel_cost', 0)) if data.get('refuel_cost') else 0
            }
            
            # Add optional fields if they exist
            if make:
                car_data['vehicle_make'] = make.name
            
            if model:
                car_data['vehicle_model'] = model.name
            
            if year:
                car_data['year'] = year
            
            if data.get('colour', '').strip():
                car_data['colour'] = VehicleColor.sanitize_name(data.get('colour', '').strip())
            
            if data.get('dekra_condition'):
                car_data['dekra_condition'] = data.get('dekra_condition')
            else:
                car_data['dekra_condition'] = "Good"  # Default
            
            if data.get('licence_number', '').strip():
                car_data['licence_number'] = data.get('licence_number', '').strip().upper()
            
            if data.get('registration_number', '').strip():
                car_data['registration_number'] = data.get('registration_number', '').strip().upper()
            elif car_data.get('licence_number'):
                # Use licence number as registration if not provided
                car_data['registration_number'] = car_data['licence_number']
            
            if dealer:
                car_data['source'] = dealer.dealer_name
                car_data['dealer_id'] = dealer.dealer_id
            
            # Handle stand relationship
            if stand and car_data['repair_status'] == 'On Display':
                car_data['stand_id'] = stand.stand_id
                car_data['date_added_to_stand'] = datetime.now().date()
                car_data['current_location'] = f"Stand: {stand.stand_name}"
            
            # Set the current location based on repair status if not already set by stand
            if 'stand_id' not in car_data:
                if car_data['repair_status'] == 'Purchased':
                    car_data['current_location'] = "Dealer's Lot"
                elif car_data['repair_status'] == 'Waiting for Repairs':
                    car_data['current_location'] = 'Base (Awaiting Repairs)'
                elif car_data['repair_status'] == 'In Repair':
                    provider = RepairProvider.query.first()
                    car_data['current_location'] = f"Repair: {provider.location if provider else 'Unknown'}"
                elif car_data['repair_status'] == 'On Display':
                    # If no specific stand was selected but status is On Display
                    stand = Stand.query.first()
                    if stand:
                        car_data['stand_id'] = stand.stand_id
                        car_data['date_added_to_stand'] = datetime.now().date()
                        car_data['current_location'] = f"Stand: {stand.stand_name}"
                    else:
                        car_data['current_location'] = "On Display at Stand"
            
            # Create the car
            car = Car(**car_data)
            db.session.add(car)
            db.session.commit()
            
            flash(f'Car {car.vehicle_name} added successfully', 'success')
            return redirect(url_for('cars.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding car: {str(e)}', 'danger')
            return redirect(url_for('cars.create'))
    
    # GET request - fetch dealers and stands for dropdowns
    dealers = Dealer.query.all()
    stands = Stand.query.all()
    return render_template('cars/create.html', dealers=dealers, stands=stands)

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
        
        # Populate the stand field with stands
        stands = Stand.query.all()
        form.stand_id.choices = [(s.stand_id, s.stand_name) for s in stands]
        
        if form.validate_on_submit():
            # Check the required fields
            if not form.vehicle_name.data or not form.vehicle_name.data.strip():
                form.vehicle_name.errors.append('Vehicle name is required')
                return render_template('cars/edit.html', form=form, car=car)
                
            if form.purchase_price.data is None or form.purchase_price.data < 0:
                form.purchase_price.errors.append('Purchase price is required and must be non-negative')
                return render_template('cars/edit.html', form=form, car=car)
            
            # Handle optional make field
            make = None
            if form.vehicle_make.data and form.vehicle_make.data.strip():
                make_name = form.vehicle_make.data.strip()
                make = VehicleMake.get_or_create(make_name)
                car.vehicle_make = VehicleMake.sanitize_name(make_name) if make else ''
            else:
                car.vehicle_make = ''
            
            # Handle optional model field
            if form.vehicle_model.data and form.vehicle_model.data.strip() and make:
                model_name = form.vehicle_model.data.strip()
                model = VehicleModel.get_or_create(model_name, make_id=make.id)
                car.vehicle_model = VehicleModel.sanitize_name(model_name) if model else ''
            else:
                car.vehicle_model = ''
            
            # Update basic fields - handle these manually to skip optional fields if they're empty
            car.vehicle_name = form.vehicle_name.data.strip()
            car.purchase_price = form.purchase_price.data
            
            # Optional fields - only update if they have values
            if form.year.data:
                car.year = form.year.data
                
            if form.colour.data and form.colour.data.strip():
                car.colour = VehicleColor.sanitize_name(form.colour.data.strip())
                
            if form.dekra_condition.data:
                car.dekra_condition = form.dekra_condition.data
            elif not car.dekra_condition:
                car.dekra_condition = "Good"  # Default
                
            if form.licence_number.data and form.licence_number.data.strip():
                car.licence_number = form.licence_number.data.strip().upper()
                
            if form.registration_number.data and form.registration_number.data.strip():
                car.registration_number = form.registration_number.data.strip().upper()
            elif car.licence_number and not car.registration_number:
                # Use licence number if registration is empty
                car.registration_number = car.licence_number
                
            if form.date_bought.data:
                car.date_bought = form.date_bought.data
            elif not car.date_bought:
                car.date_bought = datetime.now().date()
                
            if form.refuel_cost.data is not None:
                car.refuel_cost = form.refuel_cost.data
                
            if form.current_location.data:
                car.current_location = form.current_location.data.strip()
                
            if form.repair_status.data:
                car.repair_status = form.repair_status.data
            elif not car.repair_status:
                car.repair_status = 'Purchased'  # Default
                
            # Handle stand relationship and date_added_to_stand
            previous_stand_id = car.stand_id
            
            # Is the car newly being displayed at a stand?
            if form.repair_status.data == 'On Display' and form.stand_id.data:
                # Changing to a different stand or adding to a stand for the first time
                if form.stand_id.data != previous_stand_id:
                    car.stand_id = form.stand_id.data
                    
                    # Only update date_added_to_stand if the car is going to a new stand
                    # or was not previously on a stand
                    if previous_stand_id is None:
                        car.date_added_to_stand = datetime.now().date()
                    elif not form.date_added_to_stand.data:
                        car.date_added_to_stand = datetime.now().date()
                    
                    # Update location based on the new stand
                    stand = Stand.query.get(form.stand_id.data)
                    if stand:
                        car.current_location = f"Stand: {stand.stand_name}"
            elif form.repair_status.data == 'On Display' and not form.stand_id.data:
                # Status is On Display but no stand selected - find a default stand
                stand = Stand.query.first()
                if stand:
                    car.stand_id = stand.stand_id
                    
                    # Only update date if necessary
                    if previous_stand_id is None:
                        car.date_added_to_stand = datetime.now().date()
                    
                    car.current_location = f"Stand: {stand.stand_name}"
            elif form.repair_status.data and form.repair_status.data != 'On Display':
                # Car is being moved out of a stand
                car.stand_id = None
            
            # Handle date_added_to_stand directly from form if provided
            if form.date_added_to_stand.data:
                car.date_added_to_stand = form.date_added_to_stand.data
                
            if form.date_sold.data:
                car.date_sold = form.date_sold.data
            
            # Optional dealer relationship
            if form.source.data:
                dealer = Dealer.query.get(form.source.data)
                if dealer:
                    car.source = dealer.dealer_name
                    car.dealer_id = dealer.dealer_id
            
            # Set the current location based on repair status if not already set
            if not form.current_location.data or not form.current_location.data.strip():
                if car.repair_status == 'Purchased':
                    car.current_location = "Dealer's Lot"
                elif car.repair_status == 'Waiting for Repairs':
                    car.current_location = 'Base (Awaiting Repairs)'
                elif car.repair_status == 'In Repair':
                    provider = RepairProvider.query.first()
                    car.current_location = f"Repair: {provider.location if provider else 'Unknown'}"
                elif car.repair_status == 'On Display' and not car.stand_id:
                    # If status is On Display but no stand is assigned
                    stand = Stand.query.first()
                    if stand:
                        car.stand_id = stand.stand_id
                        
                        # Only update date if necessary
                        if previous_stand_id is None:
                            car.date_added_to_stand = datetime.now().date()
                        
                        car.current_location = f"Stand: {stand.stand_name}"
                    else:
                        car.current_location = "On Display at Stand"
            
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
        
        # Populate the stand field with stands
        stands = Stand.query.all()
        form.stand_id.choices = [(s.stand_id, s.stand_name) for s in stands]
        
        # Set the current dealer as selected
        if car.dealer_id:
            form.source.data = car.dealer_id
            
        # Set the current stand as selected
        if car.stand_id:
            form.stand_id.data = car.stand_id
    
    return render_template('cars/edit.html', form=form, car=car, stands=Stand.query.all())

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