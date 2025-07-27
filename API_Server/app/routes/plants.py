from flask import Blueprint, request, jsonify, current_app
from app.models import PlantAnalysis, User
from app.services.ai_service import analyze_plant_image, convert_image_to_blob
from app.routes.auth import jwt_required
from app.extensions import db

bp = Blueprint('plants', __name__)

@bp.route('/analyze', methods=['POST'])
@jwt_required
def analyze_plant():
    try:
        user_id = request.user_id  # Set by jwt_required decorator
        current_app.logger.info(f"🔍 [Vertex AI] Starting plant analysis for user_id: {user_id}")
        
        current_app.logger.info(f"📊 [Vertex AI] Querying User table for user_id: {user_id}")
        user = User.query.get(user_id)
        current_app.logger.info(f"📊 [Vertex AI] User query result: {user.name if user else 'None'}")
        
        if not user:
            current_app.logger.warning(f"⚠️ [Vertex AI] User not found for user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        # Get image from request
        if 'image' not in request.files:
            current_app.logger.warning("⚠️ [Vertex AI] No image provided in request")
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        current_app.logger.info(f"📸 [Vertex AI] Processing image file: {image_file.filename}")
    
        # Analyze with Vertex AI
        current_app.logger.info("🤖 [Vertex AI] Starting AI image analysis")
        analysis_result = analyze_plant_image(image_file)
        current_app.logger.info(f"🤖 [Vertex AI] AI analysis completed: {analysis_result}")
        
        # Convert to blob for database storage
        image_blob = convert_image_to_blob(image_file)
        current_app.logger.info(f"💾 [Vertex AI] Image converted to blob, size: {len(image_blob) if image_blob else 0} bytes")
        
        # Save analysis to database
        current_app.logger.info("💽 [Vertex AI] Creating PlantAnalysis object")
        analysis = PlantAnalysis(
            user_id=user.id,
            image_url=analysis_result.get('image_url', 'vertex_ai_analysis'),
            disease_detected=analysis_result.get('disease'),
            confidence_score=analysis_result.get('confidence'),
            recommendations=analysis_result.get('recommendations')
        )
        current_app.logger.info(f"💽 [Vertex AI] PlantAnalysis created: user_id={analysis.user_id}, disease={analysis.disease_detected}")
        
        current_app.logger.info("💽 [Vertex AI] Adding PlantAnalysis to database session")
        db.session.add(analysis)
        current_app.logger.info("💽 [Vertex AI] PlantAnalysis added to session")
        
        current_app.logger.info("💽 [Vertex AI] Committing database transaction")
        db.session.commit()
        current_app.logger.info(f"✅ [Vertex AI] PlantAnalysis committed to database with ID: {analysis.id}")
        
        response_data = {
            'analysis_id': analysis.id,
            'disease': analysis_result.get('disease'),
            'confidence': analysis_result.get('confidence'),
            'recommendations': analysis_result.get('recommendations'),
            'prevention_tips': analysis_result.get('prevention_tips'),
            'severity': analysis_result.get('severity'),
            'affected_parts': analysis_result.get('affected_parts'),
            'ai_source': 'vertex_ai'
        }
        current_app.logger.info(f"📤 [Vertex AI] Returning response: {response_data}")
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ [Vertex AI] Error during plant analysis: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 [Vertex AI] Database session rolled back")
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
@jwt_required
def get_analysis_history():
    try:
        user_id = request.user_id  # Set by jwt_required decorator
        current_app.logger.info(f"📜 [Vertex AI] Getting analysis history for user_id: {user_id}")
        
        current_app.logger.info(f"📊 [Vertex AI] Querying User table for user_id: {user_id}")
        user = User.query.get(user_id)
        current_app.logger.info(f"📊 [Vertex AI] User query result: {user.name if user else 'None'}")
        
        if not user:
            current_app.logger.warning(f"⚠️ [Vertex AI] User not found for user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's analysis history
        current_app.logger.info(f"📊 [Vertex AI] Querying PlantAnalysis for user_id: {user.id}")
        analyses = PlantAnalysis.query.filter_by(user_id=user.id).order_by(PlantAnalysis.created_at.desc()).all()
        current_app.logger.info(f"📊 [Vertex AI] Found {len(analyses)} plant analyses for user")
        
        history = []
        for i, analysis in enumerate(analyses):
            current_app.logger.info(f"📊 [Vertex AI] Processing analysis {i+1}: ID={analysis.id}, disease={analysis.disease_detected}")
            history.append({
                'id': analysis.id,
                'disease_detected': analysis.disease_detected,
                'confidence_score': analysis.confidence_score,
                'recommendations': analysis.recommendations,
                'created_at': analysis.created_at.isoformat(),
                'ai_source': 'vertex_ai'
            })
        
        current_app.logger.info(f"📤 [Vertex AI] Returning {len(history)} analysis records")
        return jsonify({'history': history}), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ [Vertex AI] Error getting analysis history: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
        current_app.logger.info(f"📤 Returning {len(history)} analysis records")
        return jsonify({'history': history}), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Error getting analysis history: {str(e)}")
        return jsonify({'error': str(e)}), 500
