"""
Utility functions for missing persons data scraping
Contains helper functions for data processing and serialization
"""

import pickle
import base64
import json
import unicodedata
import random
import matplotlib.pyplot as plt
import cv2
import numpy as np
from typing import List, Any
import pandas as pd
import os


def normalize_text_data(dataframe: pd.DataFrame, exclude_columns: List[str] = None) -> pd.DataFrame:
    """
    Normalize text columns in a DataFrame using Unicode NFC normalization
    
    Args:
        dataframe: Input DataFrame
        exclude_columns: List of column names to exclude from normalization
    
    Returns:
        DataFrame with normalized text columns
    """
    if exclude_columns is None:
        exclude_columns = []
    
    df_normalized = dataframe.copy()
    
    for column_name in df_normalized.columns:
        if column_name not in exclude_columns and df_normalized[column_name].dtype == 'object':
            df_normalized[column_name] = df_normalized[column_name].apply(
                lambda x: unicodedata.normalize('NFC', x) if isinstance(x, str) else x
            )
    
    return df_normalized


def serialize_image_matrices(image_matrices: List[np.ndarray]) -> List[bytes]:
    """
    Serialize image matrices using pickle
    
    Args:
        image_matrices: List of image matrices (numpy arrays)
    
    Returns:
        List of serialized image data
    """
    return [pickle.dumps(matrix) for matrix in image_matrices]


def convert_image_to_json(serialized_image: bytes) -> str:
    """
    Convert serialized image to JSON string with base64 encoding
    
    Args:
        serialized_image: Pickled image data
    
    Returns:
        JSON string containing base64 encoded image
    """
    if not serialized_image:
        return ''
    image_base64 = base64.b64encode(serialized_image).decode('utf-8')
    return json.dumps({'image': image_base64})


def display_sample_images(image_matrices: List[np.ndarray], num_samples: int = 5) -> None:
    """
    Display a sample of images from the collected matrices
    
    Args:
        image_matrices: List of image matrices to sample from
        num_samples: Number of images to display
    """
    if not image_matrices:
        print("No images available to display")
        return
    
    # Ensure we don't request more images than available
    num_samples = min(num_samples, len(image_matrices))
    random_sample_images = random.sample(image_matrices, num_samples)
    
    fig, axes = plt.subplots(1, num_samples, figsize=(15, 5))
    
    # Handle single image case
    if num_samples == 1:
        axes = [axes]
    
    for i in range(num_samples):
        axes[i].imshow(cv2.cvtColor(random_sample_images[i], cv2.COLOR_BGR2RGB))
        axes[i].axis('off')
    
    plt.show()


def create_required_directories(base_directory: str = "data") -> None:
    """
    Create necessary output directories if they don't exist
    
    Args:
        base_directory: Base directory for data storage
    """
    directories_to_create = [
        os.path.join(base_directory, "raw", "missing_persons"),
        os.path.join(base_directory, "raw", "found_persons"),
        os.path.join(base_directory, "processed")
    ]
    
    for directory_path in directories_to_create:
        os.makedirs(directory_path, exist_ok=True)


def save_dataframe_to_csv(dataframe: pd.DataFrame, file_path: str, 
                         separator: str = ';', encoding: str = 'utf-8-sig') -> None:
    """
    Save DataFrame to CSV with consistent formatting
    
    Args:
        dataframe: DataFrame to save
        file_path: Output file path
        separator: CSV separator character (default ';' as in original)
        encoding: File encoding (default 'utf-8-sig' as in original)
    """
    try:
        # Ensure directory exists
        directory_path = os.path.dirname(file_path)
        if directory_path:
            os.makedirs(directory_path, exist_ok=True)
        
        # Save with same parameters as original
        dataframe.to_csv(file_path, index=False, sep=separator, encoding=encoding)
        print(f"Data successfully saved to: {file_path}")
        print(f"Shape: {dataframe.shape}")
        
    except Exception as e:
        print(f"Error saving DataFrame to {file_path}: {e}")
        raise


def process_found_persons_data(soup_found_persons) -> List[List[str]]:
    """
    Extract found persons data from soup object
    
    Args:
        soup_found_persons: BeautifulSoup object of found persons page
    
    Returns:
        List of [name, date, photo_url] for each found person
    """
    from .config import PHOTO_CSS_CLASS
    
    # Extract data elements (reproducing original)
    found_names = soup_found_persons.find_all('h5')
    found_dates = soup_found_persons.find_all('p')
    found_photos = soup_found_persons.find_all('img', {'class': PHOTO_CSS_CLASS})
    
    found_persons_info = []
    
    # Process each found person (reproducing original logic)
    for i in range(len(found_names)):
        person_name = found_names[i].text
        occurrence_date = found_dates[i].text.strip('Hecho ocurrido el:')
        photo_source = found_photos[i].get('src')
        
        found_persons_info.append([person_name, occurrence_date, photo_source])
    
    return found_persons_info
