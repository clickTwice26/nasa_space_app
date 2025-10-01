from app import db
from app.models.user import User, UserSession, OnboardingProgress
from flask import session, request
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, timezone
import secrets
import uuid
import re
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for handling user authentication"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def get_user_profile(user_id):
        """Get user profile information"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            return {
                'success': True,
                'user': user.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get profile: {str(e)}'}
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email address"""
        try:
            user = User.query.filter_by(email=email.lower()).first()
            return user.to_dict() if user else None
        except Exception:
            return None
    
    @staticmethod 
    def get_user_by_username(username):
        """Get user by username"""
        try:
            user = User.query.filter_by(username=username.lower()).first()
            return user.to_dict() if user else None
        except Exception:
            return None

    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Za-z]', password):
            return False, "Password must contain at least one letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 20:
            return False, "Username must be less than 20 characters"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, "Username is valid"
    
    @staticmethod
    def register_user(email, username, password, **kwargs):
        """Register a new user"""
        try:
            # Validate input
            if not AuthService.validate_email(email):
                return {'success': False, 'message': 'Invalid email format'}
            
            is_valid, message = AuthService.validate_username(username)
            if not is_valid:
                return {'success': False, 'message': message}
            
            is_valid, message = AuthService.validate_password(password)
            if not is_valid:
                return {'success': False, 'message': message}
            
            # Check if user already exists
            if User.query.filter_by(email=email.lower()).first():
                return {'success': False, 'message': 'Email already registered'}
            
            if User.query.filter_by(username=username.lower()).first():
                return {'success': False, 'message': 'Username already taken'}
            
            # Create new user
            user = User(
                email=email,
                username=username,
                password=password,
                **kwargs
            )
            
            db.session.add(user)
            db.session.flush()  # Get user ID before commit
            
            # Create onboarding progress
            onboarding = OnboardingProgress(user_id=user.id)
            db.session.add(onboarding)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Registration failed: {str(e)}'}

    # --- Multi-step registration helpers ---
    @staticmethod
    def set_user_role(user: User, role: str):
        if role not in ['student', 'farmer', 'researcher']:
            raise ValueError('Invalid role type')
        user.profile_type = role
        db.session.commit()
        return user

    @staticmethod
    def set_user_location(user: User, payload: dict):
        location_type = payload.get('location_type')
        if location_type not in ['fixed', 'journey']:
            raise ValueError('Invalid location_type')
        user.location_type = location_type

        # Reset all coordinate fields first to avoid stale data
        user.latitude = None
        user.longitude = None
        user.start_latitude = None
        user.start_longitude = None
        user.end_latitude = None
        user.end_longitude = None

        if location_type == 'fixed':
            try:
                user.latitude = float(payload.get('latitude'))
                user.longitude = float(payload.get('longitude'))
            except (TypeError, ValueError):
                raise ValueError('Latitude and longitude are required for fixed location')
        else:  # journey
            try:
                user.start_latitude = float(payload.get('start_latitude'))
                user.start_longitude = float(payload.get('start_longitude'))
                user.end_latitude = float(payload.get('end_latitude'))
                user.end_longitude = float(payload.get('end_longitude'))
            except (TypeError, ValueError):
                raise ValueError('Start and end coordinates are required for journey location')
        db.session.commit()
        return user

    @staticmethod
    def create_complete_user(user_data):
        """Create a complete user with all information in one step"""
        try:
            # Validate required fields
            required_fields = ['email', 'username', 'password', 'profile_type', 'location_type']
            for field in required_fields:
                if not user_data.get(field):
                    return {'success': False, 'message': f'{field} is required'}
            
            # Check if user already exists
            if AuthService.get_user_by_email(user_data['email']):
                return {'success': False, 'message': 'Email already registered'}
            if AuthService.get_user_by_username(user_data['username']):
                return {'success': False, 'message': 'Username already taken'}
            
            # Create user
            user = User(
                email=user_data['email'],
                username=user_data['username'],
                password=user_data['password'],
                profile_type=user_data['profile_type'],
                location_type=user_data['location_type'],
                onboarding_completed=user_data.get('onboarding_completed', True)
            )
            
            # Add location data
            if user_data['location_type'] == 'fixed':
                user.latitude = user_data.get('latitude')
                user.longitude = user_data.get('longitude')
            elif user_data['location_type'] == 'journey':
                user.start_latitude = user_data.get('start_latitude')
                user.start_longitude = user_data.get('start_longitude')
                user.end_latitude = user_data.get('end_latitude')
                user.end_longitude = user_data.get('end_longitude')
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Registration completed successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating complete user: {str(e)}")
            return {'success': False, 'message': 'Registration failed'}

    @staticmethod
    def complete_registration(user: User):
        # Mark onboarding as completed if essential pieces exist
        if user.profile_type and (user.location_type == 'fixed' and user.latitude is not None or
                                  user.location_type == 'journey' and user.start_latitude is not None and user.end_latitude is not None):
            user.onboarding_completed = True
            db.session.commit()
        return user
    
    @staticmethod
    def authenticate_user(email_or_username, password):
        """Authenticate user with email/username and password"""
        try:
            # Find user by email or username
            user = User.query.filter(
                (User.email == email_or_username.lower()) |
                (User.username == email_or_username.lower())
            ).first()
            
            if not user:
                return {'success': False, 'message': 'Invalid credentials'}
            
            if not user.is_active:
                return {'success': False, 'message': 'Account is deactivated'}
            
            if not user.check_password(password):
                return {'success': False, 'message': 'Invalid credentials'}
            
            # Update last login
            user.update_last_login()
            
            return {
                'success': True,
                'message': 'Authentication successful',
                'user': user.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Authentication failed: {str(e)}'}
    
    @staticmethod
    def create_session(user_id, expires_hours=24):
        """Create a new user session"""
        try:
            # Generate session ID
            session_id = secrets.token_urlsafe(64)
            
            # Set expiration
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
            
            # Get request details
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            # Create session
            user_session = UserSession(
                session_id=session_id,
                user_id=user_id,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.add(user_session)
            db.session.commit()
            
            return {
                'success': True,
                'session_id': session_id,
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Session creation failed: {str(e)}'}
    
    @staticmethod
    def get_session(session_id):
        """Get active session by session ID"""
        try:
            user_session = UserSession.query.filter_by(
                session_id=session_id,
                is_active=True
            ).first()
            
            if not user_session:
                return {'success': False, 'message': 'Session not found'}
            
            if user_session.is_expired():
                user_session.deactivate()
                return {'success': False, 'message': 'Session expired'}
            
            # Update last activity
            user_session.last_activity = datetime.now(timezone.utc)
            db.session.commit()
            
            return {
                'success': True,
                'session': user_session.to_dict(),
                'user': user_session.user.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Session retrieval failed: {str(e)}'}
    
    @staticmethod
    def logout_session(session_id):
        """Logout and deactivate session"""
        try:
            user_session = UserSession.query.filter_by(session_id=session_id).first()
            
            if user_session:
                user_session.deactivate()
                return {'success': True, 'message': 'Logged out successfully'}
            
            return {'success': False, 'message': 'Session not found'}
            
        except Exception as e:
            return {'success': False, 'message': f'Logout failed: {str(e)}'}
    
    @staticmethod
    def logout_all_sessions(user_id):
        """Logout all sessions for a user"""
        try:
            UserSession.query.filter_by(user_id=user_id, is_active=True).update({
                'is_active': False
            })
            db.session.commit()
            
            return {'success': True, 'message': 'All sessions logged out'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Logout failed: {str(e)}'}
    
    @staticmethod
    def cleanup_expired_sessions():
        """Clean up expired sessions (should be run periodically)"""
        try:
            expired_sessions = UserSession.query.filter(
                UserSession.expires_at < datetime.now(timezone.utc),
                UserSession.is_active == True
            ).all()
            
            for session in expired_sessions:
                session.deactivate()
            
            db.session.commit()
            
            return {'success': True, 'cleaned': len(expired_sessions)}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Cleanup failed: {str(e)}'}


class OnboardingService:
    """Service for managing user onboarding process"""
    
    @staticmethod
    def get_onboarding_progress(user_id):
        """Get user's onboarding progress"""
        try:
            progress = OnboardingProgress.query.filter_by(user_id=user_id).first()
            
            if not progress:
                # Create new onboarding progress
                progress = OnboardingProgress(user_id=user_id)
                db.session.add(progress)
                db.session.commit()
            
            return {
                'success': True,
                'progress': progress.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get progress: {str(e)}'}
    
    @staticmethod
    def update_onboarding_step(user_id, step_name, data=None):
        """Update onboarding step completion"""
        try:
            progress = OnboardingProgress.query.filter_by(user_id=user_id).first()
            
            if not progress:
                progress = OnboardingProgress(user_id=user_id)
                db.session.add(progress)
                db.session.flush()
            
            # Complete the step
            progress.complete_step(step_name)
            
            # Update user profile if data provided
            if data and step_name == 'profile_type':
                user = User.query.get(user_id)
                if user:
                    user.profile_type = data.get('profile_type')
                    user.full_name = data.get('full_name')
            
            elif data and step_name == 'location':
                user = User.query.get(user_id)
                if user:
                    user.location = data.get('location')
                    user.district = data.get('district')
                    if user.profile_type == 'farmer':
                        user.farm_size = data.get('farm_size')
                        user.primary_crop = data.get('primary_crop')
            
            elif data and step_name == 'preferences':
                progress.selected_features = data.get('selected_features', [])
                progress.notification_preferences = data.get('notification_preferences', {})
            
            db.session.commit()
            
            return {
                'success': True,
                'progress': progress.to_dict(),
                'message': f'Step {step_name} completed'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Failed to update step: {str(e)}'}
    
    @staticmethod
    def complete_onboarding(user_id):
        """Complete the entire onboarding process"""
        try:
            progress = OnboardingProgress.query.filter_by(user_id=user_id).first()
            user = User.query.get(user_id)
            
            if not progress or not user:
                return {'success': False, 'message': 'User or progress not found'}
            
            # Mark all steps as completed
            progress.step_welcome = True
            progress.step_profile_type = True
            progress.step_location = True
            progress.step_preferences = True
            progress.step_completed = True
            progress.completed_at = datetime.now(timezone.utc)
            
            # Update user onboarding status
            user.onboarding_completed = True
            user.onboarding_step = 100
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Onboarding completed successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Failed to complete onboarding: {str(e)}'}


class ProfileService:
    """Service for managing user profiles"""
    
    @staticmethod
    def update_profile(user_id, data):
        """Update user profile information"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Update allowed fields
            allowed_fields = [
                'full_name', 'location', 'district', 'farm_size', 
                'primary_crop', 'profile_type'
            ]
            
            for field in allowed_fields:
                if field in data and data[field] is not None:
                    setattr(user, field, data[field])
            
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Profile update failed: {str(e)}'}
    
    @staticmethod
    def get_user_profile(user_id):
        """Get user profile information"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            return {
                'success': True,
                'user': user.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get profile: {str(e)}'}