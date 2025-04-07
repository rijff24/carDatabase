from app import create_app, db
from app.models import Car, Sale
from sqlalchemy import text

app = create_app()

def list_all_sales():
    """List all sales in the database"""
    with app.app_context():
        sales = Sale.query.all()
        
        print(f"Found {len(sales)} sales records:")
        for sale in sales:
            car = Car.query.get(sale.car_id)
            car_details = f"{car.vehicle_make} {car.vehicle_model}" if car else "Unknown car"
            print(f"Sale ID: {sale.sale_id}, Car ID: {sale.car_id} ({car_details}), Date: {sale.sale_date}")
            
        # Check for duplicate sales for the same car
        with db.engine.connect() as conn:
            duplicates = conn.execute(
                text("SELECT car_id, COUNT(*) as count FROM sales GROUP BY car_id HAVING count > 1")
            ).fetchall()
            
            if duplicates:
                print("\nFound cars with multiple sale records:")
                for car_id, count in duplicates:
                    car = Car.query.get(car_id)
                    car_details = f"{car.vehicle_make} {car.vehicle_model}" if car else "Unknown car"
                    print(f"Car ID: {car_id} ({car_details}) has {count} sale records")

def check_car_sales(car_id):
    """Check sales for a specific car"""
    with app.app_context():
        car = Car.query.get(car_id)
        if not car:
            print(f"Car with ID {car_id} not found!")
            return
            
        sales = Sale.query.filter_by(car_id=car_id).all()
        print(f"Car ID: {car_id} ({car.vehicle_make} {car.vehicle_model})")
        print(f"Car date_sold: {car.date_sold}")
        print(f"Found {len(sales)} sales records:")
        
        for sale in sales:
            print(f"  Sale ID: {sale.sale_id}, Date: {sale.sale_date}, Price: {sale.sale_price}")

def fix_inconsistencies():
    """Fix inconsistencies between cars and sales"""
    with app.app_context():
        # Find cars marked as sold but without a sale record
        cars_sold_no_sale = Car.query.filter(Car.date_sold.isnot(None)).all()
        for car in cars_sold_no_sale:
            sales = Sale.query.filter_by(car_id=car.car_id).all()
            if not sales:
                print(f"Car ID {car.car_id} is marked as sold but has no sale record. Fixing...")
                car.date_sold = None
                car.repair_status = 'On Display' if car.stand_id else 'Waiting for Repairs'
                db.session.add(car)
                
        # Find duplicate sales for the same car
        with db.engine.connect() as conn:
            duplicates = conn.execute(
                text("SELECT car_id, COUNT(*) as count FROM sales GROUP BY car_id HAVING count > 1")
            ).fetchall()
            
            for car_id, count in duplicates:
                print(f"Car ID {car_id} has {count} sales records. Cleaning up...")
                
                # Get all sales for this car
                sales = Sale.query.filter_by(car_id=car_id).order_by(Sale.sale_date.desc()).all()
                
                # Keep only the most recent sale
                for i, sale in enumerate(sales):
                    if i > 0:  # Skip the first (most recent) one
                        print(f"  Deleting sale ID {sale.sale_id}")
                        db.session.delete(sale)
                        
        # Commit all changes
        db.session.commit()
        print("Fixes applied.")

def unsell_car(car_id):
    """Force unsell a specific car"""
    with app.app_context():
        car = Car.query.get(car_id)
        if not car:
            print(f"Car with ID {car_id} not found!")
            return
            
        # Delete all sales for this car
        sales = Sale.query.filter_by(car_id=car_id).all()
        for sale in sales:
            print(f"Deleting sale ID {sale.sale_id} for car ID {car_id}")
            db.session.delete(sale)
            
        # Reset car status
        car.date_sold = None
        car.sale_price = None
        if car.stand_id:
            stand_name = car.stand.stand_name if car.stand else "Stand"
            car.repair_status = 'On Display'
            car.current_location = f"Stand: {stand_name}"
        else:
            car.repair_status = 'Waiting for Repairs'
            car.current_location = 'Base (Awaiting Repairs)'
            
        db.session.commit()
        print(f"Car ID {car_id} has been forcibly unsold.")

if __name__ == "__main__":
    print("Sales Database Management Tool")
    print("==============================")
    
    list_all_sales()
    print("\nChecking car ID 4:")
    check_car_sales(4)
    
    answer = input("\nWould you like to fix inconsistencies? (y/n): ")
    if answer.lower() == 'y':
        fix_inconsistencies()
        
    answer = input("\nWould you like to force unsell car ID 4? (y/n): ")
    if answer.lower() == 'y':
        unsell_car(4)
        
    # Re-check after changes
    if answer.lower() == 'y':
        print("\nAfter changes:")
        check_car_sales(4)
        list_all_sales() 