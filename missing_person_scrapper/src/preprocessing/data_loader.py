"""
Data loading module for missing persons preprocessing
Handles loading and combining multiple CSV files from different dates
"""

import os
import pandas as pd
from typing import List, Dict, Optional
import glob
from pathlib import Path

from .config import (
    MISSING_PERSONS_RAW_DIR, FOUND_PERSONS_RAW_DIR,
    CSV_DELIMITER, CSV_ENCODING, COLUMN_MAPPINGS, FOUND_PERSONS_COLUMNS
)


class DataLoader:
    """
    Handles loading and combining CSV files from raw data directories
    """
    
    def __init__(self):
        self.missing_persons_dir = MISSING_PERSONS_RAW_DIR
        self.found_persons_dir = FOUND_PERSONS_RAW_DIR
        
    def load_and_combine_missing_persons_data(self) -> pd.DataFrame:
        """
        Load and combine all missing persons CSV files from raw directory
        
        Returns:
            Combined DataFrame with all missing persons data
        """
        print(f"Loading missing persons data from: {self.missing_persons_dir}")
        
        if not os.path.exists(self.missing_persons_dir):
            raise FileNotFoundError(f"Missing persons directory not found: {self.missing_persons_dir}")
        
        combined_missing_data = pd.DataFrame()
        csv_files_found = []
        
        for filename in os.listdir(self.missing_persons_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.missing_persons_dir, filename)
                csv_files_found.append(filename)
                
                try:
                    # Load CSV with same parameters as original
                    df_file = pd.read_csv(file_path, delimiter=CSV_DELIMITER, encoding=CSV_ENCODING)
                    
                    if combined_missing_data.empty:
                        combined_missing_data = df_file
                    else:
                        combined_missing_data = pd.concat([combined_missing_data, df_file], 
                                                        axis=0, ignore_index=True)
                    
                    print(f"  Loaded: {filename} ({len(df_file)} records)")
                    
                except Exception as e:
                    print(f"  Error loading {filename}: {e}")
                    continue
        
        if combined_missing_data.empty:
            raise ValueError(f"No valid CSV files found in {self.missing_persons_dir}")
        
        print(f"Combined {len(csv_files_found)} files into {len(combined_missing_data)} total records")
        
        initial_count = len(combined_missing_data)
        combined_missing_data = combined_missing_data.drop_duplicates()
        duplicates_removed = initial_count - len(combined_missing_data)
        
        if duplicates_removed > 0:
            print(f"Removed {duplicates_removed} duplicate records")
        
        return combined_missing_data
    
    def load_and_combine_found_persons_data(self) -> pd.DataFrame:
        """
        Load and combine all found persons CSV files from raw directory
        
        Returns:
            Combined DataFrame with all found persons data
        """
        print(f"Loading found persons data from: {self.found_persons_dir}")
        
        if not os.path.exists(self.found_persons_dir):
            raise FileNotFoundError(f"Found persons directory not found: {self.found_persons_dir}")
        
        combined_found_data = pd.DataFrame()
        csv_files_found = []
        
        for filename in os.listdir(self.found_persons_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.found_persons_dir, filename)
                csv_files_found.append(filename)
                
                try:
                    df_file = pd.read_csv(file_path, delimiter=CSV_DELIMITER, encoding=CSV_ENCODING)
                    combined_found_data = pd.concat([combined_found_data, df_file], ignore_index=True)
                    
                    print(f"  Loaded: {filename} ({len(df_file)} records)")
                    
                except Exception as e:
                    print(f"  Error loading {filename}: {e}")
                    continue
        
        if combined_found_data.empty:
            print("Warning: No found persons data loaded")
            return pd.DataFrame()
        
        print(f"Combined {len(csv_files_found)} found persons files into {len(combined_found_data)} total records")
        
        return combined_found_data
    
    def standardize_column_names(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Standardize column names using provided mapping
        
        Args:
            df: DataFrame to standardize
            column_mapping: Dictionary mapping original -> standard names
            
        Returns:
            DataFrame with standardized column names
        """
        df_standardized = df.copy()
        
        # Apply column mapping where columns exist
        existing_columns = df.columns.tolist()
        mapping_applied = {}
        
        for original_col, standard_col in column_mapping.items():
            if original_col in existing_columns:
                df_standardized.rename(columns={original_col: standard_col}, inplace=True)
                mapping_applied[original_col] = standard_col
        
        print(f"Standardized {len(mapping_applied)} column names")
        
        return df_standardized
    
    def load_all_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load and standardize all data (missing persons and found persons)
        
        Returns:
            Tuple of (missing_persons_df, found_persons_df)
        """
        print("=== Starting Data Loading Process ===")
        
        # Load missing persons data
        missing_persons_raw = self.load_and_combine_missing_persons_data()
        missing_persons_standardized = self.standardize_column_names(
            missing_persons_raw, COLUMN_MAPPINGS
        )
        
        # Load found persons data  
        found_persons_raw = self.load_and_combine_found_persons_data()
        if not found_persons_raw.empty:
            found_persons_standardized = self.standardize_column_names(
                found_persons_raw, FOUND_PERSONS_COLUMNS
            )
        else:
            found_persons_standardized = pd.DataFrame()
        
        print("=== Data Loading Complete ===")
        
        return missing_persons_standardized, found_persons_standardized
    
    def get_data_summary(self, missing_df: pd.DataFrame, found_df: pd.DataFrame) -> Dict:
        """
        Get summary statistics of loaded data
        
        Args:
            missing_df: Missing persons DataFrame
            found_df: Found persons DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'missing_persons': {
                'total_records': len(missing_df),
                'columns': missing_df.columns.tolist(),
                'date_range': None,
                'null_counts': missing_df.isnull().sum().to_dict()
            },
            'found_persons': {
                'total_records': len(found_df),
                'columns': found_df.columns.tolist() if not found_df.empty else [],
                'date_range': None,
                'null_counts': found_df.isnull().sum().to_dict() if not found_df.empty else {}
            }
        }
        
        return summary


def validate_data_directories() -> bool:
    """
    Validate that required data directories exist and contain CSV files
    
    Returns:
        True if directories are valid, False otherwise
    """
    directories_to_check = [MISSING_PERSONS_RAW_DIR, FOUND_PERSONS_RAW_DIR]
    
    for directory in directories_to_check:
        if not os.path.exists(directory):
            print(f"Warning: Directory does not exist: {directory}")
            return False
        
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        if not csv_files:
            print(f"Warning: No CSV files found in: {directory}")
            if directory == MISSING_PERSONS_RAW_DIR:
                return False  # Missing persons data is required
    
    return True


def get_available_csv_files() -> Dict[str, List[str]]:
    """
    Get list of available CSV files in each directory
    
    Returns:
        Dictionary with lists of CSV files for each directory
    """
    available_files = {
        'missing_persons': [],
        'found_persons': []
    }
    
    if os.path.exists(MISSING_PERSONS_RAW_DIR):
        available_files['missing_persons'] = [
            f for f in os.listdir(MISSING_PERSONS_RAW_DIR) if f.endswith('.csv')
        ]
    
    if os.path.exists(FOUND_PERSONS_RAW_DIR):
        available_files['found_persons'] = [
            f for f in os.listdir(FOUND_PERSONS_RAW_DIR) if f.endswith('.csv')
        ]
    
    return available_files
