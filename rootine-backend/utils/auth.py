from functools import wraps
from flask import request, jsonify
from firebase_admin import auth

def verify_firebase_token(token):
    try:
        # Verify the Firebase token
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying Firebase token: {e}")
        return None

def firebase_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401

        token = auth_header.split(' ')[1]
        decoded_token = verify_firebase_token(token)
        if not decoded_token:
            return jsonify({'error': 'Invalid or expired token'}), 401

        request.decoded_token = decoded_token
        return f(*args, **kwargs)
    return decorated_function