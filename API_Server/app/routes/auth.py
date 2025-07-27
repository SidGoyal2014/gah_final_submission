import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from app.models import User
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys

bp = Blueprint('auth', __name__)

def generate_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def decode_jwt(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    current_app.logger.info(f"🔐 Received registration data: {data}")
    sys.stdout.flush()  # Force flush stdout
    
    # Debug database connection information
    current_app.logger.info(f"💾 Database URI: {current_app.config.get('SQLALCHEMY_DATABASE_URI')}")
    current_app.logger.info(f"💾 Database engine: {db.engine}")
    current_app.logger.info(f"💾 Database connection info: {db.engine.url}")
    
    # Test database connection
    try:
        with db.engine.connect() as conn:
            current_app.logger.info("✅ Database connection successful")
    except Exception as e:
        current_app.logger.error(f"❌ Database connection failed: {str(e)}")
        return jsonify({'error': 'Database connection failed'}), 500
    
    required_fields = ['name', 'phone', 'password', 'gender', 'state', 'city', 'age']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if phone already exists
    existing_user = User.query.filter_by(phone=data['phone']).first()
    current_app.logger.info(f"📊 Existing user check for phone {data['phone']}: {existing_user.name if existing_user else 'None'}")
    
    if existing_user:
        return jsonify({'error': 'Phone number already registered'}), 409

    # Generate password hash and debug
    password_hash = generate_password_hash(data['password'])
    current_app.logger.info(f"🔐 Generated password hash length: {len(password_hash)}")
    current_app.logger.info(f"🔐 Password hash: {password_hash[:50]}...")  # Show first 50 chars for debugging
    
    try:
        current_app.logger.info("💽 Creating User object")
        user = User(
            name=data['name'],
            phone=data['phone'],
            password_hash=password_hash,
            gender=data['gender'],
            state=data['state'],
            city=data['city'],
            age=data['age'],
            language=data.get('language', 'english')
        )
        current_app.logger.info(f"💽 User object created: {user.name}, {user.phone}")
        
        current_app.logger.info("💽 Adding User to database session")
        db.session.add(user)
        current_app.logger.info("💽 User added to session")
        
        current_app.logger.info("💽 Committing user registration to database")
        db.session.commit()
        current_app.logger.info(f"✅ User committed to database with ID: {user.id}")
        
        return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201
        
    except Exception as e:
        current_app.logger.error(f"❌ Error during user registration: {str(e)}")
        db.session.rollback()
        current_app.logger.info("🔄 Database session rolled back")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    current_app.logger.info(f"🔐 Login attempt for phone: {data.get('phone', 'Not provided')}")
    
    phone = data.get('phone')
    password = data.get('password')
    if not phone or not password:
        return jsonify({'error': 'Phone and password required'}), 400

    current_app.logger.info(f"📊 Querying User table for phone: {phone}")
    user = User.query.filter_by(phone=phone).first()
    
    if not user:
        current_app.logger.warning(f"⚠️ No user found with phone: {phone}")
        return jsonify({'error': 'Invalid phone or password'}), 401
    
    current_app.logger.info(f"🔐 Checking password for user: {user.name}")
    password_valid = check_password_hash(user.password_hash, password)
    
    if not password_valid:
        current_app.logger.warning(f"⚠️ Invalid password for user: {user.name}")
        return jsonify({'error': 'Invalid phone or password'}), 401

    current_app.logger.info(f"🔐 Generating JWT token for user: {user.name} (ID: {user.id})")
    token = generate_jwt(user.id)
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'phone': user.phone,
            'gender': user.gender,
            'state': user.state,
            'city': user.city,
            'age': user.age,
            'language': user.language
        }
    }), 200

def jwt_required(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        token = auth_header.replace('Bearer ', '')
        payload = decode_jwt(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        request.user_id = payload['user_id']
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper