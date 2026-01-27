"""
Test script for Welcome System with enhanced profile collection
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from welcome_system import WelcomeSystem

def test_class_extraction():
    """Test the class extraction functionality"""
    
    # Create a mock welcome system
    class MockBot:
        pass
    
    welcome_system = WelcomeSystem(MockBot())
    
    # Test cases
    test_cases = [
        # Direct numbers
        ("6", "6"),
        ("10", "10"),
        ("12", "12"),
        
        # With class/grade
        ("John Smith, Class 10", "10"),
        ("Sarah, Grade 8", "8"),
        ("Mike class 12", "12"),
        ("Alex grade 7", "7"),
        
        # Ordinals
        ("I'm in 6th", "6"),
        ("Tom 10th grade", "10"),
        ("Lisa 12th", "12"),
        
        # Word forms
        ("sixth grade", "6"),
        ("I'm in seventh", "7"),
        ("eighth class", "8"),
        ("ninth grade", "9"),
        ("tenth standard", "10"),
        ("eleventh class", "11"),
        ("twelfth grade", "12"),
        
        # Complex cases
        ("My name is John Smith and I'm in class 10", "10"),
        ("Sarah Johnson, 8th grade student", "8"),
        ("Alex - Class 12", "12"),
        
        # Invalid cases
        ("John Smith", None),
        ("I'm a student", None),
        ("Class 13", None),
        ("Grade 5", None),
        ("", None),
    ]
    
    print("🧪 Testing Class Extraction Logic\n")
    
    passed = 0
    failed = 0
    
    for input_text, expected in test_cases:
        result = welcome_system.extract_class_from_text(input_text)
        
        if result == expected:
            print(f"✅ '{input_text}' → {result}")
            passed += 1
        else:
            print(f"❌ '{input_text}' → {result} (expected {expected})")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed - check the logic")

def test_email_validation():
    """Test Gmail validation"""
    
    class MockBot:
        pass
    
    welcome_system = WelcomeSystem(MockBot())
    
    test_cases = [
        # Valid Gmail addresses
        ("john.smith@gmail.com", True),
        ("test123@gmail.com", True),
        ("user.name+tag@gmail.com", True),
        ("simple@gmail.com", True),
        
        # Invalid cases
        ("john@yahoo.com", False),
        ("test@outlook.com", False),
        ("invalid-email", False),
        ("@gmail.com", False),
        ("user@gmail", False),
        ("", False),
        (None, False),
    ]
    
    print("\n📧 Testing Email Validation\n")
    
    passed = 0
    failed = 0
    
    for email, expected in test_cases:
        result = welcome_system.validate_email(email)
        
        if result == expected:
            print(f"✅ '{email}' → {result}")
            passed += 1
        else:
            print(f"❌ '{email}' → {result} (expected {expected})")
            failed += 1
    
    print(f"\n📊 Email Results: {passed} passed, {failed} failed")

def test_social_links():
    """Test social links extraction"""
    
    class MockBot:
        pass
    
    welcome_system = WelcomeSystem(MockBot())
    
    test_cases = [
        # Valid links
        ("github.com/johnsmith", {"github": "https://github.com/johnsmith"}),
        ("https://linkedin.com/in/johnsmith", {"linkedin": "https://linkedin.com/in/johnsmith"}),
        ("youtube.com/@johnsmith", {"youtube": "https://youtube.com/@johnsmith"}),
        ("open.spotify.com/user/johnsmith", {"spotify": "https://open.spotify.com/user/johnsmith"}),
        
        # Multiple links
        ("GitHub: github.com/john\nLinkedIn: linkedin.com/in/john", 
         {"github": "https://github.com/john", "linkedin": "https://linkedin.com/in/john"}),
        
        # Skip cases
        ("none", {}),
        ("skip", {}),
        ("n/a", {}),
        ("", {}),
    ]
    
    print("\n🔗 Testing Social Links Extraction\n")
    
    passed = 0
    failed = 0
    
    for input_text, expected in test_cases:
        result = welcome_system.validate_social_links(input_text)
        
        if result == expected:
            print(f"✅ '{input_text}' → {result}")
            passed += 1
        else:
            print(f"❌ '{input_text}' → {result}")
            print(f"   Expected: {expected}")
            failed += 1
    
    print(f"\n📊 Links Results: {passed} passed, {failed} failed")

if __name__ == "__main__":
    test_class_extraction()
    test_email_validation()
    test_social_links()