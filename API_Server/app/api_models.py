from flask_restx import fields
from app.extensions import api

# Authentication Models
auth_register_model = api.model('AuthRegister', {
    'name': fields.String(required=True, description='User full name'),
    'phone': fields.String(required=True, description='Phone number (unique identifier)'),
    'password': fields.String(required=True, description='User password'),
    'gender': fields.String(required=True, enum=['Male', 'Female', 'Other'], description='User gender'),
    'state': fields.String(required=True, description='User state'),
    'city': fields.String(required=True, description='User city'),
    'age': fields.Integer(required=True, description='User age'),
    'email': fields.String(description='User email (optional)')
})

auth_login_model = api.model('AuthLogin', {
    'phone': fields.String(required=True, description='Phone number'),
    'password': fields.String(required=True, description='User password')
})

auth_response_model = api.model('AuthResponse', {
    'message': fields.String(description='Response message'),
    'token': fields.String(description='JWT authentication token'),
    'user': fields.Raw(description='User information')
})

# User/Farmer Models
user_profile_model = api.model('UserProfile', {
    'id': fields.Integer(description='User ID'),
    'name': fields.String(description='User name'),
    'phone': fields.String(description='Phone number'),
    'gender': fields.String(description='Gender'),
    'state': fields.String(description='State'),
    'city': fields.String(description='City'),
    'age': fields.Integer(description='Age'),
    'email': fields.String(description='Email'),
    'location': fields.String(description='Location'),
    'created_at': fields.String(description='Account creation date'),
    'total_fields': fields.Integer(description='Total number of fields'),
    'total_crops': fields.Integer(description='Total number of crops')
})

# Field Models
field_create_model = api.model('FieldCreate', {
    'name': fields.String(required=True, description='Field name for identification'),
    'address': fields.String(required=True, description='Field address'),
    'city': fields.String(required=True, description='City'),
    'state': fields.String(required=True, description='State'),
    'pin_code': fields.String(required=True, description='PIN code'),
    'soil_type': fields.String(required=True, description='Type of soil'),
    'total_area': fields.Float(required=True, description='Total area in acres/hectares'),
    'soil_ph': fields.Float(description='Soil pH level'),
    'irrigation_type': fields.String(description='Type of irrigation (drip, sprinkler, flood, etc.)'),
    'water_source': fields.String(description='Water source (borewell, canal, river, etc.)'),
    'latitude': fields.Float(description='GPS latitude'),
    'longitude': fields.Float(description='GPS longitude')
})

field_response_model = api.model('FieldResponse', {
    'id': fields.Integer(description='Field ID'),
    'name': fields.String(description='Field name'),
    'address': fields.String(description='Field address'),
    'city': fields.String(description='City'),
    'state': fields.String(description='State'),
    'pin_code': fields.String(description='PIN code'),
    'soil_type': fields.String(description='Soil type'),
    'soil_ph': fields.Float(description='Soil pH'),
    'total_area': fields.Float(description='Total area'),
    'irrigation_type': fields.String(description='Irrigation type'),
    'water_source': fields.String(description='Water source'),
    'latitude': fields.Float(description='Latitude'),
    'longitude': fields.Float(description='Longitude'),
    'created_at': fields.String(description='Creation date'),
    'updated_at': fields.String(description='Last update date'),
    'crop_count': fields.Integer(description='Number of crops in this field')
})

# Crop Models
crop_create_model = api.model('CropCreate', {
    'field_id': fields.Integer(required=True, description='Field ID where crop is planted'),
    'crop_type': fields.String(required=True, description='Type of crop (Rice, Wheat, Cotton, etc.)'),
    'variety': fields.String(description='Specific variety of the crop'),
    'sowing_date': fields.String(required=True, description='Sowing date (YYYY-MM-DD format)'),
    'expected_harvest_date': fields.String(description='Expected harvest date (YYYY-MM-DD format)'),
    'area': fields.Float(required=True, description='Area covered by this crop in acres/hectares'),
    'subsidy_eligible': fields.Boolean(description='Whether crop is eligible for subsidy'),
    'seed_quantity': fields.Float(description='Quantity of seeds used'),
    'seed_cost': fields.Float(description='Cost of seeds'),
    'fertilizer_used': fields.String(description='Types of fertilizers used'),
    'pesticide_used': fields.String(description='Types of pesticides used'),
    'irrigation_frequency': fields.Integer(description='Irrigation frequency per week'),
    'growth_stage': fields.String(description='Current growth stage'),
    'expected_yield': fields.Float(description='Expected yield in quintals/tons'),
    'notes': fields.String(description='Additional notes')
})

crop_response_model = api.model('CropResponse', {
    'id': fields.Integer(description='Crop ID'),
    'field_id': fields.Integer(description='Field ID'),
    'field_name': fields.String(description='Field name'),
    'crop_type': fields.String(description='Crop type'),
    'variety': fields.String(description='Crop variety'),
    'sowing_date': fields.String(description='Sowing date'),
    'expected_harvest_date': fields.String(description='Expected harvest date'),
    'area': fields.Float(description='Area'),
    'subsidy_eligible': fields.Boolean(description='Subsidy eligibility'),
    'seed_quantity': fields.Float(description='Seed quantity'),
    'seed_cost': fields.Float(description='Seed cost'),
    'fertilizer_used': fields.String(description='Fertilizers used'),
    'pesticide_used': fields.String(description='Pesticides used'),
    'irrigation_frequency': fields.Integer(description='Irrigation frequency'),
    'growth_stage': fields.String(description='Growth stage'),
    'expected_yield': fields.Float(description='Expected yield'),
    'actual_yield': fields.Float(description='Actual yield'),
    'harvest_date': fields.String(description='Harvest date'),
    'market_price': fields.Float(description='Market price'),
    'notes': fields.String(description='Notes'),
    'created_at': fields.String(description='Creation date'),
    'updated_at': fields.String(description='Last update date')
})

harvest_model = api.model('HarvestData', {
    'harvest_date': fields.String(description='Harvest date (YYYY-MM-DD), defaults to today'),
    'actual_yield': fields.Float(description='Actual yield achieved'),
    'market_price': fields.Float(description='Price at which crop was sold')
})

# Plant Analysis Models
plant_analysis_response_model = api.model('PlantAnalysisResponse', {
    'analysis_id': fields.Integer(description='Analysis ID'),
    'disease': fields.String(description='Detected disease'),
    'confidence': fields.Float(description='Confidence score (0-100)'),
    'recommendations': fields.String(description='Treatment recommendations'),
    'prevention_tips': fields.String(description='Prevention tips')
})

# Weather Models
weather_response_model = api.model('WeatherResponse', {
    'location': fields.String(description='Location name'),
    'temperature': fields.Float(description='Temperature in Celsius'),
    'humidity': fields.Float(description='Humidity percentage'),
    'wind_speed': fields.Float(description='Wind speed'),
    'description': fields.String(description='Weather description'),
    'source': fields.String(description='Data source')
})

forecast_response_model = api.model('ForecastResponse', {
    'location': fields.String(description='Location'),
    'forecast_days': fields.Integer(description='Number of forecast days'),
    'forecast': fields.List(fields.Raw, description='Forecast data')
})

# Crop Recommendation Models
crop_recommendation_request_model = api.model('CropRecommendationRequest', {
    'soil_type': fields.String(description='Soil type'),
    'climate_zone': fields.String(description='Climate zone'),
    'location': fields.String(description='Location'),
    'season': fields.String(description='Season')
})

crop_recommendation_response_model = api.model('CropRecommendationResponse', {
    'recommendation_id': fields.Integer(description='Recommendation ID'),
    'recommended_crops': fields.List(fields.String, description='List of recommended crops'),
    'farming_tips': fields.String(description='Farming tips'),
    'best_practices': fields.String(description='Best practices')
})

# Analytics Models
crop_analytics_model = api.model('CropAnalytics', {
    'summary': fields.Raw(description='Summary statistics'),
    'distribution': fields.Raw(description='Crop type and growth stage distribution'),
    'yield_analysis': fields.Raw(description='Yield analysis data'),
    'financial': fields.Raw(description='Financial analysis')
})

# Error Models
error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

success_model = api.model('Success', {
    'message': fields.String(description='Success message')
})
