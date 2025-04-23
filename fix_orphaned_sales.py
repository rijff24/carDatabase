"""
Script to fix orphaned sales records.

This script:
1. Identifies sales records that don't have a valid car reference
2. Checks for inconsistencies between car.date_sold and car.sale records
3. Fixes both types of issues to ensure data integrity

Usage:
python fix_orphaned_sales.py [--fix] [--verbose]
"""

from app import create_app, db
from app.models import Car, Sale
import argparse

app = create_app()

def fix_orphaned_sales(fix_mode=True, verbose=False):
    """
    Find and fix sales without valid car references.
    
    Args:
        fix_mode (bool): If True, fix orphaned sales. If False, just report.
        verbose (bool): If True, print detailed information.
    
    Returns:
        int: Number of orphaned sales found
    """
    print("Checking for orphaned sales...")
    
    with app.app_context():
        # Find sales without a valid car
        orphaned_sales = Sale.query.filter(Sale.car == None).all()
        
        if orphaned_sales:
            print(f"Found {len(orphaned_sales)} sales without valid car references:")
            
            for sale in orphaned_sales:
                print(f"  - Sale ID {sale.sale_id}, Car ID {sale.car_id}, Date: {sale.sale_date}")
                
                if fix_mode:
                    # For now, we'll delete the orphaned sale as there's no way to recover the car
                    print(f"    Deleting orphaned sale ID {sale.sale_id}")
                    db.session.delete(sale)
            
            if fix_mode and orphaned_sales:
                db.session.commit()
                print(f"Fixed {len(orphaned_sales)} orphaned sales.")
        else:
            print("No issues found. All sales have valid car references.")
    
    return len(orphaned_sales)

def check_and_fix_car_sale_consistency(fix_mode=True, verbose=False):
    """
    Check all cars for inconsistencies between date_sold and sale records.
    
    Args:
        fix_mode (bool): If True, fix inconsistencies. If False, just report.
        verbose (bool): If True, print detailed information.
    
    Returns:
        int: Number of inconsistencies found
    """
    print("\nChecking for car/sale consistency issues...")
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
    print("Orphaned Sales and Consistency Fixer")
    print("==============================")
    
    parser = argparse.ArgumentParser(description='Fix orphaned sales and data consistency issues')
    parser.add_argument('--no-fix', action='store_true', help='Report but do not fix issues')
    parser.add_argument('--verbose', action='store_true', help='Print detailed information')
    args = parser.parse_args()
    
    fix_mode = not args.no_fix
    
    # First check for orphaned sales
    orphaned_count = fix_orphaned_sales(fix_mode=fix_mode, verbose=args.verbose)
    
    # Then check for consistency issues
    inconsistent_count = check_and_fix_car_sale_consistency(fix_mode=fix_mode, verbose=args.verbose)
    
    # Report overall results
    if orphaned_count == 0 and inconsistent_count == 0:
        print("\nSuccess! No data integrity issues found.")
    else:
        total_issues = orphaned_count + inconsistent_count
        print(f"\nFound {total_issues} total issues.")
        if not fix_mode:
            print("Run without --no-fix flag to repair these issues.") 