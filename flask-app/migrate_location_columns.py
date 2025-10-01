#!/usr/bin/env python3
"""
Migration script to add location tracking columns to users table.
Adds: location_type, latitude, longitude, start_latitude, start_longitude, end_latitude, end_longitude
"""
from app import create_app, db
import sqlalchemy as sa

def migrate():
    app = create_app()
    app.app_context().push()
    
    print("🔄 Adding location tracking columns to users table...")
    
    migrations = [
        "ALTER TABLE users ADD COLUMN location_type VARCHAR(20)",
        "ALTER TABLE users ADD COLUMN latitude FLOAT",
        "ALTER TABLE users ADD COLUMN longitude FLOAT",
        "ALTER TABLE users ADD COLUMN start_latitude FLOAT",
        "ALTER TABLE users ADD COLUMN start_longitude FLOAT",
        "ALTER TABLE users ADD COLUMN end_latitude FLOAT",
        "ALTER TABLE users ADD COLUMN end_longitude FLOAT",
    ]
    
    for migration_sql in migrations:
        try:
            db.session.execute(sa.text(migration_sql))
            column_name = migration_sql.split('ADD COLUMN ')[1].split(' ')[0]
            print(f"  ✅ Added column: {column_name}")
        except Exception as e:
            if 'duplicate column name' in str(e).lower():
                column_name = migration_sql.split('ADD COLUMN ')[1].split(' ')[0]
                print(f"  ⏭️  Column already exists: {column_name}")
            else:
                print(f"  ❌ Error: {e}")
                raise
    
    db.session.commit()
    print("\n✅ Migration completed successfully!")
    
    # Verify
    print("\n📋 Updated schema:")
    result = db.session.execute(sa.text('PRAGMA table_info(users)'))
    for row in result:
        if row[1] in ['location_type', 'latitude', 'longitude', 'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude']:
            print(f"  ✓ {row[1]} ({row[2]})")

if __name__ == '__main__':
    migrate()
