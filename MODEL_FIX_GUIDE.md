# Model Fix Guide - PneumoNet AI

## Issue

The pre-trained `pneumonia_model.keras` was created with TensorFlow 2.13.0, but the API is now using TensorFlow 2.20.0. Due to internal compatibility changes in Keras, the model might fail to load directly.

## Solution

There are **three options** to fix this:

### Option 1: Retrain the Model (Recommended)

This ensures you get a model fully compatible with TensorFlow 2.20.0:

```bash
# 1. Run the training notebook
jupyter notebook pneumonia_detection.ipynb

# Or in VS Code:
# - Open pneumonia_detection.ipynb
# - Click "Run All" or run cells sequentially
# - The notebook will automatically save a compatible model
```

The training notebook will:
- Download the chest X-ray dataset from Kaggle
- Train the model with MobileNetV2 transfer learning
- Save the model as `pneumonia_model.keras` (compatible with TensorFlow 2.20.0)

**Time needed:** 30-60 minutes (depending on hardware)

**Kaggle Setup:** You'll need a Kaggle account API key. Get one from [https://www.kaggle.com/settings/account](https://www.kaggle.com/settings/account)

---

### Option 2: Convert the Model (Quick Fix)

If you want to keep the existing model, convert it to a format compatible with the new TensorFlow version:

```python
import tensorflow as tf

# Load the old model without compiling
old_model = tf.keras.models.load_model('pneumonia_model.keras', compile=False)

# Recompile it
old_model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Save in the new format
old_model.save('pneumonia_model.keras')

print("✓ Model converted and saved!")
```

**Time needed:** 5 minutes

---

### Option 3: Use the API as a Framework (Development)

The Flask API is fully functional - it just needs a trained model. You can:

1. Use the API for testing and development
2. Train your own custom model
3. Replace `pneumonia_model.keras` with your trained model

All API endpoints will work once a compatible model is in place.

---

## Next Steps

1. **Choose one option above**
2. **Re-train or convert the model**
3. **Restart the API:** `python app.py`
4. **Test the API:** `python test_api.py`

## Verification

After fixing the model, test it:

```bash
# 1. Start the API
python app.py

# 2. In another terminal, check if model loaded
curl http://localhost:5000/info

# 3. Should see model info like:
# {
#   "model_name": "PneumoNet AI",
#   "status": "ready"
# }
```

## API Status While Model Missing

Even without a compatible model, the API provides:
- ✅ Health checks (`/health`)
- ✅ API documentation (`/`)
- ✅ Error messages with solutions (`/predict`, `/info`)
- ✅ Ready for custom models or retraining

Once a compatible model is in place, all prediction endpoints become active:
- ✅ Single image prediction (`/predict`)
- ✅ Batch prediction (`/predict-batch`)
- ✅ Model information (`/info`)
- ✅ Threshold management (`/threshold`)

---

## Requirements

- **For Option 1 (Retrain):**
  - Kaggle account with API key
  - Internet connection to download data
  - 30-60 minutes
  - ~2GB storage for dataset

- **For Option 2 (Convert):**
  - 5 minutes
  - No internet needed

- **For Option 3 (Framework):**
  - Existing trained model file or train your own

---

## Troubleshooting

### Still getting model not loaded error?

1. Verify file exists:
   ```bash
   ls -la pneumonia_model.keras
   ```

2. Check file is not corrupted (should be 15-25MB):
   ```bash
   file pneumonia_model.keras
   ```

3. Try Option 2 (Convert) if file exists

4. Use Option 1 (Retrain) if conversion fails

### Kaggle API issues?

1. Download API token from Kaggle account settings
2. Place in `~/.kaggle/kaggle.json`
3. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`
4. Install kagglehub: `pip install kagglehub`

---

**Ready to fix the model? Choose an option above and start!**
