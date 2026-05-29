"""
Scraping module for missing persons data collection
Contains all web scraping functionality and image capture capabilities
"""

from .web_scraper import (
    fetch_page_soup,
    extract_case_links_from_main_page,
    extract_photo_urls_from_main_page,
    extract_case_data_from_detail_page,
    scrape_missing_persons_text_data,
    scrape_found_persons_data,
    get_column_structure_from_sample_case
)

from .image_handler import (
    initialize_chrome_driver,
    capture_image_screenshot,
    capture_images_from_link_list,
    capture_images_with_error_recovery,
    ImageCaptureManager
)

from .utils import (
    normalize_text_data,
    serialize_image_matrices,
    convert_image_to_json,
    display_sample_images,
    create_required_directories,
    save_dataframe_to_csv,
    process_found_persons_data
)

from .config import (
    TODAY_DATE,
    REQUEST_HEADERS,
    BASE_URL,
    MISSING_ADULTS_URL,
    MISSING_MINORS_URL,
    FOUND_PERSONS_URL,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    MISSING_PERSONS_FILENAME,
    FOUND_PERSONS_FILENAME,
    CSV_SEPARATOR,
    CSV_ENCODING
)

__all__ = [
    # Web scraper functions
    'fetch_page_soup',
    'extract_case_links_from_main_page',
    'extract_photo_urls_from_main_page',
    'extract_case_data_from_detail_page',
    'scrape_missing_persons_text_data',
    'scrape_found_persons_data',
    'get_column_structure_from_sample_case',
    
    # Image handler functions
    'initialize_chrome_driver',
    'capture_image_screenshot',
    'capture_images_from_link_list',
    'capture_images_with_error_recovery',
    'ImageCaptureManager',
    
    # Utility functions
    'normalize_text_data',
    'serialize_image_matrices',
    'convert_image_to_json',
    'display_sample_images',
    'create_required_directories',
    'save_dataframe_to_csv',
    'process_found_persons_data',
    
    # Configuration constants
    'TODAY_DATE',
    'REQUEST_HEADERS',
    'BASE_URL',
    'MISSING_ADULTS_URL',
    'MISSING_MINORS_URL',
    'FOUND_PERSONS_URL',
    'RAW_DATA_DIR',
    'PROCESSED_DATA_DIR',
    'MISSING_PERSONS_FILENAME',
    'FOUND_PERSONS_FILENAME',
    'CSV_SEPARATOR',
    'CSV_ENCODING'
]