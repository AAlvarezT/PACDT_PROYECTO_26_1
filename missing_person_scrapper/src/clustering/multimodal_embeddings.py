"""
Multimodal embeddings module for clustering analysis
Handles image and text embedding extraction using deep learning models
"""

import numpy as np
import pandas as pd
import json
import base64
import pickle
import torch
import torch.nn as nn
from torchvision import models, transforms
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from typing import Tuple, List, Dict, Optional
import warnings
import cv2

from .config import (
    DEVICE, IMAGE_EMBEDDING_CONFIG, TEXT_EMBEDDING_CONFIG,
    TEXT_FEATURES, IMAGE_FEATURE
)


class ImageEmbeddingExtractor:
    """
    Extracts image embeddings using pre-trained ResNet50
    Reproduces the original ResNet50 embedding logic with correct image handling
    """
    
    def __init__(self):
        self.device = DEVICE
        self.model = None
        self.transform = None
        self.embedding_size = IMAGE_EMBEDDING_CONFIG['embedding_size']
        self._initialize_model()
        self._setup_transforms()
    
    def _initialize_model(self):
        """Initialize ResNet50 model for feature extraction"""
        print(f"Initializing ResNet50 on {self.device}...")
        
        # Reproduce original: models.resnet50(pretrained=True).to(device)
        resnet_model = models.resnet50(pretrained=IMAGE_EMBEDDING_CONFIG['pretrained']).to(self.device)
        
        # Reproduce original: nn.Sequential(*list(resnet.children())[:-1]).eval()
        self.model = nn.Sequential(*list(resnet_model.children())[:-1]).eval()
        
        print("ResNet50 model initialized successfully")
    
    def _setup_transforms(self):
        """Setup image transformations"""
        # Reproduce original transform pipeline
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(IMAGE_EMBEDDING_CONFIG['input_size']),
            transforms.ToTensor(),
            transforms.Normalize(
                IMAGE_EMBEDDING_CONFIG['normalization_mean'],
                IMAGE_EMBEDDING_CONFIG['normalization_std']
            )
        ])
        
        print("Image transforms setup complete")
    
    def _process_single_image(self, serialized_image_data: str) -> np.ndarray:
        """
        Process a single serialized image to extract embeddings
        
        Args:
            serialized_image_data: JSON string con imagen serializada (pickle + base64)
            
        Returns:
            Image embedding vector or zeros if processing fails
        """
        try:
            if pd.isna(serialized_image_data) or not serialized_image_data:
                # No image data available
                return np.zeros(self.embedding_size)
            
            # Parse JSON to get base64 string (como en el ejemplo del usuario)
            try:
                if isinstance(serialized_image_data, str) and serialized_image_data.strip().startswith('{'):
                    image_json = json.loads(serialized_image_data)
                    if 'image' in image_json:
                        base64_str = image_json['image']
                    else:
                        print("Warning: 'image' key not found in JSON")
                        return np.zeros(self.embedding_size)
                else:
                    # Assume it's directly the base64 string
                    base64_str = serialized_image_data
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Warning: Failed to parse JSON: {e}")
                return np.zeros(self.embedding_size)
            
            # Decode using the exact same method as the user's example
            image_array = self._decode_image_from_serialized_base64(base64_str)
            
            if image_array is None:
                return np.zeros(self.embedding_size)
            
            # Apply transforms (reproduce original: transform_img(arr).unsqueeze(0).to(device))
            image_tensor = self.transform(image_array).unsqueeze(0).to(self.device)
            
            # Extract features (reproduce original: resnet(img).squeeze().cpu().numpy())
            with torch.no_grad():
                embedding_vector = self.model(image_tensor).squeeze().cpu().numpy()
            
            return embedding_vector
            
        except Exception as e:
            # Reproduce original: return np.zeros(2048,)
            print(f"Warning: Failed to process image: {e}")
            return np.zeros(self.embedding_size)
    
    def _decode_image_from_serialized_base64(self, base64_str: str) -> np.ndarray:
        """
        Decode image from serialized base64 using pickle (exact copy of user's method)
        
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
    
    def extract_embeddings(self, df_subset: pd.DataFrame, image_column: str = IMAGE_FEATURE) -> np.ndarray:
        """
        Extract embeddings from a DataFrame with serialized images
        Reproduces the original embed_images function
        
        Args:
            df_subset: DataFrame containing serialized images
            image_column: Name of column containing serialized images
            
        Returns:
            Array of image embeddings
        """
        print(f"Extracting image embeddings from {len(df_subset)} samples...")
        
        if image_column not in df_subset.columns:
            print(f"Warning: {image_column} not found in DataFrame, using zeros")
            return np.zeros((len(df_subset), self.embedding_size))
        
        # Set up progress bar (reproduce original: tqdm.pandas)
        tqdm.pandas(desc="Processing Images")
        
        # Process images and extract embeddings
        embeddings_list = df_subset[image_column].progress_apply(self._process_single_image)
        
        # Stack embeddings (reproduce original: np.vstack(...))
        image_embeddings = np.vstack(embeddings_list.values)
        
        print(f"Image embeddings shape: {image_embeddings.shape}")
        
        return image_embeddings


class TextEmbeddingExtractor:
    """
    Extracts text embeddings using SentenceTransformer
    Reproduces the original text embedding logic with correct column names
    """
    
    def __init__(self):
        self.device = DEVICE
        self.model = None
        self.embedding_size = TEXT_EMBEDDING_CONFIG['embedding_size']
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize SentenceTransformer model"""
        print(f"Initializing SentenceTransformer on {self.device}...")
        
        # Reproduce original: SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)
        self.model = SentenceTransformer(
            TEXT_EMBEDDING_CONFIG['model_name'],
            device=self.device
        )
        
        print("SentenceTransformer model initialized successfully")
    
    def _combine_text_features(self, df_subset: pd.DataFrame) -> List[str]:
        """
        Combine multiple text columns into single text for embedding
        Reproduces the original text combination logic with correct column names
        
        Args:
            df_subset: DataFrame with text columns
            
        Returns:
            List of combined text strings
        """
        # Map actual column names from preprocessing to text features
        available_text_columns = {}
        for internal_name, actual_column in TEXT_FEATURES.items():
            if actual_column in df_subset.columns:
                available_text_columns[internal_name] = actual_column
            else:
                print(f"Warning: Text column '{actual_column}' not found in DataFrame")
        
        if not available_text_columns:
            print("Warning: No text columns found, using empty strings")
            return [''] * len(df_subset)
        
        # Reproduce original text combination logic:
        # texts = (df_subset['Vestimenta'].fillna('') + '. ' + ...)
        combined_texts = []
        
        for idx in range(len(df_subset)):
            text_parts = []
            
            for internal_name, actual_column in available_text_columns.items():
                text_value = df_subset.iloc[idx][actual_column]
                if pd.notna(text_value) and str(text_value).strip():
                    # Clean and prepare text
                    clean_text = str(text_value).strip()
                    if clean_text and clean_text.lower() not in ['nan', 'none', 'null', '']:
                        text_parts.append(clean_text)
            
            # Join with '. ' as in original
            combined_text = '. '.join(text_parts) if text_parts else ''
            combined_texts.append(combined_text)
        
        # Log some examples for debugging
        non_empty_texts = [t for t in combined_texts if t.strip()]
        if non_empty_texts:
            print(f"Sample combined texts (first 3):")
            for i, text in enumerate(non_empty_texts[:3]):
                print(f"  {i+1}: {text[:100]}{'...' if len(text) > 100 else ''}")
        else:
            print("Warning: All combined texts are empty")
        
        return combined_texts
    
    def extract_embeddings(self, df_subset: pd.DataFrame) -> np.ndarray:
        """
        Extract text embeddings from DataFrame
        Reproduces the original embed_texts function
        
        Args:
            df_subset: DataFrame containing text columns
            
        Returns:
            Array of text embeddings
        """
        print(f"Extracting text embeddings from {len(df_subset)} samples...")
        
        # Combine text features (reproduce original text combination)
        combined_texts = self._combine_text_features(df_subset)
        
        # Extract embeddings (reproduce original: model_text.encode(...))
        text_embeddings = self.model.encode(
            combined_texts,
            show_progress_bar=TEXT_EMBEDDING_CONFIG['show_progress'],
            convert_to_numpy=True
        )
        
        print(f"Text embeddings shape: {text_embeddings.shape}")
        
        return text_embeddings


class MultimodalEmbeddingExtractor:
    """
    Coordinates extraction of embeddings from multiple modalities
    Handles the complete multimodal embedding pipeline
    """
    
    def __init__(self):
        self.image_extractor = ImageEmbeddingExtractor()
        self.text_extractor = TextEmbeddingExtractor()
    
    def extract_all_embeddings(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """
        Extract embeddings from all modalities for train and test sets
        Reproduces the original embedding extraction workflow
        
        Args:
            train_df: Training DataFrame
            test_df: Test DataFrame
            
        Returns:
            Dictionary with embeddings for each modality
        """
        print("=== Starting Multimodal Embedding Extraction ===")
        
        embeddings = {}
        
        # Extract image embeddings (reproduce original image processing)
        print("\n1. Extracting image embeddings...")
        tqdm.pandas(desc="Embed Imágenes TRAIN")
        image_embeddings_train = self.image_extractor.extract_embeddings(train_df)
        
        tqdm.pandas(desc="Embed Imágenes TEST")
        image_embeddings_test = self.image_extractor.extract_embeddings(test_df)
        
        embeddings['image'] = (image_embeddings_train, image_embeddings_test)
        print(f"Image embeddings shapes: {image_embeddings_train.shape}, {image_embeddings_test.shape}")
        
        # Extract text embeddings (reproduce original text processing)
        print("\n2. Extracting text embeddings...")
        text_embeddings_train = self.text_extractor.extract_embeddings(train_df)
        text_embeddings_test = self.text_extractor.extract_embeddings(test_df)
        
        embeddings['text'] = (text_embeddings_train, text_embeddings_test)
        print(f"Text embeddings shapes: {text_embeddings_train.shape}, {text_embeddings_test.shape}")
        
        print("=== Multimodal Embedding Extraction Complete ===")
        
        return embeddings
    
    def validate_embeddings(self, embeddings: Dict[str, Tuple[np.ndarray, np.ndarray]]) -> Dict[str, Dict]:
        """
        Validate extracted embeddings
        
        Args:
            embeddings: Dictionary with embeddings for each modality
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {}
        
        for modality, (train_emb, test_emb) in embeddings.items():
            validation_results[modality] = {
                'train_shape': train_emb.shape,
                'test_shape': test_emb.shape,
                'train_has_nan': np.isnan(train_emb).any(),
                'test_has_nan': np.isnan(test_emb).any(),
                'train_has_inf': np.isinf(train_emb).any(),
                'test_has_inf': np.isinf(test_emb).any(),
                'train_mean': np.mean(train_emb),
                'test_mean': np.mean(test_emb),
                'train_std': np.std(train_emb),
                'test_std': np.std(test_emb),
                'train_zeros_percentage': np.mean(train_emb == 0) * 100,
                'test_zeros_percentage': np.mean(test_emb == 0) * 100
            }
        
        return validation_results
    
    def save_embeddings(self, embeddings: Dict[str, Tuple[np.ndarray, np.ndarray]], 
                       output_path: str) -> None:
        """
        Save embeddings to disk
        
        Args:
            embeddings: Dictionary with embeddings for each modality
            output_path: Path to save embeddings
        """
        try:
            # Prepare data for saving
            save_data = {}
            
            for modality, (train_emb, test_emb) in embeddings.items():
                save_data[f'{modality}_train'] = train_emb
                save_data[f'{modality}_test'] = test_emb
            
            # Save as compressed numpy archive
            np.savez_compressed(output_path, **save_data)
            print(f"Embeddings saved to: {output_path}")
            
        except Exception as e:
            print(f"Error saving embeddings: {e}")
    
    def load_embeddings(self, file_path: str) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """
        Load embeddings from disk
        
        Args:
            file_path: Path to load embeddings from
            
        Returns:
            Dictionary with loaded embeddings
        """
        try:
            loaded_data = np.load(file_path)
            
            embeddings = {}
            modalities = set()
            
            # Extract modality names
            for key in loaded_data.keys():
                if key.endswith('_train'):
                    modalities.add(key[:-6])  # Remove '_train'
            
            # Reconstruct embeddings dictionary
            for modality in modalities:
                train_key = f'{modality}_train'
                test_key = f'{modality}_test'
                
                if train_key in loaded_data and test_key in loaded_data:
                    embeddings[modality] = (loaded_data[train_key], loaded_data[test_key])
            
            print(f"Embeddings loaded from: {file_path}")
            return embeddings
            
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            return {}


def check_device_availability():
    """Check and display available computing devices"""
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU device: {torch.cuda.get_device_name(0)}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    print(f"Using device: {DEVICE}")


def optimize_memory_usage():
    """Optimize memory usage for large embedding operations"""
    import gc
    
    # Clear GPU cache if using CUDA
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # Run garbage collection
    gc.collect()
    
    print("Memory optimization complete")
