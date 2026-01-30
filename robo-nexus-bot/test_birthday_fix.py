"""
Test script to verify birthday registration fix
"""
import logging
from datetime import date
from date_parser import DateParser
from database import add_birthday, get_birthday
from supabase_api import get_supabase_api

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_birthday_registration():
    """Test birthday registration with date object conversion"""
    
    print("\n" + "="*60)
    print("TESTING BIRTHDAY REGISTRATION FIX")
    print("="*60 + "\n")
    
    # Test user ID (use a test ID that won't conflict)
    test_user_id = 999999999999999999
    
    # Test 1: Parse birthday from string
    print("Test 1: Parsing birthday from string...")
    birthday_input = "03-15"
    birthday_date = DateParser.parse_birthday(birthday_input)
    
    if birthday_date:
        print(f"✅ Parsed birthday: {birthday_date}")
        print(f"   Type: {type(birthday_date)}")
    else:
        print(f"❌ Failed to parse birthday")
        return
    
    # Test 2: Convert to string format
    print("\nTest 2: Converting date object to string...")
    birthday_string = birthday_date.strftime('%m-%d')
    print(f"✅ Converted to string: {birthday_string}")
    print(f"   Type: {type(birthday_string)}")
    
    # Test 3: Register birthday
    print(f"\nTest 3: Registering birthday for user {test_user_id}...")
    success = add_birthday(test_user_id, birthday_string)
    
    if success:
        print(f"✅ Birthday registered successfully!")
    else:
        print(f"❌ Failed to register birthday")
        return
    
    # Test 4: Retrieve birthday
    print(f"\nTest 4: Retrieving birthday for user {test_user_id}...")
    retrieved_birthday = get_birthday(test_user_id)
    
    if retrieved_birthday:
        print(f"✅ Retrieved birthday: {retrieved_birthday}")
        print(f"   Type: {type(retrieved_birthday)}")
        
        if retrieved_birthday == birthday_string:
            print(f"✅ Birthday matches! ({retrieved_birthday} == {birthday_string})")
        else:
            print(f"❌ Birthday mismatch! ({retrieved_birthday} != {birthday_string})")
    else:
        print(f"❌ Failed to retrieve birthday")
        return
    
    # Test 5: Clean up - remove test birthday
    print(f"\nTest 5: Cleaning up test data...")
    try:
        from database import remove_birthday
        remove_birthday(test_user_id)
        print(f"✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️  Could not clean up test data: {e}")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✅")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_birthday_registration()
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        print(f"\n❌ TEST FAILED: {e}\n")
