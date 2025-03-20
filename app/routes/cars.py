from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.car import Car
from app.models.stand import Stand
from app.models.dealer import Dealer
from app.utils.forms import CarForm, CarSaleForm
from app import db
from datetime import datetime

cars_bp = Blueprint('cars', __name__)

@cars_bp.route('/')
@login_required
def index():
    """List all cars"""
    # Get filter parameters
    status = request.args.get('status', 'All')
    
    # Base query
    query = Car.query
    
    # Apply filters
    if status != 'All':
        query = query.filter(Car.repair_status == status)
    
    # Apply sorting (default: newest purchases first)
    sort_by = request.args.get('sort_by', 'date_bought')
    sort_dir = request.args.get('sort_dir', 'desc')
    
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
    """Create a new car"""
    form = CarForm()
    
    if form.validate_on_submit():
        car = Car(
            vehicle_name=form.vehicle_name.data,
            vehicle_make=form.vehicle_make.data,
            vehicle_model=form.vehicle_model.data,
            year=form.year.data,
            colour=form.colour.data,
            dekra_condition=form.dekra_condition.data,
            licence_number=form.licence_number.data,
            registration_number=form.registration_number.data,
            purchase_price=form.purchase_price.data,
            source=form.source.data,
            date_bought=form.date_bought.data,
            refuel_cost=form.refuel_cost.data or 0.00,
            current_location=form.current_location.data,
            repair_status=form.repair_status.data
        )
        
        db.session.add(car)
        db.session.commit()
        
        flash('Car added successfully', 'success')
        return redirect(url_for('cars.index'))
    
    return render_template('cars/create.html', form=form)

@cars_bp.route('/<int:car_id>')
@login_required
def view(car_id):
    """View car details"""
    car = Car.query.get_or_404(car_id)
    sale_form = None
    
    # If car is on display but not sold, prepare sale form
    if car.repair_status == 'On Display' and not car.date_sold:
        sale_form = CarSaleForm(car_id=car.car_id)
        sale_form.dealer_id.choices = [(d.dealer_id, d.dealer_name) for d in Dealer.query.all()]
    
    return render_template('cars/view.html', car=car, sale_form=sale_form)

@cars_bp.route('/<int:car_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(car_id):
    """Edit car details"""
    car = Car.query.get_or_404(car_id)
    form = CarForm(obj=car)
    
    if form.validate_on_submit():
        form.populate_obj(car)
        db.session.commit()
        
        flash('Car updated successfully', 'success')
        return redirect(url_for('cars.view', car_id=car.car_id))
    
    return render_template('cars/edit.html', form=form, car=car)

@cars_bp.route('/<int:car_id>/delete', methods=['POST'])
@login_required
def delete(car_id):
    """Delete a car"""
    car = Car.query.get_or_404(car_id)
    
    db.session.delete(car)
    db.session.commit()
    
    flash('Car deleted successfully', 'success')
    return redirect(url_for('cars.index'))

@cars_bp.route('/<int:car_id>/move-to-stand', methods=['POST'])
@login_required
def move_to_stand(car_id):
    """Move a car to a stand"""
    car = Car.query.get_or_404(car_id)
    stand_id = request.form.get('stand_id', type=int)
    
    if not stand_id:
        flash('Please select a stand', 'danger')
        return redirect(url_for('cars.view', car_id=car_id))
    
    stand = Stand.query.get_or_404(stand_id)
    
    car.stand_id = stand_id
    car.date_added_to_stand = datetime.now().date()
    car.repair_status = 'On Display'
    car.current_location = f"Stand: {stand.stand_name}"
    
    db.session.commit()
    
    flash(f'Car moved to {stand.stand_name} stand', 'success')
    return redirect(url_for('cars.view', car_id=car_id))

@cars_bp.route('/<int:car_id>/record-sale', methods=['POST'])
@login_required
def record_sale(car_id):
    """Record a car sale"""
    car = Car.query.get_or_404(car_id)
    form = CarSaleForm(request.form)
    form.dealer_id.choices = [(d.dealer_id, d.dealer_name) for d in Dealer.query.all()]
    
    if form.validate():
        car.date_sold = form.date_sold.data
        car.sale_price = form.sale_price.data
        car.dealer_id = form.dealer_id.data
        car.repair_status = 'Sold'
        
        # Calculate final costs
        car.final_cost_price = car.purchase_price + car.total_repair_cost + car.refuel_cost
        
        db.session.commit()
        
        flash('Sale recorded successfully', 'success')
        return redirect(url_for('cars.view', car_id=car_id))
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('cars.view', car_id=car_id)) 