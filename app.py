import os
from flask import Flask, request, render_template, send_file, flash, redirect, url_for, jsonify
import requests
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import io

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
REMOVE_BG_API_KEY = os.getenv('REMOVE_BG_API_KEY', 'JtDK8gimnE92X1ggYfrJLwP8')  # Using the API key from Flutter app as default

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/editor', methods=['GET', 'POST'])
def editor():
    if request.method == 'POST':
        # Check if API key is configured
        if not REMOVE_BG_API_KEY:
            return 'Please configure your Remove.bg API key', 400

        # Check if a file was uploaded
        if 'file' not in request.files:
            return 'No file selected', 400

        file = request.files['file']
        if file.filename == '':
            return 'No file selected', 400

        if file and allowed_file(file.filename):
            try:
                # Call remove.bg API
                response = requests.post(
                    'https://api.remove.bg/v1.0/removebg',
                    headers={'X-Api-Key': REMOVE_BG_API_KEY},
                    files={'image_file': file},
                    data={'size': 'auto'}
                )
                
                if response.status_code == 200:
                    # Return the processed image directly
                    return send_file(
                        io.BytesIO(response.content),
                        mimetype='image/png'
                    )
                else:
                    return f'Error: {response.status_code} - {response.text}', 400

            except Exception as e:
                return f'Error processing image: {str(e)}', 500
        else:
            return 'Allowed file types are: png, jpg, jpeg', 400

    return render_template('editor.html')

if __name__ == '__main__':
    app.run(debug=True) 