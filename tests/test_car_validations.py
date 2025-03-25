import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000'

def login_user(session):
    """Login as test user to access protected routes"""
    print("\n=== Logging in as test user ===")
    
    # Get CSRF token from login page
    response = session.get(f'{BASE_URL}/auth/login')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    # Login
    data = {
        'username': 'testuser123',
        'password': 'TestPass123!',
        'remember_me': True,
        'csrf_token': csrf_token
    }
    response = session.post(f'{BASE_URL}/auth/login', data=data)
    print(f"Login Status: {response.status_code}")
    return response.status_code == 200 or response.status_code == 302

def get_csrf_token(session, url):
    """Get CSRF token from a page"""
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        csrf_token = None
        for form in soup.find_all('form'):
            csrf_input = form.find('input', {'name': 'csrf_token'})
            if csrf_input:
                csrf_token = csrf_input['value']
                break
                
        if not csrf_token:
            print("Could not find CSRF token, using an empty value")
            csrf_token = ""
        return csrf_token
    except Exception as e:
        print(f"Error extracting CSRF token: {e}")
        return ""

def create_test_stand(session):
    """Create a test stand if none exists"""
    print("\n=== Creating test stand ===")
    
    # Get CSRF token from stands page
    csrf_token = get_csrf_token(session, f'{BASE_URL}/stands/create')
    
    # Create a stand
    data = {
        'stand_name': f'Test Stand {datetime.now().strftime("%Y%m%d%H%M%S")}',
        'location': 'Test Location',
        'additional_info': 'Created for testing',
        'csrf_token': csrf_token
    }
    
    response = session.post(f'{BASE_URL}/stands/create', data=data)
    
    if response.status_code in (200, 302):
        print("Stand created or already exists")
        return 1  # Assume stand ID 1
    else:
        print(f"Failed to create stand: {response.status_code}")
        return None

def create_test_dealer(session):
    """Create a test dealer if none exists"""
    print("\n=== Creating test dealer ===")
    
    # Get CSRF token from dealers page
    csrf_token = get_csrf_token(session, f'{BASE_URL}/dealers/create')
    
    # Create a dealer
    data = {
        'dealer_name': f'Test Dealer {datetime.now().strftime("%Y%m%d%H%M%S")}',
        'contact_info': 'Test Contact Info',
        'csrf_token': csrf_token
    }
    
    response = session.post(f'{BASE_URL}/dealers/create', data=data)
    
    if response.status_code in (200, 302):
        print("Dealer created or already exists")
        return 1  # Assume dealer ID 1
    else:
        print(f"Failed to create dealer: {response.status_code}")
        return None

def create_test_car(session):
    """Create a test car if none exists"""
    print("\n=== Creating test car ===")
    
    # First, check if cars page loads and if there's already a car
    response = session.get(f'{BASE_URL}/cars/')
    if 'car-row-1' in response.text:
        print("Car with ID 1 already exists")
        return 1
    
    # Create a dealer if needed
    dealer_id = create_test_dealer(session)
    if not dealer_id:
        print("Cannot create car without a dealer")
        return None
    
    # Get CSRF token from cars/create page
    csrf_token = get_csrf_token(session, f'{BASE_URL}/cars/create')
    
    # Create a car
    today = datetime.now().date()
    data = {
        'vehicle_name': f'Test Car {datetime.now().strftime("%Y%m%d%H%M%S")}',
        'vehicle_make': 'Tesla',
        'vehicle_model': 'Model 3',
        'year': '2023',
        'colour': 'Red',
        'dekra_condition': 'Platinum',
        'licence_number': 'TEST123GP',
        'registration_number': 'TEST123GP',
        'purchase_price': '1000000',
        'source': dealer_id,
        'date_bought': today.strftime('%Y-%m-%d'),
        'repair_status': 'Purchased',
        'current_location': 'Test Location',
        'refuel_cost': '0',
        'csrf_token': csrf_token
    }
    
    response = session.post(f'{BASE_URL}/cars/create', data=data)
    
    if response.status_code in (200, 302):
        print("Test car created successfully")
        # Try to get the ID of the newly created car
        response = session.get(f'{BASE_URL}/cars/')
        # Simple approach: return ID 1 (most likely the first car)
        return 1
    else:
        print(f"Failed to create car: {response.status_code}")
        if response.status_code == 400:
            print(f"Form errors: {response.text[:200]}")
        return None

def test_car_index_validation():
    """Test car index route parameter validation"""
    print("\n=== Testing Car Index Validation ===")
    
    session = requests.Session()
    if not login_user(session):
        print("Failed to login, cannot test protected routes")
        return
    
    # Test 1: Valid parameters
    print("\nTest 1: Valid parameters")
    params = {
        'status': 'On Display',
        'search': 'VW',
        'sort_by': 'vehicle_make',
        'sort_dir': 'asc'
    }
    response = session.get(f'{BASE_URL}/cars/', params=params)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success: Valid parameters accepted")
    else:
        print(f"Unexpected response: {response.text[:100]}")
    
    # Test 2: Invalid status parameter
    print("\nTest 2: Invalid status parameter")
    params = {
        'status': 'Invalid_Status',
        'search': '',
        'sort_by': 'vehicle_make',
        'sort_dir': 'asc'
    }
    response = session.get(f'{BASE_URL}/cars/', params=params)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 400:
        print("Success: Validation failure correctly detected")
    else:
        print(f"Unexpected response: {response.text[:100]}")
    
    # Test 3: Invalid sort field
    print("\nTest 3: Invalid sort field")
    params = {
        'status': 'All',
        'search': '',
        'sort_by': 'invalid_field',
        'sort_dir': 'asc'
    }
    response = session.get(f'{BASE_URL}/cars/', params=params)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 400:
        print("Success: Validation failure correctly detected")
    else:
        print(f"Unexpected response: {response.text[:100]}")
    
    # Test 4: Invalid sort direction
    print("\nTest 4: Invalid sort direction")
    params = {
        'status': 'All',
        'search': '',
        'sort_by': 'vehicle_make',
        'sort_dir': 'invalid'
    }
    response = session.get(f'{BASE_URL}/cars/', params=params)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 400:
        print("Success: Validation failure correctly detected")
    else:
        print(f"Unexpected response: {response.text[:100]}")

def test_car_view_validation():
    """Test car view route parameter validation"""
    print("\n=== Testing Car View Validation ===")
    
    session = requests.Session()
    if not login_user(session):
        print("Failed to login, cannot test protected routes")
        return
    
    # Create a test car if needed
    car_id = create_test_car(session)
    if not car_id:
        print("Cannot test car view without a valid car")
        return
    
    # Test 1: Valid car_id
    print("\nTest 1: Valid car_id")
    response = session.get(f'{BASE_URL}/cars/{car_id}')
    print(f"Status Code: {response.status_code}")
    print(f"Success: {'200' in str(response.status_code)}")
    
    # Test 2: Invalid car_id (non-numeric)
    print("\nTest 2: Invalid car_id (non-numeric)")
    response = session.get(f'{BASE_URL}/cars/abc')
    print(f"Status Code: {response.status_code}")
    print(f"Error Message: {'404' in str(response.status_code)}")
    
    # Test 3: Non-existent car_id
    print("\nTest 3: Non-existent car_id")
    response = session.get(f'{BASE_URL}/cars/9999')
    print(f"Status Code: {response.status_code}")
    print(f"Error Message: {'404' in str(response.status_code)}")

def test_move_to_stand_validation():
    """Test move to stand route parameter validation"""
    print("\n=== Testing Move to Stand Validation ===")
    
    session = requests.Session()
    if not login_user(session):
        print("Failed to login, cannot test protected routes")
        return
    
    # Create a test stand if needed
    stand_id = create_test_stand(session)
    if not stand_id:
        print("Cannot test move-to-stand without a valid stand")
        return
    
    # Create a test car if needed
    car_id = create_test_car(session)
    if not car_id:
        print("Cannot test move-to-stand without a valid car")
        return
    
    # Get CSRF token from the car page
    csrf_token = get_csrf_token(session, f'{BASE_URL}/cars/{car_id}')
    print(f"Using CSRF token: {csrf_token[:10]}...")
    
    # Test 1: Valid parameters
    print("\nTest 1: Valid parameters")
    data = {
        'stand_id': stand_id,
        'csrf_token': csrf_token
    }
    response = session.post(f'{BASE_URL}/cars/{car_id}/move-to-stand', data=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 302:
        print("Success: Redirect after successful operation")
    else:
        print(f"Unexpected response: {response.text[:100]}")
    
    # Test 2: Invalid car_id
    print("\nTest 2: Invalid car_id")
    data = {
        'stand_id': stand_id,
        'csrf_token': csrf_token
    }
    response = session.post(f'{BASE_URL}/cars/abc/move-to-stand', data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Error Message: {'validation failed' in response.text or '404' in str(response.status_code)}")
    
    # Test 3: Invalid stand_id
    print("\nTest 3: Invalid stand_id")
    data = {
        'stand_id': 'abc',
        'csrf_token': csrf_token
    }
    response = session.post(f'{BASE_URL}/cars/{car_id}/move-to-stand', data=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 400:
        print("Success: Validation failure detected")
    else:
        print(f"Unexpected response: {response.text[:100]}")

if __name__ == '__main__':
    # Run tests
    test_car_index_validation()
    test_car_view_validation()
    test_move_to_stand_validation() 