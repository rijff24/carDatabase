from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app import db
from app.models.car import VehicleMake, VehicleModel, Car
from app.models.dealer import Dealer

vehicle_data = Blueprint('vehicle_data', __name__)

@vehicle_data.route('/makes-models')
@login_required
def makes_models():
    """Display vehicle makes and models page"""
    makes = VehicleMake.query.order_by(VehicleMake.name).all()
    return render_template('vehicle_data/makes_models.html', makes=makes)

@vehicle_data.route('/api/makes')
@login_required
def get_makes():
    """API endpoint to get vehicle makes with optional filtering"""
    query = request.args.get('query', '')
    
    # Filter makes by query
    makes_query = VehicleMake.query
    if query:
        makes_query = makes_query.filter(VehicleMake.name.ilike(f'%{query}%'))
    
    # Order by name and retrieve data
    makes = makes_query.order_by(VehicleMake.name).all()
    
    # Convert to list of names
    make_names = [make.name for make in makes]
    
    return jsonify(make_names)

@vehicle_data.route('/api/models')
@login_required
def get_models():
    """API endpoint to get vehicle models with optional filtering"""
    query = request.args.get('query', '')
    make_name = request.args.get('make', '')
    
    # Filter models by query
    models_query = VehicleModel.query
    
    # Apply make filter if provided
    if make_name:
        # Find the make ID based on name
        make = VehicleMake.query.filter(db.func.lower(VehicleMake.name) == db.func.lower(make_name)).first()
        if make:
            models_query = models_query.filter(VehicleModel.make_id == make.id)
    
    # Apply search query if provided
    if query:
        models_query = models_query.filter(VehicleModel.name.ilike(f'%{query}%'))
    
    # Order by name and retrieve data
    models = models_query.order_by(VehicleModel.name).all()
    
    # Convert to list of names
    model_names = [model.name for model in models]
    
    return jsonify(model_names)

@vehicle_data.route('/api/years')
@login_required
def get_years():
    """API endpoint to get vehicle years with optional filtering"""
    query = request.args.get('query', '')
    
    # Get distinct years from cars
    years_query = db.session.query(Car.year.distinct())
    if query:
        years_query = years_query.filter(db.cast(Car.year, db.String).ilike(f'%{query}%'))
    
    # Order by year and retrieve data
    years = [str(year[0]) for year in years_query.order_by(Car.year.desc()).all()]
    
    return jsonify(years)

@vehicle_data.route('/api/colors')
@login_required
def get_colors():
    """API endpoint to get vehicle colors with optional filtering"""
    query = request.args.get('query', '')
    
    # Get distinct colors from cars
    colors_query = db.session.query(Car.colour.distinct()).filter(Car.colour != None)
    if query:
        colors_query = colors_query.filter(Car.colour.ilike(f'%{query}%'))
    
    # Order by color and retrieve data
    colors = [color[0] for color in colors_query.order_by(Car.colour).all()]
    
    return jsonify(colors)

@vehicle_data.route('/api/dealers')
@login_required
def get_dealers():
    """API endpoint to get dealers with optional filtering"""
    query = request.args.get('query', '')
    
    # Filter dealers by query
    dealers_query = Dealer.query
    if query:
        dealers_query = dealers_query.filter(Dealer.dealer_name.ilike(f'%{query}%'))
    
    # Order by name and retrieve data
    dealers = dealers_query.order_by(Dealer.dealer_name).all()
    
    # Convert to list of objects with id and name
    dealer_data = [{'id': dealer.dealer_id, 'name': dealer.dealer_name} for dealer in dealers]
    
    return jsonify(dealer_data)

@vehicle_data.route('/api/makes/<int:make_id>/models')
@login_required
def get_models_by_make(make_id):
    """API endpoint to get models for a specific make"""
    try:
        make = VehicleMake.query.get_or_404(make_id)
        models = VehicleModel.query.filter_by(make_id=make_id).order_by(VehicleModel.name).all()
        
        # Convert to JSON-serializable format
        models_data = [{'id': model.id, 'name': model.name} for model in models]
        
        return jsonify({'make_id': make_id, 'make_name': make.name, 'models': models_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehicle_data.route('/add-make', methods=['POST'])
@login_required
def add_make():
    """Add a new vehicle make"""
    name = request.form.get('name', '').strip()
    
    if not name:
        flash('Make name is required', 'danger')
        return redirect(url_for('vehicle_data.makes_models'))
    
    try:
        # Use the sanitize_name method to process the name
        sanitized_name = VehicleMake.sanitize_name(name)
        
        # Check if make already exists (case-insensitive)
        existing = VehicleMake.query.filter(
            db.func.lower(VehicleMake.name) == db.func.lower(sanitized_name)
        ).first()
        
        if existing:
            flash(f'Make "{existing.name}" already exists', 'warning')
            return redirect(url_for('vehicle_data.makes_models'))
        
        # Create new make
        new_make = VehicleMake(name=sanitized_name)
        db.session.add(new_make)
        db.session.commit()
        
        flash(f'Make "{new_make.name}" added successfully', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('A make with this name already exists', 'danger')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'An error occurred while adding the make: {str(e)}', 'danger')
    
    return redirect(url_for('vehicle_data.makes_models'))

@vehicle_data.route('/edit-make', methods=['POST'])
@login_required
def edit_make():
    """Edit an existing vehicle make"""
    make_id = request.form.get('make_id')
    name = request.form.get('name', '').strip()
    
    if not make_id or not name:
        flash('Make ID and name are required', 'danger')
        return redirect(url_for('vehicle_data.makes_models'))
    
    try:
        make = VehicleMake.query.get_or_404(make_id)
        old_name = make.name
        
        # Use the sanitize_name method to process the name
        sanitized_name = VehicleMake.sanitize_name(name)
        
        # Check if another make with this name already exists
        existing = VehicleMake.query.filter(
            db.func.lower(VehicleMake.name) == db.func.lower(sanitized_name),
            VehicleMake.id != make.id
        ).first()
        
        if existing:
            flash(f'Another make with name "{existing.name}" already exists', 'warning')
            return redirect(url_for('vehicle_data.makes_models'))
        
        make.name = sanitized_name
        db.session.commit()
        
        flash(f'Make updated from "{old_name}" to "{make.name}"', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('A make with this name already exists', 'danger')
    except SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred while updating the make', 'danger')
    
    return redirect(url_for('vehicle_data.makes_models'))

@vehicle_data.route('/delete-make', methods=['POST'])
@login_required
def delete_make():
    """Delete a vehicle make and its associated models"""
    make_id = request.form.get('make_id')
    
    if not make_id:
        flash('Make ID is required', 'danger')
        return redirect(url_for('vehicle_data.makes_models'))
    
    try:
        make = VehicleMake.query.get_or_404(make_id)
        make_name = make.name
        
        # Check if there are any cars using this make
        cars_using_make = Car.query.filter_by(vehicle_make=make.name).count()
        if cars_using_make > 0:
            flash(f'Cannot delete make "{make_name}" because it is being used by {cars_using_make} cars. '
                  f'Please update or remove those cars first.', 'warning')
            return redirect(url_for('vehicle_data.makes_models'))
        
        # Delete all models associated with this make
        models = VehicleModel.query.filter_by(make_id=make.id).all()
        for model in models:
            # Check if any cars are using this model
            cars_using_model = Car.query.filter_by(vehicle_model=model.name).count()
            if cars_using_model > 0:
                flash(f'Cannot delete make "{make_name}" because its model "{model.name}" '
                      f'is being used by {cars_using_model} cars. Please update or remove those cars first.', 'warning')
                return redirect(url_for('vehicle_data.makes_models'))
            db.session.delete(model)
        
        # Delete the make
        db.session.delete(make)
        db.session.commit()
        
        flash(f'Make "{make_name}" and its models have been deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the make: {str(e)}', 'danger')
    
    return redirect(url_for('vehicle_data.makes_models'))

@vehicle_data.route('/add-model', methods=['POST'])
@login_required
def add_model():
    """Add a new vehicle model"""
    make_id = request.form.get('make_id')
    name = request.form.get('name', '').strip()
    
    if not make_id or not name:
        flash('Make ID and model name are required', 'danger')
        return redirect(url_for('vehicle_data.makes_models'))
    
    try:
        make = VehicleMake.query.get_or_404(make_id)
        
        # Use the sanitize_name method to process the name
        sanitized_name = VehicleModel.sanitize_name(name)
        
        # Check if model already exists for this make (case-insensitive)
        existing = VehicleModel.query.filter(
            db.func.lower(VehicleModel.name) == db.func.lower(sanitized_name),
            VehicleModel.make_id == make.id
        ).first()
        
        if existing:
            flash(f'Model "{existing.name}" already exists for make "{make.name}"', 'warning')
            return redirect(url_for('vehicle_data.makes_models'))
        
        # Create new model
        new_model = VehicleModel(name=sanitized_name, make_id=make.id)
        db.session.add(new_model)
        db.session.commit()
        
        flash(f'Model "{new_model.name}" added successfully to make "{make.name}"', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('A model with this name already exists for this make', 'danger')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'An error occurred while adding the model: {str(e)}', 'danger')
    
    return redirect(url_for('vehicle_data.makes_models'))

@vehicle_data.route('/edit-model', methods=['POST'])
@login_required
def edit_model():
    """Edit an existing vehicle model"""
    model_id = request.form.get('model_id')
    make_id = request.form.get('make_id')
    name = request.form.get('name', '').strip()
    
    if not model_id or not make_id or not name:
        flash('Model ID, make ID, and name are required', 'danger')
        return redirect(url_for('vehicle_data.makes_models'))
    
    try:
        model = VehicleModel.query.get_or_404(model_id)
        make = VehicleMake.query.get_or_404(make_id)
        old_name = model.name
        
        # Use the sanitize_name method to process the name
        sanitized_name = VehicleModel.sanitize_name(name)
        
        # Check if another model with this name already exists for this make
        existing = VehicleModel.query.filter(
            db.func.lower(VehicleModel.name) == db.func.lower(sanitized_name),
            VehicleModel.make_id == make.id,
            VehicleModel.id != model.id
        ).first()
        
        if existing:
            flash(f'Another model with name "{existing.name}" already exists for make "{make.name}"', 'warning')
            return redirect(url_for('vehicle_data.makes_models'))
        
        model.name = sanitized_name
        db.session.commit()
        
        flash(f'Model updated from "{old_name}" to "{model.name}"', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('A model with this name already exists for this make', 'danger')
    except SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred while updating the model', 'danger')
    
    return redirect(url_for('vehicle_data.makes_models'))

@vehicle_data.route('/delete-model', methods=['POST'])
@login_required
def delete_model():
    """Delete a vehicle model"""
    model_id = request.form.get('model_id')
    
    if not model_id:
        flash('Model ID is required', 'danger')
        return redirect(url_for('vehicle_data.makes_models'))
    
    try:
        model = VehicleModel.query.get_or_404(model_id)
        model_name = model.name
        make_name = model.make.name
        
        # Check if there are any cars using this model
        cars_using_model = Car.query.filter_by(vehicle_model=model.name).count()
        if cars_using_model > 0:
            flash(f'Cannot delete model "{model_name}" because it is being used by {cars_using_model} cars. '
                  f'Please update or remove those cars first.', 'warning')
            return redirect(url_for('vehicle_data.makes_models'))
        
        # Delete the model
        db.session.delete(model)
        db.session.commit()
        
        flash(f'Model "{model_name}" has been deleted successfully from make "{make_name}"', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the model: {str(e)}', 'danger')
    
    return redirect(url_for('vehicle_data.makes_models'))

@vehicle_data.route('/move-model', methods=['POST'])
@login_required
def move_model():
    """Move a model to a different make"""
    model_id = request.form.get('model_id')
    new_make_id = request.form.get('new_make_id')
    
    if not model_id or not new_make_id:
        flash('Model ID and new make ID are required', 'danger')
        return redirect(url_for('vehicle_data.makes_models'))
    
    try:
        model = VehicleModel.query.get_or_404(model_id)
        new_make = VehicleMake.query.get_or_404(new_make_id)
        old_make_name = model.make.name
        model_name = model.name
        
        # Check if a model with this name already exists in the target make
        existing = VehicleModel.query.filter(
            db.func.lower(VehicleModel.name) == db.func.lower(model.name),
            VehicleModel.make_id == new_make.id,
            VehicleModel.id != model.id
        ).first()
        
        if existing:
            flash(f'A model with name "{existing.name}" already exists in make "{new_make.name}"', 'warning')
            return redirect(url_for('vehicle_data.makes_models'))
        
        # Move the model to the new make
        model.make_id = new_make.id
        db.session.commit()
        
        flash(f'Model "{model_name}" moved successfully from make "{old_make_name}" to "{new_make.name}"', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'An error occurred while moving the model: {str(e)}', 'danger')
    
    return redirect(url_for('vehicle_data.makes_models')) 