from app import db
from app.models.community import Community, CommunityMember, CommunityPost, PostLike, PostComment, PostAttachment
from app.models.user import User
from datetime import datetime, timezone
from sqlalchemy import desc, and_, or_
import logging

logger = logging.getLogger(__name__)


class CommunityService:
    """Service class for community operations"""
    
    @staticmethod
    def get_user_communities(user_id, limit=10, offset=0):
        """Get communities the user is a member of"""
        try:
            communities = db.session.query(Community).join(CommunityMember).filter(
                and_(
                    CommunityMember.user_id == user_id,
                    CommunityMember.is_active == True,
                    Community.is_active == True
                )
            ).order_by(desc(CommunityMember.joined_at)).limit(limit).offset(offset).all()
            
            return [community.to_dict(include_user_info=user_id) for community in communities]
        except Exception as e:
            logger.error(f"Error getting user communities: {str(e)}")
            return []
    
    @staticmethod
    def get_suggested_communities(user_id, limit=5):
        """Get suggested communities for the user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return []
            
            # Get communities user is not a member of
            user_community_ids = db.session.query(CommunityMember.community_id).filter(
                and_(
                    CommunityMember.user_id == user_id,
                    CommunityMember.is_active == True
                )
            ).subquery()
            
            # Suggest based on location, primary crop, or popular communities
            query = Community.query.filter(
                and_(
                    Community.is_active == True,
                    Community.is_public == True,
                    ~Community.id.in_(user_community_ids)
                )
            )
            
            # Priority: same district, same primary crop, then by member count
            if user.district:
                query = query.filter(
                    or_(
                        Community.district == user.district,
                        Community.district.is_(None)
                    )
                )
            
            if user.primary_crop:
                query = query.filter(
                    or_(
                        Community.category == user.primary_crop,
                        Community.category == 'general'
                    )
                )
            
            communities = query.order_by(desc(Community.member_count)).limit(limit).all()
            
            return [community.to_dict(include_user_info=user_id) for community in communities]
        except Exception as e:
            logger.error(f"Error getting suggested communities: {str(e)}")
            return []
    
    @staticmethod
    def join_community(user_id, community_id):
        """Join a community"""
        try:
            # Check if community exists and is active
            community = Community.query.filter_by(id=community_id, is_active=True).first()
            if not community:
                return {'success': False, 'message': 'Community not found'}
            
            # Check if user is already a member
            existing_member = CommunityMember.query.filter_by(
                community_id=community_id,
                user_id=user_id
            ).first()
            
            if existing_member:
                if existing_member.is_active:
                    return {'success': False, 'message': 'Already a member of this community'}
                else:
                    # Reactivate membership
                    existing_member.is_active = True
                    existing_member.joined_at = datetime.now(timezone.utc)
            else:
                # Create new membership
                member = CommunityMember(
                    community_id=community_id,
                    user_id=user_id,
                    role='member',
                    is_approved=not community.requires_approval
                )
                db.session.add(member)
            
            db.session.commit()
            
            # Update community stats
            community.update_stats()
            
            return {'success': True, 'message': 'Successfully joined community'}
        except Exception as e:
            logger.error(f"Error joining community: {str(e)}")
            db.session.rollback()
            return {'success': False, 'message': 'Failed to join community'}
    
    @staticmethod
    def leave_community(user_id, community_id):
        """Leave a community"""
        try:
            member = CommunityMember.query.filter_by(
                community_id=community_id,
                user_id=user_id,
                is_active=True
            ).first()
            
            if not member:
                return {'success': False, 'message': 'Not a member of this community'}
            
            # Check if user is the creator
            community = Community.query.get(community_id)
            if community and community.created_by == user_id:
                return {'success': False, 'message': 'Community creator cannot leave'}
            
            member.is_active = False
            db.session.commit()
            
            # Update community stats
            if community:
                community.update_stats()
            
            return {'success': True, 'message': 'Successfully left community'}
        except Exception as e:
            logger.error(f"Error leaving community: {str(e)}")
            db.session.rollback()
            return {'success': False, 'message': 'Failed to leave community'}
    
    @staticmethod
    def get_community_feed(user_id, community_id=None, post_type=None, limit=20, offset=0):
        """Get community feed posts"""
        try:
            # Build query - show all public posts regardless of membership
            if community_id:
                # If specific community requested, show only that community's posts
                query = CommunityPost.query.filter(
                    and_(
                        CommunityPost.community_id == community_id,
                        CommunityPost.is_active == True,
                        CommunityPost.is_approved == True
                    )
                )
            else:
                # Show all public posts from all communities
                query = CommunityPost.query.join(Community).filter(
                    and_(
                        Community.is_public == True,
                        Community.is_active == True,
                        CommunityPost.is_active == True,
                        CommunityPost.is_approved == True
                    )
                )
            
            # Filter by post type if specified
            if post_type and post_type != 'all':
                query = query.filter(CommunityPost.post_type == post_type)
            
            # Order by pinned first, then by creation date
            posts = query.order_by(
                desc(CommunityPost.is_pinned),
                desc(CommunityPost.created_at)
            ).limit(limit).offset(offset).all()
            
            return [post.to_dict(include_user_info=user_id) for post in posts]
        except Exception as e:
            logger.error(f"Error getting community feed: {str(e)}")
            return []
    
    @staticmethod
    def create_post(user_id, community_id, content, post_type='text', **kwargs):
        """Create a new community post"""
        try:
            # Check if user is a member of the community
            member = CommunityMember.query.filter_by(
                community_id=community_id,
                user_id=user_id,
                is_active=True,
                is_approved=True
            ).first()
            
            if not member:
                return {'success': False, 'message': 'You must be a member to post'}
            
            # Create post
            post = CommunityPost(
                community_id=community_id,
                user_id=user_id,
                content=content,
                post_type=post_type,
                **kwargs
            )
            
            db.session.add(post)
            db.session.commit()
            
            # Update community stats
            community = Community.query.get(community_id)
            if community:
                community.update_stats()
            
            return {
                'success': True, 
                'message': 'Post created successfully',
                'post': post.to_dict(include_user_info=user_id)
            }
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            db.session.rollback()
            return {'success': False, 'message': 'Failed to create post'}
    
    @staticmethod
    def like_post(user_id, post_id):
        """Like or unlike a post"""
        try:
            post = CommunityPost.query.get(post_id)
            if not post:
                return {'success': False, 'message': 'Post not found'}
            
            existing_like = PostLike.query.filter_by(
                post_id=post_id,
                user_id=user_id
            ).first()
            
            if existing_like:
                # Toggle like
                existing_like.is_active = not existing_like.is_active
                action = 'liked' if existing_like.is_active else 'unliked'
            else:
                # Create new like
                like = PostLike(post_id=post_id, user_id=user_id)
                db.session.add(like)
                action = 'liked'
            
            db.session.commit()
            
            # Update post stats
            post.update_engagement_stats()
            
            return {
                'success': True, 
                'message': f'Post {action}',
                'is_liked': post.is_liked_by(user_id),
                'likes_count': post.likes_count
            }
        except Exception as e:
            logger.error(f"Error liking post: {str(e)}")
            db.session.rollback()
            return {'success': False, 'message': 'Failed to like post'}
    
    @staticmethod
    def add_comment(user_id, post_id, content, parent_id=None):
        """Add a comment to a post"""
        try:
            post = CommunityPost.query.get(post_id)
            if not post:
                return {'success': False, 'message': 'Post not found'}
            
            # Check if user is a member of the community
            member = CommunityMember.query.filter_by(
                community_id=post.community_id,
                user_id=user_id,
                is_active=True,
                is_approved=True
            ).first()
            
            if not member:
                return {'success': False, 'message': 'You must be a member to comment'}
            
            comment = PostComment(
                post_id=post_id,
                user_id=user_id,
                content=content,
                parent_id=parent_id
            )
            
            db.session.add(comment)
            db.session.commit()
            
            # Update post stats
            post.update_engagement_stats()
            
            return {
                'success': True, 
                'message': 'Comment added successfully',
                'comment': comment.to_dict()
            }
        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")
            db.session.rollback()
            return {'success': False, 'message': 'Failed to add comment'}
    
    @staticmethod
    def get_post_comments(post_id, limit=20, offset=0):
        """Get comments for a post"""
        try:
            comments = PostComment.query.filter_by(
                post_id=post_id,
                is_active=True,
                parent_id=None  # Only top-level comments
            ).order_by(PostComment.created_at).limit(limit).offset(offset).all()
            
            return [comment.to_dict() for comment in comments]
        except Exception as e:
            logger.error(f"Error getting comments: {str(e)}")
            return []
    
    @staticmethod
    def get_community_stats():
        """Get overall community statistics"""
        try:
            total_communities = Community.query.filter_by(is_active=True).count()
            total_members = CommunityMember.query.filter_by(is_active=True).count()
            total_posts = CommunityPost.query.filter_by(is_active=True).count()
            
            # Popular communities
            popular_communities = Community.query.filter_by(
                is_active=True,
                is_public=True
            ).order_by(desc(Community.member_count)).limit(5).all()
            
            return {
                'total_communities': total_communities,
                'total_members': total_members,
                'total_posts': total_posts,
                'popular_communities': [c.to_dict() for c in popular_communities]
            }
        except Exception as e:
            logger.error(f"Error getting community stats: {str(e)}")
            return {
                'total_communities': 0,
                'total_members': 0,
                'total_posts': 0,
                'popular_communities': []
            }
    
    @staticmethod
    def search_communities(query, user_id, limit=10):
        """Search for communities"""
        try:
            communities = Community.query.filter(
                and_(
                    Community.is_active == True,
                    Community.is_public == True,
                    or_(
                        Community.name.ilike(f'%{query}%'),
                        Community.description.ilike(f'%{query}%'),
                        Community.category.ilike(f'%{query}%')
                    )
                )
            ).order_by(desc(Community.member_count)).limit(limit).all()
            
            return [community.to_dict(include_user_info=user_id) for community in communities]
        except Exception as e:
            logger.error(f"Error searching communities: {str(e)}")
            return []
    
    @staticmethod
    def create_community(user_id, name, description, category='general', **kwargs):
        """Create a new community"""
        try:
            community = Community(
                name=name,
                description=description,
                category=category,
                created_by=user_id,
                **kwargs
            )
            
            db.session.add(community)
            db.session.flush()  # Get the ID
            
            # Add creator as admin member
            member = CommunityMember(
                community_id=community.id,
                user_id=user_id,
                role='admin'
            )
            
            db.session.add(member)
            db.session.commit()
            
            # Update stats
            community.update_stats()
            
            return {
                'success': True,
                'message': 'Community created successfully',
                'community': community.to_dict(include_user_info=user_id)
            }
        except Exception as e:
            logger.error(f"Error creating community: {str(e)}")
            db.session.rollback()
            return {'success': False, 'message': 'Failed to create community'}
    
    @staticmethod
    def get_popular_communities(limit=9):
        """Get popular communities ordered by member count"""
        try:
            communities = Community.query.filter(
                and_(
                    Community.is_active == True,
                    Community.is_public == True
                )
            ).order_by(desc(Community.member_count)).limit(limit).all()
            
            return [community.to_dict() for community in communities]
        except Exception as e:
            logger.error(f"Error getting popular communities: {str(e)}")
            return []