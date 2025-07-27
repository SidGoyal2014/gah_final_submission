from flask_restx import Namespace

# Create API namespaces for different modules
auth_ns = Namespace('auth', description='Authentication operations')
farmer_ns = Namespace('farmer', description='Farmer profile and management operations')
fields_ns = Namespace('fields', description='Field management operations')
crops_ns = Namespace('crops', description='Crop management and analytics operations')
plants_ns = Namespace('plants', description='Plant disease analysis operations')
weather_ns = Namespace('weather', description='Weather information operations')
