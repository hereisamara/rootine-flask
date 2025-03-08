import unittest
import requests
from flask import Flask
from io import BytesIO
import sys
import os

# Ensure the real environment is used, not the testing environment
if 'IS_TESTING' in os.environ:
    del os.environ['IS_TESTING']

# Add the parent directory to the sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

# Firebase API details
FIREBASE_API_KEY = 'apikey'  # Replace with your Firebase API key

class CreateUserProfileApiRealTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def get_firebase_id_token_existing_user(self, email, password):
        login_url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}'
        login_payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        login_response = requests.post(login_url, json=login_payload)
        self.assertEqual(login_response.status_code, 200)
        
        id_token = login_response.json()['idToken']
        return id_token
    
    def get_firebase_id_token_new_user(self, email, password):
        """Helper method to register and get Firebase ID token"""
        register_url = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}'
        register_payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        register_response = requests.post(register_url, json=register_payload)
        self.assertEqual(register_response.status_code, 200)

        login_url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}'
        login_payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        login_response = requests.post(login_url, json=login_payload)
        self.assertEqual(login_response.status_code, 200)
        
        id_token = login_response.json()['idToken']
        return id_token
    
    def test_login_user(self):
        email = 'amara_user@example.com'
        password = 'testpassword'

        # Get the Firebase ID token by registering and logging in the user
        id_token = self.get_firebase_id_token_existing_user(email, password)
        print()
        print(id_token)
        
    @unittest.skip("Not now")
    def test_create_user_profile(self):
        email = 'amara_user@example.com'
        password = 'testpassword'

        # Get the Firebase ID token by registering and logging in the user
        id_token = self.get_firebase_id_token(email, password)

        # Path to the test image file
        image_path = 'Planner pagepalnner.png'
        
        with open(image_path, 'rb') as image_file:
            data = {
                'name': 'Test User',
                'email': email,  # Include the email in the data
                'photo': (image_file, 'Planner_pageplanner_1.png')  # File must be included in the data dictionary
            }
            headers = {'Authorization': f'Bearer {id_token}'}

            # The 'content_type' parameter should not be manually set for multipart/form-data; it's handled automatically
            response = self.app.post('/api/create_user_profile', headers=headers, data=data)

            self.assertEqual(response.status_code, 201)
            self.assertIn('User profile created successfully', response.get_json()['message'])
            print('Profile URL:', response.get_json()['profile_url'])
            
    @unittest.skip("Not now")
    def test_update_user_profile_no_profile_image(self):
        ## use already existing user
        email = 'amara_user@example.com'
        password = 'testpassword'

        # Get the Firebase ID token by registering and logging in the user
        id_token = self.get_firebase_id_token_existing_user(email, password)

        update_data = {
            'email': 'updateduser_amara@example.com', # cannot be updated, will be ignored
            'name': 'Updated Amara User',
        }
        
        headers = {'Authorization': f'Bearer {id_token}'}
        response = self.app.put('/api/update_user_profile', headers=headers, data=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('User profile updated successfully', response.get_json()['message'])
        print('Profile URL:', response.get_json()['profile_url'])

    @unittest.skip("Not now")
    def test_update_user_profile(self):
        ## use already existing user
        email = 'amara_user@example.com'
        password = 'testpassword'

        # Get the Firebase ID token by registering and logging in the user
        id_token = self.get_firebase_id_token_existing_user(email, password)

        # Path to the test image file
        image_path = 'unittests/test_images/user_2.png'
        
        # Update user profile
        with open(image_path, 'rb') as image_file:
            update_data = {
                'email': 'amara_user@example.com',
                'name': 'Khin Eaindray Htun',
                'photo': (image_file, 'user.png')
            }
            
            headers = {'Authorization': f'Bearer {id_token}'}
            response = self.app.put('/api/update_user_profile', headers=headers, data=update_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('User profile updated successfully', response.get_json()['message'])
            print('Profile URL:', response.get_json()['profile_url'])
            
if __name__ == '__main__':
    unittest.main()
    