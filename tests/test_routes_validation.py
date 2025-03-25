import unittest
from app import create_app, db
from app.models.user import User
from app.models.car import Car
from app.models.repair import Repair
from app.models.part import Part
from app.models.repair_provider import RepairProvider
from app.models.stand import Stand
from app.models.dealer import Dealer
import json
from datetime import datetime, timedelta

class RoutesValidationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        
        # Disable CSRF protection for testing
        self.app.config['WTF_CSRF_ENABLED'] = False
        # Configure app for testing
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = True
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Delete existing test user if it exists
        User.query.filter_by(username='testuser').delete()
        db.session.commit()
        
        # Create a test user with required fields
        user = User(username='testuser', 
                   full_name='Test User', 
                   password='password123',
                   role='user')
        db.session.add(user)
        db.session.commit()  # Commit user separately to ensure it succeeds
        
        # Create test data
        self.create_test_data()
        
        # Login the test user
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_data(self):
        try:
            # Create test dealer
            dealer = Dealer(
                dealer_name='Test Dealer',
                contact_info='test@dealer.com',
                address='123 Dealer St',
                date_joined=datetime.now()
            )
            db.session.add(dealer)
            db.session.flush()  # Get dealer ID
            print(f"Created dealer with ID: {dealer.dealer_id}")
            
            # Create test stand
            stand = Stand(
                stand_name='Test Stand',
                location='Test Location',
                capacity=10
            )
            db.session.add(stand)
            db.session.flush()  # Get stand ID
            print(f"Created stand with ID: {stand.stand_id}")
            
            # Create test car
            car = Car(
                vehicle_name='Test Car',
                vehicle_make='Test Make',
                vehicle_model='Test Model',
                year=2020,
                colour='Black',
                dekra_condition='Platinum',
                licence_number='ABC123',
                registration_number='123ABC',
                purchase_price=100000,
                source='Test Dealer',
                dealer_id=dealer.dealer_id,
                date_bought=datetime.now().date() - timedelta(days=30),
                current_location='Test Location',
                repair_status='Waiting for Repairs'
            )
            db.session.add(car)
            db.session.flush()  # Get car ID
            print(f"Created car with ID: {car.car_id}")
            
            # Create test provider
            provider = RepairProvider(
                provider_name='Test Provider',
                service_type='Test Service',
                contact_info='test@provider.com',
                location='Test Location'
            )
            db.session.add(provider)
            db.session.flush()  # Get provider ID
            print(f"Created provider with ID: {provider.provider_id}")
            
            # Create test part
            part = Part(
                part_name='Test Part',
                description='Test Description',
                manufacturer='Test Manufacturer',
                standard_price=100
            )
            db.session.add(part)
            db.session.flush()  # Get part ID
            print(f"Created part with ID: {part.part_id}")
            
            # Create test repair
            repair = Repair(
                car_id=car.car_id,
                repair_type='Workshop Repairs',
                provider_id=provider.provider_id,
                start_date=datetime.now().date() - timedelta(days=5),
                repair_cost=500
            )
            db.session.add(repair)
            db.session.flush()  # Get repair ID
            print(f"Created repair with ID: {repair.repair_id}")
            
            # Commit all changes
            db.session.commit()
            
            # Store IDs for testing
            self.dealer_id = dealer.dealer_id
            self.stand_id = stand.stand_id
            self.car_id = car.car_id
            self.provider_id = provider.provider_id
            self.part_id = part.part_id
            self.repair_id = repair.repair_id
            
            print(f"Stored IDs for testing: dealer={self.dealer_id}, stand={self.stand_id}, car={self.car_id}, provider={self.provider_id}, part={self.part_id}, repair={self.repair_id}")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating test data: {str(e)}")
            raise
    
    # Tests for repairs routes
    def test_repairs_index_validation(self):
        # Test with invalid sort_by parameter
        response = self.client.get('/repairs/?sort_by=invalid_field&sort_dir=desc')
        self.assertEqual(response.status_code, 400)  # Should fail validation
        
        # Test with invalid sort_dir parameter
        response = self.client.get('/repairs/?sort_by=start_date&sort_dir=invalid')
        self.assertEqual(response.status_code, 400)  # Should fail validation
    
    def test_repairs_view_validation(self):
        # Test with non-existent repair ID
        response = self.client.get('/repairs/9999')
        self.assertEqual(response.status_code, 404)  # Should return 404 Not Found
        
        # Test with invalid repair ID (non-integer)
        response = self.client.get('/repairs/invalid')
        self.assertEqual(response.status_code, 404)
    
    # Tests for parts routes
    def test_parts_index_validation(self):
        # Test with invalid sort_by parameter
        response = self.client.get('/parts/?sort_by=invalid_field&sort_dir=asc')
        self.assertEqual(response.status_code, 400)  # Should fail validation
        
        # Test with invalid sort_dir parameter
        response = self.client.get('/parts/?sort_by=part_name&sort_dir=invalid')
        self.assertEqual(response.status_code, 400)  # Should fail validation
    
    def test_parts_view_validation(self):
        # Test with non-existent part ID
        response = self.client.get('/parts/9999')
        self.assertEqual(response.status_code, 404)  # Should return 404 Not Found
        
        # Test with invalid part ID (non-integer)
        response = self.client.get('/parts/invalid')
        self.assertEqual(response.status_code, 404)
    
    # Tests for providers routes
    def test_providers_view_validation(self):
        # Test with non-existent provider ID
        response = self.client.get('/providers/9999')
        self.assertEqual(response.status_code, 404)  # Should return 404 Not Found
        
        # Test with invalid provider ID (non-integer)
        response = self.client.get('/providers/invalid')
        self.assertEqual(response.status_code, 404)
    
    # Tests for stands routes
    def test_stands_view_validation(self):
        # Test with non-existent stand ID
        response = self.client.get('/stands/9999')
        self.assertEqual(response.status_code, 404)  # Should return 404 Not Found
        
        # Test with invalid stand ID (non-integer)
        response = self.client.get('/stands/invalid')
        self.assertEqual(response.status_code, 404)
    
    # Tests for dealers routes
    def test_dealers_view_validation(self):
        # Test with non-existent dealer ID
        response = self.client.get('/dealers/9999')
        self.assertEqual(response.status_code, 404)  # Should return 404 Not Found
        
        # Test with invalid dealer ID (non-integer)
        response = self.client.get('/dealers/invalid')
        self.assertEqual(response.status_code, 404)
    
    # Tests for reports routes
    def test_sales_performance_validation(self):
        # Test with invalid period parameter
        response = self.client.get('/reports/sales-performance?period=invalid&year=2023')
        self.assertEqual(response.status_code, 400)  # Should fail validation
        
        # Test with invalid year parameter
        response = self.client.get('/reports/sales-performance?period=monthly&year=invalid')
        self.assertEqual(response.status_code, 400)  # Should fail validation

if __name__ == '__main__':
    unittest.main() 