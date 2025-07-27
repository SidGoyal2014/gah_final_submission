from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import FarmerScheme, User
from sqlalchemy.exc import SQLAlchemyError
from app.routes.auth import jwt_required
import logging
import os
import requests

# Create blueprint
bp = Blueprint('help_farmers', __name__)
logger = logging.getLogger(__name__)

@bp.route('/schemes', methods=['GET'])
def get_all_schemes():
    """Get all farmer schemes with optional filtering"""
    try:
        # Get query parameters for filtering
        state_central = request.args.get('state_central')
        scheme_category = request.args.get('category')
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query with filters
        query = FarmerScheme.query
        
        if state_central:
            query = query.filter(FarmerScheme.state_central.ilike(f'%{state_central}%'))
        
        if scheme_category:
            query = query.filter(FarmerScheme.scheme_category.ilike(f'%{scheme_category}%'))
        
        if status:
            query = query.filter(FarmerScheme.status.ilike(f'%{status}%'))
        
        # # Execute query with pagination
        # schemes = query.order_by(FarmerScheme.created_at.desc())\
        schemes = query.offset(offset)\
                        .limit(limit)\
                        .all()
        
        # Get total count for pagination
        total_count = query.count()
        
        return jsonify({
            'success': True,
            'data': [scheme.to_dict() for scheme in schemes],
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_next': (offset + limit) < total_count
            }
        }), 200
        
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching schemes: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error occurred',
            'error': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching schemes: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500

@bp.route('/schemes/<int:scheme_id>', methods=['GET'])
def get_scheme_by_id(scheme_id):
    """Get a specific farmer scheme by ID"""
    try:
        scheme = FarmerScheme.query.filter_by(id=scheme_id).first()
        
        if not scheme:
            return jsonify({
                'success': False,
                'message': 'Scheme not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': scheme.to_dict()
        }), 200
        
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching scheme {scheme_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error occurred',
            'error': str(e)
        }), 500

# @bp.route('/schemes/by-state/<state>', methods=['GET'])
# def get_schemes_by_state(state):
#     """Get farmer schemes filtered by state"""
#     try:
#         schemes = FarmerScheme.query.filter(
#             FarmerScheme.state_central.ilike(f'%{state}%')
#         ).order_by(FarmerScheme.scheme_name).all()
        
#         return jsonify({
#             'success': True,
#             'data': [scheme.to_dict() for scheme in schemes],
#             'state': state,
#             'count': len(schemes)
#         }), 200
        
#     except SQLAlchemyError as e:
#         logger.error(f"Database error fetching schemes for state {state}: {str(e)}")
#         return jsonify({
#             'success': False,
#             'message': 'Database error occurred',
#             'error': str(e)
#         }), 500

# @bp.route('/schemes/by-category/<category>', methods=['GET'])
# def get_schemes_by_category(category):
#     """Get farmer schemes filtered by category"""
#     try:
#         schemes = FarmerScheme.query.filter(
#             FarmerScheme.scheme_category.ilike(f'%{category}%')
#         ).order_by(FarmerScheme.scheme_name).all()
        
#         return jsonify({
#             'success': True,
#             'data': [scheme.to_dict() for scheme in schemes],
#             'scheme_category': category,
#             'count': len(schemes)
#         }), 200
        
#     except SQLAlchemyError as e:
#         logger.error(f"Database error fetching schemes for category {category}: {str(e)}")
#         return jsonify({
#             'success': False,
#             'message': 'Database error occurred',
#             'error': str(e)
#         }), 500

@bp.route('/schemes/search', methods=['GET'])
def search_schemes():
    """Search farmer schemes by name or objective"""
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({
                'success': False,
                'message': 'Search term is required'
            }), 400
        
        schemes = FarmerScheme.query.filter(
            db.or_(
                FarmerScheme.scheme_name.ilike(f'%{search_term}%'),
                FarmerScheme.objective.ilike(f'%{search_term}%'),
                FarmerScheme.target_beneficiaries.ilike(f'%{search_term}%')
            )
        ).order_by(FarmerScheme.scheme_name).all()
        
        return jsonify({
            'success': True,
            'data': [scheme.to_dict() for scheme in schemes],
            'search_term': search_term,
            'count': len(schemes)
        }), 200
        
    except SQLAlchemyError as e:
        logger.error(f"Database error searching schemes: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error occurred',
            'error': str(e)
        }), 500

# @bp.route('/schemes/categories', methods=['GET'])
# def get_scheme_categories():
#     """Get all unique scheme categories"""
#     try:
#         categories = db.session.query(FarmerScheme.scheme_category)\
#                               .filter(FarmerScheme.scheme_category.isnot(None))\
#                               .distinct()\
#                               .all()
        
#         category_list = [cat[0] for cat in categories if cat[0]]
        
#         return jsonify({
#             'success': True,
#             'data': sorted(category_list),
#             'count': len(category_list)
#         }), 200
        
#     except SQLAlchemyError as e:
#         logger.error(f"Database error fetching categories: {str(e)}")
#         return jsonify({
#             'success': False,
#             'message': 'Database error occurred',
#             'error': str(e)
#         }), 500

# @bp.route('/schemes/states', methods=['GET'])
# def get_scheme_states():
#     """Get all unique states/central schemes"""
#     try:
#         states = db.session.query(FarmerScheme.state_central)\
#                           .filter(FarmerScheme.state_central.isnot(None))\
#                           .distinct()\
#                           .all()
        
#         state_list = [state[0] for state in states if state[0]]
        
#         return jsonify({
#             'success': True,
#             'data': sorted(state_list),
#             'count': len(state_list)
#         }), 200
        
#     except SQLAlchemyError as e:
#         logger.error(f"Database error fetching states: {str(e)}")
#         return jsonify({
#             'success': False,
#             'message': 'Database error occurred',
#             'error': str(e)
#         }), 500

# @bp.route('/schemes/stats', methods=['GET'])
# def get_scheme_statistics():
#     """Get statistics about farmer schemes"""
#     try:
#         total_schemes = FarmerScheme.query.count()
        
#         # Count by category
#         category_stats = db.session.query(
#             FarmerScheme.scheme_category,
#             db.func.count(FarmerScheme.id).label('count')
#         ).group_by(FarmerScheme.scheme_category)\
#          .all()
        
#         # Count by state/central
#         state_stats = db.session.query(
#             FarmerScheme.state_central,
#             db.func.count(FarmerScheme.id).label('count')
#         ).group_by(FarmerScheme.state_central)\
#          .order_by(db.func.count(FarmerScheme.id).desc())\
#          .limit(10)\
#          .all()
        
#         return jsonify({
#             'success': True,
#             'data': {
#                 'total_schemes': total_schemes,
#                 'by_category': [{'category': c[0], 'count': c[1]} for c in category_stats if c[0]],
#                 'top_states': [{'state_central': s[0], 'count': s[1]} for s in state_stats if s[0]]
#             }
#         }), 200
        
#     except SQLAlchemyError as e:
#         logger.error(f"Database error fetching statistics: {str(e)}")
#         return jsonify({
#             'success': False,
#             'message': 'Database error occurred',
#             'error': str(e)
#         }), 500
        
#     except SQLAlchemyError as e:
#         logger.error(f"Database error fetching statistics: {str(e)}")
#         return jsonify({
#             'success': False,
#             'message': 'Database error occurred',
#             'error': str(e)
#         }), 500


#####################################################
#### CRISIS SCHEMES ROUTES
#####################################################

@bp.route('/crisis/schemes', methods=['GET'])
def get_all_crisis_schemes():
    """Get all farmer crisis schemes"""
    try:
        # Import the crisis schemes model
        from app.models import FarmerSchemeCrisis
        
        # Get query parameters for filtering (optional since only 8 rows)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query - fetch all crisis schemes
        query = FarmerSchemeCrisis.query
        
        # Execute query with pagination (though probably not needed for 8 rows)
        schemes = query.offset(offset)\
                        .limit(limit)\
                        .all()
        
        # Get total count
        total_count = query.count()
        
        return jsonify({
            'success': True,
            'data': [scheme.to_dict() for scheme in schemes],
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_next': (offset + limit) < total_count
            }
        }), 200
        
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching crisis schemes: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error occurred',
            'error': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching crisis schemes: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500

@bp.route('/crisis/schemes/search', methods=['GET'])
def search_crisis_schemes():
    """Search farmer crisis schemes by name or purpose"""
    try:
        from app.models import FarmerSchemeCrisis
        
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({
                'success': False,
                'message': 'Search term is required'
            }), 400
        
        schemes = FarmerSchemeCrisis.query.filter(
            db.or_(
                FarmerSchemeCrisis.scheme_name.ilike(f'%{search_term}%'),
                FarmerSchemeCrisis.purpose.ilike(f'%{search_term}%'),
                FarmerSchemeCrisis.coverage.ilike(f'%{search_term}%')
            )
        ).all()
        
        return jsonify({
            'success': True,
            'data': [scheme.to_dict() for scheme in schemes],
            'search_term': search_term,
            'count': len(schemes)
        }), 200
        
    except SQLAlchemyError as e:
        logger.error(f"Database error searching crisis schemes: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error occurred',
            'error': str(e)
        }), 500

#####################################################
#### TUTORIALS AND VIDEOS ROUTES
#####################################################

@bp.route('/tutorials', methods=['GET'])
def get_tutorials():
    """
    Get tutorials based on topic
    """
    topic = request.args.get('topic', '').strip()
    phone = request.args.get('phone', '').strip()

    if not topic:
        return jsonify({
            'success': False,
            'message': 'Topic is required'
        }), 400

    # Get the user from user id
    user = User.query.get(phone)

    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404
    
    # Fetch tutorials from the database or external API
    tutorials = fetch_tutorials(topic, user.language)

    return jsonify({
        'success': True,
        'data': tutorials
    }), 200

def fetch_tutorials(topic, language='english', max_results=100):
    """
    Fetch tutorial videos from YouTube Data API based on topic and language
    """
    try:
        # Get YouTube API key from environment variables
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        
        if not youtube_api_key:
            logger.error("YouTube API key not found in environment variables")
            return []

        # Map language codes for better search results
        language_map = {
            'english': 'en',
            'hindi': 'hi',
            'bengali': 'bn',
            'tamil': 'ta',
            'telugu': 'te',
            'marathi': 'mr',
            'gujarati': 'gu',
            'kannada': 'kn',
            'malayalam': 'ml',
            'punjabi': 'pa',
            'urdu': 'ur'
        }

        # Get language code
        lang_code = language_map.get(language.lower(), 'en')

        # Construct search query - add farming/agriculture context
        search_query = f"{topic} farming agriculture tutorial"
        if language.lower() != 'english':
            search_query += f" {language}"

        # YouTube Data API v3 search endpoint
        youtube_search_url = "https://www.googleapis.com/youtube/v3/search"
        
        params = {
            'part': 'snippet',
            'q': search_query,
            'type': 'video',
            'maxResults': max_results,
            'key': youtube_api_key,
            'relevanceLanguage': lang_code,
            'safeSearch': 'strict',
            'videoDefinition': 'any',
            'videoCaption': 'any',
            'order': 'relevance'
        }

        response = requests.get(youtube_search_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        data = response.json()
        
        # Parse and format the response
        tutorials = []
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            video_id = item.get('id', {}).get('videoId')
            
            if video_id:
                tutorial = {
                    'title': snippet.get('title', 'No Title'),
                    'description': snippet.get('description', '')[:200] + '...' if len(snippet.get('description', '')) > 200 else snippet.get('description', ''),
                    'video_id': video_id,
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                    'channel_title': snippet.get('channelTitle', 'Unknown Channel'),
                    'published_at': snippet.get('publishedAt', ''),
                    'language': language,
                    'topic': topic
                }
                tutorials.append(tutorial)

        logger.info(f"Successfully fetched {len(tutorials)} tutorials for topic: {topic}, language: {language}")
        return tutorials

    except Exception as e:
        logger.error(f"Error in fetch_tutorials: {str(e)}")
        return None

@bp.route('/tutorials/categories', methods=['GET'])
def get_tutorial_categories():
    """Get suggested tutorial categories for farming"""
    categories = [
        {
            'category': 'Crop Management',
            'topics': ['rice farming', 'wheat cultivation', 'corn growing', 'vegetable farming', 'organic farming']
        },
        {
            'category': 'Irrigation',
            'topics': ['drip irrigation', 'sprinkler systems', 'water management', 'rainwater harvesting']
        },
        {
            'category': 'Pest Control',
            'topics': ['integrated pest management', 'organic pesticides', 'crop protection', 'disease prevention']
        },
        {
            'category': 'Soil Health',
            'topics': ['soil testing', 'composting', 'fertilizer application', 'soil conservation']
        },
        {
            'category': 'Modern Techniques',
            'topics': ['precision farming', 'greenhouse farming', 'hydroponic farming', 'smart farming']
        },
        {
            'category': 'Livestock',
            'topics': ['dairy farming', 'poultry farming', 'goat farming', 'animal husbandry']
        }
    ]
    
    return jsonify({
        'success': True,
        'data': categories
    }), 200

@bp.route('/tutorials/popular', methods=['GET'])
def get_popular_tutorials():
    """Get popular farming tutorial topics"""
    try:
        language = request.args.get('language', 'english').strip().lower()
        
        popular_topics = [
            'organic farming techniques',
            'drip irrigation setup',
            'crop rotation methods',
            'pest control natural methods',
            'soil preparation techniques',
            'greenhouse farming',
            'composting methods',
            'seed treatment techniques'
        ]
        
        # Fetch tutorials for each popular topic (limit to 3 per topic)
        all_tutorials = []
        for topic in popular_topics[:4]:  # Limit to 4 topics to avoid API quota issues
            tutorials = fetch_tutorials(topic, language, 3)
            if tutorials:
                all_tutorials.extend(tutorials)
        
        return jsonify({
            'success': True,
            'data': all_tutorials,
            'count': len(all_tutorials),
            'language': language
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching popular tutorials: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while fetching popular tutorials',
            'error': str(e)
        }), 500