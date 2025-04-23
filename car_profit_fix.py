from app.models.car import Car
from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta
from sqlalchemy import func

# Add the profit property to the Car model
def profit(self):
    """Calculate profit (sale price - total investment)"""
    if not self.sale_price or not self.date_sold:
        return None
    return float(self.sale_price) - float(self.total_investment)

# Add the method to the Car class
Car.profit = hybrid_property(profit)

# Now let's test if our fix works
try:
    # Query for sold cars in the last 30 days
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    sold_cars = Car.query.filter(Car.date_sold >= thirty_days_ago).all()
    
    print(f"Found {len(sold_cars)} cars sold in the last 30 days")
    
    # Try to access profit on each car
    for car in sold_cars:
        profit = car.profit
        print(f"Car {car.car_id}: {car.vehicle_make} {car.vehicle_model} - Profit: {profit}")
    
    # Calculate average profit
    profits = [car.profit for car in sold_cars if car.profit is not None]
    avg_profit = sum(profits) / len(profits) if profits else 0
    print(f"Average profit: {avg_profit}")
    
    print("The profit property was successfully added to the Car model!")
except Exception as e:
    print(f"Error: {e}") 