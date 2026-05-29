"""
Data cleaning module for missing persons preprocessing
Handles basic data cleaning operations like combining names, extracting numeric values
"""

import pandas as pd
import numpy as np
import re
from typing import Optional, Dict, List

from .config import CLEANING_CONFIG


class DataCleaner:
    """
    Handles basic data cleaning operations
    """
    
    def __init__(self):
        self.age_pattern = CLEANING_CONFIG['age_pattern']
        self.height_pattern = CLEANING_CONFIG['height_pattern']
        self.weight_pattern = CLEANING_CONFIG.get('weight_pattern', r'(\d+\.?\d*)')
        self.time_replacements = CLEANING_CONFIG['time_replacements']
        
    def combine_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Combine first and last names into full name
        
        Args:
            df: DataFrame with first_names and last_names columns
            
        Returns:
            DataFrame with full_name column
        """
        df_cleaned = df.copy()
        
        if 'first_names' in df.columns and 'last_names' in df.columns:
            print("Combining first and last names...")
            
            # Handle missing values before concatenation
            df_cleaned['first_names'] = df_cleaned['first_names'].fillna('')
            df_cleaned['last_names'] = df_cleaned['last_names'].fillna('')
            
            df_cleaned['full_name'] = df_cleaned['first_names'].str.cat(
                df_cleaned['last_names'], sep=' '
            )
            
            # Clean up extra spaces
            df_cleaned['full_name'] = df_cleaned['full_name'].str.strip()
            
            print(f"Combined names for {len(df_cleaned)} records")
            
        else:
            print("Warning: Required name columns not found for combination")
        
        return df_cleaned
    
    def extract_numeric_age(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract numeric age from age text
        
        Args:
            df: DataFrame with age_raw column
            
        Returns:
            DataFrame with age_cleaned column
        """
        df_cleaned = df.copy()
        
        if 'age_raw' in df.columns:
            print("Extracting numeric age values...")
            
            df_cleaned['age_cleaned'] = df_cleaned['age_raw'].astype(str).str.extract(
                self.age_pattern, expand=False
            )
            
            # Convert to numeric
            df_cleaned['age_cleaned'] = pd.to_numeric(df_cleaned['age_cleaned'], errors='coerce')
            
            # Summary statistics
            valid_ages = df_cleaned['age_cleaned'].notna().sum()
            print(f"Extracted {valid_ages} valid age values from {len(df_cleaned)} records")
            
        else:
            print("Warning: age_raw column not found")
        
        return df_cleaned
    
    def extract_numeric_height(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract numeric height from height text

        Args:
            df: DataFrame with height_raw column
            
        Returns:
            DataFrame with height_cleaned column
        """
        df_cleaned = df.copy()
        
        if 'height_raw' in df.columns:
            print("Extracting numeric height values...")
            
            df_cleaned['height_cleaned'] = df_cleaned['height_raw'].astype(str).str.extract(
                self.height_pattern, expand=False
            )
            
            # Convert to numeric
            df_cleaned['height_cleaned'] = pd.to_numeric(df_cleaned['height_cleaned'], errors='coerce')
            
            # Summary statistics
            valid_heights = df_cleaned['height_cleaned'].notna().sum()
            print(f"Extracted {valid_heights} valid height values from {len(df_cleaned)} records")
            
        else:
            print("Warning: height_raw column not found")
        
        return df_cleaned
    
    def extract_numeric_weight(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract numeric weight from weight text (if weight column exists)
        
        Args:
            df: DataFrame with weight_raw column
            
        Returns:
            DataFrame with weight_cleaned column
        """
        df_cleaned = df.copy()
        
        if 'weight_raw' in df.columns:
            print("Extracting numeric weight values...")
            
            # Extract numeric weight using same pattern as height
            df_cleaned['weight_cleaned'] = df_cleaned['weight_raw'].astype(str).str.extract(
                self.weight_pattern, expand=False
            )
            
            # Convert to numeric
            df_cleaned['weight_cleaned'] = pd.to_numeric(df_cleaned['weight_cleaned'], errors='coerce')
            
            # Summary statistics
            valid_weights = df_cleaned['weight_cleaned'].notna().sum()
            print(f"Extracted {valid_weights} valid weight values from {len(df_cleaned)} records")
            
        return df_cleaned
    
    def split_datetime_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Split datetime columns into separate date and time columns

        Args:
            df: DataFrame with datetime columns to split
            
        Returns:
            DataFrame with split date and time columns
        """
        df_cleaned = df.copy()
        
        # Define datetime columns to split (original column -> [date_col, time_col])
        datetime_splits = {
            'report_datetime_raw': ['report_date', 'report_time'],        # equivalent to 'Fecha' -> ['Fecha de Denuncia', 'Hora de Denuncia']
            'birth_datetime_raw': ['birth_date', 'birth_time'],           # equivalent to 'F./ NACIMIENTO' -> ['Fecha de Nacimiento', 'Hora de Nacimiento']
            'incident_datetime_raw': ['incident_date', 'incident_time']   # equivalent to 'FECHA DEL HECHO' -> ['Fecha del Hecho', 'Hora del Hecho']
        }
        
        for original_col, [date_col, time_col] in datetime_splits.items():
            if original_col in df.columns:
                print(f"Splitting {original_col} into date and time...")
                
                split_result = df_cleaned[original_col].astype(str).str.split(' ', n=1, expand=True)
                
                if split_result.shape[1] >= 2:
                    df_cleaned[date_col] = split_result[0]
                    df_cleaned[time_col] = split_result[1]
                else:
                    # Handle cases where there's no time component
                    df_cleaned[date_col] = split_result[0]
                    df_cleaned[time_col] = np.nan
                
                print(f"  Created {date_col} and {time_col}")
            else:
                print(f"Warning: {original_col} column not found for splitting")
        
        return df_cleaned
    
    def remove_processed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove columns that are no longer needed after processing

        Args:
            df: DataFrame to clean up
            
        Returns:
            DataFrame with unnecessary columns removed
        """
        df_cleaned = df.copy()
        columns_to_drop = CLEANING_CONFIG['columns_to_drop']
        
        # Only drop columns that exist
        existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
        
        if existing_columns_to_drop:
            df_cleaned.drop(columns=existing_columns_to_drop, inplace=True)
            print(f"Removed {len(existing_columns_to_drop)} processed columns: {existing_columns_to_drop}")
        
        return df_cleaned
    
    def apply_basic_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all basic cleaning operations in sequence
        
        Args:
            df: Raw DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        print("=== Starting Basic Data Cleaning ===")
        
        df_cleaned = self.combine_names(df)
        
        df_cleaned = self.extract_numeric_age(df_cleaned)
        df_cleaned = self.extract_numeric_height(df_cleaned)
        df_cleaned = self.extract_numeric_weight(df_cleaned)  # if weight column exists
        
        df_cleaned = self.split_datetime_columns(df_cleaned)
        
        df_cleaned = self.remove_processed_columns(df_cleaned)
        
        print("=== Basic Data Cleaning Complete ===")
        
        return df_cleaned
    
    def get_cleaning_summary(self, original_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> Dict:
        """
        Generate summary of cleaning operations
        
        Args:
            original_df: Original DataFrame before cleaning
            cleaned_df: DataFrame after cleaning
            
        Returns:
            Dictionary with cleaning summary statistics
        """
        summary = {
            'records_processed': len(original_df),
            'records_after_cleaning': len(cleaned_df),
            'columns_before': len(original_df.columns),
            'columns_after': len(cleaned_df.columns),
            'new_columns_created': [],
            'columns_removed': [],
            'data_quality': {}
        }
        
        # Identify new columns
        original_cols = set(original_df.columns)
        cleaned_cols = set(cleaned_df.columns)
        summary['new_columns_created'] = list(cleaned_cols - original_cols)
        summary['columns_removed'] = list(original_cols - cleaned_cols)
        
        # Data quality metrics
        if 'full_name' in cleaned_df.columns:
            summary['data_quality']['names_combined'] = cleaned_df['full_name'].notna().sum()
        
        if 'age_cleaned' in cleaned_df.columns:
            summary['data_quality']['valid_ages'] = cleaned_df['age_cleaned'].notna().sum()
        
        if 'height_cleaned' in cleaned_df.columns:
            summary['data_quality']['valid_heights'] = cleaned_df['height_cleaned'].notna().sum()
        
        return summary


def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate that DataFrame contains required columns
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        True if all required columns exist, False otherwise
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        return False
    
    return True
