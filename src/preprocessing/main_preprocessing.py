"""
Main preprocessing script for missing persons data
Orchestrates the complete preprocessing workflow INCLUDING geocoding
"""

import os
import sys
import pandas as pd
from typing import Tuple, Dict

# Local imports
from .config import (
    PROCESSED_DATA_DIR, CONSOLIDATED_MISSING_FILENAME, 
    CONSOLIDATED_FOUND_FILENAME, FINAL_ANALYSIS_FILENAME, GEOCODED_FILENAME
)
from .data_loader import DataLoader, validate_data_directories
from .data_cleaner import DataCleaner
from .temporal_processor import TemporalProcessor
from .feature_engineer import FeatureEngineer
from .geocoder import GeoCoder, get_peru_shapefile_path


def main_preprocessing_workflow() -> Tuple[pd.DataFrame, Dict]:
    """
    Main preprocessing workflow that ALWAYS includes geocoding
    
    Complete workflow:
    1. Load and combine missing persons CSV files
    2. Load and combine found persons CSV files
    3. Clean basic data (names, ages, heights)
    4. Split datetime columns
    5. Process temporal data
    6. Create appeared status
    7. Calculate temporal features
    8. GEOCODE addresses
    9. Save processed data
    
    Returns:
        Tuple of (final_dataset, processing_summary)
    """
    print("=== Missing Persons Data Preprocessing + Geocoding Started ===")
    print("Complete workflow including geocoding...")
    
    try:
        # Validate data directories exist
        if not validate_data_directories():
            raise FileNotFoundError("Required data directories not found or empty")
        
        # Initialize processors
        data_loader = DataLoader()
        data_cleaner = DataCleaner()
        temporal_processor = TemporalProcessor()
        feature_engineer = FeatureEngineer()
        
        # Step 1: Load and combine all data
        print("\n1. Loading and combining data...")
        missing_persons_raw, found_persons_raw = data_loader.load_all_data()
        
        # Step 2: Apply basic data cleaning
        print("\n2. Applying basic data cleaning...")
        missing_persons_cleaned = data_cleaner.apply_basic_cleaning(missing_persons_raw)
        
        # Step 3: Process temporal data
        print("\n3. Processing temporal data...")
        missing_persons_temporal = temporal_processor.apply_temporal_processing(missing_persons_cleaned)
        
        # Step 4: Apply feature engineering
        print("\n4. Applying feature engineering...")
        missing_persons_features = feature_engineer.apply_feature_engineering(
            missing_persons_temporal, found_persons_raw
        )
        
        # Step 5: GEOCODING (ALWAYS INCLUDED)
        print("\n5. Starting geocoding process...")
        shapefile_path = get_peru_shapefile_path()
        geocoder = GeoCoder(shapefile_path=shapefile_path)
        
        print("Using optimized geocoding...")
        final_dataset = geocoder.geocodificar_optimizado(
            missing_persons_features, 
            location_column='incident_location'
        )
        
        # Step 6: Save processed datasets
        print("\n6. Saving processed datasets...")
        save_processed_datasets(final_dataset, found_persons_raw)
        
        # Step 7: Generate processing summary
        print("\n7. Generating processing summary...")
        processing_summary = generate_processing_summary(
            missing_persons_raw, final_dataset, data_cleaner, 
            temporal_processor, feature_engineer, geocoder
        )
        
        print("\n=== Preprocessing + Geocoding Summary ===")
        print(f"Total records processed: {len(missing_persons_raw)}")
        print(f"Final dataset records: {len(final_dataset)}")
        print(f"Found persons records: {len(found_persons_raw)}")
        print(f"Appeared cases: {final_dataset['appeared_status'].sum()}")
        print(f"Appearance rate: {(final_dataset['appeared_status'].sum() / len(final_dataset)) * 100:.2f}%")
        
        # Geocoding summary
        if 'Latitud' in final_dataset.columns:
            geocoded_count = final_dataset['Latitud'].notna().sum()
            geocoding_rate = (geocoded_count / len(final_dataset)) * 100
            print(f"Geocoded addresses: {geocoded_count} ({geocoding_rate:.2f}%)")
        
        print("\n=== Data Preprocessing + Geocoding Completed Successfully ===")
        
        return final_dataset, processing_summary
        
    except Exception as e:
        print(f"\nError during data preprocessing + geocoding: {e}")
        print("Please check the logs above for specific error details.")
        sys.exit(1)


def save_processed_datasets(final_dataset: pd.DataFrame, found_persons_df: pd.DataFrame) -> None:
    """
    Save all processed datasets including geocoded data
    
    Args:
        final_dataset: Final processed dataset with geocoding
        found_persons_df: Found persons dataset
    """
    # Ensure processed data directory exists
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    # Save final analysis dataset
    final_dataset_path = os.path.join(PROCESSED_DATA_DIR, FINAL_ANALYSIS_FILENAME)
    final_dataset.to_csv(final_dataset_path, index=False, encoding='utf-8-sig')
    print(f"Saved final analysis dataset: {final_dataset_path}")
    
    # Save geocoded dataset (this is the file that eliminates the "not found" message)
    geocoded_path = os.path.join(PROCESSED_DATA_DIR, GEOCODED_FILENAME)
    final_dataset.to_csv(geocoded_path, index=False, encoding='utf-8-sig')
    print(f"Saved geocoded dataset: {geocoded_path}")
    
    # Save consolidated missing persons data (without engineered features for reference)
    missing_persons_basic = final_dataset.drop(columns=[
        'appeared_status', 'hours_to_appear', 'hours_to_report',
        'found_date', 'found_time', 'age_category', 'height_category',
        'incident_year', 'incident_month', 'incident_day_of_week', 'incident_quarter',
        'has_photo', 'has_distinctive_marks', 'has_complete_temporal_data'
    ], errors='ignore')
    
    consolidated_missing_path = os.path.join(PROCESSED_DATA_DIR, CONSOLIDATED_MISSING_FILENAME)
    missing_persons_basic.to_csv(consolidated_missing_path, index=False, encoding='utf-8-sig')
    print(f"Saved consolidated missing persons: {consolidated_missing_path}")
    
    # Save consolidated found persons data
    if not found_persons_df.empty:
        consolidated_found_path = os.path.join(PROCESSED_DATA_DIR, CONSOLIDATED_FOUND_FILENAME)
        found_persons_df.to_csv(consolidated_found_path, index=False, encoding='utf-8-sig')
        print(f"Saved consolidated found persons: {consolidated_found_path}")


def generate_processing_summary(original_df: pd.DataFrame, final_df: pd.DataFrame,
                               data_cleaner: DataCleaner, temporal_processor: TemporalProcessor,
                               feature_engineer: FeatureEngineer, geocoder: GeoCoder) -> Dict:
    """
    Generate comprehensive summary of preprocessing operations including geocoding
    
    Args:
        original_df: Original raw dataset
        final_df: Final processed dataset with geocoding
        data_cleaner: DataCleaner instance used
        temporal_processor: TemporalProcessor instance used
        feature_engineer: FeatureEngineer instance used
        geocoder: GeoCoder instance used
        
    Returns:
        Dictionary with comprehensive processing summary
    """
    summary = {
        'processing_overview': {
            'original_records': len(original_df),
            'final_records': len(final_df),
            'records_retained': len(final_df) / len(original_df) * 100,
            'original_columns': len(original_df.columns),
            'final_columns': len(final_df.columns)
        },
        'data_cleaning': data_cleaner.get_cleaning_summary(original_df, final_df),
        'temporal_processing': temporal_processor.get_temporal_summary(final_df),
        'feature_engineering': feature_engineer.get_feature_engineering_summary(final_df),
        'geocoding': {
            'geocoded_records': final_df['Latitud'].notna().sum() if 'Latitud' in final_df.columns else 0,
            'geocoding_success_rate': 0,
            'district_validation_available': geocoder.gdf_peru_distritos is not None,
            'shapefile_path': geocoder.shapefile_path
        },
        'data_quality_metrics': calculate_data_quality_metrics(final_df),
        'geocodified_data_available': True  # Always True now since we always geocode
    }
    
    # Calculate geocoding success rate
    if 'Latitud' in final_df.columns:
        geocoded_count = final_df['Latitud'].notna().sum()
        total_count = len(final_df)
        summary['geocoding']['geocoding_success_rate'] = (geocoded_count / total_count) * 100
    
    if 'En_Distrito' in final_df.columns:
        valid_districts = final_df['En_Distrito'].sum()
        summary['geocoding']['addresses_in_valid_districts'] = valid_districts
    
    return summary


def calculate_data_quality_metrics(df: pd.DataFrame) -> Dict:
    """
    Calculate data quality metrics for the final dataset
    
    Args:
        df: Final processed DataFrame
        
    Returns:
        Dictionary with data quality metrics
    """
    quality_metrics = {
        'completeness': {},
        'validity': {},
        'consistency': {}
    }
    
    # Completeness metrics
    total_records = len(df)
    for column in df.columns:
        non_null_count = df[column].notna().sum()
        quality_metrics['completeness'][column] = {
            'non_null_count': non_null_count,
            'completeness_percentage': (non_null_count / total_records) * 100
        }
    
    # Validity metrics for specific columns
    if 'age_cleaned' in df.columns:
        valid_ages = ((df['age_cleaned'] >= 0) & (df['age_cleaned'] <= 120)).sum()
        quality_metrics['validity']['age_cleaned'] = {
            'valid_count': valid_ages,
            'validity_percentage': (valid_ages / total_records) * 100
        }
    
    if 'height_cleaned' in df.columns:
        valid_heights = ((df['height_cleaned'] >= 50) & (df['height_cleaned'] <= 250)).sum()
        quality_metrics['validity']['height_cleaned'] = {
            'valid_count': valid_heights,
            'validity_percentage': (valid_heights / total_records) * 100
        }
    
    # Consistency metrics
    if all(col in df.columns for col in ['incident_date', 'report_date']):
        consistent_dates = (df['report_date'] >= df['incident_date']).sum()
        quality_metrics['consistency']['report_after_incident'] = {
            'consistent_count': consistent_dates,
            'consistency_percentage': (consistent_dates / total_records) * 100
        }
    
    return quality_metrics


def validate_preprocessing_results(df: pd.DataFrame) -> bool:
    """
    Validate that preprocessing results meet expected criteria
    
    Args:
        df: Final processed DataFrame
        
    Returns:
        True if validation passes, False otherwise
    """
    validation_checks = []
    
    # Check required columns exist
    required_columns = ['full_name', 'age_cleaned', 'appeared_status', 'Latitud', 'Longitud']
    missing_required = [col for col in required_columns if col not in df.columns]
    if missing_required:
        print(f"Validation failed: Missing required columns: {missing_required}")
        validation_checks.append(False)
    else:
        validation_checks.append(True)
    
    # Check data types
    if 'appeared_status' in df.columns:
        if df['appeared_status'].dtype != bool:
            print("Validation failed: appeared_status should be boolean")
            validation_checks.append(False)
        else:
            validation_checks.append(True)
    
    # Check geocoding results
    if 'Latitud' in df.columns:
        geocoded_count = df['Latitud'].notna().sum()
        if geocoded_count == 0:
            print("Validation warning: No addresses were geocoded")
        else:
            print(f"Validation passed: {geocoded_count} addresses geocoded")
    
    return all(validation_checks)


if __name__ == "__main__":
    final_data, summary = main_preprocessing_workflow()
    
    # Validate results
    if validate_preprocessing_results(final_data):
        print("✓ Preprocessing validation passed")
    else:
        print("✗ Preprocessing validation failed")
        sys.exit(1)