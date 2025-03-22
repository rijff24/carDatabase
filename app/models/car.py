from datetime import datetime
from app import db

class Car(db.Model):
    """Car model representing the cars table"""
    __tablename__ = 'cars'

    car_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_name = db.Column(db.String(100), nullable=False)
    vehicle_make = db.Column(db.String(50), nullable=False)
    vehicle_model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    colour = db.Column(db.String(50), nullable=False)
    dekra_condition = db.Column(db.String(20), nullable=False)
    licence_number = db.Column(db.String(20), nullable=False)
    registration_number = db.Column(db.String(20), nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    recon_cost = db.Column(db.Numeric(10, 2), nullable=True)
    final_cost_price = db.Column(db.Numeric(10, 2), nullable=True)
    source = db.Column(db.String(50), nullable=False)
    date_bought = db.Column(db.Date, nullable=False, default=datetime.now().date)
    date_added_to_stand = db.Column(db.Date, nullable=True)
    date_sold = db.Column(db.Date, nullable=True)
    refuel_cost = db.Column(db.Numeric(10, 2), default=0.00)
    current_location = db.Column(db.String(100), nullable=False)
    repair_status = db.Column(db.String(30), nullable=False)
    stand_id = db.Column(db.Integer, db.ForeignKey('stands.stand_id'), nullable=True)
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealers.dealer_id'), nullable=True)
    sale_price = db.Column(db.Numeric(10, 2), nullable=True)

    # Relationships
    repairs = db.relationship('Repair', backref='car', lazy='dynamic', cascade='all, delete-orphan')
    stand = db.relationship('Stand', backref='cars')
    dealer = db.relationship('Dealer', foreign_keys=[dealer_id])

    def __repr__(self):
        return f'<Car {self.vehicle_make} {self.vehicle_model} ({self.year})>'
    
    @property
    def days_in_recon(self):
        """Calculate days in reconditioning"""
        if not self.date_added_to_stand or not self.date_bought:
            return None
        return (self.date_added_to_stand - self.date_bought).days
    
    @property
    def days_on_stand(self):
        """Calculate days on stand"""
        if not self.date_sold or not self.date_added_to_stand:
            return None
        return (self.date_sold - self.date_added_to_stand).days
    
    @property
    def total_repair_cost(self):
        """Calculate total repair costs for this car"""
        return sum(repair.repair_cost for repair in self.repairs.all())
    
    @property
    def profit(self):
        """Calculate profit from sale"""
        if not self.sale_price:
            return None
        return self.sale_price - (self.purchase_price + self.total_repair_cost + self.refuel_cost)
    
    @property
    def commission(self):
        """Calculate commission based on profit"""
        profit = self.profit
        if profit is None:
            return None
        return 10000 if profit > 30000 else 5000
    
    @property
    def total_investment(self):
        """Calculate total investment in the car"""
        return self.purchase_price + self.total_repair_cost + self.refuel_cost
    
    @property
    def sold(self):
        """Check if the car is sold"""
        return self.date_sold is not None 