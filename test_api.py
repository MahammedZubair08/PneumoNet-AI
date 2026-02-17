"""
Test script for the PneumoNet AI Flask API
Provides functions to test the API endpoints with sample images
"""

import requests
import json
import sys
from pathlib import Path
import base64
from PIL import Image
import io


class PneumoNetAPITester:
    """Test client for PneumoNet AI API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the API tester
        
        Args:
            base_url: Base URL of the Flask API
        """
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> dict:
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return {'status': 'success', 'data': response.json()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_model_info(self) -> dict:
        """Get model information"""
        try:
            response = self.session.get(f"{self.base_url}/info")
            response.raise_for_status()
            return {'status': 'success', 'data': response.json()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def predict_image_file(self, image_path: str) -> dict:
        """
        Predict for a single image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Prediction results
        """
        try:
            if not Path(image_path).exists():
                return {'status': 'error', 'message': f'File not found: {image_path}'}
            
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = self.session.post(f"{self.base_url}/predict", files=files)
            
            response.raise_for_status()
            return {'status': 'success', 'data': response.json()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def predict_image_base64(self, image_path: str) -> dict:
        """
        Predict for a single image using base64 encoding
        
        Args:
            image_path: Path to image file
            
        Returns:
            Prediction results
        """
        try:
            if not Path(image_path).exists():
                return {'status': 'error', 'message': f'File not found: {image_path}'}
            
            with open(image_path, 'rb') as f:
                image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            payload = {'image': image_base64}
            response = self.session.post(
                f"{self.base_url}/predict",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            return {'status': 'success', 'data': response.json()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def predict_batch_images(self, image_paths: list) -> dict:
        """
        Predict for multiple images
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            Prediction results for all images
        """
        try:
            files = []
            for image_path in image_paths:
                if not Path(image_path).exists():
                    return {'status': 'error', 'message': f'File not found: {image_path}'}
                files.append(('images', open(image_path, 'rb')))
            
            response = self.session.post(f"{self.base_url}/predict-batch", files=files)
            
            # Close all files
            for _, file_obj in files:
                file_obj.close()
            
            response.raise_for_status()
            return {'status': 'success', 'data': response.json()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_threshold(self) -> dict:
        """Get current classification threshold"""
        try:
            response = self.session.get(f"{self.base_url}/threshold")
            response.raise_for_status()
            return {'status': 'success', 'data': response.json()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def update_threshold(self, threshold: float) -> dict:
        """
        Update classification threshold
        
        Args:
            threshold: New threshold value (0-1)
            
        Returns:
            Update status
        """
        try:
            payload = {'threshold': threshold}
            response = self.session.post(
                f"{self.base_url}/threshold",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return {'status': 'success', 'data': response.json()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def create_test_image(self, filename: str = "test_image.jpg", 
                         size: tuple = (224, 224)) -> str:
        """
        Create a test image for API testing
        
        Args:
            filename: Output filename
            size: Image size as (width, height)
            
        Returns:
            Path to created test image
        """
        try:
            # Create a simple test image (gradient)
            import numpy as np
            
            width, height = size
            image_array = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Create a gradient pattern
            for i in range(height):
                image_array[i, :, 0] = int((i / height) * 255)  # Red gradient
                image_array[i, :, 1] = int(((height - i) / height) * 255)  # Green inverse
            
            image = Image.fromarray(image_array)
            image.save(filename)
            return filename
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None


def print_result(title: str, result: dict):
    """Pretty print test result"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(json.dumps(result, indent=2))


def run_tests(base_url: str = "http://localhost:5000", test_image: str = None):
    """
    Run comprehensive API tests
    
    Args:
        base_url: Base URL of the API
        test_image: Path to test image (optional)
    """
    tester = PneumoNetAPITester(base_url)
    
    print("\n" + "="*60)
    print("PneumoNet AI - API Test Suite")
    print("="*60)
    
    # Test 1: Health check
    print("\n[Test 1] Health Check")
    result = tester.health_check()
    print_result("Health Check", result)
    
    if result['status'] != 'success':
        print("\n❌ API is not running! Start the Flask app first:")
        print("   python app.py")
        return
    
    # Test 2: Model info
    print("\n[Test 2] Model Information")
    result = tester.get_model_info()
    print_result("Model Info", result)
    
    # Test 3: Get current threshold
    print("\n[Test 3] Get Current Threshold")
    result = tester.get_threshold()
    print_result("Current Threshold", result)
    
    # Test 4: Update threshold
    print("\n[Test 4] Update Threshold to 0.45")
    result = tester.update_threshold(0.45)
    print_result("Update Threshold", result)
    
    # Test 5: Reset threshold
    print("\n[Test 5] Reset Threshold to 0.5")
    result = tester.update_threshold(0.5)
    print_result("Reset Threshold", result)
    
    # Test 6: Create and predict on test image
    if test_image is None:
        print("\n[Test 6] Creating test image...")
        test_image = tester.create_test_image()
        print(f"Test image created: {test_image}")
    
    if test_image:
        print("\n[Test 7] Single Image Prediction (File Upload)")
        result = tester.predict_image_file(test_image)
        print_result("Single Image Prediction", result)
        
        print("\n[Test 8] Single Image Prediction (Base64)")
        result = tester.predict_image_base64(test_image)
        print_result("Base64 Image Prediction", result)
        
        print("\n[Test 9] Batch Image Prediction")
        result = tester.predict_batch_images([test_image, test_image])
        print_result("Batch Prediction", result)
    
    print("\n" + "="*60)
    print("✅ Test Suite Completed")
    print("="*60)


if __name__ == '__main__':
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    test_image = sys.argv[2] if len(sys.argv) > 2 else None
    
    run_tests(base_url, test_image)
