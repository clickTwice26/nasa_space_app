#!/usr/bin/env python3
"""
Database initialization script for TerraPulse authentication system
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User, UserSession, OnboardingProgress
from app.services.auth_service import AuthService
from datetime import datetime, timezone

def init_database():
    """Initialize the database with tables and sample data"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Creating database tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ Database tables created successfully!")
            
            # Check if we need to create a test user
            if not User.query.first():
                print("🔄 Creating test user...")
                
                # Create a test user
                result = AuthService.register_user(
                    email="test@terrapulse.com",
                    username="testuser",
                    password="testpass123",
                    full_name="Test User",
                    profile_type="farmer",
                    location="Dhaka, Bangladesh",
                    district="Dhaka"
                )
                
                if result['success']:
                    print("✅ Test user created successfully!")
                    print("   Email: test@terrapulse.com")
                    print("   Username: testuser")
                    print("   Password: testpass123")
                else:
                    print(f"❌ Failed to create test user: {result['message']}")
            
            # Print database info
            user_count = User.query.count()
            session_count = UserSession.query.count()
            onboarding_count = OnboardingProgress.query.count()
            
            print(f"\n📊 Database Statistics:")
            print(f"   Users: {user_count}")
            print(f"   Sessions: {session_count}")
            print(f"   Onboarding records: {onboarding_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {str(e)}")
            return False

if __name__ == '__main__':
    print("🌱 TerraPulse Database Initialization")
    print("=" * 40)
    
    success = init_database()
    
    if success:
        print("\n✅ Database initialization completed successfully!")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)