
import cv2
import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from backend.imageProcessing.validation import is_tar_road
from backend.calculations.regModel.pothole_model import get_pothole_model
from backend.calculations.pothole_areas import get_pothole_area

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        if is_tar_road(file_path):  # this is what happens if the image contains a tar road
            pothole_price = 0
            meter_areas, edited_img = get_pothole_area(file_path)
            for area in meter_areas:
                price = get_pothole_model(area, 0, 1)
                pothole_price += price

            # Encode the edited image to base64
            _, buffer = cv2.imencode('.jpg', edited_img)
            img_str = base64.b64encode(buffer).decode('utf-8')

            return jsonify({"message": f"The cost of this is R{pothole_price}", "img": img_str,"price":pothole_price})

        else:  # this happens when the image does not contain a tar road
            message = """The image does not contain a road, please enter an image with a road
                or the image is not clear, please Re-take the picture and try again"""
            return jsonify({"message": message}), 200
    else:
        return jsonify({"message": "This format is not supported"}), 400

if __name__ == '__main__':
    app.run(debug=True)

