from app import create_app, db
from app.models import Car, Dealer, Sale
from datetime import datetime, date, timedelta
import random
import decimal

def main():
    """Add sample sales data for different years to test reports"""
    app = create_app()
    
    with app.app_context():
        print("Starting sample sales data creation...")
        
        # Get available cars 
        cars = Car.query.all()
        
        if not cars:
            print("No cars found. Please add cars to the database first.")
            return
            
        # Get all dealers
        dealers = Dealer.query.all()
        
        if not dealers:
            print("No dealers found. Please add dealers to the database first.")
            return
            
        # Create sample sales for years 2023, 2024, and 2025
        create_historical_sales(cars, dealers)
        
        print("Successfully created sample sales!")

def create_historical_sales(cars, dealers):
    """Create sales for different years to test reports"""
    years = [2023, 2024, 2025]
    payment_methods = ["Cash", "Bank Transfer", "Credit Card", "Financing"]
    
    # Create sales data for each year
    for year in years:
        # Create four sales for each year (one per quarter)
        for quarter in range(1, 5):
            # Determine month in the quarter
            month = (quarter - 1) * 3 + random.randint(1, 3)
            
            # Pick a random day
            day = random.randint(1, 28)
            
            # Create the sale date
            sale_date = date(year, month, day)
            
            # Pick a car and dealer
            car = random.choice(cars)
            dealer = random.choice(dealers)
            
            # Calculate sale price (10-30% markup)
            base_price = 180000.00 + random.randint(-30000, 50000)
            markup = random.uniform(1.1, 1.3)
            sale_price = decimal.Decimal(str(round(base_price * markup, 2)))
            
            # Create the sale
            sale = Sale(
                car_id=car.car_id,
                dealer_id=dealer.dealer_id,
                sale_price=sale_price,
                sale_date=sale_date,
                payment_method=random.choice(payment_methods),
                customer_name=f"Customer {year}-{quarter}",
                customer_contact=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                notes=f"Sample sale for {year} Q{quarter}"
            )
            
            # Update car details to match the sale
            car.date_sold = sale_date
            car.repair_status = "Sold"
            car.sale_price = sale_price
            
            # Save to database
            db.session.add(sale)
            db.session.add(car)
            
            print(f"Created sale: {year}-{month}-{day} - {car.vehicle_make} {car.vehicle_model} - ${sale_price}")
    
    # Commit all changes
    db.session.commit()

if __name__ == "__main__":
    main() 