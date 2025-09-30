#!/usr/bin/env python3
"""
Database initialization script for NASA Space App
Creates tables and populates with sample data
"""

from app import create_app, db
from app.models import Mission, DataRecord, Spacecraft
from datetime import datetime, date
import json

def init_database():
    """Initialize database with sample data"""
    
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate
        print("🗑️  Dropping existing tables...")
        db.drop_all()
        
        print("🏗️  Creating new tables...")
        db.create_all()
        
        print("📊 Adding sample missions...")
        sample_missions = [
            Mission(
                name="Artemis I",
                description="Uncrewed test flight around the Moon",
                launch_date=date(2022, 11, 16),
                status="Completed",
                mission_type="Lunar",
                agency="NASA"
            ),
            Mission(
                name="Mars 2020 Perseverance",
                description="Mars rover mission to search for ancient microbial life",
                launch_date=date(2020, 7, 30),
                status="Active",
                mission_type="Mars Exploration",
                agency="NASA"
            ),
            Mission(
                name="Hubble Space Telescope",
                description="Space telescope for deep space observations",
                launch_date=date(1990, 4, 24),
                status="Active",
                mission_type="Deep Space",
                agency="NASA"
            ),
            Mission(
                name="ISS Expedition 70",
                description="International Space Station crew mission",
                launch_date=date(2023, 9, 15),
                status="Active",
                mission_type="ISS",
                agency="NASA"
            ),
            Mission(
                name="JWST",
                description="James Webb Space Telescope - Next generation space observatory",
                launch_date=date(2021, 12, 25),
                status="Active",
                mission_type="Deep Space",
                agency="NASA"
            )
        ]
        
        for mission in sample_missions:
            db.session.add(mission)
        
        db.session.commit()
        print(f"✅ Added {len(sample_missions)} missions")
        
        print("🛰️  Adding sample spacecraft...")
        sample_spacecraft = [
            Spacecraft(
                name="Orion Capsule",
                mission_id=1,  # Artemis I
                spacecraft_type="capsule",
                status="Completed Mission",
                launch_date=date(2022, 11, 16),
                mass=26520,  # kg
                orbit_type="Trans-lunar"
            ),
            Spacecraft(
                name="Perseverance Rover",
                mission_id=2,  # Mars 2020
                spacecraft_type="rover",
                status="Active",
                launch_date=date(2020, 7, 30),
                mass=1025,  # kg
                orbit_type="Mars Surface"
            ),
            Spacecraft(
                name="Hubble Space Telescope",
                mission_id=3,  # Hubble
                spacecraft_type="telescope",
                status="Active",
                launch_date=date(1990, 4, 24),
                mass=11110,  # kg
                power=2800,  # watts
                orbit_type="LEO"
            )
        ]
        
        for spacecraft in sample_spacecraft:
            db.session.add(spacecraft)
        
        db.session.commit()
        print(f"✅ Added {len(sample_spacecraft)} spacecraft")
        
        print("📡 Adding sample data records...")
        sample_data_records = [
            DataRecord(
                mission_id=2,  # Mars 2020
                record_type="image",
                data_source="MASTCAM-Z",
                timestamp=datetime(2024, 1, 15, 14, 30, 0),
                latitude=-18.4447,
                longitude=77.4509,
                altitude=-2574,
                data_values={"resolution": "1600x1200", "filter": "RGB", "exposure_time": "0.1s"},
                file_path="/data/mars/perseverance/images/sol_1050_mastcamz_001.jpg",
                file_size=2048000,
                checksum="abc123def456"
            ),
            DataRecord(
                mission_id=3,  # Hubble
                record_type="observation",
                data_source="Wide Field Camera 3",
                timestamp=datetime(2024, 1, 20, 10, 15, 30),
                data_values={
                    "target": "NGC 1234",
                    "exposure_time": 1200,
                    "filter": "F814W",
                    "magnitude": 18.5
                },
                file_path="/data/hubble/observations/hst_ngc1234_f814w.fits",
                file_size=16777216,
                checksum="def456ghi789"
            ),
            DataRecord(
                mission_id=4,  # ISS
                record_type="telemetry",
                data_source="ISS ECLSS",
                timestamp=datetime(2024, 1, 25, 16, 45, 0),
                latitude=45.2345,
                longitude=-122.6789,
                altitude=408000,
                data_values={
                    "oxygen_level": 20.8,
                    "co2_level": 0.03,
                    "pressure": 101.325,
                    "temperature": 22.5
                },
                file_size=1024
            ),
            DataRecord(
                mission_id=5,  # JWST
                record_type="observation",
                data_source="NIRCam",
                timestamp=datetime(2024, 1, 30, 8, 20, 15),
                data_values={
                    "target": "WASP-96b",
                    "instrument": "NIRCam",
                    "exposure_time": 3600,
                    "wavelength_range": "0.6-5.0 microns"
                },
                file_path="/data/jwst/observations/wasp96b_nircam_001.fits",
                file_size=134217728,
                checksum="ghi789jkl012"
            ),
            DataRecord(
                mission_id=2,  # Mars 2020 - Additional record
                record_type="sensor",
                data_source="MOXIE",
                timestamp=datetime(2024, 2, 1, 12, 0, 0),
                latitude=-18.4447,
                longitude=77.4509,
                altitude=-2574,
                data_values={
                    "oxygen_production_rate": 5.37,  # grams per hour
                    "power_consumption": 300,  # watts
                    "temperature": 800,  # celsius
                    "status": "normal"
                },
                file_size=512
            )
        ]
        
        for record in sample_data_records:
            db.session.add(record)
        
        db.session.commit()
        print(f"✅ Added {len(sample_data_records)} data records")
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n📊 Summary:")
        print(f"   Missions: {Mission.query.count()}")
        print(f"   Spacecraft: {Spacecraft.query.count()}")
        print(f"   Data Records: {DataRecord.query.count()}")
        
        print("\n🚀 You can now start the Flask application:")
        print("   python app.py")

if __name__ == "__main__":
    init_database()