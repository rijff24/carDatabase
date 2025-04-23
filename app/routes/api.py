from flask import Blueprint, jsonify, request
from app.models import Car
from sqlalchemy import func

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/vehicle-models')
def vehicle_models():
    """Get all vehicle models for a specific make"""
    make = request.args.get('make')
    
    if not make:
        return jsonify({'error': 'Vehicle make is required'}), 400
    
    # Query for models matching the specified make
    models = Car.query.with_entities(Car.vehicle_model).filter(
        Car.vehicle_make == make
    ).distinct().order_by(Car.vehicle_model).all()
    
    # Extract model names from the query results
    model_names = [model[0] for model in models]
    
    return jsonify({'models': model_names})

@api_bp.route('/vehicle-makes')
def vehicle_makes():
    """Get all unique vehicle makes"""
    makes = Car.query.with_entities(Car.vehicle_make).distinct().order_by(Car.vehicle_make).all()
    make_names = [make[0] for make in makes]
    
    return jsonify({'makes': make_names})

@api_bp.route('/stands')
def stands():
    """Get all stands with basic information"""
    from app.models import Stand
    
    stands_data = []
    stands = Stand.query.all()
    
    for stand in stands:
        stands_data.append({
            'id': stand.stand_id,
            'name': stand.stand_name,
            'location': stand.location,
            'capacity': stand.capacity
        })
    
    return jsonify({'stands': stands_data}) 