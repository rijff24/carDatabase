"""
Test script for unselling a car - manual testing purpose
"""
from app import create_app, db
from app.models import Car, Sale

app = create_app()

def check_car_sold_status(car_id):
    """Check if a car is sold and print its details"""
    with app.app_context():
        car = Car.query.get(car_id)
        if not car:
            print(f"Car with ID {car_id} not found!")
            return
        
        # Build output string
        output = []
        output.append(f"Car ID: {car.car_id}")
        output.append(f"Make/Model: {car.vehicle_make} {car.vehicle_model}")
        output.append(f"Date Sold: {car.date_sold}")
        
        # Handle the multiple rows warning with a query instead of accessing car.sale
        sale = Sale.query.filter_by(car_id=car.car_id).first()
        output.append(f"Has Sale Record: {sale is not None}")
        
        output.append(f"Current Location: {car.current_location}")
        output.append(f"Repair Status: {car.repair_status}")
        
        if sale:
            output.append(f"Sale Price: {sale.sale_price}")
            output.append(f"Sale Date: {sale.sale_date}")
        
        # Print all at once
        print("\n".join(output))

if __name__ == "__main__":
    car_id = 4  # Change this to test different cars
    check_car_sold_status(car_id) 