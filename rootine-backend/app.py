from flask import Flask, jsonify, request
import os
import requests
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Import and register blueprints
from users.routes import user_bp
from plants.routes import plant_bp

app.register_blueprint(user_bp)
app.register_blueprint(plant_bp)


# Set your Roboflow API key and model URL
ROBOFLOW_API_KEY = "apikey"
ROBOFLOW_MODEL_URL = "https://detect.roboflow.com/plant-disease-identifier/2"

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/process_image', methods=['POST'])
def process_image():
    
    print(request.content_type)  # Debugging: Check content type
    print(request.files)  # Debugging: Check files part

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Send image to Roboflow for processing
        with open(filepath, 'rb') as img_file:
            response = requests.post(
                ROBOFLOW_MODEL_URL,
                files={'file': img_file},
                params={'api_key': ROBOFLOW_API_KEY}
            )
        
        if response.status_code == 200:
            response_data = response.json()
            return_data = {'class': None, 'conf': None}
            if(response_data.get('predicted_classes', None)):
                if(len(response_data['predicted_classes'])> 0):
                    predicted_class = response_data['predicted_classes']
                    return_data['class'] = str(predicted_class[0])
                    return_data['conf'] = response_data['predictions'][predicted_class[0]]['confidence']
                
            return jsonify(return_data), 200
        else:
            return jsonify({'error': 'Failed to process image with Roboflow'}), response.status_code
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True)
