from flask import Blueprint, request, jsonify, current_app
from app.models import CropRecommendation, User, Field, Crop
from app.services.ai_service import get_crop_recommendations
from app.routes.auth import jwt_required
from app.extensions import db

bp = Blueprint('farmer', __name__)

@bp.route('/profile', methods=['GET'])
def get_profile():
    try:
        phone = request.args.get("phone")
        # user_id = request.user_id
        # current_app.logger.info(f"👤 Getting profile for user_id: {user_id}")
        
        current_app.logger.info(f"📊 Querying User table for phone: {phone}")
        user = User.query.filter_by(phone=phone).first()
        current_app.logger.info(f"📊 User query result: {user.name if user else 'None'}")
        
        if not user:
            current_app.logger.warning(f"⚠️ User not found for phone: {phone}")
            return jsonify({'error': 'User not found'}), 404

        current_app.logger.info(f"📊 Loading fields relationship for user {user.id}")
        fields_count = len(user.fields)
        current_app.logger.info(f"📊 User has {fields_count} fields")
        
        current_app.logger.info(f"📊 Calculating total crops for user {user.id}")
        total_crops = sum(len(field.crops) for field in user.fields)
        current_app.logger.info(f"📊 User has {total_crops} total crops across all fields")

        user_data = {
            'id': user.id,
            'name': user.name,
            'phone': user.phone,
            'gender': user.gender,
            'state': user.state,
            'city': user.city,
            'age': user.age,
            'email': user.email,
            'location': user.location,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'language': user.language,
            'total_fields': fields_count,
            'total_crops': total_crops
        }
        current_app.logger.info(f"📤 Returning user profile data")
        return jsonify({'user': user_data}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error getting user profile: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/dashboard', methods=['GET'])
@jwt_required
def get_dashboard():
    try:
        user_id = request.user_id
        current_app.logger.info(f"📊 Getting dashboard for user_id: {user_id}")
        
        current_app.logger.info(f"📊 Querying User table for user_id: {user_id}")
        user = User.query.get(user_id)
        current_app.logger.info(f"📊 User query result: {user.name if user else 'None'}")
        
        if not user:
            current_app.logger.warning(f"⚠️ User not found for user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        # Get summary statistics
        current_app.logger.info(f"📊 Loading fields relationship for user {user.id}")
        total_fields = len(user.fields)
        current_app.logger.info(f"📊 User has {total_fields} fields")
        
        current_app.logger.info(f"📊 Calculating total area for user {user.id}")
        total_area = sum(field.total_area for field in user.fields)
        current_app.logger.info(f"📊 Total area: {total_area}")
        
        current_app.logger.info(f"📊 Calculating total crops for user {user.id}")
        total_crops = sum(len(field.crops) for field in user.fields)
        current_app.logger.info(f"📊 Total crops: {total_crops}")
        
        # Recent activities
        current_app.logger.info("📊 Building recent crops list")
        recent_crops = []
        for field in user.fields:
            current_app.logger.info(f"📊 Processing field {field.id} ({field.name}) with {len(field.crops)} crops")
            for crop in field.crops:
                current_app.logger.info(f"📊 Processing crop {crop.id}: {crop.crop_type}")
                recent_crops.append({
                    'crop_id': crop.id,
                    'crop_type': crop.crop_type,
                    'field_name': field.name,
                    'growth_stage': crop.growth_stage,
                    'sowing_date': crop.sowing_date.isoformat() if crop.sowing_date else None,
                    'area': crop.area
                })
        
        # Sort by sowing date (most recent first)
        current_app.logger.info(f"📊 Sorting {len(recent_crops)} crops by sowing date")
        recent_crops.sort(key=lambda x: x['sowing_date'] or '1900-01-01', reverse=True)
        recent_crops = recent_crops[:5]  # Limit to 5 most recent
        current_app.logger.info(f"📊 Limited to {len(recent_crops)} most recent crops")

        active_crops_count = len([crop for field in user.fields for crop in field.crops if crop.growth_stage != 'Harvested'])
        current_app.logger.info(f"📊 Active crops count: {active_crops_count}")

        dashboard_data = {
            'user': {
                'name': user.name,
                'location': f"{user.city}, {user.state}"
            },
            'summary': {
                'total_fields': total_fields,
                'total_area': total_area,
                'total_crops': total_crops,
                'active_crops': active_crops_count
            },
            'recent_crops': recent_crops
        }
        current_app.logger.info(f"📤 Returning dashboard data")
        return jsonify({'dashboard': dashboard_data}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error getting dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/update_profile', methods=['PUT'])
@jwt_required
def update_profile():
    try:
        user_id = request.user_id  # Set by jwt_required decorator
        current_app.logger.info(f"✏️ Updating profile for user_id: {user_id}")
        
        user = User.query.get(user_id)
        current_app.logger.info(f"📊 User query result: {user.name if user else 'None'}")
        
        if not user:
            current_app.logger.warning(f"⚠️ User not found for user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        current_app.logger.info(f"📥 Received profile update data: {data}")

        # Update user profile - only allow certain fields to be updated
        updateable_fields = ['name', 'gender', 'state', 'city', 'age', 'email', 'location', 'language']
        
        updated_fields = []
        for key in updateable_fields:
            if key in data:
                old_value = getattr(user, key)
                new_value = data[key]
                setattr(user, key, new_value)
                updated_fields.append(f"{key}: {old_value} -> {new_value}")
                current_app.logger.info(f"💽 Updated user.{key}: {old_value} -> {new_value}")

        current_app.logger.info("💽 Committing profile updates to database")
        db.session.commit()
        current_app.logger.info(f"✅ Profile updated successfully. Changed fields: {updated_fields}")

        # Return updated user details
        user_data = {
            'id': user.id,
            'name': user.name,
            'phone': user.phone,
            'gender': user.gender,
            'state': user.state,
            'city': user.city,
            'age': user.age,
            'email': user.email,
            'language': user.language,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
        current_app.logger.info(f"📤 Returning updated profile data")
        return jsonify({'message': 'Profile updated successfully', 'user': user_data}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error updating profile: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500

@bp.route('/recommend', methods=['POST'])
@jwt_required
def recommend_crops():
    try:
        user_id = request.user_id
        current_app.logger.info(f"🌾 Getting crop recommendations for user_id: {user_id}")
        
        current_app.logger.info(f"📊 Querying User table for user_id: {user_id}")
        user = User.query.get(user_id)
        current_app.logger.info(f"📊 User query result: {user.name if user else 'None'}")
        
        if not user:
            current_app.logger.warning(f"⚠️ User not found for user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        current_app.logger.info(f"📥 Received recommendation request data: {data}")
        
        # Get crop recommendations using AI
        current_app.logger.info("🤖 Getting AI crop recommendations")
        recommendations = get_crop_recommendations(
            soil_type=data.get('soil_type'),
            climate_zone=data.get('climate_zone'),
            location=data.get('location'),
            season=data.get('season')
        )
        current_app.logger.info(f"🤖 AI recommendations received: {recommendations}")
        
        # Save recommendation to database
        current_app.logger.info("💽 Creating CropRecommendation object")
        crop_rec = CropRecommendation(
            user_id=user.id,
            soil_type=data.get('soil_type'),
            climate_zone=data.get('climate_zone'),
            recommended_crops=str(recommendations.get('crops', [])),
            season=data.get('season')
        )
        current_app.logger.info(f"💽 CropRecommendation created: user_id={crop_rec.user_id}, soil_type={crop_rec.soil_type}")
        
        current_app.logger.info("💽 Adding CropRecommendation to database session")
        db.session.add(crop_rec)
        current_app.logger.info("💽 CropRecommendation added to session")
        
        current_app.logger.info("💽 Committing database transaction")
        db.session.commit()
        current_app.logger.info(f"✅ CropRecommendation committed to database with ID: {crop_rec.id}")
        
        response_data = {
            'recommendation_id': crop_rec.id,
            'recommended_crops': recommendations.get('crops'),
            'farming_tips': recommendations.get('farming_tips'),
            'best_practices': recommendations.get('best_practices')
        }
        current_app.logger.info(f"📤 Returning recommendation response")
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Error getting crop recommendations: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500