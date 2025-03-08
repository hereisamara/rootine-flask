from flask import request, jsonify
from . import user_bp
from utils.auth import firebase_auth_required
from extensions import bucket, users_collection

@user_bp.route('/api/create_user_profile', methods=['POST'])
@firebase_auth_required
def create_user_profile():
    user_id = request.decoded_token['uid']
    email = request.decoded_token['email']

    if request.content_type == 'application/json':
        name = request.json.get('name')
    else:
        name = request.form.get('name')
        
    if 'photo' not in request.files:
        photo_url = ""
    else:
        photo = request.files['photo']
        blob = bucket.blob(f'{user_id}/{photo.filename}')
        blob.upload_from_file(photo)
        # Optionally make the file public
        blob.make_public()
        photo_url = blob.public_url

    # Prepare user profile data to store in MongoDB
    profile_data = {
        '_id': user_id,  # Use Firebase UID as MongoDB primary key
        'email': email,
        'name': name,
        'plants': [],
        'profile_url': photo_url
    }

    # Save the user profile in MongoDB
    users_collection.insert_one(profile_data)
    return jsonify({'message': 'User profile created successfully', 'user_id': user_id, 'profile_url': photo_url}), 201

@user_bp.route('/api/update_user_profile', methods=['PUT'])
@firebase_auth_required
def update_user_profile():
    user_id = request.decoded_token['uid']
    email = request.decoded_token['email']

    # Retrieve the existing user profile
    existing_profile = users_collection.find_one({'_id': user_id})
    if not existing_profile:
        return jsonify({'error': 'Profile not found'}), 404


    if request.content_type == 'application/json':
        name = request.json.get('name', existing_profile.get('name'))
    else:
        name = request.form.get('name', existing_profile.get('name'))


    photo_url = existing_profile.get('profile_url', "")

    ## need to delete previous profile picture
    if 'photo' in request.files:
        photo = request.files['photo']
        blob = bucket.blob(f'{user_id}/{photo.filename}')
        blob.upload_from_file(photo)
        # Optionally make the file public
        blob.make_public()
        photo_url = blob.public_url
    else:
        photo_url = None

    # Prepare updated user profile data
    update_data = {
        'email': email,
        'name': name,
        'profile_url': photo_url
    }

    # Update the user profile in MongoDB
    users_collection.update_one({'_id': user_id}, {'$set': update_data})
    return jsonify({'message': 'User profile updated successfully', 'user_id': user_id, 'profile_url': photo_url}), 200

@user_bp.route('/api/get_user_profile', methods=['GET'])
@firebase_auth_required
def get_user_profile():
    user_id = request.decoded_token['uid']

    # Retrieve the existing user profile
    user_profile = users_collection.find_one({'_id': user_id})
    if user_profile:
        user_profile_data = {}
        user_profile_data['_id'] = str(user_profile['_id'])
        user_profile_data['name'] = str(user_profile['name'])
        user_profile_data['email'] = str(user_profile['email'])
        user_profile_data['profile_url'] = str(user_profile['profile_url'])
        return jsonify(user_profile_data), 200
    
    return jsonify({'error': 'Profile not found'}), 404