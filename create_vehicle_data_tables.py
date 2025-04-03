"""Script to create and populate vehicle years and colors tables"""
import sys
from datetime import datetime
from app import create_app, db
from app.models.car import VehicleYear, VehicleColor, Car
import os

# List of common car colors
COMMON_COLORS = [
    "Black", "White", "Silver", "Gray", "Red", "Blue", "Green", "Yellow", 
    "Orange", "Brown", "Purple", "Gold", "Beige", "Burgundy", "Champagne", 
    "Charcoal", "Bronze", "Copper", "Cream", "Maroon", "Navy", "Pink", "Tan",
    "Turquoise", "Ivory", "Pearl White", "Metallic Blue", "Metallic Gray",
    "Metallic Silver", "Matte Black"
]

def create_vehicle_data():
    """Create and populate vehicle_years and vehicle_colors tables"""
    app = create_app(os.getenv('FLASK_ENV') or 'default')
    
    with app.app_context():
        created_tables = []
        
        # Create and populate vehicle_years table
        if not VehicleYear.__table__.exists(db.engine):
            VehicleYear.__table__.create(db.engine)
            created_tables.append("vehicle_years")
            
            # Generate years from 1990 to current year
            current_year = datetime.now().year
            years = list(range(1990, current_year + 1))
            
            # Add existing years from the cars table
            existing_years = db.session.query(Car.year).distinct().all()
            for year_tuple in existing_years:
                year = year_tuple[0]
                if year and year not in years:
                    years.append(year)
            
            # Sort years
            years.sort()
            
            # Add all years to the database
            for year in years:
                db.session.add(VehicleYear(year=year))
            
            db.session.commit()
            print(f"Added {len(years)} years to vehicle_years table")
        else:
            print("vehicle_years table already exists")
        
        # Create and populate vehicle_colors table
        if not VehicleColor.__table__.exists(db.engine):
            VehicleColor.__table__.create(db.engine)
            created_tables.append("vehicle_colors")
            
            # Add predefined colors
            colors = COMMON_COLORS.copy()
            
            # Add existing colors from the cars table
            existing_colors = db.session.query(Car.colour).distinct().all()
            for color_tuple in existing_colors:
                color = color_tuple[0]
                if color:
                    sanitized_color = VehicleColor.sanitize_name(color)
                    if sanitized_color and sanitized_color not in colors:
                        colors.append(sanitized_color)
            
            # Sort colors alphabetically
            colors.sort()
            
            # Add all colors to the database
            for color in colors:
                db.session.add(VehicleColor(name=color))
            
            db.session.commit()
            print(f"Added {len(colors)} colors to vehicle_colors table")
        else:
            print("vehicle_colors table already exists")
        
        return created_tables

if __name__ == "__main__":
    print("Creating vehicle data tables...")
    created = create_vehicle_data()
    
    if created:
        print(f"Successfully created tables: {', '.join(created)}")
        sys.exit(0)
    else:
        print("No new tables created. Tables may already exist.")
        sys.exit(0) 