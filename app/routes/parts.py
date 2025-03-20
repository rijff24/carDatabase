from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from app.models.part import Part
from app.utils.forms import PartForm
from app import db

parts_bp = Blueprint('parts', __name__)

@parts_bp.route('/')
@login_required
def index():
    """List all parts"""
    # Get sorting parameters
    sort_by = request.args.get('sort_by', 'part_name')
    sort_dir = request.args.get('sort_dir', 'asc')
    
    # Apply sorting
    if sort_dir == 'desc':
        parts = Part.query.order_by(getattr(Part, sort_by).desc()).all()
    else:
        parts = Part.query.order_by(getattr(Part, sort_by)).all()
    
    return render_template(
        'parts/index.html',
        parts=parts,
        current_sort=sort_by,
        current_sort_dir=sort_dir
    )

@parts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new part"""
    form = PartForm()
    
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
        return redirect(url_for('parts.index'))
    
    return render_template('parts/create.html', form=form)

@parts_bp.route('/<int:part_id>')
@login_required
def view(part_id):
    """View part details"""
    part = Part.query.get_or_404(part_id)
    return render_template('parts/view.html', part=part)

@parts_bp.route('/<int:part_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(part_id):
    """Edit part details"""
    part = Part.query.get_or_404(part_id)
    form = PartForm(obj=part)
    
    if form.validate_on_submit():
        form.populate_obj(part)
        db.session.commit()
        
        flash('Part updated successfully', 'success')
        return redirect(url_for('parts.view', part_id=part.part_id))
    
    return render_template('parts/edit.html', form=form, part=part)

@parts_bp.route('/<int:part_id>/delete', methods=['POST'])
@login_required
def delete(part_id):
    """Delete a part"""
    part = Part.query.get_or_404(part_id)
    
    # Check if part is used in any repairs
    if part.repair_parts:
        flash('Cannot delete part because it is used in repairs', 'danger')
        return redirect(url_for('parts.view', part_id=part_id))
    
    db.session.delete(part)
    db.session.commit()
    
    flash('Part deleted successfully', 'success')
    return redirect(url_for('parts.index')) 