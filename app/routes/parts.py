from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from app.models.part import Part
from app.models.car import Car
from app.utils.forms import PartForm
from app.utils.validators import validate_params, validate_form
from app.utils.helpers import safe_get_or_404
from app import db
from app.models.setting import Setting
from sqlalchemy import func

parts_bp = Blueprint('parts', __name__)

VALID_SORT_FIELDS = ['part_id', 'part_name', 'manufacturer', 'storage_location', 'standard_price', 'make', 'model', 'stock_quantity', 'weight']
VALID_SORT_DIRS = ['asc', 'desc']

@parts_bp.route('/')
@login_required
@validate_params(
    sort_by=(str, False, 'part_name', lambda x: x in VALID_SORT_FIELDS),
    sort_dir=(str, False, 'asc', lambda x: x in VALID_SORT_DIRS),
    search=(str, False, None),
    min_price=(float, False, None, lambda x: x >= 0),
    max_price=(float, False, None, lambda x: x >= 0),
    manufacturer=(str, False, None)
)
def index():
    """List all parts"""
    # Get validated parameters
    params = request.validated_params
    sort_by = params.get('sort_by', 'part_name')
    sort_dir = params.get('sort_dir', 'asc')
    search = params.get('search')
    min_price = params.get('min_price')
    max_price = params.get('max_price')
    manufacturer = params.get('manufacturer')
    
    # Start with base query
    query = Part.query
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Part.part_name.ilike(search_term) | 
            Part.description.ilike(search_term)
        )
    
    if min_price is not None:
        query = query.filter(Part.standard_price >= min_price)
        
    if max_price is not None:
        query = query.filter(Part.standard_price <= max_price)
        
    if manufacturer:
        query = query.filter(Part.manufacturer.ilike(f"%{manufacturer}%"))
    
    # Apply sorting - check if sort field exists in model
    if sort_by == 'storage_location':
        # Use the storage_location field (which maps to location in database)
        if sort_dir == 'desc':
            query = query.order_by(Part.storage_location.desc())
        else:
            query = query.order_by(Part.storage_location)
    elif sort_by == 'location':
        # For backwards compatibility with older code
        if sort_dir == 'desc':
            query = query.order_by(Part.storage_location.desc())
        else:
            query = query.order_by(Part.storage_location)
    elif hasattr(Part, sort_by):
        if sort_dir == 'desc':
            query = query.order_by(getattr(Part, sort_by).desc())
        else:
            query = query.order_by(getattr(Part, sort_by))
    else:
        # Default to part_name if sort field doesn't exist
        query = query.order_by(Part.part_name)
    
    parts = query.all()
    
    return render_template(
        'parts/index.html',
        parts=parts,
        current_sort=sort_by,
        current_sort_dir=sort_dir,
        current_search=search,
        current_min_price=min_price,
        current_max_price=max_price,
        current_manufacturer=manufacturer
    )

@parts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new part"""
    is_modal = request.args.get('modal', '0') == '1'
    return_to = request.args.get('return_to', None)
    
    if request.method == 'POST':
        form = PartForm(formdata=request.form)
        
        if form.validate_on_submit():
            # Sanitize part name (trim + lowercase for match)
            part_name = form.part_name.data.strip()
            
            # Sanitize form inputs with proper casing
            manufacturer = form.manufacturer.data.strip() if form.manufacturer.data else None
            
            # Create a dummy part to use is_duplicate method
            dummy_part = Part(part_id=0, part_name=part_name)
            
            # Check if part already exists (using name, make, model)
            existing_parts = Part.query.filter(
                func.lower(func.trim(Part.part_name)) == part_name.lower().strip()
            ).all()
            
            existing_part = None
            for part in existing_parts:
                # The is_duplicate now only considers name
                if part.is_duplicate(part_name):
                    existing_part = part
                    break
            
            if existing_part:
                # Increase stock by submitted amount
                existing_part.stock_quantity += form.stock_quantity.data
                
                # Optionally update price and other optional fields if provided
                if form.description.data:
                    existing_part.description = form.description.data
                if manufacturer:
                    existing_part.manufacturer = manufacturer
                if form.standard_price.data is not None:
                    existing_part.standard_price = form.standard_price.data
                if hasattr(form, 'storage_location') and form.storage_location.data:
                    existing_part.storage_location = form.storage_location.data
                
                db.session.commit()
                flash('Part already exists — stock updated', 'success')
                
                # Return the part ID for selection
                part = existing_part
            else:
                # Insert normally
                part = Part(
                    part_name=part_name,
                    description=form.description.data,
                    manufacturer=manufacturer,
                    standard_price=form.standard_price.data,
                    stock_quantity=form.stock_quantity.data,
                    storage_location=form.storage_location.data if hasattr(form, 'storage_location') else None
                )
                
                db.session.add(part)
                db.session.commit()
                flash('New part added', 'success')
            
            if return_to:
                # Append the part ID to the return URL for selection
                if '?' in return_to:
                    return_to += f'&new_part_id={part.part_id}'
                else:
                    return_to += f'?new_part_id={part.part_id}'
                    
                return redirect(return_to)
            else:
                return redirect(url_for('parts.index'))
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        form = PartForm()
    
    # If it's a modal request, return only the form without the base template
    if is_modal:
        return render_template('parts/modal_form.html', form=form)
    
    return render_template('parts/create.html', form=form)

@parts_bp.route('/create-ajax', methods=['POST'])
@login_required
def create_ajax():
    """Create a new part via AJAX"""
    try:
        form = PartForm(formdata=request.form)
        
        if form.validate_on_submit():
            # Sanitize part name (trim + lowercase for match)
            part_name = form.part_name.data.strip()
            
            # Sanitize form inputs with proper casing
            manufacturer = form.manufacturer.data.strip() if form.manufacturer.data else None
            
            # Create a dummy part to use is_duplicate method
            dummy_part = Part(part_id=0, part_name=part_name)
            
            # Check if part already exists (using name, make, model)
            existing_parts = Part.query.filter(
                func.lower(func.trim(Part.part_name)) == part_name.lower().strip()
            ).all()
            
            existing_part = None
            for part in existing_parts:
                # The is_duplicate now only considers name
                if part.is_duplicate(part_name):
                    existing_part = part
                    break
            
            if existing_part:
                # Increase stock by submitted amount
                existing_part.stock_quantity += form.stock_quantity.data
                
                # Optionally update price and other optional fields if provided
                if form.description.data:
                    existing_part.description = form.description.data
                if manufacturer:
                    existing_part.manufacturer = manufacturer
                if form.standard_price.data is not None:
                    existing_part.standard_price = form.standard_price.data
                if hasattr(form, 'storage_location') and form.storage_location.data:
                    existing_part.storage_location = form.storage_location.data
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'part_id': existing_part.part_id,
                    'part_name': existing_part.part_name,
                    'message': f'Part "{existing_part.part_name}" already exists — stock updated',
                    'is_update': True
                })
            else:
                # Insert normally
                part = Part(
                    part_name=part_name,
                    description=form.description.data,
                    manufacturer=manufacturer,
                    standard_price=form.standard_price.data,
                    stock_quantity=form.stock_quantity.data,
                    storage_location=form.storage_location.data if hasattr(form, 'storage_location') else None
                )
                
                db.session.add(part)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'part_id': part.part_id,
                    'part_name': part.part_name,
                    'message': f'New part "{part.part_name}" added',
                    'is_update': False
                })
        else:
            # Collect validation errors
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            return jsonify({
                'success': False,
                'message': f"Form validation failed: {', '.join(error_messages)}"
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f"An error occurred: {str(e)}"
        })

@parts_bp.route('/<int:part_id>')
@login_required
@validate_params(part_id=(int, True))
def view(part_id):
    """View part details"""
    part = safe_get_or_404(Part, part_id, f"Part with ID {part_id} not found")
    return render_template('parts/view.html', part=part)

@parts_bp.route('/edit/<int:part_id>', methods=['GET', 'POST'])
@login_required
@validate_params(part_id=(int, True))
def edit(part_id):
    """Edit part details"""
    part = safe_get_or_404(Part, part_id, f"Part with ID {part_id} not found")
    
    if request.method == 'POST':
        form = PartForm(formdata=request.form, obj=part)
        
        if form.validate_on_submit():
            # Sanitize form inputs with proper casing before populating
            manufacturer = form.manufacturer.data.strip() if form.manufacturer.data else None
            
            # Update the form object with sanitized values
            form.manufacturer.data = manufacturer
            
            # Populate the model with form data including sanitized fields
            form.populate_obj(part)
            db.session.commit()
            
            flash('Part updated successfully', 'success')
            return redirect(url_for('parts.view', part_id=part.part_id))
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        form = PartForm(obj=part)
    
    return render_template('parts/edit.html', form=form, part=part)

@parts_bp.route('/edit_ajax/<int:part_id>', methods=['POST'])
@login_required
@validate_params(part_id=(int, True))
def edit_ajax(part_id):
    """Edit part details via AJAX"""
    part = safe_get_or_404(Part, part_id, f"Part with ID {part_id} not found")
    
    if request.method == 'POST':
        form = PartForm(formdata=request.form)
        
        if form.validate_on_submit():
            # Sanitize form inputs with proper casing
            part.part_name = form.part_name.data.strip()
            part.description = form.description.data
            part.manufacturer = form.manufacturer.data.strip() if form.manufacturer.data else None
            part.standard_price = form.standard_price.data
            part.stock_quantity = form.stock_quantity.data
            
            db.session.commit()
            
            response = {
                'status': 'success',
                'message': 'Part updated successfully',
                'part': {
                    'id': part.part_id,
                    'part_name': part.part_name,
                    'description': part.description,
                    'manufacturer': part.manufacturer,
                    'standard_price': float(part.standard_price) if part.standard_price else None,
                    'stock_quantity': part.stock_quantity,
                    'make': part.make,
                    'model': part.model
                }
            }
            return jsonify(response)
        else:
            # Collect validation errors
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            return jsonify({
                'status': 'error',
                'errors': error_messages
            }), 400
    else:
        return jsonify({
            'status': 'error',
            'message': 'Method not allowed'
        }), 405

@parts_bp.route('/<int:part_id>/delete', methods=['POST'])
@login_required
@validate_params(part_id=(int, True))
def delete(part_id):
    """Delete a part"""
    part = safe_get_or_404(Part, part_id, f"Part with ID {part_id} not found")
    
    # Check if part is used in any repairs
    if part.repair_parts:
        flash('Cannot delete part because it is used in repairs', 'danger')
        return redirect(url_for('parts.view', part_id=part_id))
    
    db.session.delete(part)
    db.session.commit()
    
    flash('Part deleted successfully', 'success')
    return redirect(url_for('parts.index'))

# Routes for autocomplete suggestion endpoints

@parts_bp.route('/autocomplete/makes')
@login_required
def autocomplete_makes():
    """Return a list of distinct car makes for autocomplete"""
    query = request.args.get('query', '').strip().lower()
    
    # Get distinct makes from cars table
    makes_query = db.session.query(func.distinct(Car.vehicle_make))\
        .filter(Car.vehicle_make != None)\
        .filter(func.lower(Car.vehicle_make).contains(query))\
        .order_by(Car.vehicle_make)
    
    makes = [make[0] for make in makes_query.all() if make[0]]
    
    return jsonify(makes)

@parts_bp.route('/autocomplete/models')
@login_required
def autocomplete_models():
    """Return a list of distinct car models for autocomplete"""
    query = request.args.get('query', '').strip().lower()
    make = request.args.get('make', '').strip()
    
    # Start with base query
    models_query = db.session.query(func.distinct(Car.vehicle_model))\
        .filter(Car.vehicle_model != None)
    
    # Filter by make if provided
    if make:
        models_query = models_query.filter(func.lower(Car.vehicle_make) == make.lower())
    
    # Filter by search query
    if query:
        models_query = models_query.filter(func.lower(Car.vehicle_model).contains(query))
    
    # Order and get results
    models = [model[0] for model in models_query.order_by(Car.vehicle_model).all() if model[0]]
    
    return jsonify(models)

@parts_bp.route('/autocomplete/manufacturers')
@login_required
def autocomplete_manufacturers():
    """Return a list of distinct part manufacturers for autocomplete"""
    query = request.args.get('query', '').strip().lower()
    
    # Get distinct manufacturers from parts table
    manufacturers_query = db.session.query(func.distinct(Part.manufacturer))\
        .filter(Part.manufacturer != None)\
        .filter(func.lower(Part.manufacturer).contains(query))\
        .order_by(Part.manufacturer)
    
    manufacturers = [mfg[0] for mfg in manufacturers_query.all() if mfg[0]]
    
    return jsonify(manufacturers)

@parts_bp.route('/autocomplete/storage-locations')
@login_required
def autocomplete_storage_locations():
    """Return a list of distinct storage locations for autocomplete"""
    query = request.args.get('query', '').strip().lower()
    
    try:
        # Get distinct storage locations from parts table
        # Note: storage_location is mapped to 'location' column in the database
        locations_query = db.session.query(func.distinct(Part.storage_location))\
            .filter(Part.storage_location != None)
        
        # Apply search filter if provided
        if query:
            locations_query = locations_query.filter(func.lower(Part.storage_location).contains(query))
            
        # Order and execute query
        locations_query = locations_query.order_by(Part.storage_location)
        locations = [loc[0] for loc in locations_query.all() if loc[0]]
        
        return jsonify(locations)
    except Exception as e:
        # If there's an error, return an empty list
        print(f"Error in storage locations autocomplete: {str(e)}")
        return jsonify([]) 