from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from app import db
from app.models.repair_provider import RepairProvider
from app.utils.forms import RepairProviderForm, RepairForm
from app.utils.validators import validate_params, validate_form
from app.utils.helpers import safe_get_or_404

providers_bp = Blueprint('providers', __name__)

VALID_SERVICE_TYPES = ['All', 'Upholstery', 'Panel Beating', 'Tires/Suspension', 'Workshop Repairs', 
                       'Car Wash', 'Air Conditioning', 'Brakes/Clutch', 'Windscreen', 'Other']
VALID_SORT_FIELDS = ['provider_name', 'service_type', 'location', 'rating']
VALID_SORT_DIRS = ['asc', 'desc']

@providers_bp.route('/')
@login_required
@validate_params(
    search=(str, False, None),
    service_type=(str, False, 'All', lambda x: x in VALID_SERVICE_TYPES),
    rating=(int, False, None, lambda x: 1 <= x <= 5),
    sort_by=(str, False, 'provider_name', lambda x: x in VALID_SORT_FIELDS),
    sort_dir=(str, False, 'asc', lambda x: x in VALID_SORT_DIRS)
)
def index():
    """List all repair providers with filtering options"""
    # Get validated parameters
    params = request.validated_params
    search = params.get('search')
    service_type = params.get('service_type', 'All')
    rating = params.get('rating')
    sort_by = params.get('sort_by', 'provider_name')
    sort_dir = params.get('sort_dir', 'asc')
    
    # Start with base query
    query = RepairProvider.query
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            RepairProvider.provider_name.ilike(search_term) | 
            RepairProvider.location.ilike(search_term) |
            RepairProvider.contact_info.ilike(search_term)
        )
    
    if service_type != 'All':
        query = query.filter(RepairProvider.service_type == service_type)
        
    if rating:
        query = query.filter(RepairProvider.rating == rating)
    
    # Apply sorting
    if sort_dir == 'desc':
        query = query.order_by(getattr(RepairProvider, sort_by).desc())
    else:
        query = query.order_by(getattr(RepairProvider, sort_by))
    
    providers = query.all()
    
    return render_template(
        'providers/index.html', 
        providers=providers,
        service_types=VALID_SERVICE_TYPES,
        current_search=search,
        current_service_type=service_type,
        current_rating=rating,
        current_sort=sort_by,
        current_sort_dir=sort_dir
    )

@providers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new repair provider"""
    is_modal = request.args.get('modal', '0') == '1'
    return_to = request.args.get('return_to', None)
    
    if request.method == 'POST':
        form = RepairProviderForm(formdata=request.form)
        
        if form.validate_on_submit():
            # If custom service type is selected, use that instead
            service_type = form.custom_service_type.data if form.service_type.data == 'custom' else form.service_type.data
            
            provider = RepairProvider(
                provider_name=form.provider_name.data,
                service_type=service_type,
                contact_info=form.contact_info.data,
                location=form.location.data,
                notes=form.notes.data,
                rating=form.rating.data
            )
            
            db.session.add(provider)
            db.session.commit()
            
            flash(f'Service provider "{provider.provider_name}" has been added successfully.', 'success')
            
            if return_to:
                return redirect(return_to)
            else:
                return redirect(url_for('providers.index'))
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        form = RepairProviderForm()
    
    # If it's a modal request, return only the form without the base template
    try:
        if is_modal:
            return render_template('providers/modal_form.html', form=form)
        
        return render_template('providers/create.html', form=form)
    except Exception as e:
        if is_modal:
            return jsonify({
                'success': False,
                'message': f"Error loading form: {str(e)}"
            }), 500
        raise

@providers_bp.route('/create-ajax', methods=['POST'])
@login_required
def create_ajax():
    """Create a new provider via AJAX"""
    try:
        form = RepairProviderForm(formdata=request.form)
        
        if form.validate_on_submit():
            # If custom service type is selected, use that instead
            service_type = form.custom_service_type.data if form.service_type.data == 'custom' else form.service_type.data
            
            provider = RepairProvider(
                provider_name=form.provider_name.data,
                service_type=service_type,
                contact_info=form.contact_info.data,
                location=form.location.data,
                notes=form.notes.data,
                rating=form.rating.data
            )
            
            db.session.add(provider)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'provider_id': provider.provider_id,
                'provider_name': provider.provider_name,
                'service_type': provider.service_type,
                'message': f'Provider "{provider.provider_name}" added successfully'
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

@providers_bp.route('/<int:provider_id>')
@login_required
@validate_params(provider_id=(int, True))
def view(provider_id):
    provider = safe_get_or_404(RepairProvider, provider_id, f"Provider with ID {provider_id} not found")
    return render_template('providers/view.html', provider=provider)

@providers_bp.route('/<int:provider_id>/edit', methods=['GET', 'POST'])
@login_required
@validate_params(provider_id=(int, True))
def edit(provider_id):
    provider = safe_get_or_404(RepairProvider, provider_id, f"Provider with ID {provider_id} not found")
    
    if request.method == 'POST':
        form = RepairProviderForm(formdata=request.form, obj=provider)
        
        if form.validate_on_submit():
            provider.provider_name = form.provider_name.data
            # If custom service type is selected, use that instead
            provider.service_type = form.custom_service_type.data if form.service_type.data == 'custom' else form.service_type.data
            provider.contact_info = form.contact_info.data
            provider.location = form.location.data
            provider.notes = form.notes.data
            provider.rating = form.rating.data
            
            db.session.commit()
            
            flash(f'Service provider "{provider.provider_name}" has been updated successfully.', 'success')
            return redirect(url_for('providers.view', provider_id=provider.provider_id))
        else:
            # Show what validation errors occurred
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            flash(f"Form validation failed: {', '.join(error_messages)}", 'danger')
    else:
        # Check if provider's service_type is in the standard options
        form = RepairProviderForm(obj=provider)
        # If provider service type isn't in the standard options, set to custom
        service_types = [choice[0] for choice in form.service_type.choices if choice[0] != 'custom']
        if provider.service_type not in service_types:
            form.service_type.data = 'custom'
            form.custom_service_type.data = provider.service_type
    
    return render_template('providers/edit.html', form=form, provider=provider)

@providers_bp.route('/<int:provider_id>/delete', methods=['POST'])
@login_required
@validate_params(provider_id=(int, True))
def delete(provider_id):
    provider = safe_get_or_404(RepairProvider, provider_id, f"Provider with ID {provider_id} not found")
    provider_name = provider.provider_name
    
    # Check if provider has repairs before deleting
    if provider.repairs:
        flash(f'Cannot delete "{provider_name}" because it has {len(provider.repairs)} associated repairs.', 'danger')
        return redirect(url_for('providers.view', provider_id=provider_id))
    
    db.session.delete(provider)
    db.session.commit()
    
    flash(f'Service provider "{provider_name}" has been deleted.', 'success')
    return redirect(url_for('providers.index'))

@providers_bp.route('/<int:provider_id>/service-type', methods=['GET'])
@login_required
@validate_params(provider_id=(int, True))
def get_service_type(provider_id):
    """Get a provider's service type - used for auto-selecting repair type"""
    provider = safe_get_or_404(RepairProvider, provider_id, f"Provider with ID {provider_id} not found")
    return jsonify({
        'success': True,
        'service_type': provider.service_type
    })

@providers_bp.route('/normalize-service-types', methods=['GET'])
@login_required
def normalize_service_types():
    """Admin endpoint to normalize all provider service types to match repair types"""
    
    # Valid repair types from the RepairForm
    valid_types = [choice[0] for choice in RepairForm.repair_type.kwargs['choices']]
    
    providers = RepairProvider.query.all()
    updates_count = 0
    
    for provider in providers:
        # Check if the service type exactly matches one of the valid types
        if provider.service_type not in valid_types:
            original_type = provider.service_type
            
            # Do a case-insensitive match first
            for valid_type in valid_types:
                if provider.service_type.lower() == valid_type.lower():
                    provider.service_type = valid_type
                    updates_count += 1
                    break
            else:  # No match found in the for loop
                # Default to 'Other' if no match
                provider.service_type = 'Other'
                updates_count += 1
    
    if updates_count > 0:
        db.session.commit()
        flash(f'Successfully updated {updates_count} provider service types', 'success')
    else:
        flash('No provider service types needed updating', 'info')
    
    return redirect(url_for('providers.index')) 