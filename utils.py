"""
Utility functions for image processing and model predictions
"""

import numpy as np
from PIL import Image
import io
import base64
from typing import Tuple, Union


def load_image_from_path(image_path: str) -> Image.Image:
    """
    Load an image from file path
    
    Args:
        image_path: Path to the image file
        
    Returns:
        PIL Image object
    """
    return Image.open(image_path).convert('RGB')


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Load an image from bytes
    
    Args:
        image_bytes: Image data as bytes
        
    Returns:
        PIL Image object
    """
    return Image.open(io.BytesIO(image_bytes)).convert('RGB')


def load_image_from_base64(image_base64: str) -> Image.Image:
    """
    Load an image from base64 encoded string
    
    Args:
        image_base64: Base64 encoded image string
        
    Returns:
        PIL Image object
    """
    image_data = base64.b64decode(image_base64)
    return Image.open(io.BytesIO(image_data)).convert('RGB')


def image_to_base64(image: Image.Image) -> str:
    """
    Convert PIL Image to base64 string
    
    Args:
        image: PIL Image object
        
    Returns:
        Base64 encoded image string
    """
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()
    return base64.b64encode(image_bytes).decode('utf-8')


def resize_image(image: Image.Image, size: Tuple[int, int] = (224, 224)) -> Image.Image:
    """
    Resize image to specified dimensions
    
    Args:
        image: PIL Image object
        size: Target size as (width, height)
        
    Returns:
        Resized PIL Image
    """
    return image.resize(size, Image.Resampling.LANCZOS)


def normalize_image(image_array: np.ndarray) -> np.ndarray:
    """
    Normalize image array to 0-1 range
    
    Args:
        image_array: NumPy array with images
        
    Returns:
        Normalized NumPy array
    """
    return image_array.astype(np.float32) / 255.0


def prepare_image_for_model(image: Image.Image, size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    Prepare image for model prediction with all preprocessing steps
    
    Args:
        image: PIL Image object
        size: Target input size
        
    Returns:
        Preprocessed image array ready for prediction
    """
    # Resize
    image = resize_image(image, size)
    
    # Convert to array
    image_array = np.array(image, dtype=np.float32)
    
    # Normalize
    image_array = normalize_image(image_array)
    
    # Add batch dimension
    image_array = np.expand_dims(image_array, axis=0)
    
    return image_array


def format_prediction_response(prediction: float, threshold: float = 0.5, 
                              filename: str = "unknown") -> dict:
    """
    Format model prediction into a readable response
    
    Args:
        prediction: Raw prediction value from model
        threshold: Threshold for classification
        filename: Name of the input file
        
    Returns:
        Formatted prediction dictionary
    """
    confidence = float(prediction)
    is_pneumonia = confidence > threshold
    
    return {
        'filename': filename,
        'pneumonia_probability': round(confidence, 4),
        'normal_probability': round(1 - confidence, 4),
        'predicted_class': 'PNEUMONIA' if is_pneumonia else 'NORMAL',
        'confidence': round(max(confidence, 1 - confidence) * 100, 2),
        'threshold_used': threshold
    }


def validate_image(image: Image.Image, min_size: int = 50) -> Tuple[bool, str]:
    """
    Validate image for prediction
    
    Args:
        image: PIL Image object
        min_size: Minimum image dimension
        
    Returns:
        Tuple of (is_valid, message)
    """
    if image.width < min_size or image.height < min_size:
        return False, f"Image too small. Minimum size: {min_size}x{min_size}"
    
    return True, "Image valid"
