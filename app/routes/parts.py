from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from app.models.part import Part
from app.utils.forms import PartForm
from app.utils.validators import validate_params, validate_form
from app.utils.helpers import safe_get_or_404
from app import db
from app.models.setting import Setting

parts_bp = Blueprint('parts', __name__)

VALID_SORT_FIELDS = ['part_name', 'manufacturer', 'standard_price']
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
    
    # Apply sorting
    if sort_dir == 'desc':
        query = query.order_by(getattr(Part, sort_by).desc())
    else:
        query = query.order_by(getattr(Part, sort_by))
    
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
            part = Part(
                part_name=form.part_name.data,
                description=form.description.data,
                manufacturer=form.manufacturer.data,
                standard_price=form.standard_price.data
            )
            
            db.session.add(part)
            db.session.commit()
            
            flash('Part added successfully', 'success')
            
            if return_to:
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
            part = Part(
                part_name=form.part_name.data,
                description=form.description.data,
                manufacturer=form.manufacturer.data,
                standard_price=form.standard_price.data
            )
            
            db.session.add(part)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'part_id': part.part_id,
                'part_name': part.part_name,
                'message': f'Part "{part.part_name}" added successfully'
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

@parts_bp.route('/<int:part_id>/edit', methods=['GET', 'POST'])
@login_required
@validate_params(part_id=(int, True))
def edit(part_id):
    """Edit part details"""
    part = safe_get_or_404(Part, part_id, f"Part with ID {part_id} not found")
    
    if request.method == 'POST':
        form = PartForm(formdata=request.form, obj=part)
        
        if form.validate_on_submit():
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