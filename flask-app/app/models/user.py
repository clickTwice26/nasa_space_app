from app import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class User(db.Model):
    """User model for authentication and profile management"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Basic user information
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    full_name = db.Column(db.String(100), nullable=True)
    profile_type = db.Column(db.String(20), nullable=True)  # 'student', 'farmer', 'researcher'
    location = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    
    # Location capture enhancements
    location_type = db.Column(db.String(20), nullable=True)  # 'fixed' | 'journey'
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    start_latitude = db.Column(db.Float, nullable=True)
    start_longitude = db.Column(db.Float, nullable=True)
    end_latitude = db.Column(db.Float, nullable=True)
    end_longitude = db.Column(db.Float, nullable=True)
    
    # Farmer-specific fields
    farm_size = db.Column(db.Float, nullable=True)  # in hectares
    primary_crop = db.Column(db.String(50), nullable=True)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Onboarding status
    onboarding_completed = db.Column(db.Boolean, default=False, nullable=False)
    onboarding_step = db.Column(db.Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, username, password, **kwargs):
        self.email = email.lower().strip()
        self.username = username.lower().strip()
        self.set_password(password)
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def complete_onboarding(self):
        """Mark onboarding as completed"""
        self.onboarding_completed = True
        self.onboarding_step = 100  # Final step
        db.session.commit()
    
    def get_profile_completion(self):
        """Calculate profile completion percentage"""
        fields = ['full_name', 'profile_type', 'location', 'district']
        completed = sum(1 for field in fields if getattr(self, field))
        
        if self.profile_type == 'farmer':
            fields.extend(['farm_size', 'primary_crop'])
            completed += sum(1 for field in ['farm_size', 'primary_crop'] if getattr(self, field))
        
        return int((completed / len(fields)) * 100)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'profile_type': self.profile_type,
            'location': self.location,
            'district': self.district,
            'location_type': self.location_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'start_latitude': self.start_latitude,
            'start_longitude': self.start_longitude,
            'end_latitude': self.end_latitude,
            'end_longitude': self.end_longitude,
            'farm_size': self.farm_size,
            'primary_crop': self.primary_crop,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'onboarding_completed': self.onboarding_completed,
            'onboarding_step': self.onboarding_step,
            'profile_completion': self.get_profile_completion(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserSession(db.Model):
    """User session model for session management"""
    
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session details
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_activity = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __init__(self, session_id, user_id, expires_at, **kwargs):
        self.session_id = session_id
        self.user_id = user_id
        self.expires_at = expires_at
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def is_expired(self):
        """Check if session is expired"""
        return datetime.now(timezone.utc) > self.expires_at
    
    def extend_session(self, hours=24):
        """Extend session expiration"""
        from datetime import timedelta
        self.expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)
        self.last_activity = datetime.now(timezone.utc)
        db.session.commit()
    
    def deactivate(self):
        """Deactivate the session"""
        self.is_active = False
        db.session.commit()
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'is_expired': self.is_expired()
        }
    
    def __repr__(self):
        return f'<UserSession {self.session_id[:8]}...>'


class OnboardingProgress(db.Model):
    """Track user onboarding progress"""
    
    __tablename__ = 'onboarding_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Onboarding steps
    step_welcome = db.Column(db.Boolean, default=False, nullable=False)
    step_profile_type = db.Column(db.Boolean, default=False, nullable=False)
    step_location = db.Column(db.Boolean, default=False, nullable=False)
    step_preferences = db.Column(db.Boolean, default=False, nullable=False)
    step_completed = db.Column(db.Boolean, default=False, nullable=False)
    
    # Additional data collected during onboarding
    selected_features = db.Column(db.JSON, nullable=True)  # Features user is interested in
    notification_preferences = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship
    user = db.relationship('User', backref='onboarding_progress', uselist=False)
    
    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_current_step(self):
        """Get the current onboarding step"""
        if not self.step_welcome:
            return 1
        elif not self.step_profile_type:
            return 2
        elif not self.step_location:
            return 3
        elif not self.step_preferences:
            return 4
        elif not self.step_completed:
            return 5
        else:
            return 6  # Completed
    
    def complete_step(self, step_name):
        """Mark a specific step as completed"""
        if hasattr(self, f'step_{step_name}'):
            setattr(self, f'step_{step_name}', True)
            
            # If all steps are completed, mark as completed
            if self.get_current_step() > 5:
                self.step_completed = True
                self.completed_at = datetime.now(timezone.utc)
                
                # Update user's onboarding status
                self.user.complete_onboarding()
        
        db.session.commit()
    
    def get_progress_percentage(self):
        """Calculate onboarding progress percentage"""
        steps = [
            self.step_welcome,
            self.step_profile_type,
            self.step_location,
            self.step_preferences,
            self.step_completed
        ]
        completed_steps = sum(steps)
        return int((completed_steps / len(steps)) * 100)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'current_step': self.get_current_step(),
            'progress_percentage': self.get_progress_percentage(),
            'steps': {
                'welcome': self.step_welcome,
                'profile_type': self.step_profile_type,
                'location': self.step_location,
                'preferences': self.step_preferences,
                'completed': self.step_completed
            },
            'selected_features': self.selected_features,
            'notification_preferences': self.notification_preferences,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<OnboardingProgress User:{self.user_id} Step:{self.get_current_step()}>'