from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.repair import Repair
from app.models.car import Car
from app.models.repair_provider import RepairProvider
from app.models.part import Part, RepairPart
from app.utils.forms import RepairForm, RepairPartForm
from app import db
from datetime import datetime

repairs_bp = Blueprint('repairs', __name__)

@repairs_bp.route('/')
@login_required
def index():
    """List all repairs"""
    # Get filter parameters
    car_id = request.args.get('car_id', type=int)
    status = request.args.get('status', 'All')
    
    # Base query
    query = Repair.query
    
    # Apply filters
    if car_id:
        query = query.filter(Repair.car_id == car_id)
    
    if status == 'Completed':
        query = query.filter(Repair.end_date != None)
    elif status == 'In Progress':
        query = query.filter(Repair.end_date == None)
    
    # Apply sorting (default: newest repairs first)
    sort_by = request.args.get('sort_by', 'start_date')
    sort_dir = request.args.get('sort_dir', 'desc')
    
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
    form = RepairForm()
    
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
        car = Car.query.get(form.car_id.data)
        if car.repair_status != 'In Repair':
            car.repair_status = 'In Repair'
            car.current_location = f"Repair: {form.repair_type.data}"
        
        db.session.add(repair)
        db.session.commit()
        
        flash('Repair added successfully', 'success')
        return redirect(url_for('repairs.view', repair_id=repair.repair_id))
    
    return render_template('repairs/create.html', form=form)

@repairs_bp.route('/<int:repair_id>')
@login_required
def view(repair_id):
    """View repair details"""
    repair = Repair.query.get_or_404(repair_id)
    part_form = RepairPartForm(repair_id=repair.repair_id)
    part_form.part_id.choices = [(p.part_id, p.part_name) for p in Part.query.all()]
    
    repair_parts = RepairPart.query.filter_by(repair_id=repair_id).all()
    
    return render_template(
        'repairs/view.html', 
        repair=repair, 
        part_form=part_form,
        repair_parts=repair_parts
    )

@repairs_bp.route('/<int:repair_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(repair_id):
    """Edit repair details"""
    repair = Repair.query.get_or_404(repair_id)
    form = RepairForm(obj=repair)
    
    # Populate form choices
    form.car_id.choices = [(c.car_id, f"{c.vehicle_make} {c.vehicle_model} ({c.year})") 
                           for c in Car.query.all()]
    form.provider_id.choices = [(p.provider_id, f"{p.provider_name} ({p.service_type})") 
                               for p in RepairProvider.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(repair)
        
        # If repair is marked as complete (end_date is set), update car status
        car = Car.query.get(repair.car_id)
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
    
    return render_template('repairs/edit.html', form=form, repair=repair)

@repairs_bp.route('/<int:repair_id>/delete', methods=['POST'])
@login_required
def delete(repair_id):
    """Delete a repair"""
    repair = Repair.query.get_or_404(repair_id)
    
    # Check if this is the only active repair for the car
    car = Car.query.get(repair.car_id)
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
def complete(repair_id):
    """Mark a repair as complete"""
    repair = Repair.query.get_or_404(repair_id)
    
    if repair.end_date:
        flash('Repair is already marked as complete', 'warning')
        return redirect(url_for('repairs.view', repair_id=repair_id))
    
    repair.end_date = datetime.now().date()
    
    # Check if this is the last active repair for this car
    car = Car.query.get(repair.car_id)
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
def add_part(repair_id):
    """Add a part to a repair"""
    repair = Repair.query.get_or_404(repair_id)
    form = RepairPartForm(request.form)
    form.part_id.choices = [(p.part_id, p.part_name) for p in Part.query.all()]
    
    if form.validate():
        repair_part = RepairPart(
            repair_id=repair_id,
            part_id=form.part_id.data,
            purchase_price=form.purchase_price.data,
            purchase_date=form.purchase_date.data,
            vendor=form.vendor.data
        )
        
        db.session.add(repair_part)
        db.session.commit()
        
        flash('Part added to repair successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('repairs.view', repair_id=repair_id))

@repairs_bp.route('/parts/<int:record_id>/remove', methods=['POST'])
@login_required
def remove_part(record_id):
    """Remove a part from a repair"""
    repair_part = RepairPart.query.get_or_404(record_id)
    repair_id = repair_part.repair_id
    
    # First fetch the record
    db.session.refresh(repair_part)
    
    # Then delete it
    db.session.delete(repair_part)
    db.session.commit()
    
    flash('Part removed from repair successfully', 'success')
    return redirect(url_for('repairs.view', repair_id=repair_id)) 