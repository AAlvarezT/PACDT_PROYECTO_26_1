"""
Face processing module for regression analysis
Handles face detection, cropping, and preprocessing using MTCNN
"""

import numpy as np
import pandas as pd
import torch
import json
import base64
import pickle
import cv2
from facenet_pytorch import MTCNN
from tqdm.auto import tqdm
from typing import List, Optional, Tuple, Union, Dict
import warnings

from .config import DEVICE, FACE_PROCESSING_CONFIG

warnings.filterwarnings('ignore')


class FaceProcessor:
    """
    Handles face detection and cropping using MTCNN
    Reproduces the original face processing logic with batch capabilities
    """
    
    def __init__(self):
        self.device = DEVICE
        self.mtcnn = None
        self.default_face_shape = FACE_PROCESSING_CONFIG['default_face_tensor_shape']
        self.batch_size = FACE_PROCESSING_CONFIG['batch_size_face_processing']
        self._initialize_mtcnn()
    
    def _initialize_mtcnn(self):
        """Initialize MTCNN face detector"""
        print(f"Initializing MTCNN face detector on {self.device}...")
        
        # Reproduce original: MTCNN(image_size=160, margin=20, device=device, post_process=True)
        self.mtcnn = MTCNN(
            image_size=FACE_PROCESSING_CONFIG['mtcnn_params']['image_size'],
            margin=FACE_PROCESSING_CONFIG['mtcnn_params']['margin'],
            device=self.device,
            post_process=FACE_PROCESSING_CONFIG['mtcnn_params']['post_process']
        )
        
        print("MTCNN face detector initialized successfully")
    
    def crop_single_face(self, serialized_image: str) -> torch.Tensor:
        """
        Extract and crop face from a single serialized image
        
        Args:
            serialized_image: JSON string containing serialized image data
            
        Returns:
            Cropped face tensor or default tensor if no face detected
        """
        try:
            if pd.isna(serialized_image) or not serialized_image:
                return torch.zeros(self.default_face_shape)
            
            # Parse JSON to get base64 string
            try:
                if isinstance(serialized_image, str) and serialized_image.strip().startswith('{'):
                    image_json = json.loads(serialized_image)
                    if 'image' in image_json:
                        base64_str = image_json['image']
                    else:
                        print("Warning: 'image' key not found in JSON")
                        return torch.zeros(self.default_face_shape)
                else:
                    # Assume it's directly the base64 string
                    base64_str = serialized_image
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Warning: Failed to parse JSON: {e}")
                return torch.zeros(self.default_face_shape)
            
            # Decode using pickle + base64 method (same as clustering code)
            image_array = self._decode_image_from_serialized_base64(base64_str)
            
            if image_array is None:
                return torch.zeros(self.default_face_shape)
            
            # Reproduce original: f=mtcnn(arr)
            cropped_face = self.mtcnn(image_array)
            
            # Reproduce original: return f if f is not None else torch.zeros(3,160,160)
            if cropped_face is not None:
                return cropped_face
            else:
                return torch.zeros(self.default_face_shape)
                
        except Exception as e:
            # Return default tensor if any error occurs
            print(f"Warning: Error processing image - {e}")
            return torch.zeros(self.default_face_shape)
    
    def _decode_image_from_serialized_base64(self, base64_str: str) -> np.ndarray:
        """
        Decode image from serialized base64 using pickle (exact same method as clustering)
        
        Args:
            base64_str: Base64 encoded string containing pickled numpy array
            
        Returns:
            RGB numpy array or None if failed
        """
        try:
            # Decode the base64 string to get the serialized data
            serialized_data = base64.b64decode(base64_str)
            
            # Deserialize the data using pickle to get the numpy array
            numpy_array = pickle.loads(serialized_data)
            
            # Convert the numpy array to an image using OpenCV
            img_rgb = cv2.cvtColor(numpy_array, cv2.COLOR_BGR2RGB)
            
            return img_rgb
            
        except Exception as e:
            print(f"Warning: Error decoding or converting image: {e}")
            return None
    
    def batch_crop_faces(self, indices: List[int], df: pd.DataFrame, 
                        image_column: str = 'serialized_image') -> torch.Tensor:
        """
        Crop faces from a batch of images specified by indices
        
        Args:
            indices: List of DataFrame indices to process
            df: DataFrame containing serialized images
            image_column: Name of column containing serialized images
            
        Returns:
            Stacked tensor of cropped faces
        """
        print(f"Processing {len(indices)} images for face extraction...")
        
        # Reproduce original: [crop(df.loc[i,'photo_matrix']) for i in tqdm(idxs,"↳ faces")]
        cropped_faces = []
        
        for idx in tqdm(indices, desc="↳ Extracting faces"):
            try:
                serialized_image = df.loc[idx, image_column]
                cropped_face = self.crop_single_face(serialized_image)
                cropped_faces.append(cropped_face)
            except Exception as e:
                print(f"Error processing image at index {idx}: {e}")
                cropped_faces.append(torch.zeros(self.default_face_shape))
        
        # Reproduce original: torch.stack([...])
        face_tensor_batch = torch.stack(cropped_faces)
        
        print(f"Face extraction complete. Output shape: {face_tensor_batch.shape}")
        
        return face_tensor_batch
    
    def process_dataframe_faces(self, df: pd.DataFrame, 
                               train_indices: np.ndarray, test_indices: np.ndarray,
                               image_column: str = 'serialized_image') -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Process faces for train and test splits
        
        Args:
            df: DataFrame containing image data
            train_indices: Indices for training set
            test_indices: Indices for test set
            image_column: Name of column containing serialized images
            
        Returns:
            Tuple of (train_faces, test_faces) tensors
        """
        print("=== Starting Face Processing ===")
        
        # Process training faces (reproduce original: F_tr = batch_crop(idx_tr))
        print("Processing training set faces...")
        train_faces = self.batch_crop_faces(train_indices.tolist(), df, image_column)
        
        # Process test faces (reproduce original: F_te = batch_crop(idx_te))
        print("Processing test set faces...")
        test_faces = self.batch_crop_faces(test_indices.tolist(), df, image_column)
        
        print("=== Face Processing Complete ===")
        print(f"Training faces shape: {train_faces.shape}")
        print(f"Test faces shape: {test_faces.shape}")
        
        return train_faces, test_faces
    
    def validate_face_tensors(self, face_tensors: torch.Tensor) -> Dict[str, any]:
        """
        Validate face tensor quality and characteristics
        
        Args:
            face_tensors: Tensor of face images
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {}
        
        # Basic tensor properties
        validation_results['tensor_info'] = {
            'shape': list(face_tensors.shape),
            'dtype': str(face_tensors.dtype),
            'device': str(face_tensors.device),
            'memory_usage_mb': face_tensors.numel() * face_tensors.element_size() / (1024 * 1024)
        }
        
        # Check for valid face detections (non-zero tensors)
        zero_faces = torch.all(face_tensors.view(face_tensors.shape[0], -1) == 0, dim=1)
        valid_faces = ~zero_faces
        
        validation_results['face_detection'] = {
            'total_images': len(face_tensors),
            'valid_faces': valid_faces.sum().item(),
            'failed_detections': zero_faces.sum().item(),
            'success_rate': (valid_faces.sum().item() / len(face_tensors)) * 100
        }
        
        # Statistical properties of valid faces
        if valid_faces.any():
            valid_face_tensors = face_tensors[valid_faces]
            validation_results['valid_faces_stats'] = {
                'mean_pixel_value': valid_face_tensors.mean().item(),
                'std_pixel_value': valid_face_tensors.std().item(),
                'min_pixel_value': valid_face_tensors.min().item(),
                'max_pixel_value': valid_face_tensors.max().item()
            }
        else:
            validation_results['valid_faces_stats'] = {
                'message': 'No valid faces detected'
            }
        
        # Check for unusual patterns
        validation_results['quality_checks'] = {
            'all_same_tensor': torch.all(face_tensors[0:1] == face_tensors, dim=(1,2,3)).sum().item() > 1,
            'contains_nan': torch.isnan(face_tensors).any().item(),
            'contains_inf': torch.isinf(face_tensors).any().item()
        }
        
        return validation_results
    
    def save_face_samples(self, face_tensors: torch.Tensor, output_dir: str, 
                         num_samples: int = 10) -> None:
        """
        Save sample face images for visual inspection
        
        Args:
            face_tensors: Tensor of face images
            output_dir: Directory to save samples
            num_samples: Number of sample faces to save
        """
        try:
            import os
            import torchvision.utils as vutils
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Select random samples
            indices = torch.randperm(len(face_tensors))[:num_samples]
            sample_faces = face_tensors[indices]
            
            # Save as grid
            grid_path = os.path.join(output_dir, 'face_samples_grid.png')
            vutils.save_image(sample_faces, grid_path, nrow=5, normalize=True)
            
            # Save individual samples
            for i, face_tensor in enumerate(sample_faces):
                individual_path = os.path.join(output_dir, f'face_sample_{i:02d}.png')
                vutils.save_image(face_tensor, individual_path, normalize=True)
            
            print(f"Saved {num_samples} face samples to: {output_dir}")
            
        except Exception as e:
            print(f"Error saving face samples: {e}")
    
    def get_processing_summary(self, train_faces: torch.Tensor, 
                              test_faces: torch.Tensor) -> Dict[str, any]:
        """
        Get comprehensive summary of face processing results
        
        Args:
            train_faces: Training face tensors
            test_faces: Test face tensors
            
        Returns:
            Dictionary with processing summary
        """
        summary = {
            'processing_config': FACE_PROCESSING_CONFIG,
            'train_validation': self.validate_face_tensors(train_faces),
            'test_validation': self.validate_face_tensors(test_faces)
        }
        
        # Overall statistics
        total_faces = len(train_faces) + len(test_faces)
        total_valid = (summary['train_validation']['face_detection']['valid_faces'] + 
                      summary['test_validation']['face_detection']['valid_faces'])
        
        summary['overall_stats'] = {
            'total_images_processed': total_faces,
            'total_valid_faces': total_valid,
            'overall_success_rate': (total_valid / total_faces) * 100 if total_faces > 0 else 0,
            'train_success_rate': summary['train_validation']['face_detection']['success_rate'],
            'test_success_rate': summary['test_validation']['face_detection']['success_rate']
        }
        
        return summary


def optimize_face_processing_memory():
    """Optimize memory usage for face processing operations"""
    import gc
    
    # Clear GPU cache if using CUDA
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # Run garbage collection
    gc.collect()
    
    print("Face processing memory optimization complete")


def check_mtcnn_requirements():
    """Check if MTCNN requirements are met"""
    try:
        from facenet_pytorch import MTCNN
        print("✓ facenet-pytorch is available")
        
        # Test MTCNN initialization
        test_mtcnn = MTCNN(image_size=32, device='cpu')
        print("✓ MTCNN can be initialized")
        
        return True
        
    except ImportError as e:
        print(f"✗ facenet-pytorch not available: {e}")
        print("Install with: pip install facenet-pytorch")
        return False
    except Exception as e:
        print(f"✗ MTCNN initialization failed: {e}")
        return False
