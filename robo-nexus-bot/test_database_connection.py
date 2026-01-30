"""
Simple test to check if birthday registration actually works
Run this on Replit to see what's happening
"""
import logging
import sys

# Set up logging to see everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

print("\n" + "="*60)
print("BIRTHDAY REGISTRATION DIAGNOSTIC TEST")
print("="*60 + "\n")

# Test 1: Import modules
print("Test 1: Importing modules...")
try:
    from supabase_api import get_supabase_api
    from database import add_birthday, get_birthday
    print("✅ Modules imported successfully\n")
except Exception as e:
    print(f"❌ Failed to import modules: {e}\n")
    sys.exit(1)

# Test 2: Get Supabase API instance
print("Test 2: Getting Supabase API instance...")
try:
    supabase = get_supabase_api()
    print(f"✅ Supabase API initialized")
    print(f"   URL: {supabase.url}")
    print(f"   Service key present: {'Yes' if supabase.service_key else 'No'}\n")
except Exception as e:
    print(f"❌ Failed to get Supabase API: {e}\n")
    sys.exit(1)

# Test 3: Try to register a test birthday
print("Test 3: Registering test birthday...")
test_user_id = "999999999999999999"  # Test user ID
test_birthday = "06-08"  # Your format

print(f"   User ID: {test_user_id}")
print(f"   Birthday: {test_birthday}")

try:
    success = add_birthday(test_user_id, test_birthday)
    if success:
        print(f"✅ Birthday registered successfully!\n")
    else:
        print(f"❌ Birthday registration returned False\n")
except Exception as e:
    print(f"❌ Exception during registration: {e}\n")
    import traceback
    traceback.print_exc()

# Test 4: Try to retrieve the birthday
print("Test 4: Retrieving the birthday...")
try:
    retrieved = get_birthday(test_user_id)
    if retrieved:
        print(f"✅ Birthday retrieved: {retrieved}")
        if retrieved == test_birthday:
            print(f"✅ Birthday matches!\n")
        else:
            print(f"⚠️  Birthday mismatch: expected '{test_birthday}', got '{retrieved}'\n")
    else:
        print(f"❌ Birthday not found in database\n")
except Exception as e:
    print(f"❌ Exception during retrieval: {e}\n")
    import traceback
    traceback.print_exc()

# Test 5: Direct Supabase API test
print("Test 5: Direct Supabase API test...")
try:
    result = supabase.register_birthday(test_user_id, test_birthday)
    print(f"   Direct API call result: {result}\n")
except Exception as e:
    print(f"❌ Direct API call failed: {e}\n")
    import traceback
    traceback.print_exc()

# Test 6: Check if birthday exists in database
print("Test 6: Checking all birthdays in database...")
try:
    all_birthdays = supabase.get_all_birthdays()
    print(f"   Total birthdays in database: {len(all_birthdays)}")
    
    if all_birthdays:
        print(f"   First few entries:")
        for bday in all_birthdays[:5]:
            print(f"      - User ID: {bday.get('user_id')}, Birthday: {bday.get('birthday')}")
    else:
        print(f"   ⚠️  No birthdays found in database!")
    print()
except Exception as e:
    print(f"❌ Failed to get all birthdays: {e}\n")
    import traceback
    traceback.print_exc()

# Test 7: Clean up test data
print("Test 7: Cleaning up test data...")
try:
    from database import remove_birthday
    remove_birthday(test_user_id)
    print(f"✅ Test data cleaned up\n")
except Exception as e:
    print(f"⚠️  Could not clean up: {e}\n")

print("="*60)
print("DIAGNOSTIC TEST COMPLETE")
print("="*60)
print("\nIf you see errors above, that's the real problem!")
print("Copy the error messages and show them to me.\n")
