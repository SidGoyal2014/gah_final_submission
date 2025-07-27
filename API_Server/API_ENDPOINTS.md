# AgriAssist Backend API Endpoints

*Backend uses Google Cloud SQL (MySQL) for persistent data storage with SQLAlchemy ORM. Data is never automatically deleted.*

## Cloud SQL Data Persistence

- **Production**: Google Cloud SQL instance with automated backups
- **Connection**: Unix sockets on Cloud Run for optimal performance
- **Reliability**: Connection pooling and retry logic for Cloud SQL timeouts
- **Backup**: Automated daily backups enabled on Cloud SQL instance

## Authentication Endpoints (`/api/auth`)

### POST /api/auth/register
Register a new user
**Body:**
```json
{
  "name": "string",
  "phone": "string", 
  "password": "string",
  "gender": "string",
  "state": "string",
  "city": "string",
  "age": "integer",
  "email": "string" (optional)
}
```

### POST /api/auth/login
Login user
**Body:**
```json
{
  "phone": "string",
  "password": "string"
}
```
**Response:**
```json
{
  "message": "Login successful",
  "token": "jwt_token",
  "user": {user_details}
}
```

## User/Farmer Management (`/api/farmer`)

### GET /api/farmer/profile
Get user profile (requires JWT token)

### GET /api/farmer/dashboard  
Get user dashboard with summary statistics

### PUT /api/farmer/update_profile
Update user profile (requires JWT token)

### POST /api/farmer/recommend
Get crop recommendations based on soil, climate, etc.

## Fields Management (`/api/fields`)

### POST /api/fields/create
Create a new field (requires JWT token)
**Body:**
```json
{
  "name": "string",
  "address": "string", 
  "city": "string",
  "state": "string",
  "pin_code": "string",
  "soil_type": "string",
  "total_area": "float",
  "soil_ph": "float" (optional),
  "irrigation_type": "string" (optional),
  "water_source": "string" (optional),
  "latitude": "float" (optional),
  "longitude": "float" (optional)
}
```

### GET /api/fields/list
Get all fields for the authenticated user

### GET /api/fields/{field_id}
Get detailed information about a specific field including crops

### PUT /api/fields/{field_id}/update
Update field information

### DELETE /api/fields/{field_id}/delete
Delete a field (and all associated crops)

## Crops Management (`/api/crops`)

### POST /api/crops/create
Create a new crop in a field (requires JWT token)
**Body:**
```json
{
  "field_id": "integer",
  "crop_type": "string",
  "variety": "string" (optional),
  "sowing_date": "YYYY-MM-DD",
  "expected_harvest_date": "YYYY-MM-DD" (optional),
  "area": "float",
  "subsidy_eligible": "boolean" (optional),
  "seed_quantity": "float" (optional),
  "seed_cost": "float" (optional),
  "fertilizer_used": "string" (optional),
  "pesticide_used": "string" (optional),
  "irrigation_frequency": "integer" (optional),
  "growth_stage": "string" (optional),
  "expected_yield": "float" (optional),
  "notes": "string" (optional)
}
```

### GET /api/crops/list
Get all crops for the user
**Query Parameters:**
- `field_id` (optional): Filter crops by specific field

### GET /api/crops/{crop_id}
Get detailed information about a specific crop

### PUT /api/crops/{crop_id}/update
Update crop information

### DELETE /api/crops/{crop_id}/delete
Delete a crop

### POST /api/crops/harvest/{crop_id}
Record harvest information for a crop
**Body:**
```json
{
  "harvest_date": "YYYY-MM-DD" (optional, defaults to today),
  "actual_yield": "float" (optional),
  "market_price": "float" (optional)
}
```

### GET /api/crops/test
Test endpoint to verify crops route is working

### POST /api/crops/recommend
Get AI-powered crop recommendations

### GET /api/crops/suitable
Get suitable crops for a location and season

## Plant Disease Analysis (`/api/plants`)

### POST /api/plants/analyze
Analyze plant image for diseases (requires JWT token)
**Form Data:**
- `image`: Image file

### GET /api/plants/history
Get analysis history for the user

## Weather Information (`/api/weather`)

### GET /api/weather/current
Get current weather for a location
**Query Parameters:**
- `location`: Location name

### GET /api/weather/forecast  
Get weather forecast
**Query Parameters:**
- `location`: Location name
- `days`: Number of days (default: 7)

## Data Models

### User
- Basic profile information (name, phone, location, etc.)
- Has many Fields
- Has many PlantAnalyses
- Has many CropRecommendations

### Field
- Belongs to User
- Contains location, soil, irrigation details
- Has many Crops

### Crop
- Belongs to Field
- Contains crop type, growth details, yield information
- Tracks full crop lifecycle from sowing to harvest

### PlantAnalysis
- Belongs to User
- Contains disease detection results and recommendations

### CropRecommendation
- Belongs to User
- Contains AI-generated crop recommendations

### WeatherData
- Weather information for locations

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer {jwt_token}
```

## Error Responses
All endpoints return appropriate HTTP status codes and error messages in JSON format:
```json
{
  "error": "Error message description"
}
```

## Success Responses
Successful operations typically return:
```json
{
  "message": "Success message",
  "data": {...}
}
```
