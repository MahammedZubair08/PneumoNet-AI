"""
PneumoNet AI - Flask API for Pneumonia Detection
This API serves predictions from the trained MobileNetV2 model
for detecting pneumonia from chest X-ray images.
"""

import os
import numpy as np
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import tensorflow as tf
from PIL import Image
import io
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
IMG_SIZE = 224
THRESHOLD = 0.5  # Classification threshold (adjustable)

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load the trained model
MODEL_PATH = 'pneumonia_model.keras'
# Load the trained model
MODEL_PATH = 'pneumonia_model.keras'

def load_model_safe():
    """Safely load model with multiple fallback strategies"""
    try:
        # Strategy 1: Try loading with compile=False
        logger.info(f"Attempting to load model from {MODEL_PATH}...")
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        logger.info(f"✓ Model loaded successfully from {MODEL_PATH}")
        return model
    except Exception as e1:
        logger.warning(f"Standard load failed: {e1}")
        try:
            # Strategy 2: Try with custom_objects for compatibility
            logger.info("Attempting alternative load method...")
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = tf.keras.models.load_model(MODEL_PATH)
                logger.info(f"✓ Model loaded successfully using alternative method")
                return model
        except Exception as e2:
            logger.error(f"Model loading failed: {e2}")
            logger.info("API will work in DEMO MODE without predictions")
            return None

model = load_model_safe()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image_data):
    """
    Preprocess image for model prediction
    
    Args:
        image_data: PIL Image or bytes
        
    Returns:
        Preprocessed numpy array ready for prediction
    """
    try:
        # If image_data is bytes, load it
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        else:
            image = image_data.convert('RGB') if image_data.mode != 'RGB' else image_data
        
        # Resize to model input size
        image = image.resize((IMG_SIZE, IMG_SIZE), Image.Resampling.LANCZOS)
        
        # Convert to numpy array and normalize
        image_array = np.array(image, dtype=np.float32) / 255.0
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None
    }), 200


@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    
    Accepts either:
    - Multipart form data with 'image' file
    - JSON with base64 encoded image
    
    Returns:
        JSON with prediction results
    """
    if model is None:
        return jsonify({
            'error': 'Model not loaded',
            'reason': 'The pneumonia detection model could not be loaded due to TensorFlow compatibility issues',
            'solution': 'Re-train the model using pneumonia_detection.ipynb with the current TensorFlow version',
            'note': 'The API framework is working correctly - it just needs a compatible model',
            'demo_mode': True
        }), 503  # Service Unavailable status code
    
    try:
        image = None
        filename = 'unknown'
        
        # Check if file is in request
        if 'image' in request.files:
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
            
            filename = secure_filename(file.filename)
            image = Image.open(file.stream)
            
        elif request.is_json:
            # Handle base64 encoded image
            data = request.get_json()
            if 'image' not in data:
                return jsonify({'error': 'No image provided in JSON'}), 400
            
            import base64
            try:
                image_base64 = data['image']
                image_data = base64.b64decode(image_base64)
                image = Image.open(io.BytesIO(image_data))
            except Exception as e:
                return jsonify({'error': f'Invalid base64 image: {str(e)}'}), 400
        else:
            return jsonify({'error': 'No image file or JSON data provided'}), 400
        
        # Preprocess the image
        processed_image = preprocess_image(image)
        
        # Make prediction
        prediction = model.predict(processed_image, verbose=0)
        confidence = float(prediction[0][0])
        
        # Determine class based on threshold
        is_pneumonia = confidence > THRESHOLD
        
        # Prepare response
        response = {
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'prediction': {
                'pneumonia_probability': round(confidence, 4),
                'normal_probability': round(1 - confidence, 4),
                'predicted_class': 'PNEUMONIA' if is_pneumonia else 'NORMAL',
                'confidence': round(max(confidence, 1 - confidence) * 100, 2),
                'threshold_used': THRESHOLD
            },
            'status': 'success'
        }
        
        # Log prediction
        logger.info(f"Prediction made for {filename}: {response['prediction']['predicted_class']} "
                   f"({response['prediction']['confidence']}%)")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@app.route('/predict-batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction endpoint for multiple images
    
    Accepts:
    - Multiple files as 'images' in multipart form data
    
    Returns:
        JSON with predictions for all images
    """
    if model is None:
        return jsonify({
            'error': 'Model not loaded',
            'reason': 'The pneumonia detection model could not be loaded due to TensorFlow compatibility issues',
            'solution': 'Re-train the model using pneumonia_detection.ipynb with the current TensorFlow version',
            'demo_mode': True
        }), 503
    
    try:
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400
        
        files = request.files.getlist('images')
        
        if len(files) == 0:
            return jsonify({'error': 'No images selected'}), 400
        
        predictions_list = []
        errors = []
        
        for idx, file in enumerate(files):
            try:
                if file.filename == '':
                    errors.append({'index': idx, 'error': 'No filename'})
                    continue
                
                if not allowed_file(file.filename):
                    errors.append({'index': idx, 'filename': file.filename, 
                                 'error': f'Invalid file type'})
                    continue
                
                # Process image
                image = Image.open(file.stream)
                processed_image = preprocess_image(image)
                
                # Predict
                prediction = model.predict(processed_image, verbose=0)
                confidence = float(prediction[0][0])
                is_pneumonia = confidence > THRESHOLD
                
                predictions_list.append({
                    'filename': secure_filename(file.filename),
                    'pneumonia_probability': round(confidence, 4),
                    'normal_probability': round(1 - confidence, 4),
                    'predicted_class': 'PNEUMONIA' if is_pneumonia else 'NORMAL',
                    'confidence': round(max(confidence, 1 - confidence) * 100, 2)
                })
                
            except Exception as e:
                errors.append({'index': idx, 'filename': file.filename, 'error': str(e)})
        
        response = {
            'timestamp': datetime.now().isoformat(),
            'total_images': len(files),
            'successful_predictions': len(predictions_list),
            'failed_predictions': len(errors),
            'predictions': predictions_list,
            'errors': errors if errors else None,
            'status': 'success' if len(errors) == 0 else 'partial_success'
        }
        
        logger.info(f"Batch prediction: {len(predictions_list)} successful, {len(errors)} failed")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({'error': f'Batch prediction failed: {str(e)}'}), 500


@app.route('/info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'model_name': 'PneumoNet AI',
        'model_type': 'MobileNetV2 (Transfer Learning)',
        'input_shape': (IMG_SIZE, IMG_SIZE, 3),
        'num_parameters': int(model.count_params()),
        'output_classes': ['NORMAL', 'PNEUMONIA'],
        'classification_threshold': THRESHOLD,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'status': 'ready'
    }), 200


@app.route('/threshold', methods=['GET', 'POST'])
def threshold_management():
    """Get or update the classification threshold"""
    global THRESHOLD
    
    if request.method == 'GET':
        return jsonify({
            'current_threshold': THRESHOLD,
            'description': 'Probability threshold for pneumonia classification'
        }), 200
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            new_threshold = data.get('threshold')
            
            if new_threshold is None:
                return jsonify({'error': 'threshold parameter required'}), 400
            
            if not isinstance(new_threshold, (int, float)) or not (0 <= new_threshold <= 1):
                return jsonify({'error': 'threshold must be a number between 0 and 1'}), 400
            
            THRESHOLD = new_threshold
            logger.info(f"Threshold updated to {THRESHOLD}")
            
            return jsonify({
                'status': 'success',
                'new_threshold': THRESHOLD,
                'message': 'Classification threshold updated'
            }), 200
            
        except Exception as e:
            logger.error(f"Error updating threshold: {str(e)}")
            return jsonify({'error': f'Failed to update threshold: {str(e)}'}), 500


@app.route('/', methods=['GET'])
def index():
    """API documentation and usage instructions"""
    return jsonify({
        'service': 'PneumoNet AI - Pneumonia Detection API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'This help message',
            'GET /health': 'Health check',
            'GET /info': 'Model information',
            'POST /predict': 'Single image prediction (multipart form or base64 JSON)',
            'POST /predict-batch': 'Batch image prediction',
            'GET /threshold': 'Get current classification threshold',
            'POST /threshold': 'Update classification threshold'
        },
        'usage': {
            'single_prediction_curl': 'curl -X POST -F "image=@image.jpg" http://localhost:5000/predict',
            'batch_prediction_curl': 'curl -X POST -F "images=@image1.jpg" -F "images=@image2.jpg" http://localhost:5000/predict-batch',
            'base64_prediction': 'POST /predict with JSON body: {"image": "base64_encoded_image_string"}'
        },
        'response_format': {
            'predicted_class': 'PNEUMONIA or NORMAL',
            'pneumonia_probability': 'Probability of pneumonia (0-1)',
            'normal_probability': 'Probability of normal chest (0-1)',
            'confidence': 'Confidence percentage of prediction'
        }
    }), 200


@app.route('/api/test-images', methods=['GET'])
def get_test_images():
    """Get list of available test images"""
    try:
        test_images_dir = 'test_images'
        if not os.path.exists(test_images_dir):
            return jsonify({'images': []}), 200
        
        images = [f for f in os.listdir(test_images_dir) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        images.sort()
        
        return jsonify({'images': images}), 200
    except Exception as e:
        logger.error(f"Error listing test images: {e}")
        return jsonify({'images': []}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    if model is None:
        logger.warning("Model not loaded. Check if pneumonia_model.keras exists.")
    
    # Run Flask app
    # For production, use gunicorn: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    app.run(debug=True, host='0.0.0.0', port=5000)
