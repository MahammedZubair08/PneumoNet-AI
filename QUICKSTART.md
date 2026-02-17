# PneumoNet AI - Quick Start Guide

## 🚀 What's Included

A complete Flask-based REST API for pneumonia detection with comprehensive documentation and deployment options.

### Files Created

```
PneumoNet-AI/
├── app.py                    # Main Flask API application
├── utils.py                  # Image processing utilities
├── client.py                 # Python client library for the API
├── test_api.py              # Comprehensive API test suite
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker containerization
├── docker-compose.yml       # Docker Compose configuration
├── .env.example            # Environment configuration template
├── .gitignore              # Git ignore rules
├── README_API.md           # Detailed API documentation
├── DEPLOYMENT.md           # Comprehensive deployment guide
├── QUICKSTART.md           # This file
├── pneumonia_model.keras   # Pre-trained model (existing)
└── pneumonia_detection.ipynb # Model training notebook (existing)
```

---

## 📋 Prerequisites

- **Python 3.8+**: Install from python.org
- **TensorFlow/Keras**: For model loading and inference
- **Flask**: Web framework
- **(Optional) Docker**: For containerized deployment

---

## 🏁 Getting Started - 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the API

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### 3. Test the API

Open another terminal and run:

```bash
python test_api.py
```

Or test with curl:

```bash
curl http://localhost:5000/health
```

### 4. Make Your First Prediction

```bash
curl -X POST -F "image=@your_chest_xray.jpg" http://localhost:5000/predict
```

---

## 🔑 Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/info` | GET | Model information |
| `/predict` | POST | Single image prediction |
| `/predict-batch` | POST | Multiple images prediction |
| `/threshold` | GET/POST | Manage classification threshold |

---

## 🐍 Using the Python Client

```python
from client import PneumoNetClient

# Initialize client
client = PneumoNetClient('http://localhost:5000')

# Check API health
if client.health_check():
    print("API is healthy!")

# Predict single image
result = client.predict_image('chest_xray.jpg')
print(f"Prediction: {result['prediction']['predicted_class']}")
print(f"Confidence: {result['prediction']['confidence']}%")

# Predict batch
results = client.predict_batch(['image1.jpg', 'image2.jpg'])
for pred in results['predictions']:
    print(f"{pred['filename']}: {pred['predicted_class']}")

# Adjust threshold
client.set_threshold(0.45)  # Lower = higher sensitivity
```

---

## 📦 Docker Deployment

### Quick Docker Start

```bash
# Build image
docker build -t pneumonet-api .

# Run container
docker run -p 5000:5000 pneumonet-api

# Or with Docker Compose
docker-compose up -d
```

API will be available at `http://localhost:5000`

---

## ☁️ Cloud Deployment

### AWS EC2
```bash
# See DEPLOYMENT.md for full AWS guide
```

### Google Cloud Run
```bash
gcloud run deploy pneumonet-api --source . --platform managed
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

### DigitalOcean / Azure / Other
See `DEPLOYMENT.md` for detailed instructions.

---

## 🧪 Testing Endpoints

### Using Python Client CLI

```bash
# Health check
python client.py --health

# Model info
python client.py --info

# Predict image
python client.py --predict image.jpg

# Batch predict
python client.py --batch image1.jpg image2.jpg image3.jpg

# Get threshold
python client.py --threshold

# Set threshold
python client.py --set-threshold 0.45

# Custom API URL
python client.py --url http://your-api-url:5000 --predict image.jpg
```

### Using cURL

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
  -d '{"threshold": 0.45}'
```

### Using JavaScript/Fetch API

```javascript
// Single image prediction
const formData = new FormData();
formData.append('image', imageFile); // From file input

fetch('http://localhost:5000/predict', {
    method: 'POST',
    body: formData
})
.then(res => res.json())
.then(data => console.log(data));

// Or with base64
const reader = new FileReader();
reader.onload = function(e) {
    const base64 = e.target.result.split(',')[1];
    fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({image: base64})
    })
    .then(res => res.json())
    .then(data => console.log(data));
};
reader.readAsDataURL(imageFile);
```

---

## 📊 Response Format

### Successful Prediction
```json
{
  "timestamp": "2024-02-17T10:30:45.123456",
  "filename": "xray.jpg",
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

### Error Response
```json
{
  "error": "Error message describing what went wrong"
}
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` to customize:
- `FLASK_PORT`: Change API port (default: 5000)
- `CLASSIFICATION_THRESHOLD`: Default classification threshold
- `MODEL_PATH`: Path to model file
- `MAX_CONTENT_LENGTH`: Max upload file size

Load in Flask (optional enhancement):
```python
from dotenv import load_dotenv
import os
load_dotenv()
```

---

## 🎯 Understanding Predictions

### Classification Output
- **predicted_class**: "PNEUMONIA" or "NORMAL"
- **pneumonia_probability**: 0-1 (probability of pneumonia)
- **confidence**: Percentage of confidence in the prediction

### Medical Context
- **Lower threshold** (0.3-0.4): Higher sensitivity, better for screening
- **Higher threshold** (0.6-0.7): Higher specificity, better for confirmation
- **Default** (0.5): Balanced approach

### Example Interpretation
```
pneumonia_probability: 0.8234 (82.34%)
confidence: 82.34%

Interpretation: The model is 82.34% confident this is pneumonia
```

---

## 📚 Documentation

- **API Docs**: See `README_API.md` for complete endpoint documentation
- **Deployment Guide**: See `DEPLOYMENT.md` for all deployment options
- **Model Details**: See `pneumonia_detection.ipynb` for model training

---

## 🐛 Troubleshooting

### Model not loading
```bash
# Check if model file exists
ls -la pneumonia_model.keras

# Reinstall TensorFlow
pip install --upgrade tensorflow
```

### Port 5000 in use
```bash
# Use different port
python -c "
from app import app
app.run(port=8000)
"
```

### Image prediction fails
- Ensure image format is PNG, JPG, JPEG, GIF, or BMP
- Check image file is not corrupted
- Verify image size (should be at least 50x50 pixels)

### Docker issues
```bash
# Rebuild image
docker build --no-cache -t pneumonet-api .

# Check logs
docker logs pneumonet-api
```

---

## 📈 Performance

### Inference Time
- **CPU**: ~100-300ms per image
- **GPU**: ~50-100ms per image

### Model Size
- **File Size**: ~15-20 MB (Keras format)
- **Memory**: ~500MB-1GB baseline + model

### Optimization
- Use batch predictions for multiple images
- Deploy on GPU for faster inference
- Use Docker for consistent performance

---

## 🔐 Security Notes

### For Production
1. Enable HTTPS (use Nginx reverse proxy)
2. Add API authentication (API keys or OAuth)
3. Implement rate limiting
4. Use environment variables for sensitive data
5. Monitor and log all predictions
6. Regular security updates

---

## 📞 Support

1. **Check Logs**: Check console output for error details
2. **Test API**: Run `python test_api.py` to verify setup
3. **Review Documentation**: See `README_API.md` and `DEPLOYMENT.md`
4. **Model Training**: Refer to `pneumonia_detection.ipynb`

---

## 🚀 Next Steps

1. ✅ **Current**: Flask API ready to use
2. **Deploy**: Use one of the deployment guides in `DEPLOYMENT.md`
3. **Monitor**: Set up logging and monitoring
4. **Scale**: Use load balancer with multiple instances
5. **Integrate**: Connect to your application

---

## 📝 File Reference

| File | Purpose | Edit? |
|------|---------|-------|
| `app.py` | Main API application | ✏️ Customize endpoints |
| `utils.py` | Image processing | ✏️ Enhance functions |
| `client.py` | Python client library | ✏️ Extend as needed |
| `test_api.py` | Tests | ✏️ Add custom tests |
| `requirements.txt` | Dependencies | ✏️ Add packages |
| `.env.example` | Config template | ✏️ Create `.env` |
| `Dockerfile` | Docker setup | ✏️ Multi-stage build |
| `README_API.md` | API documentation | 📖 Reference |
| `DEPLOYMENT.md` | Deployment guide | 📖 Reference |

---

## 💡 Pro Tips

1. **Use batch predictions** for multiple images (more efficient)
2. **Adjust threshold** based on use case (sensitivity vs specificity)
3. **Cache predictions** for identical images
4. **Monitor inference time** for performance baseline
5. **Use GPU** if available for faster predictions
6. **Scale horizontally** with load balancer for high traffic

---

## 📦 Deployment Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify model exists: `ls pneumonia_model.keras`
- [ ] Test locally: `python app.py && python test_api.py`
- [ ] Create `.env` file: `cp .env.example .env`
- [ ] Choose deployment platform
- [ ] Follow deployment guide in `DEPLOYMENT.md`
- [ ] Set up monitoring/logging
- [ ] Test in production
- [ ] Document any customizations

---

## Version Info

- **API Version**: 1.0.0
- **Model**: MobileNetV2 (Transfer Learning)
- **Input Size**: 224×224×3 pixels
- **Classes**: Pneumonia, Normal
- **Created**: February 2024

---

**Ready to deploy?** Start with `python app.py` and check `DEPLOYMENT.md` for your target platform.
