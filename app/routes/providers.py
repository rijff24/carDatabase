from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import db
from app.models.repair_provider import RepairProvider
from app.utils.forms import RepairProviderForm
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
    if request.method == 'POST':
        form = RepairProviderForm(formdata=request.form)
        
        if form.validate_on_submit():
            provider = RepairProvider(
                provider_name=form.provider_name.data,
                service_type=form.service_type.data,
                contact_info=form.contact_info.data,
                location=form.location.data,
                notes=form.notes.data,
                rating=form.rating.data
            )
            
            db.session.add(provider)
            db.session.commit()
            
            flash(f'Service provider "{provider.provider_name}" has been added successfully.', 'success')
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
    
    return render_template('providers/create.html', form=form)

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
            provider.service_type = form.service_type.data
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
        form = RepairProviderForm(obj=provider)
    
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