from flask import Blueprint, request, jsonify
from app.services.weather_service import get_current_weather, get_weather_forecast

bp = Blueprint('weather', __name__)

@bp.route('/current', methods=['GET'])
def current_weather():
    try:
        location = request.args.get('location')
        if not location:
            return jsonify({'error': 'Location parameter required'}), 400
        
        weather_data = get_current_weather(location)
        
        # Just return the weather data - no database operations
        return jsonify(weather_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/forecast', methods=['GET'])
def weather_forecast():
    try:
        location = request.args.get('location')
        days = request.args.get('days', 7, type=int)
        
        if not location:
            return jsonify({'error': 'Location parameter required'}), 400
        
        forecast_data = get_weather_forecast(location, days)
        
        return jsonify({
            'location': location,
            'forecast_days': days,
            'forecast': forecast_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
        if not location:
            return jsonify({'error': 'Location parameter required'}), 400
        
        forecast_data = get_weather_forecast(location, days)
        
        return jsonify({
            'location': location,
            'forecast_days': days,
            'forecast': forecast_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
