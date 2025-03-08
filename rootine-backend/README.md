# Rootine backend API - to be continued
This repository contains a Flask-based backend for managing user profiles and plant profiles. Users can create, update, retrieve, and delete their plant profiles. The application uses Firebase Authentication for user authentication and Google Cloud Storage for handling profile pictures.

### Features
- User Authentication
- User Profile Management
  -  Create user profile
  -  Update user profile
- Plant Profile Management
  -  Create plant profile
  -  Update plant profile
  -  Get all plants of a user
  -  Get plant details by ID
  -  Delete plant


### Setup
#### Prerequisites
- Python 3.7+
- Flask
- Firebase Admin SDK
- Google Cloud Storage
- MongoDB

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/hereisamara/rootine-backend/
   cd rootine-backend
   ```
2. Create and activate a virtual environment:
  ```
  python -m venv venv
  source venv/bin/activate
  # On Windows:
  venv\Scripts\activate
  ```

3. Install the dependencies:
  ```
  pip install -r requirements.txt
  ```

4. Set up Firebase Admin SDK and Google Cloud Storage
   
- Download your Firebase service account key and place it in the project directory.
- Set the GOOGLE_APPLICATION_CREDENTIALS environment variable

5. Set up MongoDB:

- Ensure MongoDB is running and accessible.
- Update the MongoDB connection URI in the extensions.py file if necessary.



### Running the Application

1. Start the Flask development server:

    ```bash
    flask run
    ```

2. The application will be available at `http://localhost:5000`.

## API Documentation

### User Authentication
- We use firebase authentication and will directly connect to the user end.
  
### User Profile Management

#### Create User Profile

- **Endpoint:** `/api/create_user_profile`
- **Method:** `POST`
- **Description:** Creates a new user profile.
- **Headers:**
  ```
  {
    "Authorization": "Bearer <firebase_id_token>"
  }
  ```

- **Request Body (JSON or Form Data):**
  ```json
  {
    "name": "John Doe",
    "photo": "file"  // Optional profile picture
  }
  ```

- **Response:**
  ```json
  {
    "message": "User profile created successfully",
    "user_id": "firebase_user_id",
    "profile_url": "url_to_profile_picture"
  }
  ```

#### Update User Profile

- **Endpoint:** `/api/update_user_profile`
- **Method:** `PUT`
- **Description:** Updates an existing user profile.
- **Headers:**
  ```
  {
    "Authorization": "Bearer <firebase_id_token>"
  }
  ```

- **Request Body (JSON or Form Data):**
  ```json
  {
    "name": "John Smith",
    "photo": "file"  // Optional new profile picture
  }
  ```

- **Response:**
  ```json
  {
    "message": "User profile updated successfully",
    "user_id": "firebase_user_id",
    "profile_url": "url_to_new_profile_picture"
  }
  ```

### Plant Profile Management

#### Create Plant Profile

- **Endpoint:** `/api/create_plant_profile`
- **Method:** `POST`
- **Description:** Creates a new plant profile.
- **Headers:**
  ```
  {
    "Authorization": "Bearer <firebase_id_token>"
  }
  ```

- **Request Body (JSON or Form Data):**
  ```json
  {
    "plant_name": "Ficus",
    "species": "Ficus benjamina",
    "planting_date": "2023-06-01",
    "location": "indoor",
    "notes": "Water once a week",
    "photo": "file"  // Optional plant picture
  }
  ```

- **Response:**
  ```json
  {
    "message": "Plant profile created successfully",
    "plant_id": "mongo_plant_id"
  }
  ```

#### Update Plant Profile

- **Endpoint:** `/api/update_plant_profile/<plant_id>`
- **Method:** `PUT`
- **Description:** Updates an existing plant profile.
- **Headers:**
  ```
  {
    "Authorization": "Bearer <firebase_id_token>"
  }
  ```

- **Request Body (JSON or Form Data):**
  ```json
  {
    "plant_name": "Ficus",
    "species": "Ficus benjamina",
    "planting_date": "2023-07-01",
    "location": "outdoor",
    "notes": "Water twice a week",
    "photo": "file"  // Optional new plant picture
  }
  ```

- **Response:**
  ```json
  {
    "message": "Plant profile updated successfully"
  }
  ```

#### Get All Plants of a User

- **Endpoint:** `/api/get_user_plants`
- **Method:** `GET`
- **Description:** Retrieves all plants associated with the authenticated user.
- **Headers:**
  ```
  {
    "Authorization": "Bearer <firebase_id_token>"
  }
  ```

- **Response:**
  ```json
  [
    {
      "plant_id": "mongo_plant_id",
      "plant_name": "Ficus",
      "species": "Ficus benjamina",
      "planting_date": "2023-06-01",
      "location": "indoor",
      "notes": "Water once a week",
      "photo_url": "url_to_plant_picture"
    },
    ...
  ]
  ```

#### Get Plant Details by ID

- **Endpoint:** `/api/get_plant/<plant_id>`
- **Method:** `GET`
- **Description:** Retrieves details of a specific plant by its ID.
- **Headers:**
  ```
  {
    "Authorization": "Bearer <firebase_id_token>"
  }
  ```

- **Response:**
  ```json
  {
    "plant_id": "mongo_plant_id",
    "plant_name": "Ficus",
    "species": "Ficus benjamina",
    "planting_date": "2023-06-01",
    "location": "indoor",
    "notes": "Water once a week",
    "photo_url": "url_to_plant_picture"
  }
  ```

#### Delete Plant

- **Endpoint:** `/api/delete_plant/<plant_id>`
- **Method:** `DELETE`
- **Description:** Deletes a plant by its ID.
- **Headers:**
  ```
  {
    "Authorization": "Bearer <firebase_id_token>"
  }
  ```

- **Response:**
  ```json
  {
    "message": "Plant deleted successfully"
  }
  ```



