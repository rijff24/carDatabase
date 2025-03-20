from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import db
from app.models.repair_provider import RepairProvider
from app.utils.forms import RepairProviderForm

providers_bp = Blueprint('providers', __name__)

@providers_bp.route('/')
@login_required
def index():
    providers = RepairProvider.query.all()
    return render_template('providers/index.html', providers=providers)

@providers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = RepairProviderForm()
    
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
    
    return render_template('providers/create.html', form=form)

@providers_bp.route('/<int:provider_id>')
@login_required
def view(provider_id):
    provider = RepairProvider.query.get_or_404(provider_id)
    return render_template('providers/view.html', provider=provider)

@providers_bp.route('/<int:provider_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(provider_id):
    provider = RepairProvider.query.get_or_404(provider_id)
    form = RepairProviderForm(obj=provider)
    
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
    
    return render_template('providers/edit.html', form=form, provider=provider)

@providers_bp.route('/<int:provider_id>/delete', methods=['POST'])
@login_required
def delete(provider_id):
    provider = RepairProvider.query.get_or_404(provider_id)
    provider_name = provider.provider_name
    
    # Check if provider has repairs before deleting
    if provider.repairs:
        flash(f'Cannot delete "{provider_name}" because it has {len(provider.repairs)} associated repairs.', 'danger')
        return redirect(url_for('providers.view', provider_id=provider_id))
    
    db.session.delete(provider)
    db.session.commit()
    
    flash(f'Service provider "{provider_name}" has been deleted.', 'success')
    return redirect(url_for('providers.index')) 