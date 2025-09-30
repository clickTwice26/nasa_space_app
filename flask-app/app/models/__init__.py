from app import db, ma
from datetime import datetime
from sqlalchemy import func

class Mission(db.Model):
    """NASA Mission model"""
    __tablename__ = 'missions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    launch_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='Active')
    mission_type = db.Column(db.String(50))  # e.g., 'Earth Observation', 'Mars', 'ISS'
    agency = db.Column(db.String(50), default='NASA')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    data_records = db.relationship('DataRecord', backref='mission', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Mission {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'launch_date': self.launch_date.isoformat() if self.launch_date else None,
            'status': self.status,
            'mission_type': self.mission_type,
            'agency': self.agency,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class DataRecord(db.Model):
    """Data records from NASA missions"""
    __tablename__ = 'data_records'
    
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), nullable=False)
    record_type = db.Column(db.String(50))  # e.g., 'telemetry', 'image', 'sensor'
    data_source = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    altitude = db.Column(db.Float)
    data_values = db.Column(db.JSON)  # Store JSON data
    file_path = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    checksum = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DataRecord {self.id} - {self.record_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'mission_id': self.mission_id,
            'record_type': self.record_type,
            'data_source': self.data_source,
            'timestamp': self.timestamp.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'data_values': self.data_values,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat()
        }

class Spacecraft(db.Model):
    """Spacecraft/Satellite model"""
    __tablename__ = 'spacecraft'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    norad_id = db.Column(db.String(20))  # NORAD catalog number
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'))
    spacecraft_type = db.Column(db.String(50))  # 'satellite', 'rover', 'orbiter', etc.
    status = db.Column(db.String(50), default='Active')
    launch_date = db.Column(db.Date)
    mass = db.Column(db.Float)  # kg
    power = db.Column(db.Float)  # watts
    orbit_type = db.Column(db.String(50))  # 'LEO', 'GEO', 'Mars orbit', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Spacecraft {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'norad_id': self.norad_id,
            'mission_id': self.mission_id,
            'spacecraft_type': self.spacecraft_type,
            'status': self.status,
            'launch_date': self.launch_date.isoformat() if self.launch_date else None,
            'mass': self.mass,
            'power': self.power,
            'orbit_type': self.orbit_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Marshmallow Schemas for serialization
class MissionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mission
        load_instance = True
        include_relationships = True

class DataRecordSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DataRecord
        load_instance = True
        include_relationships = True

class SpacecraftSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Spacecraft
        load_instance = True
        include_relationships = True

# Schema instances
mission_schema = MissionSchema()
missions_schema = MissionSchema(many=True)
data_record_schema = DataRecordSchema()
data_records_schema = DataRecordSchema(many=True)
spacecraft_schema = SpacecraftSchema()
spacecrafts_schema = SpacecraftSchema(many=True)