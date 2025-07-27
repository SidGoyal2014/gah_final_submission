# Agri-Assist Backend

AI-powered agricultural assistance backend built with Flask and Google AI technologies.

## Features

- **Plant Disease Detection**: AI-powered image analysis for identifying plant diseases
- **Crop Recommendations**: Personalized crop suggestions based on soil and climate data
- **Weather Integration**: Real-time weather data for agricultural planning
- **User Management**: Firebase authentication and user profiles
- **Data Storage**: SQLAlchemy for local data and Firebase for cloud storage

## Setup

### Prerequisites
- Python 3.12+
- Google Cloud SQL (PostgreSQL/MySQL)
- Firebase project with Admin SDK
- Google AI API key

### Cloud SQL Setup (Production)

1. **Create Cloud SQL instance:**
   ```bash
   gcloud sql instances create agri-assist-db \
     --database-version=MYSQL_8_0 \
     --tier=db-f1-micro \
     --region=us-central1 \
     --storage-type=SSD \
     --storage-size=10GB \
     --backup \
     --enable-bin-log
   ```

2. **Create database:**
   ```bash
   gcloud sql databases create agri_assist --instance=agri-assist-db
   ```

3. **Create user:**
   ```bash
   gcloud sql users create agri_user \
     --instance=agri-assist-db \
     --password=YOUR_SECURE_PASSWORD
   ```

4. **Configure Cloud SQL Proxy (for local development):**
   ```bash
   # Download Cloud SQL Proxy
   wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
   chmod +x cloud_sql_proxy
   
   # Run proxy
   ./cloud_sql_proxy -instances=PROJECT_ID:REGION:agri-assist-db=tcp:3306
   ```

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   python main.py
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Plant Analysis
- `POST /api/plants/analyze` - Analyze plant image for diseases
- `GET /api/plants/history` - Get user's analysis history

### Crop Recommendations
- `POST /api/crops/recommend` - Get crop recommendations
- `GET /api/crops/suitable` - Get suitable crops for location

### Weather
- `GET /api/weather/current` - Get current weather
- `GET /api/weather/forecast` - Get weather forecast

## Environment Variables (Cloud SQL)

```
FLASK_ENV=production
SECRET_KEY=your_secret_key
GOOGLE_AI_API_KEY=your_google_ai_key
FIREBASE_CREDENTIALS_PATH=path/to/firebase/credentials.json

# Cloud SQL Configuration
DB_TYPE=mysql
DATABASE_URL=mysql+pymysql://agri_user:password@/agri_assist?unix_socket=/cloudsql/PROJECT_ID:REGION:agri-assist-db
DB_HOST=/cloudsql/PROJECT_ID:REGION:agri-assist-db  # Unix socket for Cloud Run
DB_PORT=3306
DB_USERNAME=agri_user
DB_PASSWORD=your_secure_password
DB_NAME=agri_assist

# For local development with Cloud SQL Proxy
# DATABASE_URL=mysql+pymysql://agri_user:password@127.0.0.1:3306/agri_assist
```

## Cloud Run Deployment

1. **Build and deploy:**
   ```bash
   gcloud run deploy agri-assist-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="DB_TYPE=mysql,DB_NAME=agri_assist,DB_USERNAME=agri_user,DB_PASSWORD=YOUR_PASSWORD" \
     --add-cloudsql-instances PROJECT_ID:REGION:agri-assist-db \
     --memory 1Gi \
     --cpu 1 \
     --timeout 3600 \
     --max-instances 10
   ```

2. **Set Cloud SQL connection:**
   ```bash
   gcloud run services update agri-assist-backend \
     --add-cloudsql-instances PROJECT_ID:REGION:agri-assist-db \
     --region us-central1
   ```

## Troubleshooting Cloud SQL

### Database "Disappearing" Issues:

1. **Connection Timeouts**: Cloud SQL has idle connection timeouts
2. **Socket Path**: Use Unix sockets in Cloud Run, not TCP
3. **Connection Pooling**: Configure proper pool settings
4. **Restart Policies**: Avoid unnecessary container restarts

### Common Solutions:

1. **Check Cloud SQL instance status:**
   ```bash
   gcloud sql instances describe agri-assist-db
   ```

2. **View Cloud SQL logs:**
   ```bash
   gcloud sql operations list --instance=agri-assist-db
   ```

3. **Test connection:**
   ```bash
   gcloud sql connect agri-assist-db --user=agri_user
   ```

4. **Monitor Cloud Run logs:**
   ```bash
   gcloud logs read --filter="resource.type=cloud_run_revision" --limit 50
   ```

## Development

Run in development mode:
```bash
export FLASK_ENV=development
python main.py
```

## Production

Deploy using Cloud Run (recommended) or Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```
