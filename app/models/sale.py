from app import db
from datetime import datetime
from sqlalchemy import event

class Sale(db.Model):
    """
    Model representing a car sale transaction.
    """
    __tablename__ = 'sales'
    
    sale_id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id', ondelete='CASCADE'), nullable=False)
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealers.dealer_id'), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    payment_method = db.Column(db.String(50))
    customer_name = db.Column(db.String(100))
    customer_contact = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    car = db.relationship('Car', back_populates='sale')
    dealer = db.relationship('Dealer', back_populates='sales')
    
    def __init__(self, car_id, dealer_id, sale_price, sale_date=None, 
                 payment_method=None, customer_name=None, customer_contact=None, notes=None):
        self.car_id = car_id
        self.dealer_id = dealer_id
        self.sale_price = sale_price
        self.sale_date = sale_date or datetime.now().date()
        self.payment_method = payment_method
        self.customer_name = customer_name
        self.customer_contact = customer_contact
        self.notes = notes
        
    def __repr__(self):
        return f"<Sale {self.sale_id}: Car {self.car_id} sold for {self.sale_price}>"
        
    @property
    def profit(self):
        """Calculate profit (sale price - total cost)"""
        if not self.car or not hasattr(self.car, 'total_investment'):
            return 0
        return float(self.sale_price) - float(self.car.total_investment)
        
    @property
    def profit_margin(self):
        """Calculate profit margin as a percentage"""
        if not self.sale_price or float(self.sale_price) == 0:
            return 0
        return (self.profit / float(self.sale_price)) * 100 

# Add event listener to validate car_id before insert
@event.listens_for(Sale, 'before_insert')
def validate_car_id(mapper, connection, sale):
    from app.models import Car
    
    # Check if car exists
    car_exists = connection.execute(
        db.select(db.func.count(Car.car_id)).where(Car.car_id == sale.car_id)
    ).scalar() > 0
    
    if not car_exists:
        raise ValueError(f"Cannot create sale: Car with ID {sale.car_id} does not exist")
        
# Add event listener to update car.date_sold
@event.listens_for(Sale, 'after_insert')
def update_car_date_sold(mapper, connection, sale):
    from app.models import Car
    
    # Update the car's date_sold to match the sale date
    connection.execute(
        db.update(Car).where(Car.car_id == sale.car_id).values(date_sold=sale.sale_date)
    ) 