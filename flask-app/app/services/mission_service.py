from app import db
from app.models import Mission, mission_schema, missions_schema
from sqlalchemy.exc import IntegrityError
from datetime import datetime

class MissionService:
    """Service layer for Mission operations"""
    
    @staticmethod
    def get_all_missions():
        """Get all missions"""
        try:
            missions = Mission.query.all()
            return missions_schema.dump(missions), None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_mission_by_id(mission_id):
        """Get mission by ID"""
        try:
            mission = Mission.query.get(mission_id)
            if mission:
                return mission_schema.dump(mission), None
            return None, "Mission not found"
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def create_mission(mission_data):
        """Create a new mission"""
        try:
            mission = Mission(
                name=mission_data.get('name'),
                description=mission_data.get('description'),
                launch_date=datetime.strptime(mission_data.get('launch_date'), '%Y-%m-%d').date() if mission_data.get('launch_date') else None,
                status=mission_data.get('status', 'Active'),
                mission_type=mission_data.get('mission_type'),
                agency=mission_data.get('agency', 'NASA')
            )
            
            db.session.add(mission)
            db.session.commit()
            
            return mission_schema.dump(mission), None
        except IntegrityError:
            db.session.rollback()
            return None, "Mission with this name already exists"
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_mission(mission_id, mission_data):
        """Update an existing mission"""
        try:
            mission = Mission.query.get(mission_id)
            if not mission:
                return None, "Mission not found"
            
            # Update fields
            if 'name' in mission_data:
                mission.name = mission_data['name']
            if 'description' in mission_data:
                mission.description = mission_data['description']
            if 'launch_date' in mission_data:
                mission.launch_date = datetime.strptime(mission_data['launch_date'], '%Y-%m-%d').date()
            if 'status' in mission_data:
                mission.status = mission_data['status']
            if 'mission_type' in mission_data:
                mission.mission_type = mission_data['mission_type']
            if 'agency' in mission_data:
                mission.agency = mission_data['agency']
            
            mission.updated_at = datetime.utcnow()
            db.session.commit()
            
            return mission_schema.dump(mission), None
        except IntegrityError:
            db.session.rollback()
            return None, "Mission with this name already exists"
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_mission(mission_id):
        """Delete a mission"""
        try:
            mission = Mission.query.get(mission_id)
            if not mission:
                return False, "Mission not found"
            
            db.session.delete(mission)
            db.session.commit()
            
            return True, "Mission deleted successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_missions_by_type(mission_type):
        """Get missions by type"""
        try:
            missions = Mission.query.filter_by(mission_type=mission_type).all()
            return missions_schema.dump(missions), None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_missions_by_status(status):
        """Get missions by status"""
        try:
            missions = Mission.query.filter_by(status=status).all()
            return missions_schema.dump(missions), None
        except Exception as e:
            return None, str(e)