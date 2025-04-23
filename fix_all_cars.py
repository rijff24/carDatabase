from app import create_app, db
from app.models import Car, Sale
import argparse

app = create_app()

def check_and_fix_cars(fix_mode=False, verbose=False):
    """
    Check all cars for inconsistencies between date_sold and sale records.
    
    Args:
        fix_mode (bool): If True, fix inconsistencies. If False, just report.
        verbose (bool): If True, print detailed information.
    
    Returns:
        int: Number of inconsistencies found
    """
    inconsistencies = 0
    fixed_count = 0
    
    with app.app_context():
        # Get all cars
        cars = Car.query.all()
        print(f"Checking {len(cars)} cars for inconsistencies...")
        
        for car in cars:
            has_sale = hasattr(car, 'sale') and car.sale is not None
            
            # Case 1: Car has a sale record but date_sold is None
            if has_sale and car.date_sold is None:
                inconsistencies += 1
                print(f"Car ID {car.car_id} ({car.full_name}): Has sale record but date_sold is None")
                
                if fix_mode:
                    print(f"  - Fixing: Setting date_sold to {car.sale.sale_date}")
                    car.date_sold = car.sale.sale_date
                    fixed_count += 1
                
            # Case 2: Car's date_sold doesn't match sale date
            elif has_sale and car.date_sold != car.sale.sale_date:
                inconsistencies += 1
                print(f"Car ID {car.car_id} ({car.full_name}): date_sold ({car.date_sold}) doesn't match sale date ({car.sale.sale_date})")
                
                if fix_mode:
                    print(f"  - Fixing: Updating date_sold to {car.sale.sale_date}")
                    car.date_sold = car.sale.sale_date
                    fixed_count += 1
                
            # Case 3: Car is marked as sold but has no sale record
            elif car.date_sold is not None and not has_sale:
                inconsistencies += 1
                print(f"Car ID {car.car_id} ({car.full_name}): Has date_sold set ({car.date_sold}) but no sale record")
                
                if fix_mode:
                    print(f"  - Fixing: Clearing date_sold field")
                    car.date_sold = None
                    fixed_count += 1
            
            # Everything is consistent
            elif verbose:
                print(f"Car ID {car.car_id} ({car.full_name}): OK - {'Sold' if not car.is_available else 'Available'}")
        
        # Commit changes if any fixes were made
        if fix_mode and fixed_count > 0:
            db.session.commit()
            print(f"\nFixed {fixed_count} cars in the database.")
    
    return inconsistencies

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check and fix inconsistencies between car.date_sold and sale records')
    parser.add_argument('--fix', action='store_true', help='Fix inconsistencies (default is to just report)')
    parser.add_argument('--verbose', action='store_true', help='Print detailed information')
    args = parser.parse_args()
    
    print("Car Sales Data Consistency Checker")
    print("==================================")
    
    inconsistencies = check_and_fix_cars(fix_mode=args.fix, verbose=args.verbose)
    
    if inconsistencies == 0:
        print("\nSuccess! All cars are consistent.")
    else:
        print(f"\nFound {inconsistencies} inconsistencies.")
        if not args.fix:
            print("Run with --fix flag to repair these issues.") 