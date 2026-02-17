"""
PneumoNet AI Client Library
Simple Python client for interacting with the PneumoNet AI Flask API
"""

import requests
import base64
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import json


class PneumoNetClient:
    """
    Client for PneumoNet AI Pneumonia Detection API
    
    Usage:
        client = PneumoNetClient('http://localhost:5000')
        result = client.predict_image('chest_xray.jpg')
        print(result)
    """
    
    def __init__(self, api_url: str = "http://localhost:5000", timeout: int = 30):
        """
        Initialize the API client
        
        Args:
            api_url: Base URL of the PneumoNet AI API
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def __repr__(self) -> str:
        return f"PneumoNetClient(url='{self.api_url}')"
    
    def health_check(self) -> bool:
        """
        Check if API is healthy and responsive
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.api_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        try:
            response = self.session.get(
                f"{self.api_url}/info",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get model info: {e}")
    
    def predict_image(self, image_path: str, use_base64: bool = False) -> Dict:
        """
        Predict pneumonia for a single image
        
        Args:
            image_path: Path to image file
            use_base64: If True, send image as base64. If False, use file upload.
            
        Returns:
            Prediction results with confidence scores
            
        Example:
            result = client.predict_image('chest_xray.jpg')
            print(f"Prediction: {result['prediction']['predicted_class']}")
            print(f"Confidence: {result['prediction']['confidence']}%")
        """
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            if use_base64:
                return self._predict_base64(image_path)
            else:
                return self._predict_file_upload(image_path)
        except Exception as e:
            raise Exception(f"Prediction failed: {e}")
    
    def _predict_file_upload(self, image_path: Path) -> Dict:
        """Predict using file upload (multipart form data)"""
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = self.session.post(
                f"{self.api_url}/predict",
                files=files,
                timeout=self.timeout
            )
        
        response.raise_for_status()
        return response.json()
    
    def _predict_base64(self, image_path: Path) -> Dict:
        """Predict using base64 encoded image"""
        with open(image_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {'image': image_base64}
        response = self.session.post(
            f"{self.api_url}/predict",
            json=payload,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def predict_batch(self, image_paths: List[str]) -> Dict:
        """
        Predict for multiple images in one request
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            Batch prediction results
            
        Example:
            results = client.predict_batch(['image1.jpg', 'image2.jpg', 'image3.jpg'])
            for pred in results['predictions']:
                print(f"{pred['filename']}: {pred['predicted_class']}")
        """
        try:
            files = []
            for image_path in image_paths:
                path = Path(image_path)
                if not path.exists():
                    raise FileNotFoundError(f"Image file not found: {path}")
                files.append(('images', open(path, 'rb')))
            
            response = self.session.post(
                f"{self.api_url}/predict-batch",
                files=files,
                timeout=self.timeout
            )
            
            # Close files
            for _, file_obj in files:
                file_obj.close()
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Batch prediction failed: {e}")
    
    def get_threshold(self) -> float:
        """
        Get current classification threshold
        
        Returns:
            Current threshold value (0-1)
        """
        try:
            response = self.session.get(
                f"{self.api_url}/threshold",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()['current_threshold']
        except Exception as e:
            raise Exception(f"Failed to get threshold: {e}")
    
    def set_threshold(self, threshold: float) -> bool:
        """
        Update the classification threshold
        
        Args:
            threshold: New threshold value (0-1)
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If threshold is not between 0 and 1
            
        Example:
            client.set_threshold(0.45)  # Lower threshold for higher sensitivity
        """
        if not (0 <= threshold <= 1):
            raise ValueError("Threshold must be between 0 and 1")
        
        try:
            payload = {'threshold': threshold}
            response = self.session.post(
                f"{self.api_url}/threshold",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.status_code == 200
        except Exception as e:
            raise Exception(f"Failed to update threshold: {e}")
    
    def predict_and_display(self, image_path: str) -> None:
        """
        Predict for an image and display results in a formatted way
        
        Args:
            image_path: Path to image file
        """
        print(f"\nPredicting for: {image_path}")
        print("-" * 60)
        
        result = self.predict_image(image_path)
        pred = result['prediction']
        
        print(f"Result: {pred['predicted_class']}")
        print(f"Confidence: {pred['confidence']}%")
        print(f"Pneumonia Probability: {pred['pneumonia_probability']:.2%}")
        print(f"Normal Probability: {pred['normal_probability']:.2%}")
        print(f"Threshold Used: {pred['threshold_used']}")
        print(f"Timestamp: {result['timestamp']}")
        print("-" * 60)
    
    def predict_batch_and_display(self, image_paths: List[str]) -> None:
        """
        Predict for multiple images and display results
        
        Args:
            image_paths: List of paths to image files
        """
        print(f"\nPredicting for {len(image_paths)} images...")
        print("=" * 60)
        
        result = self.predict_batch(image_paths)
        
        print(f"Total Images: {result['total_images']}")
        print(f"Successful: {result['successful_predictions']}")
        print(f"Failed: {result['failed_predictions']}")
        print("=" * 60)
        
        for idx, pred in enumerate(result['predictions'], 1):
            print(f"\n[{idx}] {pred['filename']}")
            print(f"    Result: {pred['predicted_class']}")
            print(f"    Confidence: {pred['confidence']}%")


# Convenience functions
def predict_image(api_url: str, image_path: str) -> Dict:
    """Quick prediction for a single image"""
    client = PneumoNetClient(api_url)
    return client.predict_image(image_path)


def predict_batch(api_url: str, image_paths: List[str]) -> Dict:
    """Quick batch prediction"""
    client = PneumoNetClient(api_url)
    return client.predict_batch(image_paths)


def check_api(api_url: str) -> bool:
    """Quick API health check"""
    client = PneumoNetClient(api_url)
    return client.health_check()


# Example usage and CLI
if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='PneumoNet AI Client - Pneumonia Detection API Client'
    )
    parser.add_argument(
        '--url',
        default='http://localhost:5000',
        help='API base URL (default: http://localhost:5000)'
    )
    parser.add_argument(
        '--health',
        action='store_true',
        help='Check API health'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='Get model information'
    )
    parser.add_argument(
        '--predict',
        type=str,
        help='Predict for single image'
    )
    parser.add_argument(
        '--batch',
        nargs='+',
        help='Predict for multiple images'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        help='Get or set classification threshold'
    )
    parser.add_argument(
        '--set-threshold',
        type=float,
        help='Set new threshold value'
    )
    
    args = parser.parse_args()
    
    client = PneumoNetClient(args.url)
    
    try:
        if args.health:
            is_healthy = client.health_check()
            print(f"API Health: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
        
        elif args.info:
            info = client.get_model_info()
            print(json.dumps(info, indent=2))
        
        elif args.predict:
            client.predict_and_display(args.predict)
        
        elif args.batch:
            client.predict_batch_and_display(args.batch)
        
        elif args.threshold:
            threshold = client.get_threshold()
            print(f"Current Threshold: {threshold}")
        
        elif args.set_threshold:
            client.set_threshold(args.set_threshold)
            print(f"Threshold updated to: {args.set_threshold}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
