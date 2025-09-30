from app import db
from app.models import DataRecord, data_record_schema, data_records_schema
from datetime import datetime
import json

class DataService:
    """Service layer for Data Record operations"""
    
    @staticmethod
    def get_all_data_records(page=1, per_page=50):
        """Get all data records with pagination"""
        try:
            pagination = DataRecord.query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            result = {
                'data': data_records_schema.dump(pagination.items),
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            return result, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_data_by_mission(mission_id, page=1, per_page=50):
        """Get data records for a specific mission"""
        try:
            pagination = DataRecord.query.filter_by(mission_id=mission_id).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            result = {
                'data': data_records_schema.dump(pagination.items),
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            return result, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def create_data_record(data_record_data):
        """Create a new data record"""
        try:
            data_record = DataRecord(
                mission_id=data_record_data.get('mission_id'),
                record_type=data_record_data.get('record_type'),
                data_source=data_record_data.get('data_source'),
                timestamp=datetime.fromisoformat(data_record_data.get('timestamp')),
                latitude=data_record_data.get('latitude'),
                longitude=data_record_data.get('longitude'),
                altitude=data_record_data.get('altitude'),
                data_values=data_record_data.get('data_values'),
                file_path=data_record_data.get('file_path'),
                file_size=data_record_data.get('file_size'),
                checksum=data_record_data.get('checksum')
            )
            
            db.session.add(data_record)
            db.session.commit()
            
            return data_record_schema.dump(data_record), None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_data_by_type(record_type, page=1, per_page=50):
        """Get data records by type"""
        try:
            pagination = DataRecord.query.filter_by(record_type=record_type).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            result = {
                'data': data_records_schema.dump(pagination.items),
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            return result, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_data_by_location(lat_min, lat_max, lon_min, lon_max, page=1, per_page=50):
        """Get data records by geographic bounds"""
        try:
            pagination = DataRecord.query.filter(
                DataRecord.latitude.between(lat_min, lat_max),
                DataRecord.longitude.between(lon_min, lon_max)
            ).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            result = {
                'data': data_records_schema.dump(pagination.items),
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            return result, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_data_statistics():
        """Get basic statistics about data records"""
        try:
            total_records = DataRecord.query.count()
            record_types = db.session.query(
                DataRecord.record_type, 
                db.func.count(DataRecord.id)
            ).group_by(DataRecord.record_type).all()
            
            missions_with_data = db.session.query(
                DataRecord.mission_id,
                db.func.count(DataRecord.id)
            ).group_by(DataRecord.mission_id).all()
            
            stats = {
                'total_records': total_records,
                'record_types': [{'type': rt[0], 'count': rt[1]} for rt in record_types],
                'missions_with_data': [{'mission_id': mwd[0], 'count': mwd[1]} for mwd in missions_with_data]
            }
            
            return stats, None
        except Exception as e:
            return None, str(e)