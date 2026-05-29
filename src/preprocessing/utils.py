"""
Utility functions for preprocessing module
Contains helper functions for data validation, logging, and common operations
"""

import pandas as pd
import numpy as np
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import warnings


def log_preprocessing_step(step_name: str, details: str = "") -> None:
    """
    Log preprocessing step with timestamp
    
    Args:
        step_name: Name of the preprocessing step
        details: Additional details about the step
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if details:
        print(f"[{timestamp}] {step_name}: {details}")
    else:
        print(f"[{timestamp}] {step_name}")


def safe_division(numerator: float, denominator: float, default_value: float = 0.0) -> float:
    """
    Perform safe division with default value for division by zero
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default_value: Value to return if denominator is zero
        
    Returns:
        Result of division or default value
    """
    if denominator == 0:
        return default_value
    return numerator / denominator


def calculate_percentage(part: int, total: int, decimal_places: int = 2) -> float:
    """
    Calculate percentage with safe division
    
    Args:
        part: Part value
        total: Total value
        decimal_places: Number of decimal places to round to
        
    Returns:
        Percentage value
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, decimal_places)


def validate_dataframe_schema(df: pd.DataFrame, expected_columns: List[str], 
                             column_types: Optional[Dict[str, str]] = None) -> Tuple[bool, List[str]]:
    """
    Validate DataFrame schema against expected structure
    
    Args:
        df: DataFrame to validate
        expected_columns: List of expected column names
        column_types: Optional dictionary of column name -> expected type
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check for missing columns
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        issues.append(f"Missing columns: {missing_columns}")
    
    # Check for unexpected columns
    unexpected_columns = [col for col in df.columns if col not in expected_columns]
    if unexpected_columns:
        issues.append(f"Unexpected columns: {unexpected_columns}")
    
    # Check column types if provided
    if column_types:
        for col, expected_type in column_types.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if expected_type not in actual_type:
                    issues.append(f"Column {col} has type {actual_type}, expected {expected_type}")
    
    is_valid = len(issues) == 0
    return is_valid, issues


def detect_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    """
    Detect outliers using Interquartile Range (IQR) method
    
    Args:
        series: Pandas Series to analyze
        k: IQR multiplier for outlier detection
        
    Returns:
        Boolean Series indicating outliers
    """
    if series.dtype not in ['int64', 'float64']:
        return pd.Series([False] * len(series), index=series.index)
    
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - k * IQR
    upper_bound = Q3 + k * IQR
    
    return (series < lower_bound) | (series > upper_bound)


def standardize_text_column(series: pd.Series, remove_extra_spaces: bool = True,
                           convert_to_title: bool = False) -> pd.Series:
    """
    Standardize text column with common cleaning operations
    
    Args:
        series: Text series to standardize
        remove_extra_spaces: Whether to remove extra spaces
        convert_to_title: Whether to convert to title case
        
    Returns:
        Standardized text series
    """
    standardized = series.copy()
    
    # Convert to string and handle nulls
    standardized = standardized.astype(str)
    standardized = standardized.replace('nan', '')
    
    # Strip whitespace
    standardized = standardized.str.strip()
    
    # Remove extra spaces
    if remove_extra_spaces:
        standardized = standardized.str.replace(r'\s+', ' ', regex=True)
    
    # Convert to title case
    if convert_to_title:
        standardized = standardized.str.title()
    
    return standardized


def generate_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive data profile for a DataFrame
    
    Args:
        df: DataFrame to profile
        
    Returns:
        Dictionary with data profiling information
    """
    profile = {
        'basic_info': {
            'shape': df.shape,
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'dtypes': df.dtypes.value_counts().to_dict()
        },
        'missing_data': {
            'total_missing': df.isnull().sum().sum(),
            'missing_percentage': (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
            'columns_with_missing': df.columns[df.isnull().any()].tolist(),
            'missing_by_column': df.isnull().sum().to_dict()
        },
        'numeric_columns': {},
        'text_columns': {},
        'datetime_columns': {}
    }
    
    # Profile numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        profile['numeric_columns'][col] = {
            'mean': df[col].mean(),
            'median': df[col].median(),
            'std': df[col].std(),
            'min': df[col].min(),
            'max': df[col].max(),
            'unique_values': df[col].nunique(),
            'outliers_count': detect_outliers_iqr(df[col]).sum()
        }
    
    # Profile text columns
    text_columns = df.select_dtypes(include=['object']).columns
    for col in text_columns:
        profile['text_columns'][col] = {
            'unique_values': df[col].nunique(),
            'most_common': df[col].value_counts().head(5).to_dict(),
            'avg_length': df[col].astype(str).str.len().mean(),
            'empty_strings': (df[col] == '').sum()
        }
    
    # Profile datetime columns
    datetime_columns = df.select_dtypes(include=['datetime64']).columns
    for col in datetime_columns:
        profile['datetime_columns'][col] = {
            'min_date': df[col].min(),
            'max_date': df[col].max(),
            'date_range_days': (df[col].max() - df[col].min()).days if df[col].notna().any() else 0,
            'unique_dates': df[col].nunique()
        }
    
    return profile


def save_processing_report(summary: Dict, output_path: str) -> None:
    """
    Save processing summary as JSON report
    
    Args:
        summary: Processing summary dictionary
        output_path: Path to save the report
    """
    try:
        # Convert datetime objects to strings for JSON serialization
        json_compatible_summary = convert_datetime_to_string(summary)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_compatible_summary, f, indent=2, ensure_ascii=False)
        
        print(f"Processing report saved to: {output_path}")
        
    except Exception as e:
        print(f"Error saving processing report: {e}")


def convert_datetime_to_string(obj: Any) -> Any:
    """
    Recursively convert datetime objects to strings for JSON serialization
    
    Args:
        obj: Object to convert
        
    Returns:
        Object with datetime converted to strings
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_datetime_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime_to_string(item) for item in obj]
    elif pd.isna(obj):
        return None
    else:
        return obj


def check_data_consistency(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Check data consistency across related columns
    
    Args:
        df: DataFrame to check
        
    Returns:
        Dictionary with consistency check results
    """
    consistency_issues = {
        'temporal_inconsistencies': [],
        'logical_inconsistencies': [],
        'data_quality_issues': []
    }
    
    # Check temporal consistency
    if all(col in df.columns for col in ['incident_date', 'report_date']):
        invalid_dates = df['report_date'] < df['incident_date']
        if invalid_dates.any():
            count = invalid_dates.sum()
            consistency_issues['temporal_inconsistencies'].append(
                f"{count} records where report date is before incident date"
            )
    
    if all(col in df.columns for col in ['incident_date', 'found_date']):
        invalid_dates = (df['found_date'].notna()) & (df['found_date'] < df['incident_date'])
        if invalid_dates.any():
            count = invalid_dates.sum()
            consistency_issues['temporal_inconsistencies'].append(
                f"{count} records where found date is before incident date"
            )
    
    # Check logical consistency
    if 'appeared_status' in df.columns and 'found_date' in df.columns:
        appeared_without_date = (df['appeared_status'] == True) & (df['found_date'].isna())
        if appeared_without_date.any():
            count = appeared_without_date.sum()
            consistency_issues['logical_inconsistencies'].append(
                f"{count} records marked as appeared but without found date"
            )
    
    # Check age consistency
    if 'age_cleaned' in df.columns:
        invalid_ages = (df['age_cleaned'] < 0) | (df['age_cleaned'] > 120)
        if invalid_ages.any():
            count = invalid_ages.sum()
            consistency_issues['data_quality_issues'].append(
                f"{count} records with invalid ages (< 0 or > 120)"
            )
    
    # Check height consistency
    if 'height_cleaned' in df.columns:
        invalid_heights = (df['height_cleaned'] < 50) | (df['height_cleaned'] > 250)
        if invalid_heights.any():
            count = invalid_heights.sum()
            consistency_issues['data_quality_issues'].append(
                f"{count} records with invalid heights (< 50cm or > 250cm)"
            )
    
    return consistency_issues


def create_preprocessing_backup(df: pd.DataFrame, backup_dir: str, prefix: str) -> str:
    """
    Create backup of DataFrame during preprocessing
    
    Args:
        df: DataFrame to backup
        backup_dir: Directory to save backup
        prefix: Prefix for backup filename
        
    Returns:
        Path to created backup file
    """
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{prefix}_backup_{timestamp}.csv"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        df.to_csv(backup_path, index=False, encoding='utf-8-sig')
        print(f"Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Error creating backup: {e}")
        return ""


def suppress_warnings():
    """Suppress common pandas and data processing warnings"""
    warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
    warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)


# Suppress warnings by default when module is imported
suppress_warnings()