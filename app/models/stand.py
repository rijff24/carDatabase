from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func
from datetime import datetime

class Stand(db.Model):
    """Stand model representing the stands table"""
    __tablename__ = 'stands'

    stand_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stand_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    capacity = db.Column(db.Integer, default=10)
    date_created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    additional_info = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Stand {self.stand_name}>'
    
    @hybrid_property
    def current_car_count(self):
        """Return the number of cars currently on this stand"""
        from app.models.car import Car
        return Car.query.filter_by(stand_id=self.stand_id, date_sold=None).count()
    
    @hybrid_property
    def occupancy_rate(self):
        """Return the occupancy rate as a percentage"""
        if self.capacity == 0:
            return 0
        return (self.current_car_count / self.capacity) * 100
    
    @hybrid_property
    def cars_sold_count(self):
        """Return the number of cars sold from this stand"""
        from app.models.car import Car
        return Car.query.filter(Car.stand_id == self.stand_id, Car.date_sold.isnot(None)).count()
    
    @hybrid_property
    def avg_days_on_stand(self):
        """Return the average number of days cars spent on this stand before being sold"""
        from app.models.car import Car
        from sqlalchemy import func
        
        cars = Car.query.filter(
            Car.stand_id == self.stand_id, 
            Car.date_sold.isnot(None),
            Car.date_added_to_stand.isnot(None)
        ).all()
        
        if not cars:
            return 0
            
        total_days = sum((car.date_sold - car.date_added_to_stand).days for car in cars)
        return total_days / len(cars)
    
    @hybrid_property
    def total_profit(self):
        """Return the total profit from cars sold from this stand"""
        from app.models.car import Car
        
        cars = Car.query.filter(
            Car.stand_id == self.stand_id,
            Car.date_sold.isnot(None)
        ).all()
        
        return sum(car.profit or 0 for car in cars) 