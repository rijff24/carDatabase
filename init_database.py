from app import create_app, db
from app.models import Car, Dealer, Sale, RepairProvider, Stand
from datetime import datetime, date, timedelta
import random
import decimal

def main():
    """Initialize the database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        
        # Print all tables in the database
        print("\nTables in the database:")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(f" - {table}")
        
        # Check if we need to add sample data
        if not Car.query.first() and not Dealer.query.first():
            print("\nAdding sample data...")
            add_sample_data()
        else:
            print("\nDatabase already has data. Skipping sample data creation.")

def add_sample_data():
    """Add sample data to the database"""
    # Add sample dealers
    dealers = [
        Dealer(dealer_name="Premium Motors", contact_info="555-123-4567", address="123 Main St"),
        Dealer(dealer_name="City Auto", contact_info="555-765-4321", address="456 Oak Ave"),
        Dealer(dealer_name="Valley Cars", contact_info="555-987-6543", address="789 Pine Blvd")
    ]
    
    for dealer in dealers:
        db.session.add(dealer)
    
    # Add sample stands
    stands = [
        Stand(stand_name="Main Showroom", location="Downtown"),
        Stand(stand_name="East Side Lot", location="East Mall"),
        Stand(stand_name="West Side Lot", location="West Mall")
    ]
    
    for stand in stands:
        db.session.add(stand)
    
    # Commit to get IDs
    db.session.commit()
    
    # Add sample repair providers
    providers = [
        RepairProvider(provider_name="Quick Fix Auto", contact_info="555-222-3333", specialization="General Repairs"),
        RepairProvider(provider_name="Elite Body Shop", contact_info="555-444-5555", specialization="Body Work"),
        RepairProvider(provider_name="Motor Masters", contact_info="555-666-7777", specialization="Engine Work")
    ]
    
    for provider in providers:
        db.session.add(provider)
    
    db.session.commit()
    
    # Add sample cars
    cars = [
        Car(
            vehicle_name="Toyota Camry LE 2022",
            vehicle_make="Toyota",
            vehicle_model="Camry",
            year=2022,
            colour="Silver",
            dekra_condition="Good",
            licence_number="ABC123",
            registration_number="REG123",
            purchase_price=150000.00,
            recon_cost=5000.00,
            final_cost_price=155000.00,
            source="Auction",
            date_bought=date.today() - timedelta(days=90),
            date_added_to_stand=date.today() - timedelta(days=60),
            refuel_cost=500.00,
            current_location="Main Showroom",
            repair_status="Available",
            stand_id=stands[0].stand_id
        ),
        Car(
            vehicle_name="Honda Accord Sport 2021",
            vehicle_make="Honda",
            vehicle_model="Accord",
            year=2021,
            colour="Blue",
            dekra_condition="Excellent",
            licence_number="XYZ789",
            registration_number="REG456",
            purchase_price=180000.00,
            recon_cost=3000.00,
            final_cost_price=183000.00,
            source="Trade-in",
            date_bought=date.today() - timedelta(days=75),
            date_added_to_stand=date.today() - timedelta(days=45),
            refuel_cost=600.00,
            current_location="East Side Lot",
            repair_status="Available",
            stand_id=stands[1].stand_id
        ),
        Car(
            vehicle_name="BMW 3 Series 2020",
            vehicle_make="BMW",
            vehicle_model="3 Series",
            year=2020,
            colour="Black",
            dekra_condition="Good",
            licence_number="DEF456",
            registration_number="REG789",
            purchase_price=220000.00,
            recon_cost=7000.00,
            final_cost_price=227000.00,
            source="Dealer",
            date_bought=date.today() - timedelta(days=60),
            date_added_to_stand=date.today() - timedelta(days=30),
            refuel_cost=800.00,
            current_location="West Side Lot",
            repair_status="Available",
            stand_id=stands[2].stand_id
        )
    ]
    
    for car in cars:
        db.session.add(car)
    
    db.session.commit()
    
    # Add sample sales (selling one of the cars)
    sold_car = cars[0]
    sold_car.date_sold = date.today() - timedelta(days=10)
    sold_car.repair_status = "Sold"
    sold_car.sale_price = 185000.00
    
    sale = Sale(
        car_id=sold_car.car_id,
        dealer_id=dealers[0].dealer_id,
        sale_price=185000.00,
        sale_date=date.today() - timedelta(days=10),
        payment_method="Bank Transfer",
        customer_name="John Smith",
        customer_contact="555-888-9999",
        notes="First time buyer"
    )
    
    db.session.add(sale)
    db.session.add(sold_car)
    db.session.commit()
    
    print("Added sample dealers, stands, repair providers, cars, and a sample sale.")

if __name__ == "__main__":
    main() 