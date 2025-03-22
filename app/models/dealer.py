from app import db
from datetime import datetime

class Dealer(db.Model):
    """Dealer model representing the dealers table"""
    __tablename__ = 'dealers'

    dealer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dealer_name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(200))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, Suspended
    
    # Performance metrics
    total_sales = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    avg_days_to_sell = db.Column(db.Float, default=0.0)
    last_sale_date = db.Column(db.DateTime)
    
    # Relationships
    cars = db.relationship('Car', primaryjoin="Dealer.dealer_id==Car.dealer_id", lazy='dynamic', overlaps="dealer")
    
    def update_performance_metrics(self):
        """Update the dealer's performance metrics based on sales"""
        self.total_sales = self.cars.filter_by(repair_status='Sold').count()
        
        # Calculate total revenue
        sold_cars = self.cars.filter_by(repair_status='Sold').all()
        total_revenue = sum(car.sale_price for car in sold_cars if car.sale_price)
        self.total_revenue = total_revenue
        
        # Calculate average days to sell
        days_to_sell = []
        for car in sold_cars:
            if car.date_added_to_stand and car.date_sold:
                days = (car.date_sold - car.date_added_to_stand).days
                if days >= 0:  # Sanity check
                    days_to_sell.append(days)
        
        if days_to_sell:
            self.avg_days_to_sell = sum(days_to_sell) / len(days_to_sell)
        
        # Update last sale date
        if sold_cars:
            self.last_sale_date = max(car.date_sold for car in sold_cars if car.date_sold)
    
    def __repr__(self):
        return f'<Dealer {self.dealer_name}>' 