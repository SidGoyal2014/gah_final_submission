from flask import Blueprint, request, jsonify, current_app
from app.models import CropRecommendation, User, Field, Crop, TransactionLog
from app.services.ai_service import get_crop_recommendations
from app.routes.auth import jwt_required
from app.extensions import db
import json
import os

bp = Blueprint('transactions', __name__)

def load_cibil_data():
    """Load CIBIL score data from mock file"""
    try:
        cibil_file_path = os.path.join(current_app.root_path, 'data', 'mock', 'cibil_score.json')
        with open(cibil_file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        current_app.logger.warning("CIBIL score file not found")
        return {"farmers": []}

def get_farmer_cibil_score(phone_number):
    """Get CIBIL score for a farmer by phone number"""
    cibil_data = load_cibil_data()
    for farmer in cibil_data.get('farmers', []):
        if farmer.get('phone_number') == phone_number:
            return farmer
    return None

############################################################
### CIBIL SCORE / FORMAL DEBIT CREDIT
############################################################

@bp.route('/cibil_check/<phone_number>', methods=['GET'])
@jwt_required
def check_cibil_score(phone_number):
    try:
        user_id = request.user_id
        current_app.logger.info(f"🏦 Checking CIBIL score for phone: {phone_number}, requested by user: {user_id}")
        
        # Get CIBIL information
        cibil_info = get_farmer_cibil_score(phone_number)
        
        if not cibil_info:
            current_app.logger.warning(f"⚠️ No CIBIL data found for phone: {phone_number}")
            return jsonify({'error': 'CIBIL data not found for this phone number'}), 404
        
        # Return comprehensive CIBIL information
        response_data = {
            'farmer_info': {
                'name': cibil_info.get('name'),
                'phone_number': cibil_info.get('phone_number'),
                'cibil_score': cibil_info.get('cibil_score'),
                'last_updated': cibil_info.get('last_updated')
            },
            'loan_summary': cibil_info.get('loan_summary', {}),
            'recent_credit_history': cibil_info.get('credit_history', [])[-3:],  # Last 3 entries
            'recent_debit_history': cibil_info.get('debit_history', [])[-3:]    # Last 3 entries
        }
        
        current_app.logger.info(f"📤 Returning CIBIL information for {cibil_info.get('name')}")
        return jsonify(response_data), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error checking CIBIL score: {str(e)}")
        return jsonify({'error': str(e)}), 500

############################################################
### MANUAL TRANSACTIONS
############################################################

@bp.route('/add_new', methods=['POST'])
@jwt_required
def add_new_transaction():
    try:
        user_id = request.user_id
        current_app.logger.info(f"💰 Adding new transaction for user_id: {user_id}")

        # Get the data from post request
        data = request.get_json()
        current_app.logger.info(f"📥 Received transaction data: {data}")

        # Mandatory Fields validation
        required_fields = ['phoneNumberB', 'transaction_type', 'transaction_amount']
        if not all(field in data for field in required_fields):
            current_app.logger.warning(f"⚠️ Missing required fields in data: {data}")
            return jsonify({'error': 'Missing required fields: phoneNumberB, transaction_type, transaction_amount'}), 400

        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            current_app.logger.warning(f"⚠️ User not found for user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        # Create transaction log entry
        current_app.logger.info("💽 Creating TransactionLog object")
        transaction = TransactionLog(
            userIdA=user_id,
            phoneNumberB=data['phoneNumberB'],
            transaction_type=data['transaction_type'],
            transaction_amount=float(data['transaction_amount']),
            details=data.get('details', '')
        )
        current_app.logger.info(f"💽 Transaction created: userIdA={transaction.userIdA}, amount={transaction.transaction_amount}")

        current_app.logger.info("💽 Adding Transaction to database session")
        db.session.add(transaction)
        
        current_app.logger.info("💽 Committing database transaction")
        db.session.commit()
        current_app.logger.info(f"✅ Transaction committed to database with ID: {transaction.id}")

        # Get CIBIL score for the recipient
        cibil_info = get_farmer_cibil_score(data['phoneNumberB'])
        
        response_data = {
            'message': 'Transaction recorded successfully',
            'transaction_id': transaction.id,
            'transaction': transaction.to_dict(),
            'recipient_cibil_info': cibil_info.get('cibil_score') if cibil_info else None
        }
        current_app.logger.info(f"📤 Returning transaction response")
        return jsonify(response_data), 201

    except Exception as e:
        current_app.logger.error(f"❌ Error adding transaction: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
@jwt_required
def get_transaction_history():
    try:
        user_id = request.user_id
        current_app.logger.info(f"📜 Getting transaction history for user_id: {user_id}")
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        current_app.logger.info(f"📊 Querying TransactionLog for user_id: {user_id}")
        transactions = TransactionLog.query.filter_by(userIdA=user_id)\
                                         .order_by(TransactionLog.timestamp.desc())\
                                         .paginate(page=page, per_page=per_page, error_out=False)
        
        current_app.logger.info(f"📊 Found {len(transactions.items)} transactions for user")
        
        transaction_list = []
        for transaction in transactions.items:
            current_app.logger.info(f"📊 Processing transaction {transaction.id}")
            transaction_data = transaction.to_dict()
            
            # Add CIBIL info for recipient
            cibil_info = get_farmer_cibil_score(transaction.phoneNumberB)
            if cibil_info:
                transaction_data['recipient_cibil_score'] = cibil_info.get('cibil_score')
                transaction_data['recipient_name'] = cibil_info.get('name')
            
            transaction_list.append(transaction_data)

        response_data = {
            'transactions': transaction_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': transactions.total,
                'pages': transactions.pages,
                'has_next': transactions.has_next,
                'has_prev': transactions.has_prev
            }
        }
        current_app.logger.info(f"📤 Returning {len(transaction_list)} transactions")
        return jsonify(response_data), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error getting transaction history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/analytics', methods=['GET'])
@jwt_required
def get_transaction_analytics():
    try:
        user_id = request.user_id
        current_app.logger.info(f"📊 Getting transaction analytics for user_id: {user_id}")
        
        # Get all transactions for the user
        transactions = TransactionLog.query.filter_by(userIdA=user_id).all()
        current_app.logger.info(f"📊 Found {len(transactions)} total transactions")
        
        # Calculate analytics
        total_transactions = len(transactions)
        total_amount = sum(t.transaction_amount for t in transactions)
        
        # Transaction type breakdown
        type_breakdown = {}
        for transaction in transactions:
            t_type = transaction.transaction_type
            type_breakdown[t_type] = type_breakdown.get(t_type, 0) + 1
        
        # Monthly breakdown (last 12 months)
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        monthly_data = defaultdict(float)
        for transaction in transactions:
            month_key = transaction.timestamp.strftime('%Y-%m')
            monthly_data[month_key] += transaction.transaction_amount
        
        analytics_data = {
            'summary': {
                'total_transactions': total_transactions,
                'total_amount': total_amount,
                'average_transaction': total_amount / total_transactions if total_transactions > 0 else 0
            },
            'type_breakdown': type_breakdown,
            'monthly_breakdown': dict(monthly_data)
        }
        
        current_app.logger.info(f"📤 Returning transaction analytics")
        return jsonify({'analytics': analytics_data}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Error getting transaction analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500