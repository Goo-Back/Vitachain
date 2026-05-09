"""
Simple test for password validator without importing the full app
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.security import password_validator


def test_password_validator():
    """Test password validation functionality"""
    print("Testing password validator...")
    
    # Test valid passwords
    valid_passwords = [
        "SecurePass123!",
        "MyStrongP@ssw0rd",
        "ComplexPassword2026#",
        "ValidPass123$",
        "Str0ng!Password"
    ]
    
    print("\nTesting valid passwords:")
    for password in valid_passwords:
        is_valid, errors = password_validator.validate_password_strength(password)
        print(f"  '{password}': {'✓' if is_valid else '✗'}")
        assert is_valid, f"Password '{password}' should be valid"
        assert len(errors) == 0, f"Password '{password}' should have no errors"
    
    # Test invalid passwords
    print("\nTesting invalid passwords:")
    invalid_passwords = [
        ("short", "Too short"),
        ("nouppercase1!", "No uppercase"),
        ("NOLOWERCASE1!", "No lowercase"),
        ("NoNumbers!", "No numbers"),
        ("NoSpecial123", "No special characters")
    ]
    
    for password, reason in invalid_passwords:
        is_valid, errors = password_validator.validate_password_strength(password)
        print(f"  '{password}' ({reason}): {'✗' if not is_valid else '✓'}")
        assert not is_valid, f"Password '{password}' should be invalid"
        assert len(errors) > 0, f"Password '{password}' should have errors"
    
    # Test password strength scoring
    print("\nTesting password strength scoring:")
    strength_tests = [
        ("weak123", "weak"),
        ("StrongPass123!", "very_strong"),
        ("VeryStrongP@ssw0rd2026!", "very_strong"),
        ("a", "very_weak")
    ]
    
    for password, expected_strength in strength_tests:
        result = password_validator.get_password_strength_score(password)
        print(f"  '{password}': {result['strength']} (score: {result['score']})")
        assert result["strength"] == expected_strength, f"Password '{password}' should be {expected_strength}"
        assert 0 <= result["score"] <= 100, f"Score should be between 0 and 100"
    
    print("\n✅ All password validator tests passed!")


if __name__ == "__main__":
    test_password_validator()
