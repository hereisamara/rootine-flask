import unittest
import requests
from flask import Flask
from io import BytesIO
import json
import sys, os

# Add the parent directory to the sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

class PlantProfileApiTest(unittest.TestCase):
    FIREBASE_API_KEY = 'apikey'   # Replace with your Firebase API key

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def get_firebase_id_token(self, email, password):
        # Login the user to get the ID token
        login_url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.FIREBASE_API_KEY}'
        login_payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        login_response = requests.post(login_url, json=login_payload)
        self.assertEqual(login_response.status_code, 200)
        
        id_token = login_response.json()['idToken']
        return id_token
    @unittest.skip("Not now")
    def test_create_plant_profile(self):
        """Test creating a new plant profile"""
        email = 'amara_user@example.com'
        password = 'testpassword'

        # Get the Firebase ID token
        id_token = self.get_firebase_id_token(email, password)

        # Path to the test image file
        image_path = 'unittests/test_images/plant_2.jpg'
        
        with open(image_path, 'rb') as image_file:
            headers = {
                'Authorization': f'Bearer {id_token}'
            }
            data = {
                'plant_name': 'Ficus',
                'species': 'Ficus benjamina',
                'planting_date': '2023-06-01',
                'location': 'indoor',  # Valid location
                'notes': 'Water once a week',
                'photo': (image_file, 'test_image.jpg')
            }

            response = self.app.post(f'/api/create_plant_profile', headers=headers, data=data)
            print(response)
            self.assertEqual(response.status_code, 201)
            self.assertIn('Plant profile created successfully', response.get_json()['message'])
            print('Plant profile created:', response.get_json())
    @unittest.skip("Not now")
    def test_create_plant_profile_invalid_location(self):
        """Test creating a new plant profile with an invalid location"""
        email = 'amara_user@example.com'
        password = 'testpassword'

        # Get the Firebase ID token
        id_token = self.get_firebase_id_token(email, password)

        # Path to the test image file
        image_path = 'unittests/test_images/plant_2.jpg'
        
        with open(image_path, 'rb') as image_file:
            headers = {
                'Authorization': f'Bearer {id_token}'
            }
            data = {
                'plant_name': 'Ficus',
                'species': 'Ficus benjamina',
                'planting_date': '2023-06-01',
                'location': 'invalid_location',  # Invalid location
                'notes': 'Water once a week',
                'photo': (image_file, 'test_image.jpg')
            }

            response = self.app.post('/api/create_plant_profile', headers=headers, data=data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid location', response.get_json()['error'])
            print('Invalid location error:', response.get_json())
    @unittest.skip("Not now")
    def test_update_plant_profile(self):
        """Test updating an existing plant profile"""
        email = 'amara_user@example.com'
        password = 'testpassword'

        # Get the Firebase ID token
        id_token = self.get_firebase_id_token(email, password)

        # First, create a plant profile to update 
        image_path = 'unittests/test_images/plant_2.jpg'
        
        with open(image_path, 'rb') as image_file:
            headers = {
                'Authorization': f'Bearer {id_token}'
            }
            data = {
                'plant_name': 'Ficus',
                'species': 'Ficus benjamina',
                'planting_date': '2023-06-01',
                'location': 'indoor',  # Valid location
                'notes': 'Water once a week',
                'photo': (image_file, 'test_image.jpg')
            }

            create_response = self.app.post(f'/api/create_plant_profile', headers=headers, data=data)
            self.assertEqual(create_response.status_code, 201)
            plant_id = create_response.get_json()['plant_id']

        # Now, update the plant profile
        new_image_path = 'unittests/test_images/plant_2.jpg'
        
        with open(new_image_path, 'rb') as new_image_file:
            update_data = {
                'plant_name': 'Updated Ficus',
                'species': 'Updated Ficus benjamina',
                'planting_date': '2023-07-01',
                'location': 'outdoor',  # Valid location
                'notes': 'Updated notes',
                'photo': (new_image_file, 'new_test_image.jpg')
            }

            update_response = self.app.put(f'/api/update_plant_profile/{plant_id}', headers=headers, data=update_data)
            self.assertEqual(update_response.status_code, 200)
            self.assertIn('Plant profile updated successfully', update_response.get_json()['message'])
            print('Plant profile updated:', update_response.get_json())
    @unittest.skip("Not now")
    def test_update_plant_profile_invalid_location(self):
        """Test updating an existing plant profile with an invalid location"""
        email = 'amara_user@example.com'
        password = 'testpassword'

        # Get the Firebase ID token
        id_token = self.get_firebase_id_token(email, password)

        # First, create a plant profile to update
        image_path = 'unittests/test_images/plant_2.jpg'
        
        with open(image_path, 'rb') as image_file:
            headers = {
                'Authorization': f'Bearer {id_token}'
            }
            data = {
                'plant_name': 'Ficus',
                'species': 'Ficus benjamina',
                'planting_date': '2023-06-01',
                'location': 'indoor',  # Valid location
                'notes': 'Water once a week',
                'photo': (image_file, 'test_image.jpg')
            }

            create_response = self.app.post('/api/create_plant_profile', headers=headers, data=data)
            self.assertEqual(create_response.status_code, 201)
            plant_id = create_response.get_json()['plant_id']

        # Now, update the plant profile with an invalid location
        new_image_path = 'unittests/test_images/plant_2.jpg'
        
        with open(new_image_path, 'rb') as new_image_file:
            update_data = {
                'plant_name': 'Updated Ficus',
                'species': 'Updated Ficus benjamina',
                'planting_date': '2023-07-01',
                'location': 'invalid_location',  # Invalid location
                'notes': 'Updated notes',
                'photo': (new_image_file, 'new_test_image.jpg')
            }

            update_response = self.app.put(f'/api/update_plant_profile/{plant_id}', headers=headers, data=update_data)
            self.assertEqual(update_response.status_code, 400)
            self.assertIn('Invalid location', update_response.get_json()['error'])
            print('Invalid location error:', update_response.get_json())

    def test_get_user_plants(self):
        """Test getting all plants of a user"""
        email = 'amara_user@example.com'
        password = 'testpassword'
        
        # Get the Firebase ID token
        id_token = self.get_firebase_id_token(email, password)
        print(id_token)

        headers = {
            'Authorization': f'Bearer {id_token}'
        }

        # Get the user's plants
        response = self.app.get(f'/api/get_user_plants', headers=headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        print('User plants:', response.get_json())

    @unittest.skip("Not now")
    def test_get_plant(self):
        """Test getting plant details by ID"""
        email = 'testuser@example.com'
        password = 'testpassword'

        # Get the Firebase ID token
        id_token = self.get_firebase_id_token(email, password)

        headers = {
            'Authorization': f'Bearer {id_token}'
        }

        # First, create a plant profile to get its ID
        image_path = 'unittests/test_images/plant_2.jpg'
        
        with open(image_path, 'rb') as image_file:
            data = {
                'plant_name': 'Ficus',
                'species': 'Ficus benjamina',
                'planting_date': '2023-06-01',
                'location': 'indoor',  # Valid location
                'notes': 'Water once a week',
                'photo': (image_file, 'test_image.jpg')
            }

            create_response = self.app.post(f'/api/create_plant_profile', headers=headers, data=data)
            print(create_response.data)
            self.assertEqual(create_response.status_code, 201)
            plant_id = create_response.get_json()['plant_id']

        # Get the plant details
        response = self.app.get(f'/api/get_plant/{plant_id}', headers=headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('plant_name', response.get_json())
        print('Plant details:', response.get_json())

    @unittest.skip("Not now")
    def test_delete_plant(self):
        """Test deleting a plant by ID"""
        email = 'amara_user@example.com'
        password = 'testpassword'

        # Get the Firebase ID token
        id_token = self.get_firebase_id_token(email, password)

        headers = {
            'Authorization': f'Bearer {id_token}'
        }

        # First, create a plant profile to get its ID
        image_path = 'unittests/test_images/plant_2.jpg'
        
        with open(image_path, 'rb') as image_file:
            data = {
                'plant_name': 'Ficus',
                'species': 'Ficus benjamina',
                'planting_date': '2023-06-01',
                'location': 'indoor',  # Valid location
                'notes': 'Water once a week',
                'photo': (image_file, 'test_image.jpg')
            }

            create_response = self.app.post(f'/api/create_plant_profile', headers=headers, data=data)
            print(create_response.data)
            self.assertEqual(create_response.status_code, 201)
            plant_id = create_response.get_json()['plant_id']

        # Delete the plant
        response = self.app.delete(f'/api/delete_plant/{plant_id}', headers=headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Plant deleted successfully', response.get_json()['message'])
        print('Delete response:', response.get_json())

if __name__ == '__main__':
    unittest.main()
