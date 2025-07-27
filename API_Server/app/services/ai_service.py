import os
from PIL import Image
import io
import json

# Try to import Vertex AI, fallback to regular Google AI if not available
try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform import gapic
    import google.cloud.aiplatform as vertexai
    from vertexai.generative_models import GenerativeModel, Part
    VERTEX_AI_AVAILABLE = True
    print("✅ Vertex AI SDK loaded successfully")
except ImportError as e:
    print(f"⚠️ Vertex AI not available: {e}")
    try:
        # Try alternative import
        import vertexai
        from vertexai.generative_models import GenerativeModel, Part
        VERTEX_AI_AVAILABLE = True
        print("✅ Vertex AI SDK loaded successfully (alternative import)")
    except ImportError as e2:
        print(f"⚠️ Vertex AI alternative import failed: {e2}")
        VERTEX_AI_AVAILABLE = False
    
        # Fallback to regular Google AI
        try:
            import google.generativeai as genai
            GENAI_AVAILABLE = True
            print("✅ Google Generative AI SDK loaded as fallback")
        except ImportError as e3:
            print(f"❌ No AI SDK available: {e3}")
            GENAI_AVAILABLE = False

# Configure AI services
project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'farmai-466317')
location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

if VERTEX_AI_AVAILABLE:
    try:
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        print(f"✅ Vertex AI initialized for project: {project_id}, location: {location}")
    except Exception as e:
        print(f"⚠️ Vertex AI initialization failed: {e}")
        VERTEX_AI_AVAILABLE = False

if not VERTEX_AI_AVAILABLE and 'GENAI_AVAILABLE' in locals() and GENAI_AVAILABLE:
    # Configure Google AI as fallback
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        print("✅ Google Generative AI configured as fallback")
    else:
        print("⚠️ No Google AI API key found")
        GENAI_AVAILABLE = False
elif not VERTEX_AI_AVAILABLE:
    GENAI_AVAILABLE = False

def analyze_plant_image_vertex_ai(image_files):
    """Analyze plant image using Vertex AI"""
    print("🤖 Analyzing plant image using Vertex AI")
    try:
        # Process images for Vertex AI
        processed_images = []
        
        # Handle single image or multiple images
        if not isinstance(image_files, list):
            image_files = [image_files]
        
        for image_file in image_files:
            # Read the image data
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
                image_file.seek(0)
            else:
                image_data = image_file
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Ensure image is in RGB format
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to bytes for Vertex AI
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=95)
            img_byte_arr = img_byte_arr.getvalue()
            
            # Create image part for Vertex AI
            image_part = Part.from_data(
                mime_type="image/jpeg",
                data=img_byte_arr
            )
            
            processed_images.append(image_part)
        
        # Use Vertex AI Gemini Pro Vision for image analysis
        try:
            model = GenerativeModel("gemini-1.5-pro-vision-001")
        except Exception:
            # Fallback to a different model if the vision model is not available
            model = GenerativeModel("gemini-1.5-pro")
        
        prompt = """
        Analyze this plant image and provide a detailed agricultural assessment:
        1. Disease identification (if any) - be specific about the disease name
        2. Confidence level (0-100%) - how certain you are about the diagnosis
        3. Treatment recommendations - specific fungicides, pesticides, or organic treatments
        4. Prevention tips - how to prevent this disease in the future
        5. Severity assessment - mild, moderate, or severe
        6. Affected plant parts - leaves, stems, fruits, roots, etc.
        
        Format the response as JSON with keys: disease, confidence, recommendations, prevention_tips, severity, affected_parts
        
        If no disease is detected, indicate "Healthy Plant" for disease and provide general care tips.
        """
        
        # Prepare content for Vertex AI
        content = [prompt] + processed_images
        
        # Generate response using Vertex AI
        response = model.generate_content(content)
        
        return parse_ai_response(response.text, "Vertex AI")
        
    except Exception as e:
        print(f"❌ Vertex AI plant analysis failed: {e}")
        return create_error_response(f"Vertex AI analysis failed: {str(e)}")

def analyze_plant_image_genai(image_files):
    """Analyze plant image using Google Generative AI as fallback"""
    print("🤖 Analyzing plant image using Google Generative AI (fallback)")
    try:
        # Process images for Google AI
        processed_images = []
        
        if not isinstance(image_files, list):
            image_files = [image_files]
        
        for image_file in image_files:
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
                image_file.seek(0)
            else:
                image_data = image_file
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=95)
            img_byte_arr = img_byte_arr.getvalue()
            
            # Create image part for Google AI
            image_part = {
                "mime_type": "image/jpeg",
                "data": img_byte_arr
            }
            
            processed_images.append(image_part)
        
        # Use Google AI Gemini Pro Vision
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = """
        Analyze this plant image and provide a detailed agricultural assessment:
        1. Disease identification (if any) - be specific about the disease name
        2. Confidence level (0-100%) - how certain you are about the diagnosis
        3. Treatment recommendations - specific fungicides, pesticides, or organic treatments
        4. Prevention tips - how to prevent this disease in the future
        5. Severity assessment - mild, moderate, or severe
        6. Affected plant parts - leaves, stems, fruits, roots, etc.
        
        Format the response as JSON with keys: disease, confidence, recommendations, prevention_tips, severity, affected_parts
        
        If no disease is detected, indicate "Healthy Plant" for disease and provide general care tips.
        """
        
        # Prepare content
        content = [prompt] + processed_images
        
        response = model.generate_content(content)
        
        return parse_ai_response(response.text, "Google AI")
        
    except Exception as e:
        print(f"❌ Google AI plant analysis failed: {e}")
        return create_error_response(f"Google AI analysis failed: {str(e)}")

def parse_ai_response(response_text, ai_source):
    """Parse AI response and extract JSON data"""
    try:
        print(f"🤖 {ai_source} Response: {response_text}")
        
        # Try to extract JSON from response
        if '{' in response_text and '}' in response_text:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            parsed_response = json.loads(json_str)
            
            return {
                'disease': parsed_response.get('disease', 'Analysis completed'),
                'confidence': float(parsed_response.get('confidence', 85.0)),
                'recommendations': parsed_response.get('recommendations', response_text),
                'prevention_tips': parsed_response.get('prevention_tips', 'Follow good agricultural practices'),
                'severity': parsed_response.get('severity', 'Unknown'),
                'affected_parts': parsed_response.get('affected_parts', 'Not specified'),
                'image_url': f'{ai_source.lower()}_analysis',
                'ai_source': ai_source
            }
        else:
            # Fallback if no JSON found
            return {
                'disease': 'Analysis completed',
                'confidence': 85.0,
                'recommendations': response_text,
                'prevention_tips': 'Follow recommended agricultural practices',
                'severity': 'Assessment pending',
                'affected_parts': 'Visual inspection required',
                'image_url': f'{ai_source.lower()}_analysis',
                'ai_source': ai_source
            }
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return {
            'disease': 'Analysis completed',
            'confidence': 80.0,
            'recommendations': response_text,
            'prevention_tips': 'Consult with agricultural experts for detailed guidance',
            'severity': 'Requires expert evaluation',
            'affected_parts': 'Multiple areas',
            'image_url': f'{ai_source.lower()}_analysis',
            'ai_source': ai_source
        }

def create_error_response(error_message):
    """Create a standardized error response"""
    return {
        'disease': 'Analysis failed',
        'confidence': 0.0,
        'recommendations': error_message,
        'prevention_tips': 'Consult local agricultural extension services',
        'severity': 'Unable to assess',
        'affected_parts': 'Unable to determine',
        'image_url': 'analysis_error',
        'ai_source': 'error'
    }

def create_mock_response():
    """Create a mock response when no AI service is available"""
    return {
        'disease': 'Service temporarily unavailable',
        'confidence': 0.0,
        'recommendations': 'AI analysis service is currently unavailable. Please try again later or consult a local agricultural expert.',
        'prevention_tips': 'Follow standard crop protection practices and maintain good field hygiene',
        'severity': 'Unknown',
        'affected_parts': 'Unable to determine',
        'image_url': 'mock_analysis',
        'ai_source': 'mock'
    }

def analyze_plant_image(image_files):
    """Main function to analyze plant image - tries Vertex AI first, then Google AI, then mock"""
    print("🔍 Starting plant disease analysis")
    
    # Try Vertex AI first
    if VERTEX_AI_AVAILABLE:
        print("🎯 Using Vertex AI for analysis")
        return analyze_plant_image_vertex_ai(image_files)
    
    # Fallback to Google AI
    elif GENAI_AVAILABLE:
        print("🎯 Using Google Generative AI for analysis")
        return analyze_plant_image_genai(image_files)
    
    # No AI service available - return mock response
    else:
        print("⚠️ No AI service available, returning mock response")
        return create_mock_response()

def convert_image_to_blob(image_file):
    """Convert uploaded image to blob format for database storage"""
    try:
        if hasattr(image_file, 'read'):
            image_data = image_file.read()
            image_file.seek(0)
        else:
            image_data = image_file
        
        # Optional: Compress image if too large
        image = Image.open(io.BytesIO(image_data))
        
        # Resize if image is too large (optional)
        max_size = (1024, 1024)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to JPEG blob
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=85)
        blob_data = img_byte_arr.getvalue()
        
        return blob_data
        
    except Exception as e:
        print(f"❌ Image conversion failed: {e}")
        return None

def get_crop_recommendations(soil_type=None, climate_zone=None, location=None, season=None, quick_lookup=False):
    """Get crop recommendations using available AI service"""
    print("🌾 Getting crop recommendations")
    
    try:
        # Try Vertex AI first
        if VERTEX_AI_AVAILABLE:
            return get_crop_recommendations_vertex_ai(soil_type, climate_zone, location, season)
        
        # Fallback to Google AI
        elif GENAI_AVAILABLE:
            return get_crop_recommendations_genai(soil_type, climate_zone, location, season)
        
        # No AI available - return basic recommendations
        else:
            return get_basic_crop_recommendations(soil_type, climate_zone, location, season)
            
    except Exception as e:
        print(f"❌ Error getting crop recommendations: {e}")
        return get_basic_crop_recommendations(soil_type, climate_zone, location, season)

def get_crop_recommendations_vertex_ai(soil_type, climate_zone, location, season):
    """Get crop recommendations using Vertex AI"""
    try:
        model = GenerativeModel("gemini-1.5-pro")
    except Exception:
        # Fallback if specific model not available
        model = GenerativeModel("gemini-pro")
    
    prompt = f"""
    As an agricultural expert, provide comprehensive crop recommendations for:
    - Soil type: {soil_type or 'general'}
    - Climate zone: {climate_zone or 'temperate'}
    - Location: {location or 'general'}
    - Season: {season or 'current'}
    
    Please provide:
    1. Top 5 recommended crops with reasons for each recommendation
    2. Specific farming tips for the given conditions
    3. Best practices for soil and water management
    4. Expected yield estimates for each crop
    5. Market considerations and profitability insights
    
    Format as JSON with keys: crops (array of objects with name, reason, expected_yield), farming_tips, best_practices, market_insights
    """
    
    response = model.generate_content(prompt)
    return parse_crop_recommendations(response.text, "Vertex AI")

def get_crop_recommendations_genai(soil_type, climate_zone, location, season):
    """Get crop recommendations using Google AI"""
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    As an agricultural expert, provide comprehensive crop recommendations for:
    - Soil type: {soil_type or 'general'}
    - Climate zone: {climate_zone or 'temperate'}
    - Location: {location or 'general'}
    - Season: {season or 'current'}
    
    Please provide:
    1. Top 5 recommended crops with reasons for each recommendation
    2. Specific farming tips for the given conditions
    3. Best practices for soil and water management
    
    Format as JSON with keys: crops, farming_tips, best_practices
    """
    
    response = model.generate_content(prompt)
    return parse_crop_recommendations(response.text, "Google AI")

def parse_crop_recommendations(response_text, ai_source):
    """Parse crop recommendation response"""
    try:
        print(f"🌾 {ai_source} Crop Recommendations: {response_text}")
        
        if '{' in response_text and '}' in response_text:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            parsed_response = json.loads(json_str)
            
            # Extract crop names for backward compatibility
            crops_list = []
            if 'crops' in parsed_response and isinstance(parsed_response['crops'], list):
                crops_list = [crop.get('name', crop) if isinstance(crop, dict) else crop for crop in parsed_response['crops']]
            else:
                crops_list = ['Rice', 'Wheat', 'Corn', 'Tomatoes', 'Potatoes']
            
            return {
                'crops': crops_list,
                'detailed_crops': parsed_response.get('crops', []),
                'farming_tips': parsed_response.get('farming_tips', response_text),
                'best_practices': parsed_response.get('best_practices', 'Follow local agricultural guidelines'),
                'market_insights': parsed_response.get('market_insights', 'Consult local market prices'),
                'ai_source': ai_source
            }
        else:
            return {
                'crops': ['Rice', 'Wheat', 'Corn', 'Tomatoes', 'Potatoes'],
                'farming_tips': response_text,
                'best_practices': f'AI-generated best practices from {ai_source}',
                'market_insights': 'Market analysis pending',
                'ai_source': ai_source
            }
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error in crop recommendations: {e}")
        return get_basic_crop_recommendations()

def get_basic_crop_recommendations(soil_type=None, climate_zone=None, location=None, season=None):
    """Provide basic crop recommendations when AI is not available"""
    basic_crops = {
        'clay': ['Rice', 'Wheat', 'Sugarcane'],
        'sandy': ['Millet', 'Groundnut', 'Cotton'],
        'loam': ['Corn', 'Tomatoes', 'Potatoes'],
        'black': ['Cotton', 'Sugarcane', 'Soybeans']
    }
    
    # Get crops based on soil type or use default
    crops = basic_crops.get(soil_type, ['Rice', 'Wheat', 'Corn', 'Tomatoes', 'Potatoes'])
    
    return {
        'crops': crops,
        'farming_tips': f'Basic recommendations for {soil_type or "general"} soil. Consult local agricultural extension services for detailed guidance.',
        'best_practices': 'Follow local farming guidelines and best practices for your region',
        'market_insights': 'Research local market conditions and prices',
        'ai_source': 'basic_recommendations'
    }