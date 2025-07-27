from app.extensions import db
from datetime import datetime, date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #firebase_uid = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(500), nullable=False)  # Increased to 500 to handle scrypt hashes
    gender = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    #email = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    language = db.Column(db.String(10), default='english')  # Default to English
    
    # Relationships
    plant_analyses = db.relationship('PlantAnalysis', backref='user', lazy=True)
    crop_recommendations = db.relationship('CropRecommendation', backref='user', lazy=True)
    fields = db.relationship('Field', backref='owner', lazy=True)

class PlantAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    disease_detected = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CropRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    soil_type = db.Column(db.String(50))
    climate_zone = db.Column(db.String(50))
    recommended_crops = db.Column(db.Text)
    season = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Field name for identification
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    soil_type = db.Column(db.String(50), nullable=False)
    soil_ph = db.Column(db.Float)  # Soil pH level
    total_area = db.Column(db.Float, nullable=False)  # Total area in acres/hectares
    irrigation_type = db.Column(db.String(50))  # Drip, sprinkler, flood, etc.
    water_source = db.Column(db.String(50))  # Borewell, canal, river, etc.
    latitude = db.Column(db.Float)  # GPS coordinates
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - NO CASCADE DELETE
    crops = db.relationship('Crop', backref='field', lazy=True)

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    crop_type = db.Column(db.String(100), nullable=False)  # Rice, wheat, cotton, etc.
    variety = db.Column(db.String(100))  # Specific variety of the crop
    sowing_date = db.Column(db.Date, nullable=False)
    expected_harvest_date = db.Column(db.Date)
    area = db.Column(db.Float, nullable=False)  # Area covered by this crop in acres/hectares
    subsidy_eligible = db.Column(db.Boolean, default=False)
    seed_quantity = db.Column(db.Float)  # Quantity of seeds used
    seed_cost = db.Column(db.Float)  # Cost of seeds
    fertilizer_used = db.Column(db.String(200))  # Types of fertilizers used
    pesticide_used = db.Column(db.String(200))  # Types of pesticides used
    irrigation_frequency = db.Column(db.Integer)  # Times per week
    growth_stage = db.Column(db.String(50))  # Seedling, vegetative, flowering, etc.
    expected_yield = db.Column(db.Float)  # Expected yield in quintals/tons
    actual_yield = db.Column(db.Float)  # Actual yield after harvest
    harvest_date = db.Column(db.Date)  # Actual harvest date
    market_price = db.Column(db.Float)  # Price at which crop was sold
    notes = db.Column(db.Text)  # Additional notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FarmerScheme(db.Model):
    __tablename__ = 'farmer_schemes'
    
    id = db.Column(db.Integer, primary_key=True)
    scheme_category = db.Column(db.String(100))
    state_central = db.Column(db.String(100))
    scheme_name = db.Column(db.String(255))
    implementing_agency = db.Column(db.String(255))
    objective = db.Column(db.Text)
    budget_benefits = db.Column(db.String(255))
    target_beneficiaries = db.Column(db.String(255))
    official_website = db.Column(db.String(255))
    launch_year = db.Column(db.Integer)
    status = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'scheme_category': self.scheme_category,
            'state_central': self.state_central,
            'scheme_name': self.scheme_name,
            'implementing_agency': self.implementing_agency,
            'objective': self.objective,
            'budget_benefits': self.budget_benefits,
            'target_beneficiaries': self.target_beneficiaries,
            'official_website': self.official_website,
            'launch_year': self.launch_year,
            'status': self.status
        }
    
    def is_active(self):
        """Check if scheme is currently active"""
        return self.status and self.status.lower() == 'active'


class FarmerSchemeCrisis(db.Model):
    __tablename__ = 'farmer_crisis_schemes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scheme_name = db.Column(db.String(255))
    purpose = db.Column(db.Text)
    coverage = db.Column(db.Text)
    relief_benefit = db.Column(db.Text)
    farmer_action = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'scheme_name': self.scheme_name,
            'purpose': self.purpose,
            'coverage': self.coverage,
            'relief_benefit': self.relief_benefit,
            'farmer_action': self.farmer_action
        }

class TransactionLog(db.Model):
    __tablename__ = 'transaction_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userIdA = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phoneNumberB = db.Column(db.String(15), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # e.g., 'transfer', 'payment', 'loan', 'subsidy'
    transaction_amount = db.Column(db.Float, nullable=False)
    details = db.Column(db.Text)  # JSON string or text describing the action
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'userIdA': self.userIdA,
            'phoneNumberB': self.phoneNumberB,
            'transaction_type': self.transaction_type,
            'transaction_amount': self.transaction_amount,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

class Roles(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'role_name': self.role_name,
            'description': self.description
        }

class UserRole(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    user = db.relationship('User', backref='user_roles')
    role = db.relationship('Roles', backref='user_roles')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role_id': self.role_id
        }