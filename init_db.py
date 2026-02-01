#!/usr/bin/env python3
"""
Initialization script for Rental Management System
Creates database tables and default admin user
"""

from app import app, db
from models import User, Property, Lease, Payment, MaintenanceRequest, Notification
from datetime import datetime

def init_database():
    """Initialize the database with tables and default data"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if admin user already exists
        admin_exists = User.query.filter_by(username='admin').first()
        
        if not admin_exists:
            print("\nCreating default admin user...")
            admin = User(
                username='admin',
                email='admin@rental.com',
                full_name='System Administrator',
                phone='1234567890',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')  # Change this password in production!
            
            db.session.add(admin)
            db.session.commit()
            
            print("✓ Default admin user created successfully!")
            print("\n" + "="*60)
            print("Default Admin Credentials:")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("\n✓ Admin user already exists, skipping creation.")
        
        # Create some sample users for testing
        if User.query.count() == 1:  # Only admin exists
            print("\nCreating sample users for testing...")
            
            # Sample Owner
            owner = User(
                username='owner1',
                email='owner@rental.com',
                full_name='John Property Owner',
                phone='5551234567',
                role='owner',
                address='123 Owner Street',
                is_active=True
            )
            owner.set_password('owner123')
            
            # Sample Tenant
            tenant = User(
                username='tenant1',
                email='tenant@rental.com',
                full_name='Jane Tenant',
                phone='5559876543',
                role='tenant',
                address='456 Tenant Avenue',
                is_active=True
            )
            tenant.set_password('tenant123')
            
            # Sample Staff
            staff = User(
                username='staff1',
                email='staff@rental.com',
                full_name='Bob Maintenance Staff',
                phone='5555555555',
                role='staff',
                is_active=True
            )
            staff.set_password('staff123')
            
            db.session.add_all([owner, tenant, staff])
            db.session.commit()
            
            print("✓ Sample users created successfully!")
            print("\nSample User Credentials:")
            print("-" * 60)
            print("Owner - Username: owner1, Password: owner123")
            print("Tenant - Username: tenant1, Password: tenant123")
            print("Staff - Username: staff1, Password: staff123")
            print("-" * 60)
        
        print("\n✅ Database initialization complete!")
        print("\nYou can now run the application with: python app.py")

if __name__ == '__main__':
    init_database()