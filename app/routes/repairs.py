from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.repair import Repair
from app.models.car import Car
from app.models.repair_provider import RepairProvider
from app.models.part import Part, RepairPart
from app.utils.forms import RepairForm, RepairPartForm
from app.utils.validators import validate_params, validate_form
from app.utils.helpers import safe_get_or_404
from app import db
from datetime import datetime
from app.models.setting import Setting

repairs_bp = Blueprint('repairs', __name__)

VALID_STATUSES = ['All', 'Completed', 'In Progress']
VALID_SORT_FIELDS = ['start_date', 'end_date', 'repair_type', 'repair_cost']
VALID_SORT_DIRS = ['asc', 'desc']

@repairs_bp.route('/')
@login_required
@validate_params(
    car_id=(int, False, None),
    status=(str, False, 'All', lambda x: x in VALID_STATUSES),
    sort_by=(str, False, 'start_date', lambda x: x in VALID_SORT_FIELDS),
    sort_dir=(str, False, 'desc', lambda x: x in VALID_SORT_DIRS)
)
def index():
    """List all repairs"""
    # Get validated parameters
    params = request.validated_params
    car_id = params.get('car_id')
    status = params.get('status', 'All')
    sort_by = params.get('sort_by', 'start_date')
    sort_dir = params.get('sort_dir', 'desc')
    
    # Base query
    query = Repair.query
    
    # Apply filters
    if car_id:
        query = query.filter(Repair.car_id == car_id)
    
    if status == 'Completed':
        query = query.filter(Repair.end_date != None)
    elif status == 'In Progress':
        query = query.filter(Repair.end_date == None)
    
    # Apply sorting
    if sort_dir == 'desc':
        query = query.order_by(getattr(Repair, sort_by).desc())
    else:
        query = query.order_by(getattr(Repair, sort_by))
    
    repairs = query.all()
    
    return render_template(
        'repairs/index.html',
        repairs=repairs,
        current_car_id=car_id,
        current_status=status,
        current_sort=sort_by,
        current_sort_dir=sort_dir
    )

@repairs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new repair"""
    if request.method == 'POST':
        form = RepairForm(formdata=request.form)
        
        # Populate form choices
        form.car_id.choices = [(c.car_id, f"{c.vehicle_make} {c.vehicle_model} ({c.year})") 
                            for c in Car.query.filter(Car.date_sold == None).all()]
        form.provider_id.choices = [(p.provider_id, f"{p.provider_name} ({p.service_type})") 
                                for p in RepairProvider.query.all()]
        
        if form.validate_on_submit():
            repair = Repair(
                car_id=form.car_id.data,
                repair_type=form.repair_type.data,
                provider_id=form.provider_id.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                repair_cost=form.repair_cost.data,
                additional_notes=form.additional_notes.data
            )
            
            # Update car status if it's not already in repair
            car = safe_get_or_404(Car, form.car_id.data, f"Car with ID {form.car_id.data} not found")
            if car.repair_status != 'In Repair':
                car.repair_status = 'In Repair'
                car.current_location = f"Repair: {form.repair_type.data}"
            
            db.session.add(repair)
            db.session.commit()
            
            flash('Repair added successfully', 'success')
            return redirect(url_for('repairs.view', repair_id=repair.repair_id))
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        form = RepairForm()
        # Populate form choices
        form.car_id.choices = [(c.car_id, f"{c.vehicle_make} {c.vehicle_model} ({c.year})") 
                            for c in Car.query.filter(Car.date_sold == None).all()]
        form.provider_id.choices = [(p.provider_id, f"{p.provider_name} ({p.service_type})") 
                                for p in RepairProvider.query.all()]
    
    return render_template('repairs/create.html', form=form, settings=Setting)

@repairs_bp.route('/<int:repair_id>')
@login_required
@validate_params(repair_id=(int, True))
def view(repair_id):
    """View repair details"""
    repair = safe_get_or_404(Repair, repair_id, f"Repair with ID {repair_id} not found")
    part_form = RepairPartForm(repair_id=repair.repair_id)
    part_form.part_id.choices = [(p.part_id, p.part_name) for p in Part.query.all()]
    
    repair_parts = RepairPart.query.filter_by(repair_id=repair_id).all()
    
    # Create a dictionary of parts with their details for the dropdown
    all_parts = Part.query.all()
    parts_dict = {p.part_id: p for p in all_parts}
    
    return render_template(
        'repairs/view.html', 
        repair=repair, 
        part_form=part_form,
        repair_parts=repair_parts,
        parts_dict=parts_dict,
        settings=Setting
    )

@repairs_bp.route('/<int:repair_id>/edit', methods=['GET', 'POST'])
@login_required
@validate_params(repair_id=(int, True))
def edit(repair_id):
    """Edit repair details"""
    repair = safe_get_or_404(Repair, repair_id, f"Repair with ID {repair_id} not found")
    
    if request.method == 'POST':
        form = RepairForm(formdata=request.form, obj=repair)
        
        # Populate form choices
        form.car_id.choices = [(c.car_id, f"{c.vehicle_make} {c.vehicle_model} ({c.year})") 
                               for c in Car.query.all()]
        form.provider_id.choices = [(p.provider_id, f"{p.provider_name} ({p.service_type})") 
                                   for p in RepairProvider.query.all()]
        
        if form.validate_on_submit():
            # Map form fields to model fields
            repair.car_id = form.car_id.data
            repair.repair_type = form.repair_type.data
            repair.provider_id = form.provider_id.data
            repair.start_date = form.start_date.data
            repair.end_date = form.end_date.data
            repair.repair_cost = form.repair_cost.data
            repair.additional_notes = form.additional_notes.data
            
            # If repair is marked as complete (end_date is set), update car status
            car = safe_get_or_404(Car, repair.car_id, f"Car with ID {repair.car_id} not found")
            if form.end_date.data and car.repair_status == 'In Repair':
                # Check if this is the last active repair for this car
                active_repairs = Repair.query.filter(
                    Repair.car_id == car.car_id,
                    Repair.repair_id != repair.repair_id,
                    Repair.end_date == None
                ).count()
                
                # If no other active repairs, update car status
                if active_repairs == 0:
                    car.repair_status = 'Waiting for Repairs'
                    car.current_location = 'Base (Awaiting Next Step)'
            
            db.session.commit()
            
            flash('Repair updated successfully', 'success')
            return redirect(url_for('repairs.view', repair_id=repair.repair_id))
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        # Map model fields to form fields for display
        form = RepairForm()
        form.car_id.data = repair.car_id
        form.repair_type.data = repair.repair_type
        form.provider_id.data = repair.provider_id
        form.start_date.data = repair.start_date
        form.end_date.data = repair.end_date
        form.repair_cost.data = repair.repair_cost
        form.additional_notes.data = repair.additional_notes
        
        # Populate form choices
        form.car_id.choices = [(c.car_id, f"{c.vehicle_make} {c.vehicle_model} ({c.year})") 
                              for c in Car.query.all()]
        form.provider_id.choices = [(p.provider_id, f"{p.provider_name} ({p.service_type})") 
                                   for p in RepairProvider.query.all()]
    
    return render_template('repairs/edit.html', form=form, repair=repair, settings=Setting)

@repairs_bp.route('/<int:repair_id>/delete', methods=['POST'])
@login_required
@validate_params(repair_id=(int, True))
def delete(repair_id):
    """Delete a repair"""
    repair = safe_get_or_404(Repair, repair_id, f"Repair with ID {repair_id} not found")
    
    # Check if this is the only active repair for the car
    car = safe_get_or_404(Car, repair.car_id, f"Car with ID {repair.car_id} not found")
    if car.repair_status == 'In Repair':
        active_repairs = Repair.query.filter(
            Repair.car_id == car.car_id,
            Repair.repair_id != repair.repair_id,
            Repair.end_date == None
        ).count()
        
        # If no other active repairs, update car status
        if active_repairs == 0:
            car.repair_status = 'Waiting for Repairs'
            car.current_location = 'Base (Awaiting Next Step)'
    
    # First delete all repair parts
    RepairPart.query.filter_by(repair_id=repair_id).delete()
    
    # Then delete the repair
    db.session.delete(repair)
    db.session.commit()
    
    flash('Repair deleted successfully', 'success')
    return redirect(url_for('repairs.index'))

@repairs_bp.route('/<int:repair_id>/complete', methods=['POST'])
@login_required
@validate_params(repair_id=(int, True))
def complete(repair_id):
    """Mark a repair as complete"""
    repair = safe_get_or_404(Repair, repair_id, f"Repair with ID {repair_id} not found")
    
    if repair.end_date:
        flash('Repair is already marked as complete', 'warning')
        return redirect(url_for('repairs.view', repair_id=repair_id))
    
    repair.end_date = datetime.now().date()
    
    # Check if this is the last active repair for this car
    car = safe_get_or_404(Car, repair.car_id, f"Car with ID {repair.car_id} not found")
    active_repairs = Repair.query.filter(
        Repair.car_id == car.car_id,
        Repair.repair_id != repair.repair_id,
        Repair.end_date == None
    ).count()
    
    # If no other active repairs, update car status
    if active_repairs == 0 and car.repair_status == 'In Repair':
        car.repair_status = 'Waiting for Repairs'
        car.current_location = 'Base (Awaiting Next Step)'
    
    db.session.commit()
    
    flash('Repair marked as complete', 'success')
    return redirect(url_for('repairs.view', repair_id=repair_id))

@repairs_bp.route('/<int:repair_id>/add-part', methods=['POST'])
@login_required
@validate_params(repair_id=(int, True))
def add_part(repair_id):
    """Add a part to a repair"""
    repair = safe_get_or_404(Repair, repair_id, f"Repair with ID {repair_id} not found")
    
    form = RepairPartForm(formdata=request.form)
    form.part_id.choices = [(p.part_id, p.part_name) for p in Part.query.all()]
    
    if form.validate_on_submit():
        part = safe_get_or_404(Part, form.part_id.data, f"Part with ID {form.part_id.data} not found")
        
        # Set default purchase date to today if not provided
        purchase_date = form.purchase_date.data if form.purchase_date.data else datetime.now().date()
        
        # Create repair part record
        repair_part = RepairPart(
            repair_id=repair_id,
            part_id=form.part_id.data,
            purchase_price=form.purchase_price.data,
            purchase_date=purchase_date,
            vendor=form.vendor.data
        )
        
        db.session.add(repair_part)
        
        # Check part stock and decrement if greater than 0
        quantity = form.quantity.data
        if part.stock_quantity >= quantity:
            part.stock_quantity -= quantity
            flash(f'{part.part_name} added to repair successfully. Stock decremented to {part.stock_quantity}.', 'success')
        else:
            # If not enough stock, warn the user but still add the part
            flash(f'Warning: Requested {quantity} of {part.part_name} but only {part.stock_quantity} in stock. Part added with limited inventory change.', 'warning')
            if part.stock_quantity > 0:
                part.stock_quantity = 0
        
        db.session.commit()
        
    else:
        # Show what validation errors occurred
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")
        flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    
    return redirect(url_for('repairs.view', repair_id=repair_id))

@repairs_bp.route('/parts/<int:record_id>/remove', methods=['POST'])
@login_required
@validate_params(record_id=(int, True))
def remove_part(record_id):
    """Remove a part from a repair"""
    repair_part = safe_get_or_404(RepairPart, record_id, f"Repair part with ID {record_id} not found")
    repair_id = repair_part.repair_id
    
    part = repair_part.part
    part_name = part.part_name if part else 'Part'
    
    # If we have a valid part, increment its stock
    if part:
        # Record the current stock for messaging
        old_stock = part.stock_quantity
        
        # Increment the part's stock
        part.stock_quantity += 1
        
        db.session.delete(repair_part)
        db.session.commit()
        
        flash(f'{part_name} removed from repair successfully. Stock incremented from {old_stock} to {part.stock_quantity}.', 'success')
    else:
        # If for some reason we don't have a valid part, just delete the repair_part
        db.session.delete(repair_part)
        db.session.commit()
        
        flash(f'{part_name} removed from repair successfully.', 'success')
    
    return redirect(url_for('repairs.view', repair_id=repair_id))

@repairs_bp.route('/parts/<int:record_id>/replace', methods=['POST'])
@login_required
@validate_params(record_id=(int, True))
def replace_part(record_id):
    """Replace a part on a repair with a new part"""
    repair_part = safe_get_or_404(RepairPart, record_id, f"Repair part with ID {record_id} not found")
    repair_id = repair_part.repair_id
    
    # Get the form data for the new part
    form = RepairPartForm(formdata=request.form)
    form.part_id.choices = [(p.part_id, p.part_name) for p in Part.query.all()]
    
    if form.validate_on_submit():
        # Check if the part is actually changing
        if repair_part.part_id == form.part_id.data:
            # Only update other fields if the part isn't changing
            repair_part.purchase_price = form.purchase_price.data
            repair_part.purchase_date = form.purchase_date.data
            repair_part.vendor = form.vendor.data
            db.session.commit()
            flash('Part details updated successfully.', 'success')
            return redirect(url_for('repairs.view', repair_id=repair_id))
        
        # Get the old and new parts
        old_part = repair_part.part
        new_part = safe_get_or_404(Part, form.part_id.data, f"Part with ID {form.part_id.data} not found")
        
        # Increment the old part's stock if it exists
        if old_part:
            old_part.stock_quantity += 1
            old_part_name = old_part.part_name
        else:
            old_part_name = 'Unknown Part'
        
        # Check the new part's stock and decrement if possible
        stock_warning = False
        if new_part.stock_quantity > 0:
            new_part.stock_quantity -= 1
        else:
            stock_warning = True
        
        # Update the repair part with the new information
        repair_part.part_id = form.part_id.data
        repair_part.purchase_price = form.purchase_price.data
        repair_part.purchase_date = form.purchase_date.data
        repair_part.vendor = form.vendor.data
        
        db.session.commit()
        
        # Show appropriate messages
        if stock_warning:
            flash(f'Warning: {new_part.part_name} has no stock (0 quantity). Part added to repair without changing inventory.', 'warning')
        
        flash(f'Part replaced successfully: {old_part_name} → {new_part.part_name}', 'success')
        if old_part:
            flash(f'{old_part_name} stock increased to {old_part.stock_quantity}.', 'info')
        if not stock_warning:
            flash(f'{new_part.part_name} stock decreased to {new_part.stock_quantity}.', 'info')
    else:
        # Show validation errors
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")
        flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    
    return redirect(url_for('repairs.view', repair_id=repair_id)) 