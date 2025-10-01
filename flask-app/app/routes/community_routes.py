from flask import Blueprint, request, jsonify, session
from app.routes.auth_routes import login_required, get_current_user
from app.services.community_service import CommunityService
from app.models.community import Community, CommunityPost
from app import db
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid

logger = logging.getLogger(__name__)

community_bp = Blueprint('community', __name__, url_prefix='/api/community')

# File upload configuration
UPLOAD_FOLDER = 'app/static/uploads/posts'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return the file path"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        file.save(file_path)
        # Return relative path for web access
        return f"/static/uploads/posts/{unique_filename}"
    return None


@community_bp.route('/feed')
@login_required
def get_feed():
    """Get community feed for the user"""
    try:
        user = get_current_user()
        community_id = request.args.get('community_id', type=int)
        post_type = request.args.get('type', 'all')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        posts = CommunityService.get_community_feed(
            user_id=user['id'],
            community_id=community_id,
            post_type=post_type,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'posts': posts,
            'has_more': len(posts) == limit
        })
    except Exception as e:
        logger.error(f"Community feed error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load feed'}), 500


@community_bp.route('/my-communities')
@login_required
def get_my_communities():
    """Get communities the user is a member of"""
    try:
        user = get_current_user()
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        communities = CommunityService.get_user_communities(
            user_id=user['id'],
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'communities': communities
        })
    except Exception as e:
        logger.error(f"My communities error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load communities'}), 500


@community_bp.route('/suggested')
@login_required
def get_suggested_communities():
    """Get suggested communities for the user"""
    try:
        user = get_current_user()
        limit = request.args.get('limit', 5, type=int)
        
        communities = CommunityService.get_suggested_communities(
            user_id=user['id'],
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'communities': communities
        })
    except Exception as e:
        logger.error(f"Suggested communities error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load suggestions'}), 500


@community_bp.route('/join', methods=['POST'])
@login_required
def join_community():
    """Join a community"""
    try:
        user = get_current_user()
        data = request.get_json()
        community_id = data.get('community_id')
        
        if not community_id:
            return jsonify({'success': False, 'message': 'Community ID required'}), 400
        
        result = CommunityService.join_community(
            user_id=user['id'],
            community_id=community_id
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Join community error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to join community'}), 500


@community_bp.route('/leave', methods=['POST'])
@login_required
def leave_community():
    """Leave a community"""
    try:
        user = get_current_user()
        data = request.get_json()
        community_id = data.get('community_id')
        
        if not community_id:
            return jsonify({'success': False, 'message': 'Community ID required'}), 400
        
        result = CommunityService.leave_community(
            user_id=user['id'],
            community_id=community_id
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Leave community error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to leave community'}), 500


@community_bp.route('/create', methods=['POST'])
@login_required
def create_community():
    """Create a new community"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        required_fields = ['name', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        result = CommunityService.create_community(
            user_id=user['id'],
            name=data['name'],
            description=data['description'],
            category=data.get('category', 'general'),
            district=data.get('district'),
            location=data.get('location'),
            is_public=data.get('is_public', True),
            requires_approval=data.get('requires_approval', False)
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Create community error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to create community'}), 500


@community_bp.route('/post/create', methods=['POST'])
@login_required
def create_post():
    """Create a new post with optional file upload"""
    try:
        user = get_current_user()
        
        # Handle both JSON and form data
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Form data with file upload
            data = request.form.to_dict()
            files = request.files
        else:
            # JSON data
            data = request.get_json() or {}
            files = {}
        
        # Validate required fields
        if not data.get('content') or not data.get('community_id'):
            return jsonify({
                'success': False, 
                'message': 'Content and community selection are required'
            }), 400
        
        try:
            community_id = int(data['community_id'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False, 
                'message': 'Invalid community ID'
            }), 400
        
        # Prepare post data
        post_data = {
            'title': data.get('title', '').strip(),
            'post_type': data.get('post_type', 'text'),
            'location': data.get('location', '').strip(),
            'tags': data.get('tags', '').split(',') if data.get('tags') else []
        }
        
        # Handle different post types
        post_type = data.get('post_type', 'text')
        
        if post_type == 'alert':
            post_data.update({
                'alert_type': data.get('alert_type', 'general'),
                'alert_severity': data.get('alert_severity', 'medium')
            })
            if data.get('alert_expires_at'):
                try:
                    post_data['alert_expires_at'] = datetime.fromisoformat(data['alert_expires_at'])
                except ValueError:
                    pass
        
        elif post_type == 'market':
            post_data.update({
                'market_price': float(data['market_price']) if data.get('market_price') else None,
                'market_unit': data.get('market_unit', 'kg'),
                'market_crop': data.get('market_crop', ''),
                'market_location': data.get('market_location', '')
            })
        
        elif post_type == 'event':
            post_data.update({
                'event_type': data.get('event_type', 'general'),
                'event_location': data.get('event_location', '')
            })
            if data.get('event_date'):
                try:
                    post_data['event_date'] = datetime.fromisoformat(data['event_date'])
                except ValueError:
                    pass
        
        # Handle file upload
        uploaded_file_path = None
        if 'image' in files and files['image'].filename:
            uploaded_file = files['image']
            if uploaded_file.content_length > MAX_FILE_SIZE:
                return jsonify({
                    'success': False, 
                    'message': 'File size too large. Maximum 5MB allowed.'
                }), 400
            
            uploaded_file_path = save_uploaded_file(uploaded_file)
            if uploaded_file_path:
                post_data['post_type'] = 'image'
        
        # Create the post
        result = CommunityService.create_post(
            user_id=user['id'],
            community_id=community_id,
            content=data['content'],
            **post_data
        )
        
        # If file was uploaded and post created successfully, save attachment
        if result['success'] and uploaded_file_path:
            from app.models.community import PostAttachment
            
            attachment = PostAttachment(
                post_id=result['post']['id'],
                filename=files['image'].filename,
                file_path=uploaded_file_path,
                file_type='image',
                file_size=files['image'].content_length,
                mime_type=files['image'].mimetype
            )
            db.session.add(attachment)
            db.session.commit()
            
            # Add attachment info to response
            result['post']['attachments'] = [attachment.to_dict()]
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Create post error: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'Failed to create post'
        }), 500


@community_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Like or unlike a post"""
    try:
        user = get_current_user()
        
        result = CommunityService.like_post(
            user_id=user['id'],
            post_id=post_id
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Like post error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to like post'}), 500


@community_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add a comment to a post"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'success': False, 'message': 'Comment content is required'}), 400
        
        result = CommunityService.add_comment(
            user_id=user['id'],
            post_id=post_id,
            content=data['content'],
            parent_id=data.get('parent_id')
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Add comment error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to add comment'}), 500


@community_bp.route('/post/<int:post_id>/comments')
@login_required
def get_comments(post_id):
    """Get comments for a post"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        comments = CommunityService.get_post_comments(
            post_id=post_id,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'comments': comments
        })
    except Exception as e:
        logger.error(f"Get comments error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load comments'}), 500


@community_bp.route('/search')
@login_required
def search_communities():
    """Search for communities"""
    try:
        user = get_current_user()
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({'success': False, 'message': 'Search query required'}), 400
        
        communities = CommunityService.search_communities(
            query=query,
            user_id=user['id'],
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'communities': communities
        })
    except Exception as e:
        logger.error(f"Search communities error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to search communities'}), 500


@community_bp.route('/stats')
@login_required
def get_stats():
    """Get community statistics"""
    try:
        stats = CommunityService.get_community_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load stats'}), 500


@community_bp.route('/post/topics')
@login_required
def get_post_topics():
    """Get available post topics/categories"""
    try:
        topics = [
            {'value': 'general', 'label': 'General Discussion', 'icon': 'fas fa-comments'},
            {'value': 'question', 'label': 'Ask a Question', 'icon': 'fas fa-question-circle'},
            {'value': 'success', 'label': 'Success Story', 'icon': 'fas fa-trophy'},
            {'value': 'tip', 'label': 'Farming Tip', 'icon': 'fas fa-lightbulb'},
            {'value': 'weather', 'label': 'Weather Alert', 'icon': 'fas fa-cloud-rain'},
            {'value': 'market', 'label': 'Market Price', 'icon': 'fas fa-chart-line'},
            {'value': 'pest', 'label': 'Pest Control', 'icon': 'fas fa-bug'},
            {'value': 'disease', 'label': 'Plant Disease', 'icon': 'fas fa-virus'},
            {'value': 'technology', 'label': 'AgriTech', 'icon': 'fas fa-microchip'},
            {'value': 'event', 'label': 'Event/Training', 'icon': 'fas fa-calendar'},
            {'value': 'seed', 'label': 'Seeds & Varieties', 'icon': 'fas fa-seedling'},
            {'value': 'fertilizer', 'label': 'Fertilizer', 'icon': 'fas fa-flask'},
            {'value': 'irrigation', 'label': 'Irrigation', 'icon': 'fas fa-tint'},
            {'value': 'harvest', 'label': 'Harvest Time', 'icon': 'fas fa-cut'}
        ]
        
        return jsonify({
            'success': True,
            'topics': topics
        })
    except Exception as e:
        logger.error(f"Get topics error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load topics'}), 500


@community_bp.route('/districts')
@login_required
def get_districts():
    """Get list of districts in Bangladesh"""
    try:
        districts = [
            'Barisal', 'Barguna', 'Bhola', 'Jhalokati', 'Patuakhali', 'Pirojpur',
            'Bandarban', 'Brahmanbaria', 'Chandpur', 'Chittagong', 'Comilla', 'Cox\'s Bazar',
            'Feni', 'Khagrachhari', 'Lakshmipur', 'Noakhali', 'Rangamati',
            'Dhaka', 'Faridpur', 'Gazipur', 'Gopalganj', 'Kishoreganj', 'Madaripur',
            'Manikganj', 'Munshiganj', 'Narayanganj', 'Narsingdi', 'Rajbari', 'Shariatpur', 'Tangail',
            'Bagerhat', 'Chuadanga', 'Jessore', 'Jhenaidah', 'Khulna', 'Kushtia',
            'Magura', 'Meherpur', 'Narail', 'Satkhira',
            'Jamalpur', 'Mymensingh', 'Netrakona', 'Sherpur',
            'Bogra', 'Joypurhat', 'Naogaon', 'Natore', 'Nawabganj', 'Pabna',
            'Rajshahi', 'Sirajganj',
            'Dinajpur', 'Gaibandha', 'Kurigram', 'Lalmonirhat', 'Nilphamari',
            'Panchagarh', 'Rangpur', 'Thakurgaon',
            'Habiganj', 'Moulvibazar', 'Sunamganj', 'Sylhet'
        ]
        
        return jsonify({
            'success': True,
            'districts': sorted(districts)
        })
    except Exception as e:
        logger.error(f"Get districts error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load districts'}), 500


@community_bp.route('/<int:community_id>')
@login_required
def get_community_details(community_id):
    """Get detailed information about a community"""
    try:
        user = get_current_user()
        
        community = Community.query.filter_by(id=community_id, is_active=True).first()
        if not community:
            return jsonify({'success': False, 'message': 'Community not found'}), 404
        
        return jsonify({
            'success': True,
            'community': community.to_dict(include_user_info=user['id'])
        })
    except Exception as e:
        logger.error(f"Get community details error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load community details'}), 500


@community_bp.route('/<int:community_id>/posts')
@login_required
def get_community_posts(community_id):
    """Get posts for a specific community"""
    try:
        user = get_current_user()
        post_type = request.args.get('type', 'all')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        posts = CommunityService.get_community_feed(
            user_id=user['id'],
            community_id=community_id,
            post_type=post_type,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'posts': posts,
            'has_more': len(posts) == limit
        })
    except Exception as e:
        logger.error(f"Get community posts error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load posts'}), 500