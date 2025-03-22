from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.dealer import Dealer
from app.models.car import Car
from datetime import datetime

dealers_bp = Blueprint('dealers', __name__)

@dealers_bp.route('/')
@login_required
def index():
    dealers = Dealer.query.all()
    for dealer in dealers:
        dealer.update_performance_metrics()
    db.session.commit()
    return render_template('dealers/index.html', dealers=dealers)

@dealers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        dealer_name = request.form.get('dealer_name')
        contact_info = request.form.get('contact_info')
        address = request.form.get('address')
        
        if not dealer_name:
            flash('Dealer name is required', 'danger')
            return render_template('dealers/create.html')
        
        # Check if a dealer with the same name already exists
        existing_dealer = Dealer.query.filter_by(dealer_name=dealer_name).first()
        if existing_dealer:
            flash(f'Dealer with name "{dealer_name}" already exists', 'danger')
            return render_template('dealers/create.html')
        
        dealer = Dealer(
            dealer_name=dealer_name,
            contact_info=contact_info,
            address=address,
            date_joined=datetime.utcnow()
        )
        
        try:
            db.session.add(dealer)
            db.session.commit()
            flash('Dealer added successfully', 'success')
            return redirect(url_for('dealers.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding dealer: {str(e)}', 'danger')
    
    return render_template('dealers/create.html')

@dealers_bp.route('/<int:dealer_id>')
@login_required
def view(dealer_id):
    dealer = Dealer.query.get_or_404(dealer_id)
    dealer.update_performance_metrics()
    db.session.commit()
    
    # Get dealer's cars
    cars = Car.query.filter_by(dealer_id=dealer_id).all()
    
    # Get sales history (only sold cars)
    sales_history = Car.query.filter_by(
        dealer_id=dealer_id, 
        repair_status='Sold'
    ).order_by(Car.date_sold.desc()).all()
    
    return render_template('dealers/view.html', 
                          dealer=dealer, 
                          cars=cars, 
                          sales_history=sales_history)

@dealers_bp.route('/<int:dealer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(dealer_id):
    dealer = Dealer.query.get_or_404(dealer_id)
    
    if request.method == 'POST':
        new_dealer_name = request.form.get('dealer_name')
        
        # Check if another dealer with the same name exists
        if new_dealer_name != dealer.dealer_name:
            existing_dealer = Dealer.query.filter_by(dealer_name=new_dealer_name).first()
            if existing_dealer:
                flash(f'Dealer with name "{new_dealer_name}" already exists', 'danger')
                return render_template('dealers/edit.html', dealer=dealer)
        
        dealer.dealer_name = new_dealer_name
        dealer.contact_info = request.form.get('contact_info')
        dealer.address = request.form.get('address')
        dealer.status = request.form.get('status', 'Active')
        
        try:
            db.session.commit()
            flash('Dealer updated successfully', 'success')
            return redirect(url_for('dealers.view', dealer_id=dealer.dealer_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating dealer: {str(e)}', 'danger')
    
    return render_template('dealers/edit.html', dealer=dealer)

@dealers_bp.route('/<int:dealer_id>/delete', methods=['POST'])
@login_required
def delete(dealer_id):
    dealer = Dealer.query.get_or_404(dealer_id)
    
    # Check if dealer has cars associated
    car_count = Car.query.filter_by(dealer_id=dealer_id).count()
    if car_count > 0:
        flash(f'Cannot delete dealer with {car_count} associated cars', 'danger')
        return redirect(url_for('dealers.view', dealer_id=dealer_id))
    
    try:
        db.session.delete(dealer)
        db.session.commit()
        flash('Dealer deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting dealer: {str(e)}', 'danger')
    
    return redirect(url_for('dealers.index'))

@dealers_bp.route('/<int:dealer_id>/performance')
@login_required
def performance(dealer_id):
    dealer = Dealer.query.get_or_404(dealer_id)
    dealer.update_performance_metrics()
    db.session.commit()
    
    # Get sales by month (last 12 months)
    sales_by_month = db.session.query(
        db.func.strftime('%Y-%m', Car.date_sold).label('month'),
        db.func.count().label('count'),
        db.func.sum(Car.sale_price).label('revenue')
    ).filter(
        Car.dealer_id == dealer_id,
        Car.repair_status == 'Sold'
    ).group_by('month').order_by('month').all()
    
    performance_data = {
        'labels': [row.month for row in sales_by_month],
        'sales': [row.count for row in sales_by_month],
        'revenue': [float(row.revenue or 0) for row in sales_by_month]
    }
    
    return jsonify(performance_data) 