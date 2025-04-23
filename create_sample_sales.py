from app import create_app, db
from app.models import Car, Dealer, Sale
from datetime import datetime, date, timedelta
import random
import decimal

def main():
    """Insert sample sales data for testing reports"""
    app = create_app()
    
    with app.app_context():
        print("Starting sample sales data creation...")
        
        # Get available cars that are not yet sold
        available_cars = Car.query.filter(Car.date_sold.is_(None)).all()
        
        if not available_cars:
            print("No available cars found. Please add some cars to the database first.")
            return
            
        # Get all dealers
        dealers = Dealer.query.all()
        
        if not dealers:
            print("No dealers found. Please add some dealers to the database first.")
            return
            
        # Create sample sales (one from each year 2023, 2024, 2025)
        years = [2023, 2024, 2025]
        payment_methods = ["Cash", "Bank Transfer", "Credit Card", "Financing"]
        
        # Generate sales for each year with varying months
        print(f"Found {len(available_cars)} available cars and {len(dealers)} dealers")
        
        sales_created = 0
        cars_per_year = min(len(available_cars) // len(years), 12)  # Up to 12 cars per year
        
        if cars_per_year == 0:
            print("Not enough cars available. Need at least 3 cars.")
            return
            
        print(f"Creating approximately {cars_per_year} sales per year...")
        
        # Distribute cars across years
        for year in years:
            for month in range(1, min(cars_per_year + 1, 13)):  # One sale per month up to 12
                if not available_cars:
                    print("Ran out of available cars")
                    break
                    
                # Get a car and mark it as sold
                car = available_cars.pop()
                dealer = random.choice(dealers)
                
                # Generate a sale date in the given year and month
                sale_date = date(year, month, random.randint(1, 28))
                
                # Set the car's sold date to match
                car.date_sold = sale_date
                car.repair_status = "Sold"
                
                # Calculate a reasonable sale price (10-30% markup from total cost)
                total_cost = float(car.purchase_price) + float(car.refuel_cost)
                if hasattr(car, 'total_repair_cost') and callable(getattr(car, 'total_repair_cost')):
                    total_cost += float(car.total_repair_cost)
                
                markup = random.uniform(1.1, 1.3)  # 10-30% markup
                sale_price = decimal.Decimal(str(round(total_cost * markup, 2)))
                
                # Create sale record
                sale = Sale(
                    car_id=car.car_id,
                    dealer_id=dealer.dealer_id,
                    sale_price=sale_price,
                    sale_date=sale_date,
                    payment_method=random.choice(payment_methods),
                    customer_name=f"Customer {sales_created + 1}",
                    customer_contact=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    notes=f"Sample sale for {year}-{month}"
                )
                
                # Save changes
                db.session.add(sale)
                car.sale_price = sale_price
                db.session.add(car)
                
                sales_created += 1
                print(f"Created sale for {car.vehicle_make} {car.vehicle_model} - {sale_date} - ${sale_price}")
                
        # Commit all changes
        db.session.commit()
        print(f"Successfully created {sales_created} sample sales")

if __name__ == "__main__":
    main() 