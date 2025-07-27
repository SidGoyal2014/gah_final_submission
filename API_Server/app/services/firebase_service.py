import firebase_admin
from firebase_admin import credentials, auth
import os

# Initialize Firebase Admin SDK
cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
if cred_path and os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token):
    """Verify Firebase ID token and return decoded token"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Firebase token verification failed: {e}")
        return None

def get_user_info(uid):
    """Get user information from Firebase"""
    try:
        user = auth.get_user(uid)
        return {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name,
            'email_verified': user.email_verified
        }
    except Exception as e:
        print(f"Failed to get user info: {e}")
        return None
