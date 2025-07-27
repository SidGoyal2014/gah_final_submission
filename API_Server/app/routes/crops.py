from flask import Blueprint, request, jsonify, current_app
from app.models import CropRecommendation, User, Crop, Field
from app.services.ai_service import get_crop_recommendations
from app.routes.auth import jwt_required
from app.extensions import db
from datetime import datetime, date

bp = Blueprint('crops', __name__)

@bp.route('/create', methods=['POST'])
@jwt_required
def create_crop():
    try:
        user_id = request.user_id
        current_app.logger.info(f"🌱 Creating crop for user_id: {user_id}")
        
        current_app.logger.info(f"📊 Querying User table for user_id: {user_id}")
        user = User.query.get(user_id)
        current_app.logger.info(f"📊 User query result: {user.name if user else 'None'}")
        
        if not user:
            current_app.logger.warning(f"⚠️ User not found for user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        current_app.logger.info(f"📥 Received crop data: {data}")
        
        required_fields = ['field_id', 'crop_type', 'sowing_date', 'area']
        
        if not all(field in data for field in required_fields):
            current_app.logger.warning(f"⚠️ Missing required fields in data: {data}")
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if field belongs to user
        current_app.logger.info(f"📊 Querying Field table for field_id: {data['field_id']}, user_id: {user_id}")
        field = Field.query.filter_by(id=data['field_id'], user_id=user_id).first()
        current_app.logger.info(f"📊 Field query result: {field.name if field else 'None'}")
        
        if not field:
            current_app.logger.warning(f"⚠️ Field {data['field_id']} not found or not accessible for user {user_id}")
            return jsonify({'error': 'Field not found or not accessible'}), 404

        # Parse sowing_date
        try:
            sowing_date = datetime.strptime(data['sowing_date'], '%Y-%m-%d').date()
            current_app.logger.info(f"📅 Parsed sowing_date: {sowing_date}")
        except ValueError:
            current_app.logger.warning(f"⚠️ Invalid sowing_date format: {data['sowing_date']}")
            return jsonify({'error': 'Invalid sowing_date format. Use YYYY-MM-DD'}), 400

        # Parse expected_harvest_date if provided
        expected_harvest_date = None
        if data.get('expected_harvest_date'):
            try:
                expected_harvest_date = datetime.strptime(data['expected_harvest_date'], '%Y-%m-%d').date()
                current_app.logger.info(f"📅 Parsed expected_harvest_date: {expected_harvest_date}")
            except ValueError:
                current_app.logger.warning(f"⚠️ Invalid expected_harvest_date format: {data['expected_harvest_date']}")
                return jsonify({'error': 'Invalid expected_harvest_date format. Use YYYY-MM-DD'}), 400

        current_app.logger.info("💽 Creating Crop object")
        crop = Crop(
            field_id=data['field_id'],
            crop_type=data['crop_type'],
            variety=data.get('variety'),
            sowing_date=sowing_date,
            expected_harvest_date=expected_harvest_date,
            area=data['area'],
            subsidy_eligible=data.get('subsidy_eligible', False),
            seed_quantity=data.get('seed_quantity'),
            seed_cost=data.get('seed_cost'),
            fertilizer_used=data.get('fertilizer_used'),
            pesticide_used=data.get('pesticide_used'),
            irrigation_frequency=data.get('irrigation_frequency'),
            growth_stage=data.get('growth_stage', 'Seedling'),
            expected_yield=data.get('expected_yield'),
            notes=data.get('notes')
        )
        current_app.logger.info(f"💽 Crop created: field_id={crop.field_id}, type={crop.crop_type}, area={crop.area}")

        current_app.logger.info("💽 Adding Crop to database session")
        db.session.add(crop)
        current_app.logger.info("💽 Crop added to session")
        
        current_app.logger.info("💽 Committing database transaction")
        db.session.commit()
        current_app.logger.info(f"✅ Crop committed to database with ID: {crop.id}")

        response_data = {
            'message': 'Crop created successfully',
            'crop_id': crop.id,
            'crop': {
                'id': crop.id,
                'field_id': crop.field_id,
                'crop_type': crop.crop_type,
                'variety': crop.variety,
                'sowing_date': crop.sowing_date.isoformat() if crop.sowing_date else None,
                'area': crop.area,
                'growth_stage': crop.growth_stage,
                'subsidy_eligible': crop.subsidy_eligible,
                'created_at': crop.created_at.isoformat()
            }
        }
        current_app.logger.info(f"📤 Returning crop creation response")
        return jsonify(response_data), 201

    except Exception as e:
        current_app.logger.error(f"❌ Error creating crop: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
@jwt_required
def list_crops():
    try:
        user_id = request.user_id
        field_id = request.args.get('field_id', type=int)
        current_app.logger.info(f"📋 Listing crops for user_id: {user_id}, field_id: {field_id}")
        
        if field_id:
            # Check if field belongs to user
            current_app.logger.info(f"📊 Querying Field table for field_id: {field_id}, user_id: {user_id}")
            field = Field.query.filter_by(id=field_id, user_id=user_id).first()
            current_app.logger.info(f"📊 Field query result: {field.name if field else 'None'}")
            
            if not field:
                current_app.logger.warning(f"⚠️ Field {field_id} not found or not accessible for user {user_id}")
                return jsonify({'error': 'Field not found or not accessible'}), 404
                
            current_app.logger.info(f"📊 Querying Crop table for field_id: {field_id}")
            crops = Crop.query.filter_by(field_id=field_id).all()
            current_app.logger.info(f"📊 Found {len(crops)} crops for field {field_id}")
        else:
            # Get all crops for all user's fields
            current_app.logger.info(f"📊 Querying Field table for user_id: {user_id}")
            user_fields = Field.query.filter_by(user_id=user_id).all()
            current_app.logger.info(f"📊 Found {len(user_fields)} fields for user")
            
            field_ids = [field.id for field in user_fields]
            current_app.logger.info(f"📊 Field IDs: {field_ids}")
            
            current_app.logger.info(f"📊 Querying Crop table for field_ids: {field_ids}")
            crops = Crop.query.filter(Crop.field_id.in_(field_ids)).all()
            current_app.logger.info(f"📊 Found {len(crops)} total crops for user")

        crop_list = []
        for i, crop in enumerate(crops):
            current_app.logger.info(f"📊 Processing crop {i+1}: ID={crop.id}, type={crop.crop_type}")
            current_app.logger.info(f"📊 Loading field relationship for crop {crop.id}")
            
            crop_data = {
                'id': crop.id,
                'field_id': crop.field_id,
                'field_name': crop.field.name,
                'crop_type': crop.crop_type,
                'variety': crop.variety,
                'sowing_date': crop.sowing_date.isoformat() if crop.sowing_date else None,
                'expected_harvest_date': crop.expected_harvest_date.isoformat() if crop.expected_harvest_date else None,
                'area': crop.area,
                'subsidy_eligible': crop.subsidy_eligible,
                'seed_quantity': crop.seed_quantity,
                'seed_cost': crop.seed_cost,
                'fertilizer_used': crop.fertilizer_used,
                'pesticide_used': crop.pesticide_used,
                'irrigation_frequency': crop.irrigation_frequency,
                'growth_stage': crop.growth_stage,
                'expected_yield': crop.expected_yield,
                'actual_yield': crop.actual_yield,
                'harvest_date': crop.harvest_date.isoformat() if crop.harvest_date else None,
                'market_price': crop.market_price,
                'notes': crop.notes,
                'created_at': crop.created_at.isoformat() if crop.created_at else None,
                'updated_at': crop.updated_at.isoformat() if crop.updated_at else None
            }
            crop_list.append(crop_data)

        current_app.logger.info(f"📤 Returning {len(crop_list)} crops")
        return jsonify({'crops': crop_list}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error listing crops: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:crop_id>', methods=['GET'])
@jwt_required
def get_crop(crop_id):
    try:
        user_id = request.user_id
        current_app.logger.info(f"📋 Getting crop details for crop_id: {crop_id}, user_id: {user_id}")
        
        crop = Crop.query.join(Field).filter(
            Crop.id == crop_id,
            Field.user_id == user_id
        ).first()
        
        if not crop:
            current_app.logger.warning(f"⚠️ Crop {crop_id} not found or not accessible for user {user_id}")
            return jsonify({'error': 'Crop not found or not accessible'}), 404

        crop_data = {
            'id': crop.id,
            'field_id': crop.field_id,
            'field_name': crop.field.name,
            'crop_type': crop.crop_type,
            'variety': crop.variety,
            'sowing_date': crop.sowing_date.isoformat() if crop.sowing_date else None,
            'expected_harvest_date': crop.expected_harvest_date.isoformat() if crop.expected_harvest_date else None,
            'area': crop.area,
            'subsidy_eligible': crop.subsidy_eligible,
            'seed_quantity': crop.seed_quantity,
            'seed_cost': crop.seed_cost,
            'fertilizer_used': crop.fertilizer_used,
            'pesticide_used': crop.pesticide_used,
            'irrigation_frequency': crop.irrigation_frequency,
            'growth_stage': crop.growth_stage,
            'expected_yield': crop.expected_yield,
            'actual_yield': crop.actual_yield,
            'harvest_date': crop.harvest_date.isoformat() if crop.harvest_date else None,
            'market_price': crop.market_price,
            'notes': crop.notes,
            'created_at': crop.created_at.isoformat() if crop.created_at else None,
            'updated_at': crop.updated_at.isoformat() if crop.updated_at else None
        }

        current_app.logger.info(f"📤 Returning crop details")
        return jsonify({'crop': crop_data}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error getting crop details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:crop_id>/update', methods=['PUT'])
@jwt_required
def update_crop(crop_id):
    try:
        user_id = request.user_id
        current_app.logger.info(f"✏️ Updating crop_id: {crop_id} for user_id: {user_id}")
        
        crop = Crop.query.join(Field).filter(
            Crop.id == crop_id,
            Field.user_id == user_id
        ).first()
        
        if not crop:
            current_app.logger.warning(f"⚠️ Crop {crop_id} not found or not accessible for user {user_id}")
            return jsonify({'error': 'Crop not found or not accessible'}), 404

        data = request.get_json()
        current_app.logger.info(f"📥 Received update data: {data}")
        
        # Update crop attributes
        updateable_fields = [
            'crop_type', 'variety', 'area', 'subsidy_eligible', 'seed_quantity',
            'seed_cost', 'fertilizer_used', 'pesticide_used', 'irrigation_frequency',
            'growth_stage', 'expected_yield', 'actual_yield', 'market_price', 'notes'
        ]
        
        for field_name in updateable_fields:
            if field_name in data:
                current_app.logger.info(f"✏️ Updating {field_name} to {data[field_name]}")
                setattr(crop, field_name, data[field_name])

        # Handle date fields separately
        if 'sowing_date' in data:
            try:
                crop.sowing_date = datetime.strptime(data['sowing_date'], '%Y-%m-%d').date()
                current_app.logger.info(f"📅 Updated sowing_date: {crop.sowing_date}")
            except ValueError:
                current_app.logger.warning(f"⚠️ Invalid sowing_date format: {data['sowing_date']}")
                return jsonify({'error': 'Invalid sowing_date format. Use YYYY-MM-DD'}), 400

        if 'expected_harvest_date' in data:
            try:
                crop.expected_harvest_date = datetime.strptime(data['expected_harvest_date'], '%Y-%m-%d').date()
                current_app.logger.info(f"📅 Updated expected_harvest_date: {crop.expected_harvest_date}")
            except ValueError:
                current_app.logger.warning(f"⚠️ Invalid expected_harvest_date format: {data['expected_harvest_date']}")
                return jsonify({'error': 'Invalid expected_harvest_date format. Use YYYY-MM-DD'}), 400

        if 'harvest_date' in data:
            try:
                crop.harvest_date = datetime.strptime(data['harvest_date'], '%Y-%m-%d').date()
                current_app.logger.info(f"📅 Updated harvest_date: {crop.harvest_date}")
            except ValueError:
                current_app.logger.warning(f"⚠️ Invalid harvest_date format: {data['harvest_date']}")
                return jsonify({'error': 'Invalid harvest_date format. Use YYYY-MM-DD'}), 400

        crop.updated_at = datetime.utcnow()
        current_app.logger.info(f"🕒 Updated crop timestamp: {crop.updated_at}")

        current_app.logger.info("💽 Committing database transaction")
        db.session.commit()
        current_app.logger.info(f"✅ Crop updated in database with ID: {crop.id}")

        return jsonify({
            'message': 'Crop updated successfully',
            'crop': {
                'id': crop.id,
                'crop_type': crop.crop_type,
                'growth_stage': crop.growth_stage,
                'updated_at': crop.updated_at.isoformat()
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error updating crop: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:crop_id>/delete', methods=['DELETE'])
@jwt_required
def delete_crop(crop_id):
    try:
        user_id = request.user_id
        current_app.logger.info(f"🗑️ Deleting crop_id: {crop_id} for user_id: {user_id}")
        
        crop = Crop.query.join(Field).filter(
            Crop.id == crop_id,
            Field.user_id == user_id
        ).first()
        
        if not crop:
            current_app.logger.warning(f"⚠️ Crop {crop_id} not found or not accessible for user {user_id}")
            return jsonify({'error': 'Crop not found or not accessible'}), 404

        db.session.delete(crop)
        current_app.logger.info(f"💽 Crop {crop_id} deleted from session")
        db.session.commit()
        current_app.logger.info(f"✅ Crop {crop_id} deleted from database")

        return jsonify({'message': 'Crop deleted successfully'}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error deleting crop: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500

@bp.route('/harvest/<int:crop_id>', methods=['POST'])
@jwt_required
def harvest_crop(crop_id):
    try:
        user_id = request.user_id
        current_app.logger.info(f"🌾 Recording harvest for crop_id: {crop_id}, user_id: {user_id}")
        
        crop = Crop.query.join(Field).filter(
            Crop.id == crop_id,
            Field.user_id == user_id
        ).first()
        
        if not crop:
            current_app.logger.warning(f"⚠️ Crop {crop_id} not found or not accessible for user {user_id}")
            return jsonify({'error': 'Crop not found or not accessible'}), 404

        data = request.get_json()
        current_app.logger.info(f"📥 Received harvest data: {data}")
        
        # Update harvest information
        if 'harvest_date' in data:
            try:
                crop.harvest_date = datetime.strptime(data['harvest_date'], '%Y-%m-%d').date()
                current_app.logger.info(f"📅 Updated harvest_date: {crop.harvest_date}")
            except ValueError:
                crop.harvest_date = date.today()
                current_app.logger.info(f"📅 Defaulting harvest_date to today: {crop.harvest_date}")
        else:
            crop.harvest_date = date.today()
            current_app.logger.info(f"📅 Defaulting harvest_date to today: {crop.harvest_date}")

        if 'actual_yield' in data:
            crop.actual_yield = data['actual_yield']
            current_app.logger.info(f"📈 Updated actual_yield: {crop.actual_yield}")
        
        if 'market_price' in data:
            crop.market_price = data['market_price']
            current_app.logger.info(f"💰 Updated market_price: {crop.market_price}")

        crop.growth_stage = 'Harvested'
        crop.updated_at = datetime.utcnow()
        current_app.logger.info(f"🕒 Updated crop timestamp: {crop.updated_at}")

        current_app.logger.info("💽 Committing database transaction")
        db.session.commit()
        current_app.logger.info(f"✅ Crop harvest recorded in database with ID: {crop.id}")

        return jsonify({
            'message': 'Crop harvest recorded successfully',
            'crop': {
                'id': crop.id,
                'crop_type': crop.crop_type,
                'harvest_date': crop.harvest_date.isoformat(),
                'actual_yield': crop.actual_yield,
                'market_price': crop.market_price
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error recording crop harvest: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500

@bp.route('/test', methods=['GET'])
@jwt_required
def test_route():
    return jsonify({'message': 'Crops route is working!'}), 200

@bp.route('/recommend', methods=['POST'])
@jwt_required  
def recommend_crops():
    try:
        user_id = request.user_id
        current_app.logger.info(f"🤖 Getting crop recommendations for user_id: {user_id}")
        
        user = User.query.get(user_id)
        if not user:
            current_app.logger.warning(f"⚠️ User not found for user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        current_app.logger.info(f"📥 Received recommendation data: {data}")
        
        # Get crop recommendations using AI
        recommendations = get_crop_recommendations(
            soil_type=data.get('soil_type'),
            climate_zone=data.get('climate_zone'),
            location=data.get('location'),
            season=data.get('season')
        )
        current_app.logger.info(f"📊 AI recommendations: {recommendations}")
        
        # Save recommendation to database
        crop_rec = CropRecommendation(
            user_id=user.id,
            soil_type=data.get('soil_type'),
            climate_zone=data.get('climate_zone'),
            recommended_crops=str(recommendations.get('crops', [])),
            season=data.get('season')
        )
        
        db.session.add(crop_rec)
        current_app.logger.info("💽 Recommendation added to session")
        db.session.commit()
        current_app.logger.info(f"✅ Recommendation committed to database with ID: {crop_rec.id}")
        
        return jsonify({
            'recommendation_id': crop_rec.id,
            'recommended_crops': recommendations.get('crops'),
            'farming_tips': recommendations.get('farming_tips'),
            'best_practices': recommendations.get('best_practices')
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Error getting crop recommendations: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500

@bp.route('/suitable', methods=['GET'])
def get_suitable_crops():
    try:
        location = request.args.get('location')
        season = request.args.get('season', 'current')
        
        current_app.logger.info(f"🌾 Getting suitable crops for location: {location}, season: {season}")
        suitable_crops = get_crop_recommendations(
            location=location,
            season=season,
            quick_lookup=True
        )
        
        current_app.logger.info(f"📊 Suitable crops: {suitable_crops.get('crops', [])}")
        return jsonify({
            'location': location,
            'season': season,
            'suitable_crops': suitable_crops.get('crops', [])
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Error getting suitable crops: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/analytics', methods=['GET'])
@jwt_required
def get_crop_analytics():
    try:
        user_id = request.user_id
        current_app.logger.info(f"📊 Getting crop analytics for user_id: {user_id}")
        
        # Get all user's fields and crops
        current_app.logger.info(f"📊 Querying Field table for user_id: {user_id}")
        user_fields = Field.query.filter_by(user_id=user_id).all()
        current_app.logger.info(f"📊 Found {len(user_fields)} fields for user")
        
        field_ids = [field.id for field in user_fields]
        current_app.logger.info(f"📊 Field IDs: {field_ids}")
        
        current_app.logger.info(f"📊 Querying Crop table for field_ids: {field_ids}")
        crops = Crop.query.filter(Crop.field_id.in_(field_ids)).all()
        current_app.logger.info(f"📊 Found {len(crops)} total crops for analytics")
        
        # Calculate analytics
        total_crops = len(crops)
        total_area = sum(crop.area for crop in crops)
        harvested_crops = [crop for crop in crops if crop.harvest_date is not None]
        active_crops = [crop for crop in crops if crop.growth_stage not in ['Harvested', 'Failed']]
        
        current_app.logger.info(f"📊 Analytics summary: total_crops={total_crops}, total_area={total_area}")
        current_app.logger.info(f"📊 Analytics summary: harvested={len(harvested_crops)}, active={len(active_crops)}")
        
        # Crop type distribution
        crop_types = {}
        for crop in crops:
            crop_types[crop.crop_type] = crop_types.get(crop.crop_type, 0) + 1
        current_app.logger.info(f"📊 Crop type distribution: {crop_types}")
        
        # Growth stage distribution
        growth_stages = {}
        for crop in active_crops:
            stage = crop.growth_stage or 'Unknown'
            growth_stages[stage] = growth_stages.get(stage, 0) + 1
        current_app.logger.info(f"📊 Growth stage distribution: {growth_stages}")
        
        # Yield analysis
        total_expected_yield = sum(crop.expected_yield or 0 for crop in crops)
        total_actual_yield = sum(crop.actual_yield or 0 for crop in harvested_crops)
        current_app.logger.info(f"📊 Yield analysis: expected={total_expected_yield}, actual={total_actual_yield}")
        
        # Financial analysis
        total_seed_cost = sum(crop.seed_cost or 0 for crop in crops)
        total_revenue = sum((crop.actual_yield or 0) * (crop.market_price or 0) for crop in harvested_crops)
        current_app.logger.info(f"📊 Financial analysis: seed_cost={total_seed_cost}, revenue={total_revenue}")
        
        analytics_data = {
            'summary': {
                'total_fields': len(user_fields),
                'total_crops': total_crops,
                'total_area': total_area,
                'active_crops': len(active_crops),
                'harvested_crops': len(harvested_crops)
            },
            'distribution': {
                'crop_types': crop_types,
                'growth_stages': growth_stages
            },
            'yield_analysis': {
                'total_expected_yield': total_expected_yield,
                'total_actual_yield': total_actual_yield,
                'yield_efficiency': (total_actual_yield / total_expected_yield * 100) if total_expected_yield > 0 else 0
            },
            'financial': {
                'total_seed_cost': total_seed_cost,
                'total_revenue': total_revenue,
                'net_profit': total_revenue - total_seed_cost,
                'roi_percentage': ((total_revenue - total_seed_cost) / total_seed_cost * 100) if total_seed_cost > 0 else 0
            }
        }
        
        current_app.logger.info(f"📤 Returning analytics data")
        return jsonify({'analytics': analytics_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Error getting crop analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/seasonal-report', methods=['GET'])
@jwt_required  
def get_seasonal_report():
    try:
        user_id = request.user_id
        season = request.args.get('season', 'current')
        year = request.args.get('year', datetime.now().year, type=int)
        
        current_app.logger.info(f"📅 Generating seasonal report for user_id: {user_id}, season: {season}, year: {year}")
        
        # Get all user's fields and crops for the specified period
        user_fields = Field.query.filter_by(user_id=user_id).all()
        field_ids = [field.id for field in user_fields]
        
        # Filter crops by year
        crops = Crop.query.filter(
            Crop.field_id.in_(field_ids),
            db.extract('year', Crop.sowing_date) == year
        ).all()
        
        current_app.logger.info(f"📊 Found {len(crops)} crops for seasonal report")
        
        # Season-specific filtering (basic implementation)
        if season != 'current':
            # You can implement more sophisticated season filtering based on your region's cropping calendar
            season_months = {
                'kharif': [6, 7, 8, 9],  # June to September
                'rabi': [10, 11, 12, 1, 2, 3],  # October to March
                'zaid': [4, 5]  # April to May
            }
            
            if season.lower() in season_months:
                months = season_months[season.lower()]
                crops = [crop for crop in crops if crop.sowing_date and crop.sowing_date.month in months]
                current_app.logger.info(f"📊 Filtered crops by season ({season}): {len(crops)} crops")
        
        # Generate report
        seasonal_data = {
            'season': season,
            'year': year,
            'total_crops': len(crops),
            'total_area': sum(crop.area for crop in crops),
            'crop_details': []
        }
        
        for crop in crops:
            crop_detail = {
                'crop_type': crop.crop_type,
                'variety': crop.variety,
                'field_name': crop.field.name,
                'area': crop.area,
                'sowing_date': crop.sowing_date.isoformat() if crop.sowing_date else None,
                'growth_stage': crop.growth_stage,
                'expected_yield': crop.expected_yield,
                'actual_yield': crop.actual_yield,
                'status': 'Harvested' if crop.harvest_date else 'Growing'
            }
            seasonal_data['crop_details'].append(crop_detail)
        
        current_app.logger.info(f"📤 Returning seasonal report data")
        return jsonify({'seasonal_report': seasonal_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Error generating seasonal report: {str(e)}")
        return jsonify({'error': str(e)}), 500
