# PneumoNet AI - Pneumonia Detection API

A Flask-based REST API for pneumonia detection from chest X-ray images using a trained MobileNetV2 deep learning model.

## Features

- **Single Image Prediction**: Upload individual X-ray images for pneumonia detection
- **Batch Processing**: Process multiple images in a single request
- **Base64 Support**: Send images as base64-encoded strings in JSON
- **Adjustable Threshold**: Dynamically adjust the classification threshold
- **Model Information**: Query model architecture and capabilities
- **Comprehensive Logging**: Track all predictions and API activity
- **Error Handling**: Detailed error messages and validation

## Project Structure

```
PneumoNet-AI/
├── app.py                      # Main Flask application
├── utils.py                    # Utility functions for image processing
├── test_api.py                 # API testing script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
├── pneumonia_model.keras      # Pre-trained model file
├── pneumonia_detection.ipynb  # Model training notebook
├── uploads/                   # Directory for uploaded images (auto-created)
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Virtual environment manager (venv, conda, etc.)

### Setup Steps

1. **Clone the repository** (if applicable)
   ```bash
   cd PneumoNet-AI
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify the model file exists**
   ```bash
   ls -la pneumonia_model.keras
   ```

5. **Run the Flask application**
   ```bash
   python app.py
   ```

   The API will start at `http://localhost:5000`

## API Endpoints

### 1. Health Check
**Endpoint:** `GET /health`

Check if the API is running and model is loaded.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-02-17T10:30:45.123456",
  "model_loaded": true
}
```

---

### 2. Model Information
**Endpoint:** `GET /info`

Get details about the loaded model.

**Response:**
```json
{
  "model_name": "PneumoNet AI",
  "model_type": "MobileNetV2 (Transfer Learning)",
  "input_shape": [224, 224, 3],
  "num_parameters": 2259138,
  "output_classes": ["NORMAL", "PNEUMONIA"],
  "classification_threshold": 0.5,
  "supported_formats": ["png", "jpg", "jpeg", "gif", "bmp"],
  "status": "ready"
}
```

---

### 3. Single Image Prediction
**Endpoint:** `POST /predict`

Predict pneumonia for a single image.

#### Method 1: File Upload (Multipart Form Data)

**Usage:**
```bash
curl -X POST -F "image=@path/to/image.jpg" http://localhost:5000/predict
```

**Using Python:**
```python
import requests

with open('chest_xray.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/predict', files=files)
    print(response.json())
```

#### Method 2: Base64 JSON

**Usage:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_string"}'
```

**Using Python:**
```python
import requests
import base64

with open('chest_xray.jpg', 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

payload = {'image': image_base64}
response = requests.post('http://localhost:5000/predict', json=payload)
print(response.json())
```

**Response:**
```json
{
  "timestamp": "2024-02-17T10:30:45.123456",
  "filename": "image.jpg",
  "prediction": {
    "pneumonia_probability": 0.8234,
    "normal_probability": 0.1766,
    "predicted_class": "PNEUMONIA",
    "confidence": 82.34,
    "threshold_used": 0.5
  },
  "status": "success"
}
```

**Response Fields:**
- `predicted_class`: Either "PNEUMONIA" or "NORMAL"
- `pneumonia_probability`: Probability of pneumonia (0-1)
- `normal_probability`: Probability of normal chest (0-1)
- `confidence`: Confidence percentage of the prediction
- `threshold_used`: Classification threshold used

---

### 4. Batch Image Prediction
**Endpoint:** `POST /predict-batch`

Predict for multiple images in a single request.

**Usage:**
```bash
curl -X POST -F "images=@image1.jpg" -F "images=@image2.jpg" -F "images=@image3.jpg" \
  http://localhost:5000/predict-batch
```

**Using Python:**
```python
import requests

files = [
    ('images', open('image1.jpg', 'rb')),
    ('images', open('image2.jpg', 'rb')),
    ('images', open('image3.jpg', 'rb'))
]

response = requests.post('http://localhost:5000/predict-batch', files=files)
print(response.json())
```

**Response:**
```json
{
  "timestamp": "2024-02-17T10:30:45.123456",
  "total_images": 3,
  "successful_predictions": 3,
  "failed_predictions": 0,
  "predictions": [
    {
      "filename": "image1.jpg",
      "pneumonia_probability": 0.8234,
      "normal_probability": 0.1766,
      "predicted_class": "PNEUMONIA",
      "confidence": 82.34
    },
    {
      "filename": "image2.jpg",
      "pneumonia_probability": 0.2156,
      "normal_probability": 0.7844,
      "predicted_class": "NORMAL",
      "confidence": 78.44
    }
  ],
  "errors": null,
  "status": "success"
}
```

---

### 5. Get Classification Threshold
**Endpoint:** `GET /threshold`

Get the current classification threshold.

**Usage:**
```bash
curl http://localhost:5000/threshold
```

**Response:**
```json
{
  "current_threshold": 0.5,
  "description": "Probability threshold for pneumonia classification"
}
```

---

### 6. Update Classification Threshold
**Endpoint:** `POST /threshold`

Dynamically change the classification threshold.

**Usage:**
```bash
curl -X POST http://localhost:5000/threshold \
  -H "Content-Type: application/json" \
  -d '{"threshold": 0.45}'
```

**Using Python:**
```python
import requests

payload = {'threshold': 0.45}
response = requests.post('http://localhost:5000/threshold', json=payload)
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "new_threshold": 0.45,
  "message": "Classification threshold updated"
}
```

**Note:** 
- Threshold must be between 0 and 1
- Lower threshold → More predictions as PNEUMONIA (higher sensitivity)
- Higher threshold → More predictions as NORMAL (lower sensitivity)
- Medical context typically prefers lower thresholds to avoid missing pneumonia cases

---

### 7. API Documentation
**Endpoint:** `GET /`

Get API usage information and available endpoints.

**Response:**
```json
{
  "service": "PneumoNet AI - Pneumonia Detection API",
  "version": "1.0.0",
  "endpoints": { ... },
  "usage": { ... },
  "response_format": { ... }
}
```

---

## Testing

### Using the Test Script

Run the comprehensive test suite:

```bash
# Test with default API URL (http://localhost:5000)
python test_api.py

# Test with custom URL
python test_api.py http://your-api-url:port

# Test with specific image
python test_api.py http://localhost:5000 /path/to/test/image.jpg
```

The test script will:
1. Check API health
2. Retrieve model information
3. Test threshold management
4. Create a test image
5. Run single image prediction (both file and base64)
6. Run batch prediction

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:5000/health

# Model info
curl http://localhost:5000/info

# Single prediction
curl -X POST -F "image=@test.jpg" http://localhost:5000/predict

# Batch prediction
curl -X POST -F "images=@test1.jpg" -F "images=@test2.jpg" \
  http://localhost:5000/predict-batch

# Update threshold
curl -X POST http://localhost:5000/threshold \
  -H "Content-Type: application/json" \
  -d '{"threshold": 0.4}'
```

---

## Deployment

### Development Server

For testing and development:

```bash
python app.py
```

The app runs by default on `http://0.0.0.0:5000`

### Production Deployment with Gunicorn

For production environments, use Gunicorn (included in requirements.txt):

```bash
# Basic deployment (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With custom settings
gunicorn -w 8 -b 0.0.0.0:5000 --timeout 120 --access-logfile - app:app
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py utils.py .
COPY pneumonia_model.keras .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t pneumonet-api .
docker run -p 5000:5000 pneumonet-api
```

### Cloud Deployment

#### AWS EC2
1. Launch an Ubuntu instance
2. Install Python 3.8+
3. Clone repository and install dependencies
4. Run with Gunicorn
5. Use Nginx as reverse proxy
6. Configure security groups to allow port 5000

#### Heroku
1. Create `Procfile`:
   ```
   web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   ```
2. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

#### Google Cloud Run
1. Create `Dockerfile` (see Docker section)
2. Deploy:
   ```bash
   gcloud run deploy pneumonet-api --source . --platform managed --region us-central1 --allow-unauthenticated
   ```

---

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```
FLASK_ENV=production
FLASK_PORT=5000
MODEL_PATH=pneumonia_model.keras
CLASSIFICATION_THRESHOLD=0.5
MAX_CONTENT_LENGTH=16777216
LOG_LEVEL=INFO
```

Load in your app (optional enhancement):

```python
from dotenv import load_dotenv
load_dotenv()
```

### Adjusting Threshold

The classification threshold balances sensitivity vs. specificity:

- **Lower threshold (e.g., 0.3-0.4)**: Higher sensitivity, catches more pneumonia cases but may have false positives
- **Higher threshold (e.g., 0.6-0.7)**: Higher specificity, fewer false alarms but may miss pneumonia cases

For medical applications, lower thresholds are typically preferred to minimize false negatives (missed pneumonia cases).

---

## Performance Considerations

### Model Information
- **Model Size**: ~15-20 MB (Keras format)
- **Input Size**: 224×224×3 pixels
- **Inference Time**: ~100-300ms per image (CPU), ~50-100ms (GPU)
- **Memory Usage**: ~500MB-1GB baseline + model size

### Optimization Tips

1. **Use GPU**: Deploy on GPU-enabled hardware for faster inference
   ```bash
   # GPU deployment with TensorFlow
   # Set CUDA_VISIBLE_DEVICES environment variable
   export CUDA_VISIBLE_DEVICES=0
   gunicorn -w 4 app:app
   ```

2. **Batch Processing**: Use `/predict-batch` for multiple images for better throughput

3. **Caching**: Consider caching model in memory (already done in this implementation)

4. **Load Balancing**: Use multiple workers with Gunicorn or load balancer

---

## Troubleshooting

### Model Not Loading

**Error:** `Model not loaded`

**Solution:**
1. Verify `pneumonia_model.keras` exists in the same directory
2. Check file permissions: `chmod 644 pneumonia_model.keras`
3. Ensure TensorFlow is properly installed: `pip install --upgrade tensorflow`

### Image Validation Errors

**Error:** `Invalid file type`

**Solution:**
- Use supported formats: PNG, JPG, JPEG, GIF, BMP
- Convert image to PNG/JPG if needed: `convert image.bmp -format jpg image.jpg`

### Memory Issues

**Error:** Out of memory during prediction

**Solution:**
1. Use smaller batch sizes
2. Process images one at a time
3. Increase server memory
4. Use GPU acceleration

### Slow Predictions

**Solution:**
1. Enable GPU: `export CUDA_VISIBLE_DEVICES=0`
2. Increase Gunicorn workers: `gunicorn -w 8 app:app`
3. Use load balancer with multiple instances

---

## Model Details

### Architecture
- **Base Model**: MobileNetV2 (pre-trained on ImageNet)
- **Custom Layers**:
  - GlobalAveragePooling2D
  - Dense(128, relu) with Dropout(0.5)
  - Dense(1, sigmoid) for binary classification

### Training Details
- **Dataset**: Chest X-ray images
- **Training**: Transfer learning + fine-tuning
- **Classes**: Pneumonia (1) vs Normal (0)
- **Threshold**: 0.5 (adjustable)

### Performance Metrics
- Refer to `pneumonia_detection.ipynb` for detailed training metrics and evaluation

---

## API Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input or missing required fields |
| 404 | Not Found | Endpoint not found |
| 500 | Server Error | Internal server error or model loading failure |

---

## Contributing

To improve the API:

1. Modify `app.py` for API changes
2. Update `utils.py` for utility functions
3. Extend `test_api.py` for new test scenarios
4. Update this README with documentation

---

## License

This project is provided as-is for educational and medical research purposes.

---

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review logs in the console output
3. Examine `pneumonia_detection.ipynb` for model training details
4. Test with the provided `test_api.py` script

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the API
python app.py

# 3. In another terminal, run tests
python test_api.py

# 4. Or make predictions with curl
curl -X POST -F "image=@your_image.jpg" http://localhost:5000/predict
```

---

**Version:** 1.0.0  
**Last Updated:** February 2024  
**Model Type:** MobileNetV2 Transfer Learning  
**Input Resolution:** 224×224 pixels
