from flask import Blueprint, request, jsonify, current_app
from app.models import Field, User, Crop
from app.routes.auth import jwt_required
from app.extensions import db
from datetime import datetime

bp = Blueprint('fields', __name__)

@bp.route('/create', methods=['POST'])
@jwt_required
def create_field():
    try:
        user_id = request.user_id
        current_app.logger.info(f"🌾 Creating field for user_id: {user_id}")
        
        current_app.logger.info(f"📊 Querying User table for user_id: {user_id}")
        user = User.query.get(user_id)
        current_app.logger.info(f"📊 User query result: {user.name if user else 'None'}")
        
        if not user:
            current_app.logger.warning(f"⚠️ User not found for user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        current_app.logger.info(f"📥 Received field data: {data}")
        
        required_fields = ['name', 'address', 'city', 'state', 'pin_code', 'soil_type', 'total_area']
        
        if not all(field in data for field in required_fields):
            current_app.logger.warning(f"⚠️ Missing required fields in data: {data}")
            return jsonify({'error': 'Missing required fields'}), 400

        current_app.logger.info("💽 Creating Field object")
        field = Field(
            user_id=user.id,
            name=data['name'],
            address=data['address'],
            city=data['city'],
            state=data['state'],
            pin_code=data['pin_code'],
            soil_type=data['soil_type'],
            total_area=data['total_area'],
            soil_ph=data.get('soil_ph'),
            irrigation_type=data.get('irrigation_type'),
            water_source=data.get('water_source'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        current_app.logger.info(f"💽 Field created: name={field.name}, user_id={field.user_id}, area={field.total_area}")

        current_app.logger.info("💽 Adding Field to database session")
        db.session.add(field)
        current_app.logger.info("💽 Field added to session")
        
        current_app.logger.info("💽 Committing database transaction")
        db.session.commit()
        current_app.logger.info(f"✅ Field committed to database with ID: {field.id}")

        response_data = {
            'message': 'Field created successfully',
            'field_id': field.id,
            'field': {
                'id': field.id,
                'name': field.name,
                'address': field.address,
                'city': field.city,
                'state': field.state,
                'pin_code': field.pin_code,
                'soil_type': field.soil_type,
                'total_area': field.total_area,
                'created_at': field.created_at.isoformat()
            }
        }
        current_app.logger.info(f"📤 Returning field creation response: {response_data}")
        return jsonify(response_data), 201

    except Exception as e:
        current_app.logger.error(f"❌ Error creating field: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
@jwt_required
def list_fields():
    try:
        user_id = request.user_id
        current_app.logger.info(f"📋 Listing fields for user_id: {user_id}")
        
        current_app.logger.info(f"📊 Querying Field table for user_id: {user_id}")
        fields = Field.query.filter_by(user_id=user_id).all()
        current_app.logger.info(f"📊 Found {len(fields)} fields for user")

        field_list = []
        for i, field in enumerate(fields):
            current_app.logger.info(f"📊 Processing field {i+1}: ID={field.id}, name={field.name}")
            current_app.logger.info(f"📊 Checking crops for field {field.id}")
            crop_count = len(field.crops)
            current_app.logger.info(f"📊 Field {field.id} has {crop_count} crops")
            
            field_data = {
                'id': field.id,
                'name': field.name,
                'address': field.address,
                'city': field.city,
                'state': field.state,
                'pin_code': field.pin_code,
                'soil_type': field.soil_type,
                'soil_ph': field.soil_ph,
                'total_area': field.total_area,
                'irrigation_type': field.irrigation_type,
                'water_source': field.water_source,
                'latitude': field.latitude,
                'longitude': field.longitude,
                'created_at': field.created_at.isoformat() if field.created_at else None,
                'updated_at': field.updated_at.isoformat() if field.updated_at else None,
                'crop_count': crop_count
            }
            field_list.append(field_data)

        current_app.logger.info(f"📤 Returning {len(field_list)} fields")
        return jsonify({'fields': field_list}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error listing fields: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:field_id>', methods=['GET'])
@jwt_required
def get_field(field_id):
    try:
        user_id = request.user_id
        current_app.logger.info(f"🌾 Getting field {field_id} for user_id: {user_id}")
        
        current_app.logger.info(f"📊 Querying Field table for field_id: {field_id}, user_id: {user_id}")
        field = Field.query.filter_by(id=field_id, user_id=user_id).first()
        current_app.logger.info(f"📊 Field query result: {field.name if field else 'None'}")
        
        if not field:
            current_app.logger.warning(f"⚠️ Field {field_id} not found or not accessible for user {user_id}")
            return jsonify({'error': 'Field not found'}), 404

        field_data = {
            'id': field.id,
            'name': field.name,
            'address': field.address,
            'city': field.city,
            'state': field.state,
            'pin_code': field.pin_code,
            'soil_type': field.soil_type,
            'soil_ph': field.soil_ph,
            'total_area': field.total_area,
            'irrigation_type': field.irrigation_type,
            'water_source': field.water_source,
            'latitude': field.latitude,
            'longitude': field.longitude,
            'created_at': field.created_at.isoformat() if field.created_at else None,
            'updated_at': field.updated_at.isoformat() if field.updated_at else None,
            'crops': []
        }

        # Add crop information
        current_app.logger.info(f"📊 Loading crops for field {field.id}")
        crops_count = len(field.crops)
        current_app.logger.info(f"📊 Found {crops_count} crops for field {field.id}")
        
        for i, crop in enumerate(field.crops):
            current_app.logger.info(f"📊 Processing crop {i+1}: ID={crop.id}, type={crop.crop_type}")
            crop_data = {
                'id': crop.id,
                'crop_type': crop.crop_type,
                'variety': crop.variety,
                'sowing_date': crop.sowing_date.isoformat() if crop.sowing_date else None,
                'area': crop.area,
                'growth_stage': crop.growth_stage,
                'subsidy_eligible': crop.subsidy_eligible
            }
            field_data['crops'].append(crop_data)

        current_app.logger.info(f"📤 Returning field data with {len(field_data['crops'])} crops")
        return jsonify({'field': field_data}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error getting field: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:field_id>/update', methods=['PUT'])
@jwt_required
def update_field(field_id):
    try:
        user_id = request.user_id
        current_app.logger.info(f"✏️ Updating field {field_id} for user_id: {user_id}")
        
        current_app.logger.info(f"📊 Querying Field table for field_id: {field_id}, user_id: {user_id}")
        field = Field.query.filter_by(id=field_id, user_id=user_id).first()
        current_app.logger.info(f"📊 Field query result: {field.name if field else 'None'}")
        
        if not field:
            current_app.logger.warning(f"⚠️ Field {field_id} not found or not accessible for user {user_id}")
            return jsonify({'error': 'Field not found'}), 404

        data = request.get_json()
        current_app.logger.info(f"📥 Received update data: {data}")
        
        # Update field attributes
        updateable_fields = [
            'name', 'address', 'city', 'state', 'pin_code', 'soil_type', 
            'soil_ph', 'total_area', 'irrigation_type', 'water_source', 
            'latitude', 'longitude'
        ]
        
        updated_fields = []
        for field_name in updateable_fields:
            if field_name in data:
                old_value = getattr(field, field_name)
                new_value = data[field_name]
                setattr(field, field_name, new_value)
                updated_fields.append(f"{field_name}: {old_value} -> {new_value}")
                current_app.logger.info(f"💽 Updated field.{field_name}: {old_value} -> {new_value}")

        field.updated_at = datetime.utcnow()
        current_app.logger.info(f"💽 Set updated_at to: {field.updated_at}")
        
        current_app.logger.info("💽 Committing field updates to database")
        db.session.commit()
        current_app.logger.info(f"✅ Field {field.id} updated successfully. Changed fields: {updated_fields}")

        response_data = {
            'message': 'Field updated successfully',
            'field': {
                'id': field.id,
                'name': field.name,
                'address': field.address,
                'updated_at': field.updated_at.isoformat()
            }
        }
        current_app.logger.info(f"📤 Returning update response: {response_data}")
        return jsonify(response_data), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error updating field: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:field_id>/delete', methods=['DELETE'])
@jwt_required
def delete_field(field_id):
    try:
        user_id = request.user_id
        current_app.logger.info(f"🗑️ Deleting field {field_id} for user_id: {user_id}")
        
        current_app.logger.info(f"📊 Querying Field table for field_id: {field_id}, user_id: {user_id}")
        field = Field.query.filter_by(id=field_id, user_id=user_id).first()
        current_app.logger.info(f"📊 Field query result: {field.name if field else 'None'}")
        
        if not field:
            current_app.logger.warning(f"⚠️ Field {field_id} not found or not accessible for user {user_id}")
            return jsonify({'error': 'Field not found'}), 404

        field_name = field.name
        current_app.logger.info(f"🗑️ Deleting field '{field_name}' (ID: {field.id})")
        db.session.delete(field)
        current_app.logger.info("💽 Field marked for deletion")
        
        current_app.logger.info("💽 Committing field deletion to database")
        db.session.commit()
        current_app.logger.info(f"✅ Field '{field_name}' (ID: {field_id}) deleted successfully")

        return jsonify({'message': 'Field deleted successfully'}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error deleting field: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500
