from app import db
from datetime import datetime, timezone
from sqlalchemy import text
import uuid


class Community(db.Model):
    """Community model for agricultural communities"""
    
    __tablename__ = 'communities'
    
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Basic community information
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='general')  # 'rice', 'wheat', 'vegetables', 'general'
    
    # Community settings
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    requires_approval = db.Column(db.Boolean, default=False, nullable=False)
    
    # Community stats
    member_count = db.Column(db.Integer, default=0, nullable=False)
    post_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Location-based (optional)
    district = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    
    # Ownership
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='created_communities', foreign_keys=[created_by])
    members = db.relationship('CommunityMember', backref='community', lazy=True, cascade='all, delete-orphan')
    posts = db.relationship('CommunityPost', backref='community', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, name, created_by, **kwargs):
        self.name = name
        self.created_by = created_by
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_member_count(self):
        """Get actual member count"""
        return CommunityMember.query.filter_by(community_id=self.id, is_active=True).count()
    
    def get_post_count(self):
        """Get actual post count"""
        return CommunityPost.query.filter_by(community_id=self.id, is_active=True).count()
    
    def update_stats(self):
        """Update community statistics"""
        self.member_count = self.get_member_count()
        self.post_count = self.get_post_count()
        db.session.commit()
    
    def is_member(self, user_id):
        """Check if user is a member"""
        return CommunityMember.query.filter_by(
            community_id=self.id, 
            user_id=user_id, 
            is_active=True
        ).first() is not None
    
    def get_member_role(self, user_id):
        """Get user's role in community"""
        member = CommunityMember.query.filter_by(
            community_id=self.id, 
            user_id=user_id, 
            is_active=True
        ).first()
        return member.role if member else None
    
    def to_dict(self, include_user_info=None):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'community_id': self.community_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'requires_approval': self.requires_approval,
            'member_count': self.member_count,
            'post_count': self.post_count,
            'district': self.district,
            'location': self.location,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_user_info:
            data['is_member'] = self.is_member(include_user_info)
            data['user_role'] = self.get_member_role(include_user_info)
        
        return data
    
    def __repr__(self):
        return f'<Community {self.name}>'


class CommunityMember(db.Model):
    """Community membership model"""
    
    __tablename__ = 'community_members'
    
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Membership details
    role = db.Column(db.String(20), default='member', nullable=False)  # 'admin', 'moderator', 'member'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='community_memberships')
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('community_id', 'user_id', name='unique_community_member'),)
    
    def __init__(self, community_id, user_id, **kwargs):
        self.community_id = community_id
        self.user_id = user_id
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'community_id': self.community_id,
            'user_id': self.user_id,
            'role': self.role,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'joined_at': self.joined_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user': self.user.to_dict() if self.user else None
        }
    
    def __repr__(self):
        return f'<CommunityMember Community:{self.community_id} User:{self.user_id}>'


class CommunityPost(db.Model):
    """Community post model"""
    
    __tablename__ = 'community_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Post basic info
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Post content
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(20), default='text', nullable=False)  # 'text', 'image', 'alert', 'market', 'event'
    title = db.Column(db.String(200), nullable=True)  # For alerts, market posts, events
    
    # Post metadata
    tags = db.Column(db.JSON, nullable=True)  # Array of tags
    location = db.Column(db.String(100), nullable=True)
    
    # Alert-specific fields
    alert_type = db.Column(db.String(50), nullable=True)  # 'weather', 'pest', 'disease', 'market'
    alert_severity = db.Column(db.String(20), nullable=True)  # 'low', 'medium', 'high', 'critical'
    alert_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Market-specific fields
    market_price = db.Column(db.Float, nullable=True)
    market_unit = db.Column(db.String(20), nullable=True)  # 'kg', 'ton', 'piece'
    market_crop = db.Column(db.String(50), nullable=True)
    market_location = db.Column(db.String(100), nullable=True)
    
    # Event-specific fields
    event_date = db.Column(db.DateTime, nullable=True)
    event_location = db.Column(db.String(100), nullable=True)
    event_type = db.Column(db.String(50), nullable=True)  # 'training', 'meeting', 'fair', 'workshop'
    
    # Post status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    is_approved = db.Column(db.Boolean, default=True, nullable=False)
    
    # Engagement stats
    likes_count = db.Column(db.Integer, default=0, nullable=False)
    comments_count = db.Column(db.Integer, default=0, nullable=False)
    shares_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    author = db.relationship('User', backref='community_posts')
    likes = db.relationship('PostLike', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('PostComment', backref='post', lazy=True, cascade='all, delete-orphan')
    attachments = db.relationship('PostAttachment', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, community_id, user_id, content, **kwargs):
        self.community_id = community_id
        self.user_id = user_id
        self.content = content
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_likes_count(self):
        """Get actual likes count"""
        return PostLike.query.filter_by(post_id=self.id, is_active=True).count()
    
    def get_comments_count(self):
        """Get actual comments count"""
        return PostComment.query.filter_by(post_id=self.id, is_active=True).count()
    
    def update_engagement_stats(self):
        """Update engagement statistics"""
        self.likes_count = self.get_likes_count()
        self.comments_count = self.get_comments_count()
        db.session.commit()
    
    def is_liked_by(self, user_id):
        """Check if post is liked by user"""
        return PostLike.query.filter_by(
            post_id=self.id, 
            user_id=user_id, 
            is_active=True
        ).first() is not None
    
    def to_dict(self, include_user_info=None):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'post_id': self.post_id,
            'community_id': self.community_id,
            'user_id': self.user_id,
            'content': self.content,
            'post_type': self.post_type,
            'title': self.title,
            'tags': self.tags,
            'location': self.location,
            'alert_type': self.alert_type,
            'alert_severity': self.alert_severity,
            'alert_expires_at': self.alert_expires_at.isoformat() if self.alert_expires_at else None,
            'market_price': self.market_price,
            'market_unit': self.market_unit,
            'market_crop': self.market_crop,
            'market_location': self.market_location,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'event_location': self.event_location,
            'event_type': self.event_type,
            'is_active': self.is_active,
            'is_pinned': self.is_pinned,
            'is_approved': self.is_approved,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'author': self.author.to_dict() if self.author else None
        }
        
        if include_user_info:
            data['is_liked'] = self.is_liked_by(include_user_info)
        
        return data
    
    def __repr__(self):
        return f'<CommunityPost {self.post_id[:8]}...>'


class PostLike(db.Model):
    """Post like model"""
    
    __tablename__ = 'post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='post_likes')
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_post_like'),)
    
    def __init__(self, post_id, user_id):
        self.post_id = post_id
        self.user_id = user_id
    
    def __repr__(self):
        return f'<PostLike Post:{self.post_id} User:{self.user_id}>'


class PostComment(db.Model):
    """Post comment model"""
    
    __tablename__ = 'post_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('post_comments.id'), nullable=True)  # For replies
    
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    author = db.relationship('User', backref='post_comments')
    replies = db.relationship('PostComment', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def __init__(self, post_id, user_id, content, **kwargs):
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'comment_id': self.comment_id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'content': self.content,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'author': self.author.to_dict() if self.author else None,
            'replies_count': len(self.replies) if self.replies else 0
        }
    
    def __repr__(self):
        return f'<PostComment {self.comment_id[:8]}...>'


class PostAttachment(db.Model):
    """Post attachment model for images, documents, etc."""
    
    __tablename__ = 'post_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    attachment_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False)
    
    # File details
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 'image', 'document', 'video'
    file_size = db.Column(db.Integer, nullable=True)  # in bytes
    mime_type = db.Column(db.String(100), nullable=True)
    
    # Image-specific fields
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __init__(self, post_id, filename, file_path, file_type, **kwargs):
        self.post_id = post_id
        self.filename = filename
        self.file_path = file_path
        self.file_type = file_type
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'attachment_id': self.attachment_id,
            'post_id': self.post_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<PostAttachment {self.filename}>'