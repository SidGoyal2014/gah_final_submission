import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_restx import Resource
from app.models import User
from app.extensions import db
from app.api_namespaces import auth_ns
from app.api_models import auth_register_model, auth_login_model, auth_response_model, error_model, success_model
from werkzeug.security import generate_password_hash, check_password_hash

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

@auth_ns.route('/register')
class AuthRegister(Resource):
    @auth_ns.doc('register_user')
    @auth_ns.expect(auth_register_model)
    @auth_ns.response(201, 'User registered successfully', success_model)
    @auth_ns.response(400, 'Missing required fields', error_model)
    @auth_ns.response(409, 'Phone number already registered', error_model)
    def post(self):
        """Register a new user"""
        data = request.get_json()
        required_fields = ['name', 'phone', 'password', 'gender', 'state', 'city', 'age']
        if not all(field in data for field in required_fields):
            return {'error': 'Missing required fields'}, 400

        if User.query.filter_by(phone=data['phone']).first():
            return {'error': 'Phone number already registered'}, 409

        user = User(
            name=data['name'],
            phone=data['phone'],
            password_hash=generate_password_hash(data['password']),
            gender=data['gender'],
            state=data['state'],
            city=data['city'],
            age=data['age'],
            email=data.get('email')
        )
        db.session.add(user)
        db.session.commit()
        return {'message': 'User registered successfully', 'user_id': user.id}, 201

@auth_ns.route('/login')
class AuthLogin(Resource):
    @auth_ns.doc('login_user')
    @auth_ns.expect(auth_login_model)
    @auth_ns.response(200, 'Login successful', auth_response_model)
    @auth_ns.response(400, 'Phone and password required', error_model)
    @auth_ns.response(401, 'Invalid phone or password', error_model)
    def post(self):
        """User login"""
        data = request.get_json()
        phone = data.get('phone')
        password = data.get('password')
        if not phone or not password:
            return {'error': 'Phone and password required'}, 400

        user = User.query.filter_by(phone=phone).first()
        if not user or not check_password_hash(user.password_hash, password):
            return {'error': 'Invalid phone or password'}, 401

        token = generate_jwt(user.id)
        return {
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'phone': user.phone,
                'gender': user.gender,
                'state': user.state,
                'city': user.city,
                'age': user.age
            }
        }, 200

# Legacy blueprint routes for backwards compatibility
@bp.route('/register', methods=['POST'])
def register():
    auth_register = AuthRegister()
    return auth_register.post()

@bp.route('/login', methods=['POST'])
def login():
    auth_login = AuthLogin()
    return auth_login.post()

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
