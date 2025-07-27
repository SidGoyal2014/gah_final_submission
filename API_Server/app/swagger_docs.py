#!/usr/bin/env python3
"""
Simple Swagger Documentation Setup for AgriAssist Backend
This file provides basic Swagger documentation without requiring flask-restx
Uses a simple HTML template to serve API documentation
"""

from flask import Flask, render_template_string
import os

# HTML template for Swagger-like documentation
SWAGGER_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgriAssist Backend API Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        h3 { color: #7f8c8d; }
        .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
        .method { display: inline-block; padding: 4px 8px; border-radius: 3px; color: white; font-weight: bold; margin-right: 10px; }
        .get { background-color: #27ae60; }
        .post { background-color: #e74c3c; }
        .put { background-color: #f39c12; }
        .delete { background-color: #8e44ad; }
        .description { margin: 10px 0; color: #555; }
        .parameters { margin: 10px 0; }
        .param { background: #bdc3c7; padding: 5px; margin: 5px 0; border-radius: 3px; }
        .auth-info { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .base-url { background: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .response-example { background: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; border-radius: 5px; margin: 10px 0; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌾 AgriAssist Backend API Documentation</h1>
        
        <div class="base-url">
            <strong>Base URL:</strong> <code>http://localhost:5000/api</code>
        </div>
        
        <div class="auth-info">
            <strong>🔐 Authentication:</strong> Most endpoints require JWT token in Authorization header: 
            <code>Authorization: Bearer &lt;your_jwt_token&gt;</code>
        </div>

        <h2>📋 Available Endpoints</h2>

        <h3>👤 Authentication</h3>
        <div class="endpoint">
            <span class="method post">POST</span><strong>/api/auth/register</strong>
            <div class="description">Register a new user account</div>
            <div class="parameters">
                <strong>Body Parameters:</strong>
                <div class="param">name (string, required) - User full name</div>
                <div class="param">phone (string, required) - Phone number (unique identifier)</div>
                <div class="param">password (string, required) - User password</div>
                <div class="param">gender (string, required) - User gender (Male/Female/Other)</div>
                <div class="param">state (string, required) - User state</div>
                <div class="param">city (string, required) - User city</div>
                <div class="param">age (integer, required) - User age</div>
                <div class="param">email (string, optional) - User email</div>
            </div>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span><strong>/api/auth/login</strong>
            <div class="description">User login to get JWT token</div>
            <div class="parameters">
                <strong>Body Parameters:</strong>
                <div class="param">phone (string, required) - Phone number</div>
                <div class="param">password (string, required) - User password</div>
            </div>
            <div class="response-example">
                <strong>Success Response:</strong>
                <pre>
{
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "phone": "9876543210",
    ...
  }
}
                </pre>
            </div>
        </div>

        <h3>👨‍🌾 Farmer Profile</h3>
        <div class="endpoint">
            <span class="method get">GET</span><strong>/api/farmer/profile</strong>
            <div class="description">Get user profile information</div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span><strong>/api/farmer/dashboard</strong>
            <div class="description">Get user dashboard with summary statistics</div>
        </div>

        <div class="endpoint">
            <span class="method put">PUT</span><strong>/api/farmer/update_profile</strong>
            <div class="description">Update user profile information</div>
        </div>

        <h3>🏞️ Field Management</h3>
        <div class="endpoint">
            <span class="method post">POST</span><strong>/api/fields/create</strong>
            <div class="description">Create a new field</div>
            <div class="parameters">
                <strong>Body Parameters:</strong>
                <div class="param">name (string, required) - Field name</div>
                <div class="param">address (string, required) - Field address</div>
                <div class="param">city (string, required) - City</div>
                <div class="param">state (string, required) - State</div>
                <div class="param">pin_code (string, required) - PIN code</div>
                <div class="param">soil_type (string, required) - Soil type</div>
                <div class="param">total_area (float, required) - Total area in acres/hectares</div>
                <div class="param">soil_ph (float, optional) - Soil pH level</div>
                <div class="param">irrigation_type (string, optional) - Irrigation type</div>
                <div class="param">water_source (string, optional) - Water source</div>
                <div class="param">latitude (float, optional) - GPS latitude</div>
                <div class="param">longitude (float, optional) - GPS longitude</div>
            </div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span><strong>/api/fields/list</strong>
            <div class="description">Get all fields for the user</div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span><strong>/api/fields/{field_id}</strong>
            <div class="description">Get detailed field information including crops</div>
        </div>

        <div class="endpoint">
            <span class="method put">PUT</span><strong>/api/fields/{field_id}/update</strong>
            <div class="description">Update field information</div>
        </div>

        <div class="endpoint">
            <span class="method delete">DELETE</span><strong>/api/fields/{field_id}/delete</strong>
            <div class="description">Delete a field (and all associated crops)</div>
        </div>

        <h3>🌾 Crop Management</h3>
        <div class="endpoint">
            <span class="method post">POST</span><strong>/api/crops/create</strong>
            <div class="description">Create a new crop in a field</div>
            <div class="parameters">
                <strong>Body Parameters:</strong>
                <div class="param">field_id (integer, required) - Field ID</div>
                <div class="param">crop_type (string, required) - Crop type (Rice, Wheat, etc.)</div>
                <div class="param">sowing_date (string, required) - Sowing date (YYYY-MM-DD)</div>
                <div class="param">area (float, required) - Area in acres/hectares</div>
                <div class="param">variety (string, optional) - Crop variety</div>
                <div class="param">expected_harvest_date (string, optional) - Expected harvest date</div>
                <div class="param">subsidy_eligible (boolean, optional) - Subsidy eligibility</div>
                <div class="param">seed_quantity (float, optional) - Seed quantity used</div>
                <div class="param">seed_cost (float, optional) - Cost of seeds</div>
                <div class="param">fertilizer_used (string, optional) - Fertilizers used</div>
                <div class="param">pesticide_used (string, optional) - Pesticides used</div>
                <div class="param">irrigation_frequency (integer, optional) - Irrigation per week</div>
                <div class="param">growth_stage (string, optional) - Current growth stage</div>
                <div class="param">expected_yield (float, optional) - Expected yield</div>
                <div class="param">notes (string, optional) - Additional notes</div>
            </div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span><strong>/api/crops/list</strong>
            <div class="description">Get all crops for the user</div>
            <div class="parameters">
                <strong>Query Parameters:</strong>
                <div class="param">field_id (integer, optional) - Filter by field</div>
            </div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span><strong>/api/crops/{crop_id}</strong>
            <div class="description">Get detailed crop information</div>
        </div>

        <div class="endpoint">
            <span class="method put">PUT</span><strong>/api/crops/{crop_id}/update</strong>
            <div class="description">Update crop information</div>
        </div>

        <div class="endpoint">
            <span class="method delete">DELETE</span><strong>/api/crops/{crop_id}/delete</strong>
            <div class="description">Delete a crop</div>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span><strong>/api/crops/harvest/{crop_id}</strong>
            <div class="description">Record harvest information</div>
            <div class="parameters">
                <strong>Body Parameters:</strong>
                <div class="param">harvest_date (string, optional) - Harvest date (defaults to today)</div>
                <div class="param">actual_yield (float, optional) - Actual yield achieved</div>
                <div class="param">market_price (float, optional) - Price at which crop was sold</div>
            </div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span><strong>/api/crops/analytics</strong>
            <div class="description">Get comprehensive crop analytics</div>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span><strong>/api/crops/recommend</strong>
            <div class="description">Get AI-powered crop recommendations</div>
        </div>

        <h3>🌿 Plant Disease Analysis</h3>
        <div class="endpoint">
            <span class="method post">POST</span><strong>/api/plants/analyze</strong>
            <div class="description">Analyze plant image for diseases</div>
            <div class="parameters">
                <strong>Form Data:</strong>
                <div class="param">image (file, required) - Plant image file</div>
            </div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span><strong>/api/plants/history</strong>
            <div class="description">Get plant analysis history</div>
        </div>

        <h3>🌤️ Weather Information</h3>
        <div class="endpoint">
            <span class="method get">GET</span><strong>/api/weather/current</strong>
            <div class="description">Get current weather for a location</div>
            <div class="parameters">
                <strong>Query Parameters:</strong>
                <div class="param">location (string, required) - Location name</div>
            </div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span><strong>/api/weather/forecast</strong>
            <div class="description">Get weather forecast</div>
            <div class="parameters">
                <strong>Query Parameters:</strong>
                <div class="param">location (string, required) - Location name</div>
                <div class="param">days (integer, optional) - Number of forecast days (default: 7)</div>
            </div>
        </div>

        <h2>📊 Response Formats</h2>
        <div class="response-example">
            <strong>Success Response Format:</strong>
            <pre>
{
  "message": "Operation successful",
  "data": { ... }
}
            </pre>
        </div>

        <div class="response-example">
            <strong>Error Response Format:</strong>
            <pre>
{
  "error": "Error message description"
}
            </pre>
        </div>

        <h2>🔍 Testing the API</h2>
        <p>You can test these endpoints using:</p>
        <ul>
            <li><strong>curl</strong> - Command line tool</li>
            <li><strong>Postman</strong> - GUI API testing tool</li>
            <li><strong>Python requests</strong> - Programmatic testing</li>
            <li><strong>JavaScript fetch</strong> - Frontend integration</li>
        </ul>

        <div class="response-example">
            <strong>Example curl request:</strong>
            <pre>
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"phone": "9876543210", "password": "your_password"}'
            </pre>
        </div>

        <footer style="margin-top: 40px; text-align: center; color: #7f8c8d;">
            <p>AgriAssist Backend API v1.0 | Built with Flask & ❤️ for farmers</p>
        </footer>
    </div>
</body>
</html>
'''

def setup_docs_route(app):
    """Add a /docs route to the Flask app"""
    @app.route('/docs/')
    @app.route('/docs')
    def api_docs():
        return render_template_string(SWAGGER_HTML_TEMPLATE)
    
    return app
