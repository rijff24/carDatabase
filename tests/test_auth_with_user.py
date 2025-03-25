from app import create_app, db
from app.models.user import User
import requests
from bs4 import BeautifulSoup

# Create app context and database tables
app = create_app('default')
with app.app_context():
    # Create tables
    db.create_all()
    
    # Create test user if it doesn't exist
    test_user = User.query.filter_by(username='testuser123').first()
    if not test_user:
        test_user = User(
            username='testuser123',
            full_name='Test User',
            role='user'
        )
        test_user.password = 'TestPass123!'
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully")
    else:
        print("Test user already exists")

# Test authentication
BASE_URL = 'http://localhost:5000'

def test_authentication():
    """Test authentication with valid user"""
    print("\n=== Testing Authentication with Valid User ===")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Get CSRF token
    response = session.get(f'{BASE_URL}/auth/login')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    # Test valid login
    print("\nTest: Valid login credentials")
    data = {
        'username': 'testuser123',
        'password': 'TestPass123!',
        'remember_me': True,
        'csrf_token': csrf_token
    }
    response = session.post(f'{BASE_URL}/auth/login', data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test logout
    print("\nTest: Logout")
    response = session.get(f'{BASE_URL}/auth/logout')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == '__main__':
    test_authentication() 