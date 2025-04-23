from app import create_app, db
from app.models import Car, Sale
import os

app = create_app()

def check_car(car_id):
    with open("car_diagnosis.txt", "w") as f:
        with app.app_context():
            car = Car.query.get(car_id)
            if not car:
                f.write(f"Car with ID {car_id} not found\n")
                return
            
            f.write(f"CAR DETAILS:\n")
            f.write(f"============\n")
            f.write(f"Car ID: {car.car_id}\n")
            f.write(f"Make/Model: {car.vehicle_make} {car.vehicle_model}\n")
            f.write(f"Year: {car.year}\n")
            f.write(f"Is available: {car.is_available}\n")
            f.write(f"Date sold: {car.date_sold}\n")
            
            # Check for sale record
            has_sale = hasattr(car, 'sale') and car.sale is not None
            f.write(f"Has sale record: {has_sale}\n")
            
            if has_sale:
                f.write(f"\nSALE DETAILS:\n")
                f.write(f"============\n")
                f.write(f"Sale ID: {car.sale.sale_id}\n")
                f.write(f"Sale date: {car.sale.sale_date}\n")
                f.write(f"Sale price: {car.sale.sale_price}\n")
                f.write(f"Customer: {car.sale.customer_name}\n")
                
                # Identify inconsistency
                if car.is_available and car.sale.sale_date:
                    f.write(f"\nINCONSISTENCY FOUND: Car is marked as available but has a sale record!\n")
                    f.write(f"This could be why it appears in the sales report incorrectly.\n")
            
            f.write("\nSALES REPORT CHECK:\n")
            f.write(f"============\n")
            from app.reports.standard.sales_performance import SalesPerformanceReport
            report = SalesPerformanceReport()
            report_data = report.generate()
            
            # Check report logic
            found_in_report = False
            for model in report_data.get('top_models', []):
                for car_info in model.get('cars', []):
                    if car_info.get('car_id') == car_id:
                        found_in_report = True
                        f.write(f"Car found in report under {model['make']} {model['model']}\n")
                        f.write(f"Report car details: {car_info}\n")
            
            if not found_in_report:
                f.write("Car NOT found in sales report\n")
            
            # Check SQL query directly
            f.write("\nSALES QUERY DEBUG:\n")
            f.write(f"============\n")
            from sqlalchemy import extract
            
            # Similar to the report's logic
            if car.date_sold:
                year = car.date_sold.year
                f.write(f"Checking sales for year: {year}\n")
                date_filter = extract('year', Sale.sale_date) == year
                sales_with_car = Sale.query.join(Car).filter(date_filter).filter(Car.car_id == car_id).all()
                f.write(f"Found {len(sales_with_car)} sales for car ID {car_id} in year {year}\n")
                
                for sale in sales_with_car:
                    f.write(f"Sale ID: {sale.sale_id}, Car ID: {sale.car_id}, Date: {sale.sale_date}\n")
    
    print(f"Diagnosis complete. Results written to car_diagnosis.txt")

def fix_car(car_id):
    """Fix the inconsistency between car.date_sold and the sale record."""
    with app.app_context():
        car = Car.query.get(car_id)
        if not car:
            print(f"Car with ID {car_id} not found")
            return False
        
        has_sale = hasattr(car, 'sale') and car.sale is not None
        
        # Case 1: Car has a sale record but date_sold is None
        if has_sale and car.date_sold is None:
            print(f"Fixing Car ID {car_id}: Setting date_sold to match sale date {car.sale.sale_date}")
            car.date_sold = car.sale.sale_date
            db.session.commit()
            return True
            
        # Case 2: Car's date_sold doesn't match sale date
        if has_sale and car.date_sold != car.sale.sale_date:
            print(f"Fixing Car ID {car_id}: Updating date_sold from {car.date_sold} to {car.sale.sale_date}")
            car.date_sold = car.sale.sale_date
            db.session.commit()
            return True
            
        # Case 3: Car is marked as sold but has no sale record
        if car.date_sold is not None and not has_sale:
            print(f"Fixing Car ID {car_id}: Clearing date_sold field as no sale record exists")
            car.date_sold = None
            db.session.commit()
            return True
            
        print(f"No inconsistency found for Car ID {car_id}")
        return False

if __name__ == "__main__":
    check_car(4)  # Check car with ID 4
    
    # Ask for confirmation before fixing
    response = input("Do you want to fix the inconsistency? (y/n): ")
    if response.lower() == 'y':
        if fix_car(4):
            print("Car has been fixed. Running check again to confirm...")
            check_car(4)
        else:
            print("No fix was necessary.")
    else:
        print("Fix operation cancelled.") 