import unittest
from app.utils.validators import (
    validate_email, validate_phone, validate_price,
    validate_username, validate_password, validate_date_range
)
from datetime import datetime, timedelta

class ValidatorFunctionsTestCase(unittest.TestCase):
    def test_validate_email(self):
        # Valid emails
        self.assertTrue(validate_email('test@example.com'))
        self.assertTrue(validate_email('user.name@domain.co.uk'))
        self.assertTrue(validate_email('user-name123@domain.com'))
        
        # Invalid emails
        self.assertFalse(validate_email(''))
        self.assertFalse(validate_email('invalid-email'))
        self.assertFalse(validate_email('invalid@'))
        self.assertFalse(validate_email('@domain.com'))
        self.assertFalse(validate_email('user@domain'))
    
    def test_validate_phone(self):
        # Valid phone numbers
        self.assertTrue(validate_phone('1234567890'))
        self.assertTrue(validate_phone('+27123456789'))
        self.assertTrue(validate_phone('27123456789'))
        
        # Invalid phone numbers
        self.assertFalse(validate_phone(''))
        self.assertFalse(validate_phone('123'))  # Too short
        self.assertFalse(validate_phone('123456789012345678'))  # Too long
        self.assertFalse(validate_phone('abc123456789'))  # Contains letters
    
    def test_validate_price(self):
        # Valid prices
        self.assertTrue(validate_price('100'))
        self.assertTrue(validate_price('100.00'))
        self.assertTrue(validate_price('0'))
        self.assertTrue(validate_price('0.99'))
        
        # Invalid prices
        self.assertFalse(validate_price(''))
        self.assertFalse(validate_price('-100'))  # Negative
        self.assertFalse(validate_price('100.999'))  # More than 2 decimal places
        self.assertFalse(validate_price('abc'))  # Not a number
    
    def test_validate_username(self):
        # Valid usernames
        self.assertTrue(validate_username('user123'))
        self.assertTrue(validate_username('User_123'))
        self.assertTrue(validate_username('admin'))
        
        # Invalid usernames
        self.assertFalse(validate_username(''))
        self.assertFalse(validate_username('ab'))  # Too short (< 3 chars)
        self.assertFalse(validate_username('a' * 33))  # Too long (> 32 chars)
        self.assertFalse(validate_username('user-name'))  # Contains invalid char '-'
        self.assertFalse(validate_username('user name'))  # Contains space
        self.assertFalse(validate_username('user@name'))  # Contains invalid char '@'
    
    def test_validate_password(self):
        # Valid passwords
        self.assertTrue(validate_password('P@ssw0rd'))
        self.assertTrue(validate_password('SecurePassword123!'))
        self.assertTrue(validate_password('Abcd1234!'))
        
        # Invalid passwords
        self.assertFalse(validate_password(''))
        self.assertFalse(validate_password('pass'))  # Too short (< 8 chars)
        self.assertFalse(validate_password('password'))  # No uppercase
        self.assertFalse(validate_password('PASSWORD'))  # No lowercase
        self.assertFalse(validate_password('Password'))  # No number
        self.assertFalse(validate_password('Password1'))  # No special char
    
    def test_validate_date_range(self):
        # Valid date ranges
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        self.assertTrue(validate_date_range(today, tomorrow))
        self.assertTrue(validate_date_range(today, today))  # Same day is valid
        self.assertTrue(validate_date_range(today, next_week))
        
        # Invalid date ranges
        yesterday = today - timedelta(days=1)
        self.assertFalse(validate_date_range(tomorrow, today))  # End before start
        self.assertFalse(validate_date_range(next_week, today))  # End before start

if __name__ == '__main__':
    unittest.main() 