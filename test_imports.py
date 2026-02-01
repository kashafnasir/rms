"""
Test script to verify imports work correctly
"""
print("Testing imports...")

try:
    print("1. Importing extensions...")
    from extensions import db, login_manager, migrate
    print("   ✓ Extensions imported successfully")
    
    print("2. Importing models...")
    from models import User, Property, Tenant, Lease, Payment, MaintenanceRequest, Notification
    print("   ✓ Models imported successfully")
    
    print("3. Creating app...")
    from app import create_app
    app = create_app()
    print("   ✓ App created successfully")
    
    print("\n✅ ALL IMPORTS SUCCESSFUL!")
    print("\nYou can now run: python app.py")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nPlease check the CIRCULAR_IMPORT_FIX.md file for solutions")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPlease check the CIRCULAR_IMPORT_FIX.md file for solutions")