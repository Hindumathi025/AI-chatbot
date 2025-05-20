import unittest
from app import validate_mobile_number, validate_email

class TestValidationFunctions(unittest.TestCase):
    def test_mobile_validation(self):
        # Valid mobile numbers
        self.assertTrue(validate_mobile_number('1234567890'))
        self.assertTrue(validate_mobile_number('9876543210'))
        
        # Invalid mobile numbers
        self.assertFalse(validate_mobile_number('123456789'))  # Too short
        self.assertFalse(validate_mobile_number('12345678901'))  # Too long
        self.assertFalse(validate_mobile_number('123abc4567'))  # Contains letters
        self.assertFalse(validate_mobile_number('123-456-7890'))  # Contains special chars
        self.assertFalse(validate_mobile_number(''))  # Empty
        
    def test_email_validation(self):
        # Valid emails
        self.assertTrue(validate_email('test@example.com'))
        self.assertTrue(validate_email('user.name@domain.co.in'))
        self.assertTrue(validate_email('user123@gmail.com'))
        
        # Invalid emails
        self.assertFalse(validate_email('test@example'))  # No TLD
        self.assertFalse(validate_email('test.example.com'))  # No @ symbol
        self.assertFalse(validate_email('test@.com'))  # No domain
        self.assertFalse(validate_email('@example.com'))  # No username
        self.assertFalse(validate_email(''))  # Empty

if __name__ == '__main__':
    unittest.main()