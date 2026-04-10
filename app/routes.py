from flask import Blueprint, request, jsonify
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return jsonify({'message': 'EyeSell API is running'})

@main.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filepath = os.path.join('app/uploads', image.filename)
    image.save(filepath)

    return jsonify({'message': 'Image uploaded successfully', 'path': filepath})