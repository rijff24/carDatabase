from app import create_app, db
from app.models import Sale
from sqlalchemy import inspect

def main():
    """Create the sales table in the database if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        table_exists = 'sales' in inspector.get_table_names()
        
        if table_exists:
            print("Sales table already exists.")
        else:
            # Create the sales table
            print("Creating sales table...")
            # This creates only the sales table
            Sale.__table__.create(db.engine, checkfirst=True)
            print("Sales table created successfully.")
            
        # Print all tables in the database
        print("\nAll tables in the database:")
        tables = inspector.get_table_names()
        for table in tables:
            print(f" - {table}")

if __name__ == "__main__":
    main() 