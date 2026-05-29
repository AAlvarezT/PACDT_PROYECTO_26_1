"""
Preprocessing module for missing persons data
Contains all data preprocessing functionality including cleaning, temporal processing, feature engineering, and geocoding
"""

from .data_loader import (
    DataLoader,
    validate_data_directories,
    get_available_csv_files
)

from .data_cleaner import (
    DataCleaner,
    validate_required_columns
)

from .temporal_processor import (
    TemporalProcessor
)

from .feature_engineer import (
    FeatureEngineer
)

from .geocoder import (
    GeoCoder,
    get_peru_shapefile_path
)

from .config import (
    PROJECT_ROOT,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    MISSING_PERSONS_RAW_DIR,
    FOUND_PERSONS_RAW_DIR,
    CONSOLIDATED_MISSING_FILENAME,
    CONSOLIDATED_FOUND_FILENAME,
    FINAL_ANALYSIS_FILENAME,
    GEOCODED_FILENAME,
    COLUMN_MAPPINGS,
    FOUND_PERSONS_COLUMNS,
    CLEANING_CONFIG,
    FEATURE_CONFIG,
    VALIDATION_CONFIG,
    GEOCODING_CONFIG
)

from .main_preprocessing import (
    main_preprocessing_workflow,
    save_processed_datasets,
    generate_processing_summary,
    calculate_data_quality_metrics,
    validate_preprocessing_results
)

__all__ = [
    # Main classes
    'DataLoader',
    'DataCleaner', 
    'TemporalProcessor',
    'FeatureEngineer',
    'GeoCoder',
    
    # Main workflow functions
    'main_preprocessing_workflow',
    'save_processed_datasets',
    'generate_processing_summary',
    'calculate_data_quality_metrics',
    'validate_preprocessing_results',
    
    # Utility functions
    'validate_data_directories',
    'get_available_csv_files',
    'validate_required_columns',
    'get_peru_shapefile_path',
    
    # Configuration constants
    'PROJECT_ROOT',
    'RAW_DATA_DIR',
    'PROCESSED_DATA_DIR',
    'MISSING_PERSONS_RAW_DIR',
    'FOUND_PERSONS_RAW_DIR',
    'CONSOLIDATED_MISSING_FILENAME',
    'CONSOLIDATED_FOUND_FILENAME',
    'FINAL_ANALYSIS_FILENAME',
    'GEOCODED_FILENAME',
    'COLUMN_MAPPINGS',
    'FOUND_PERSONS_COLUMNS',
    'CLEANING_CONFIG',
    'FEATURE_CONFIG',
    'VALIDATION_CONFIG',
    'GEOCODING_CONFIG'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Missing Persons Analysis Project"
__description__ = "Data preprocessing module for missing persons analysis including geocoding"