from datetime import datetime, timezone
from flask import json, request, jsonify
from bson.objectid import ObjectId
import pytz
from . import plant_bp
from utils.auth import firebase_auth_required
from extensions import bucket, users_collection, plants_collection, gm_collection, reminders_collection

VALID_LOCATIONS = ['indoor', 'outdoor']

VALID_FLOWERING_STAGES = ['Budding', 'Flowering', 'Post-Flowering', 'No Flowers']
VALID_HEALTH_STATUSES = ['Healthy', 'Stressed', 'Diseased', 'Nutrient Deficient', 'Pest Infested']

VALID_REMINDER_TYPES = ['prune', 'pest control', 'fertilize', 'water']
VALID_FREQUENCIES = ['daily', 'weekly', 'monthly', 'none']

@plant_bp.route('/api/create_plant_profile', methods=['POST'])
@firebase_auth_required
def create_plant_profile():
    user_id = request.decoded_token['uid']

    # Extract plant details from request
    if request.content_type == 'application/json':
        plant_name = request.json.get('plant_name')
        species = request.json.get('species')
        planting_date = request.json.get('planting_date')
        location = request.json.get('location')
        notes = request.json.get('notes')
    else:
        plant_name = request.form.get('plant_name')
        species = request.form.get('species')
        planting_date = request.form.get('planting_date')
        location = request.form.get('location')
        notes = request.form.get('notes')

    if not plant_name or not species or not planting_date:
        return jsonify({'error': 'Missing required plant information.'}), 400
    
    if location not in VALID_LOCATIONS:
        return jsonify({'error': 'Invalid location. Must be either "indoor" or "outdoor".'}), 400
    
    # Handle the plant profile picture
    photo_url = None
    if 'photo' in request.files:
        photo = request.files['photo']
        blob = bucket.blob(f'{user_id}/plants/{photo.filename}')
        blob.upload_from_file(photo)
        blob.make_public()
        photo_url = blob.public_url
    # Prepare plant profile data to store in MongoDB
    plant_profile_data = {
        'user_id': user_id,
        'plant_name': plant_name,
        'species': species,
        'planting_date': planting_date,
        'location': location,
        'notes': notes,
        'photo_url': photo_url
    }

    # Save the plant profile in MongoDB
    result = plants_collection.insert_one(plant_profile_data)
    
    # Optionally, add plant ID to user's plant list
    users_collection.update_one(
        {'_id': user_id},
        {'$push': {'plants': result.inserted_id}}
    )

    return jsonify({'message': 'Plant profile created successfully', 'plant_id': str(result.inserted_id)}), 201


@plant_bp.route('/api/update_plant_profile/<plant_id>', methods=['PUT'])
@firebase_auth_required
def update_plant_profile(plant_id):
    user_id = request.decoded_token['uid']
    
    # Extract plant details from request
    if request.content_type == 'application/json':
        plant_name = request.json.get('plant_name')
        species = request.json.get('species')
        planting_date = request.json.get('planting_date')
        location = request.json.get('location')
        notes = request.json.get('notes')
    else:
        plant_name = request.form.get('plant_name')
        species = request.form.get('species')
        planting_date = request.form.get('planting_date')
        location = request.form.get('location')
        notes = request.form.get('notes')

    update_data = {}
    if plant_name:
        update_data['plant_name'] = plant_name
    if species:
        update_data['species'] = species
    if planting_date:
        update_data['planting_date'] = planting_date
    if location:
        if location not in VALID_LOCATIONS:
            return jsonify({'error': 'Invalid location. Must be either "indoor" or "outdoor".'}), 400
        update_data['location'] = location
    if notes:
        update_data['notes'] = notes

    # Handle the plant profile picture
    if 'photo' in request.files:
        photo = request.files['photo']
        blob = bucket.blob(f'{user_id}/plants/{photo.filename}')
        blob.upload_from_file(photo)
        blob.make_public()
        update_data['photo_url'] = blob.public_url

    if not update_data:
        return jsonify({'error': 'No update data provided.'}), 400

    try:
        result = plants_collection.update_one(
            {'_id': ObjectId(plant_id), 'user_id': user_id},
            {'$set': update_data}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Plant profile not found or access denied.'}), 404

        return jsonify({'message': 'Plant profile updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@plant_bp.route('/api/get_user_plants', methods=['GET'])
@firebase_auth_required
def get_user_plants():
    user_id = request.decoded_token['uid']
    plants = plants_collection.find({'user_id': user_id})
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    today = datetime.now(bangkok_tz).date()
    plants_list = []

    for plant in plants:
        plant_detail = {
            '_id': str(plant['_id']),
            'name': str(plant['plant_name']),
            'image_url': str(plant['photo_url']),
            'reminders': [False, False, False, False]  # [pest control, prune, water, fertilize]
        }

        reminders = reminders_collection.find({'plant_id': plant['_id'], 'user_id': user_id})

        for reminder in reminders:
            reminder_type = reminder['reminder_type'].lower()
            frequency = reminder['frequency']
            day = reminder.get('day')
            status = reminder.get('status')

            if status != 'complete':
                if frequency == 'daily':
                    plant_detail['reminders'][get_reminder_index(reminder_type)] = True
                elif frequency == 'weekly' and day == today.weekday() + 1:
                    plant_detail['reminders'][get_reminder_index(reminder_type)] = True
                elif frequency == 'monthly' and day == today.day:
                    plant_detail['reminders'][get_reminder_index(reminder_type)] = True

        plants_list.append(plant_detail)

    return jsonify(plants_list), 200

def get_reminder_index(reminder_type):
    return VALID_REMINDER_TYPES.index(reminder_type)

@plant_bp.route('/api/get_indoor_plants', methods=['GET'])
@firebase_auth_required
def get_indoor_plants():
    user_id = request.decoded_token['uid']
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    today = datetime.now(bangkok_tz).date()
    plants = plants_collection.find({'user_id': user_id, 'location': 'indoor'})
    plants_list = []
    
    for plant in plants:
        plant_detail = {
            '_id': str(plant['_id']),
            'name': str(plant['plant_name']),
            'image_url': str(plant['photo_url']),
            'reminders': [False, False, False, False]  # [pest control, prune, water, fertilize]
        }

        reminders = reminders_collection.find({'plant_id': plant['_id'], 'user_id': user_id})

        for reminder in reminders:
            reminder_type = reminder['reminder_type'].lower()
            frequency = reminder['frequency']
            day = reminder.get('day')
            status = reminder.get('status')

            if status != 'complete':
                if frequency == 'daily':
                    plant_detail['reminders'][get_reminder_index(reminder_type)] = True
                elif frequency == 'weekly' and day == today.weekday() + 1:
                    plant_detail['reminders'][get_reminder_index(reminder_type)] = True
                elif frequency == 'monthly' and day == today.day:
                    plant_detail['reminders'][get_reminder_index(reminder_type)] = True

        plants_list.append(plant_detail)

    return jsonify(plants_list), 200


@plant_bp.route('/api/get_outdoor_plants', methods=['GET'])
@firebase_auth_required
def get_outdoor_plants():
    user_id = request.decoded_token['uid']
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    today = datetime.now(bangkok_tz).date()
    plants = plants_collection.find({'user_id': user_id, 'location': 'outdoor'})
    plants_list = []
    
    for plant in plants:
        plant_detail = {
            '_id': str(plant['_id']),
            'name': str(plant['plant_name']),
            'image_url': str(plant['photo_url']),
            'reminders': [False, False, False, False]  # [pest control, prune, water, fertilize]
        }

        reminders = reminders_collection.find({'plant_id': plant['_id'], 'user_id': user_id})

        for reminder in reminders:
            reminder_type = reminder['reminder_type'].lower()
            frequency = reminder['frequency']
            day = reminder.get('day')
            status = reminder.get('status')

            if status != 'complete':
                if frequency == 'daily':
                    plant_detail['reminders'][get_reminder_index(reminder_type)] = True
                elif frequency == 'weekly' and day == today.weekday() + 1:
                    plant_detail['reminders'][get_reminder_index(reminder_type)] = True
                elif frequency == 'monthly' and day == today.day:
                    plant_detail['reminders'][get_reminder_index(reminder_type)] = True

        plants_list.append(plant_detail)

    return jsonify(plants_list), 200


@plant_bp.route('/api/get_plant/<plant_id>', methods=['GET'])
@firebase_auth_required
def get_plant(plant_id):
    user_id = request.decoded_token['uid']
    plant = plants_collection.find_one({'_id': ObjectId(plant_id), 'user_id': user_id})
    if plant:
        planting_date = plant.get('planting_date')
        plant_age = calculate_age(planting_date) if planting_date else None
        
        # Convert MongoDB document to a dictionary suitable for your Flutter model
        plant_data = {
            '_id': str(plant['_id']),
            'name': plant.get('plant_name'),
            'location_type': plant.get('location'),
            'species': plant.get('species'),
            'age': str(plant_age),
            'date': str(planting_date),
            'note': plant.get('notes'),
            'image_url': plant.get('photo_url')
        }
        
        return jsonify(plant_data), 200
    else:
        return jsonify({'error': 'Plant not found or access denied.'}), 404


def calculate_age(planting_date):
    planting_date = datetime.strptime(planting_date, '%Y-%m-%d').date()
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    today = datetime.now(bangkok_tz).date()
    age_in_days = (today - planting_date).days
    return age_in_days


@plant_bp.route('/api/delete_plant/<plant_id>', methods=['DELETE'])
@firebase_auth_required
def delete_plant(plant_id):
    user_id = request.decoded_token['uid']
    result = plants_collection.delete_one({'_id': ObjectId(plant_id), 'user_id': user_id})
    if result.deleted_count == 1:
        # Optionally, remove the plant ID from the user's plant list
        users_collection.update_one(
            {'_id': user_id},
            {'$pull': {'plants': ObjectId(plant_id)}}
        )
        return jsonify({'message': 'Plant deleted successfully'}), 200
    else:
        return jsonify({'error': 'Plant not found or access denied.'}), 404


@plant_bp.route('/api/addTrackedData/<plant_id>', methods=['POST'])
@firebase_auth_required
def add_tracked_data(plant_id):
    user_id = request.decoded_token['uid']
    # Extract growth metrics from request
    if request.content_type == 'application/json':
        date = request.json.get('date')
        height = request.json.get('height')
        branch_count = request.json.get('branch_count')
        leaf_count = request.json.get('leaf_count')
        flowering_stage = request.json.get('flowering_stage')
        health_status = request.json.get('health_status')
    else:
        date = request.form.get('date')
        height = request.form.get('height')
        branch_count = request.form.get('branch_count')
        leaf_count = request.form.get('leaf_count')
        flowering_stage = request.form.get('flowering_stage')
        health_status = request.form.get('health_status')
    
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Expected YYYY-MM-DD.'}), 400

    if not height or not branch_count or not leaf_count or not flowering_stage or not health_status:
        return jsonify({'error': 'Missing required growth metrics information.'}), 400

    if flowering_stage not in VALID_FLOWERING_STAGES:
        return jsonify({'error': 'Invalid flowering stage. Must be one of: ' + ', '.join(VALID_FLOWERING_STAGES)}), 400

    if health_status not in VALID_HEALTH_STATUSES:
        return jsonify({'error': 'Invalid health status. Must be one of: ' + ', '.join(VALID_HEALTH_STATUSES)}), 400

    # Prepare growth metrics data to store in MongoDB
    growth_metrics_data = {
        'plant_id': ObjectId(plant_id),
        'date': date,
        'height': height,
        'branch_count': branch_count,
        'leaf_count': leaf_count,
        'flowering_stage': flowering_stage,
        'health_status': health_status
    }

    # Save the growth metrics in MongoDB
    result = gm_collection.insert_one(growth_metrics_data)
    
    growth_metrics_data['_id'] = str(result.inserted_id)
    growth_metrics_data['plant_id'] = str(growth_metrics_data['plant_id'])

    return jsonify({'message': 'Growth metrics added successfully', 'data': growth_metrics_data}), 201


@plant_bp.route('/api/getTrackedData/<plant_id>', methods=['POST'])
@firebase_auth_required
def get_tracked_data_for_date(plant_id):
    user_id = request.decoded_token['uid']

    data = request.get_json()
    date = data.get('date')

    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format. Expected YYYY-MM-DD.'}), 400

    try:
        growth_metrics = gm_collection.find_one({
            'plant_id': ObjectId(plant_id),
            'date': date
        })

        if not growth_metrics:
            return jsonify({'error': 'No growth metrics found for the given date'}), 404

        growth_metrics['_id'] = str(growth_metrics['_id'])  # Convert ObjectId to string
        growth_metrics['plant_id'] = str(growth_metrics['plant_id'])  # Convert ObjectId to string

        return jsonify(growth_metrics), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@plant_bp.route('/api/getAllTrackedData/<plant_id>', methods=['GET'])
@firebase_auth_required
def get_all_tracked_data(plant_id):
    user_id = request.decoded_token['uid']
    
    try:
        growth_metrics_cursor = gm_collection.find({
            'plant_id': ObjectId(plant_id)
        })

        growth_metrics_list = []
        for growth_metrics in growth_metrics_cursor:
            growth_metrics['_id'] = str(growth_metrics['_id'])  # Convert ObjectId to string
            growth_metrics['plant_id'] = str(growth_metrics['plant_id'])  # Convert ObjectId to string
            growth_metrics_list.append(growth_metrics)
            

        if not growth_metrics_list:
            return jsonify({'error': 'No growth metrics found for the given plant'}), 404

        return jsonify(growth_metrics_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@plant_bp.route('/api/addReminders', methods=['POST'])
@firebase_auth_required
def add_reminders():
    user_id = request.decoded_token['uid']
    
    if 'application/json' in request.content_type:
        data = request.get_json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        data = request.form.getlist('reminders')
        data = json.loads(data[0])
    else:
        return jsonify({'error': 'Invalid content type. Expected application/json or application/x-www-form-urlencoded.'}), 400

    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format. Expected a list of reminders.'}), 400

    for reminder in data:
        plant_id = reminder.get('plant_id')
        reminder_type = reminder.get('reminder_type')
        frequency = reminder.get('frequency')
        day = reminder.get('day')
        status = reminder.get('status', 'active')

        if reminder_type not in VALID_REMINDER_TYPES:
            return jsonify({'error': f'Invalid reminder type {reminder_type}. Must be one of: ' + ', '.join(VALID_REMINDER_TYPES)}), 400

        if frequency not in VALID_FREQUENCIES:
            return jsonify({'error': f'Invalid frequency {frequency}. Must be one of: ' + ', '.join(VALID_FREQUENCIES)}), 400

        if frequency == 'weekly' and (day < 1 or day > 7):
            return jsonify({'error': 'Invalid day for weekly frequency. Must be between 1 and 7.'}), 400

        if frequency == 'monthly' and (day < 1 or day > 30):
            return jsonify({'error': 'Invalid day for monthly frequency. Must be between 1 and 30.'}), 400

        existing_reminder = reminders_collection.find_one({
            'user_id': user_id,
            'plant_id': ObjectId(plant_id),
            'reminder_type': reminder_type
        })

        if existing_reminder:
            # Update the existing reminder
            reminders_collection.update_one(
                {'_id': existing_reminder['_id']},
                {'$set': {
                    'frequency': frequency,
                    'day': day,
                    'status': status
                }}
            )
        else:
            # Insert a new reminder
            reminders_collection.insert_one({
                'user_id': user_id,
                'plant_id': ObjectId(plant_id),
                'reminder_type': reminder_type,
                'frequency': frequency,
                'day': day,
                'status': status
            })

    return jsonify({'message': 'Reminders added or updated successfully'}), 201


@plant_bp.route('/api/getReminders/<plant_id>', methods=['GET'])
@firebase_auth_required
def get_reminders(plant_id):
    user_id = request.decoded_token['uid']
    query = {'user_id': user_id}
    if plant_id:
        query['plant_id'] = ObjectId(plant_id)

    reminders = reminders_collection.find(query)
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    today = datetime.now(bangkok_tz).date()
    reminders_list = []

    for reminder in reminders:
        if reminder['reminder_type'] != 'none' and reminder['status'] != 'complete':
            reminder_date = None
            if reminder['frequency'] == 'daily':
                reminder_date = today
            elif reminder['frequency'] == 'weekly' and reminder['day'] == today.weekday() + 1:
                reminder_date = today
            elif reminder['frequency'] == 'monthly' and reminder['day'] == today.day:
                reminder_date = today

            if reminder_date:
                reminder['_id'] = str(reminder['_id'])
                reminder['plant_id'] = str(reminder['plant_id'])
                reminders_list.append(reminder)

    return jsonify(reminders_list), 200

@plant_bp.route('/api/getRemindersDueToday', methods=['GET'])
@firebase_auth_required
def get_reminders_due_today():
    user_id = request.decoded_token['uid']
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    today = datetime.now(bangkok_tz).date()
    
    day_of_week = today.weekday() + 1  # Python's weekday() returns 0 (Monday) to 6 (Sunday)
    day_of_month = today.day

    # Query for reminders due today
    reminders = reminders_collection.find({
        'user_id': user_id,
        '$or': [
            {'frequency': 'daily'},
            {'frequency': 'weekly', 'day': day_of_week},
            {'frequency': 'monthly', 'day': day_of_month}
        ]
    })

    reminders_list = []
    for reminder in reminders:
        reminder['_id'] = str(reminder['_id'])
        reminder['plant_id'] = str(reminder['plant_id'])
        reminders_list.append(reminder)

    return jsonify(reminders_list), 200


@plant_bp.route('/api/updateReminderStatus', methods=['PUT'])
@firebase_auth_required
def update_reminder_status():
    user_id = request.decoded_token['uid']

    if 'application/json' in request.content_type:
        data = request.get_json()
    elif  'application/x-www-form-urlencoded' in request.content_type:
        data = request.form
    else:
        return jsonify({'error': 'Invalid content type. Expected application/json or application/x-www-form-urlencoded.'}), 400

    if not data or 'plant_id' not in data or 'reminder_type' not in data:
        return jsonify({'error': 'Invalid data format. Expected a JSON object with plant_id and reminder_type.'}), 400

    plant_id = data['plant_id']
    reminder_type = data['reminder_type']

    if reminder_type not in VALID_REMINDER_TYPES:
        return jsonify({'error': f'Invalid reminder type {reminder_type}. Must be one of: ' + ', '.join(VALID_REMINDER_TYPES)}), 400

    try:
        result = reminders_collection.update_many(
            {'user_id': user_id, 'plant_id': ObjectId(plant_id), 'reminder_type': reminder_type, 'status': 'active'},
            {'$set': {'status': 'complete'}}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Reminder status updated successfully'}), 200
        else:
            return jsonify({'message': 'No active reminders found to update'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

