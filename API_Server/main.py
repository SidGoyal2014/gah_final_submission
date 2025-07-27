from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from app.extensions import db
from app.swagger_docs import setup_docs_route
from sqlalchemy.exc import OperationalError, DisconnectionError
import time

# Load environment variables
load_dotenv()

def get_database_uri():
    """Construct database URI from environment variables with Cloud SQL support"""
    db_type = os.getenv('DB_TYPE', 'mysql')

    print('DB_TYPE : ', os.getenv('DB_TYPE'))
    if db_type.lower() == 'sqlite':
        return os.getenv('DATABASE_URL', 'sqlite:///agri_assist.db')
    
    # Check if running on Cloud Run (has Cloud SQL socket)
    if os.path.exists('/cloudsql'):
        # Cloud Run with Cloud SQL - use Unix socket
        instance_connection_name = os.getenv('CLOUD_SQL_CONNECTION_NAME')
        if instance_connection_name:
            db_name = os.getenv('DB_NAME_2', 'agri_assist')
            db_username = os.getenv('DB_USERNAME_2', 'agri_user')
            db_password = os.getenv('DB_PASSWORD_2', 'password')
            
            if db_type.lower() == 'postgresql':
                return f'postgresql+psycopg2://{db_username}:{db_password}@/{db_name}?host=/cloudsql/{instance_connection_name}'
            elif db_type.lower() == 'mysql':
                return f'mysql+pymysql://{db_username}:{db_password}@/{db_name}?unix_socket=/cloudsql/{instance_connection_name}'
    
    # For PostgreSQL/MySQL with TCP connection
    # db_host = os.getenv('DB_HOST_2', 'localhost')
    # db_port = os.getenv('DB_PORT_2', '5432' if db_type.lower() == 'postgresql' else '3306')
    # db_name = os.getenv('DB_NAME_2', 'agri_assist')
    # db_username = os.getenv('DB_USERNAME_2', 'root')
    # db_password = os.getenv('DB_PASSWORD_2', 'password')

    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432' if db_type.lower() == 'postgresql' else '3306')
    db_name = os.getenv('DB_NAME', 'agri_assist')
    db_username = os.getenv('DB_USERNAME', 'root')
    db_password = os.getenv('DB_PASSWORD', 'password')
    
    if db_type.lower() == 'postgresql':
        return f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    elif db_type.lower() == 'mysql':
        return f'mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    else:
        # Fallback to SQLite
        return os.getenv('DATABASE_URL', 'sqlite:///agri_assist.db')

# Initialize Flask app
app = Flask(__name__)

# Configuration with Cloud SQL optimizations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,  # 5 minutes
    'pool_timeout': 20,
    'pool_size': 5,
    'max_overflow': 0,
    'connect_args': {
        'charset': 'utf8mb4',
        'connect_timeout': 60,
        'read_timeout': 60,
        'write_timeout': 60,
    }
}

print(app.config['SQLALCHEMY_DATABASE_URI'])  # Debugging line to check DB URI

# Initialize extensions
db.init_app(app)  # <-- initialize db with app
CORS(app)

from app.models import User, Field, Crop, PlantAnalysis, CropRecommendation, WeatherData, FarmerScheme

# Setup API documentation
setup_docs_route(app)

# Import routes after app initialization
from app.routes import auth, plants, crops, weather, farmer, fields, help_farmer, transactions

# Register blueprints
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(plants.bp, url_prefix='/api/plants')
app.register_blueprint(crops.bp, url_prefix='/api/crops')
app.register_blueprint(weather.bp, url_prefix='/api/weather')
app.register_blueprint(farmer.bp, url_prefix='/api/farmer')
app.register_blueprint(fields.bp, url_prefix='/api/fields')
app.register_blueprint(help_farmer.bp, url_prefix='/api/farmer_schemes')
app.register_blueprint(transactions.bp, url_prefix='/api/transactions')

@app.route('/')
def index():
    return {
        'message': 'Welcome to Agri-Assist Backend API',
        'version': '1.0.0',
        'documentation': '/docs/',
        'endpoints': {
            'auth': '/api/auth',
            'farmer': '/api/farmer',
            'fields': '/api/fields',
            'plants': '/api/plants',
            'crops': '/api/crops',
            'weather': '/api/weather'
        }
    }

@app.route('/health')
def health_check():
    """Health check endpoint for Cloud Run"""
    try:
        # Test database connection
        with db.engine.connect() as conn:
            conn.execute(db.text("SELECT 1"))
        return {'status': 'healthy', 'service': 'agri-assist-backend', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'service': 'agri-assist-backend', 'database': 'disconnected', 'error': str(e)}, 503

def create_tables_with_retry(max_retries=3):
    """Create database tables with retry logic for Cloud SQL"""
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Import all models to ensure they're registered with SQLAlchemy
                #from app.models import User, Field, Crop, PlantAnalysis, CropRecommendation, WeatherData, FarmerScheme
                
                # Test connection first
                with db.engine.connect() as conn:
                    conn.execute(db.text("SELECT 1"))
                    print(f"✅ Database connection successful (attempt {attempt + 1})")
                
                # Create tables only if they don't exist - NEVER DROP
                db.create_all()
                print(f"✅ Database tables created/verified successfully")
                return True
                
        except (OperationalError, DisconnectionError) as e:
            print(f"⚠️ Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"🔄 Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"❌ Failed to connect to database after {max_retries} attempts")
                raise
        except Exception as e:
            print(f"❌ Unexpected error creating tables: {str(e)}")
            raise
    
    return False

if __name__ == "__main__":
    create_tables_with_retry()
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
