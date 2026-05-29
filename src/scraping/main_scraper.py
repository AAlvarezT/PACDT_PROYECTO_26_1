"""
Main scraping script for missing persons data collection
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import List

# Local imports
from .config import (
    RAW_DATA_DIR, MISSING_PERSONS_FILENAME, FOUND_PERSONS_FILENAME,
    MISSING_MINORS_URL, MISSING_ADULTS_URL, CSV_SEPARATOR, CSV_ENCODING
)
from .web_scraper import (
    fetch_page_soup, extract_case_links_from_main_page, 
    extract_photo_urls_from_main_page, scrape_missing_persons_text_data,
    scrape_found_persons_data, get_column_structure_from_sample_case
)
from .image_handler import capture_images_from_link_list, capture_images_with_error_recovery
from .utils import (
    normalize_text_data, serialize_image_matrices, convert_image_to_json,
    display_sample_images, create_required_directories, save_dataframe_to_csv
)


def main_scraping_workflow():

    print("=== Missing Persons Data Collection Started ===")
    print("Reproducing original notebook workflow exactly...")
    
    try:
        # Create output directories
        create_required_directories()
        
        # Step 1: Fetch main pages (reproducing original menores/mayores/ubicados)
        print("\n1. Fetching main pages...")
        minors_main_page = fetch_page_soup(MISSING_MINORS_URL)  # menores
        adults_main_page = fetch_page_soup(MISSING_ADULTS_URL)  # mayores
        
        # Step 2: Extract case links (reproducing enlaces_menores/enlaces_mayores)
        print("\n2. Extracting case links...")
        minor_case_links = extract_case_links_from_main_page(minors_main_page)  # enlaces_menores
        adult_case_links = extract_case_links_from_main_page(adults_main_page)  # enlaces_mayores
        
        print(f"Found {len(minor_case_links)} minor cases")
        print(f"Found {len(adult_case_links)} adult cases")
        
        # Step 3: Get column structure (reproducing obtener_col and column extraction)
        print("\n3. Determining data structure from sample case...")
        dataframe_columns = get_column_structure_from_sample_case(MISSING_MINORS_URL)  # columnas_df
        print(f"Extracted {len(dataframe_columns)} columns")
        
        # Step 4: Capture images for minors (reproducing matrices_fotos_menores)
        print("\n4. Capturing images for minor cases...")
        minor_image_matrices = capture_images_from_link_list(
            minor_case_links, 
            description="Procesando enlaces menores"
        )  # matrices_fotos_menores
        
        # Display sample minor images (reproducing mostrar_imagenes)
        if minor_image_matrices:
            print("Sample minor case images:")
            display_sample_images(minor_image_matrices, num_samples=5)
        
        # Step 5: Extract photo URLs for minors (reproducing Fotos_Menores)
        minor_photo_urls = extract_photo_urls_from_main_page(minors_main_page)  # Fotos_Menores
        
        # Step 6: Extract text data for minors (reproducing Info_menores loop)
        print("\n5. Extracting text data for minor cases...")
        minor_text_data, _, _ = scrape_missing_persons_text_data(MISSING_MINORS_URL, "minors")  # Info_menores
        
        # Step 7: Capture images for adults (reproducing matrices_fotos_mayores) 
        print("\n6. Capturing images for adult cases...")
        adult_image_matrices = capture_images_with_error_recovery(
            adult_case_links,
            description="Procesando enlaces mayores"
        )  # matrices_fotos_mayores
        
        # Display sample adult images (reproducing mostrar_imagenes)
        if adult_image_matrices:
            print("Sample adult case images:")
            display_sample_images(adult_image_matrices, num_samples=5)
        
        # Step 8: Extract photo URLs for adults (reproducing Fotos_Mayores)
        adult_photo_urls = extract_photo_urls_from_main_page(adults_main_page)  # Fotos_Mayores
        
        # Step 9: Extract text data for adults (reproducing Info_mayores loop)
        print("\n7. Extracting text data for adult cases...")
        adult_text_data, _, _ = scrape_missing_persons_text_data(MISSING_ADULTS_URL, "adults")  # Info_mayores
        
        # Step 10: Process and combine data (reproducing original data processing)
        print("\n8. Processing and combining data...")
        final_missing_persons_df = process_and_combine_all_data(
            minor_text_data, adult_text_data,
            minor_image_matrices, adult_image_matrices,
            minor_photo_urls, adult_photo_urls,
            dataframe_columns
        )
        
        # Step 11: Process found persons (reproducing Info_Ubicados processing)
        print("\n9. Processing found persons data...")
        found_persons_data = scrape_found_persons_data()
        found_persons_df = create_found_persons_dataframe(found_persons_data)
        
        # Step 12: Save data (reproducing original CSV saving)
        print("\n10. Saving data...")
        save_all_datasets(final_missing_persons_df, found_persons_df)
        
        # Print summary
        print("\n=== Data Collection Summary ===")
        print(f"Missing persons records: {len(final_missing_persons_df)}")
        print(f"Found persons records: {len(found_persons_df)}")
        print(f"Images captured: {len(minor_image_matrices) + len(adult_image_matrices)}")
        print(f"Data saved to: {RAW_DATA_DIR}")
        
        print("\n=== Data Collection Completed Successfully ===")
        
    except Exception as e:
        print(f"\nError during data collection: {e}")
        print("Please check the logs above for specific error details.")
        sys.exit(1)


def process_and_combine_all_data(minor_text_data: List[List[str]], 
                               adult_text_data: List[List[str]],
                               minor_images: List[np.ndarray], 
                               adult_images: List[np.ndarray],
                               minor_photo_urls: List[str],
                               adult_photo_urls: List[str],
                               column_names: List[str]) -> pd.DataFrame:
    """
    Process and combine all scraped data into final DataFrame
    
    Returns:
        Final DataFrame with all data combined
    """
    print("Combining text data and images...")
    
    # Combine text data and add images/URLs (reproducing Info_menores + Info_mayores logic)
    all_combined_data = []
    
    # Process minor cases (reproducing info_men construction)
    for i, minor_case_data in enumerate(minor_text_data):
        image_matrix = minor_images[i] if i < len(minor_images) else None
        photo_url = minor_photo_urls[i] if i < len(minor_photo_urls) else ''
        
        # Reproduce: info_men = datos + [foto_me] + [url_me]
        combined_case_info = minor_case_data + [image_matrix] + [photo_url]
        all_combined_data.append(combined_case_info)
    
    # Process adult cases (reproducing info_may construction)
    for i, adult_case_data in enumerate(adult_text_data):
        image_matrix = adult_images[i] if i < len(adult_images) else None
        photo_url = adult_photo_urls[i] if i < len(adult_photo_urls) else ''
        
        # Reproduce: info_may = datos + [foto_ma] + [url_ma]
        combined_case_info = adult_case_data + [image_matrix] + [photo_url]
        all_combined_data.append(combined_case_info)
    
    # Serialize images (reproducing serializar_imagenes)
    print("Serializing images...")
    all_images_for_serialization = [row[-2] for row in all_combined_data if row[-2] is not None]
    serialized_images = serialize_image_matrices(all_images_for_serialization)
    
    # Create DataFrame (reproducing df_menores and df_mayores creation and concat)
    print("Creating DataFrame...")
    
    # Prepare data for DataFrame
    processed_data_for_df = []
    serialized_index = 0
    
    for row in all_combined_data:
        # Replace image matrix with serialized version
        if row[-2] is not None:
            row_copy = row[:-2] + [serialized_images[serialized_index]] + [row[-1]]
            serialized_index += 1
        else:
            row_copy = row[:-2] + [''] + [row[-1]]
        
        processed_data_for_df.append(row_copy)
    
    # Create DataFrame with proper columns (reproducing columnas_df usage)
    df_columns = column_names[:-2] + ['img_serializada', 'url']  # Reproduce original naming
    missing_persons_df = pd.DataFrame(processed_data_for_df, columns=df_columns)
    
    # Convert images to JSON format (reproducing image_to_json application)
    print("Converting images to JSON format...")
    missing_persons_df['img_serializada'] = missing_persons_df['img_serializada'].apply(
        lambda x: convert_image_to_json(x) if x != '' else ''
    )
    
    # Normalize text data (reproducing Unicode normalization)
    print("Normalizing text data...")
    missing_persons_df = normalize_text_data(
        missing_persons_df, 
        exclude_columns=['img_serializada']
    )
    
    return missing_persons_df


def create_found_persons_dataframe(found_persons_data: List[List[str]]) -> pd.DataFrame:
    """
    Create DataFrame for found persons data
    
    Args:
        found_persons_data: List of [name, date, photo_url] for each found person
    
    Returns:
        DataFrame with found persons data
    """
    # Create DataFrame (reproducing df_ubicados creation)
    found_df = pd.DataFrame(found_persons_data, columns=["Nombre", "Fecha", "Img"])
    
    # Normalize text (reproducing original apply normalization)
    found_df = found_df.apply(lambda x: x.str.normalize('NFC') if x.dtype == "object" else x)
    
    return found_df


def save_all_datasets(missing_persons_df: pd.DataFrame, found_persons_df: pd.DataFrame):
    """
    Save all datasets to CSV files
    
    Args:
        missing_persons_df: Main missing persons dataset
        found_persons_df: Found persons dataset
    """
    # Create output directory path (reproducing original path structure)
    missing_persons_output_dir = os.path.join(RAW_DATA_DIR, "missing_persons")
    found_persons_output_dir = os.path.join(RAW_DATA_DIR, "found_persons")
    
    os.makedirs(missing_persons_output_dir, exist_ok=True)
    os.makedirs(found_persons_output_dir, exist_ok=True)
    
    # Save missing persons data (reproducing nombre_desaparecidos path and saving)
    missing_persons_file_path = os.path.join(missing_persons_output_dir, MISSING_PERSONS_FILENAME)
    save_dataframe_to_csv(
        missing_persons_df, 
        missing_persons_file_path, 
        separator=CSV_SEPARATOR, 
        encoding=CSV_ENCODING
    )
    
    # Save found persons data (reproducing nombre_ubicados path and saving)
    found_persons_file_path = os.path.join(found_persons_output_dir, FOUND_PERSONS_FILENAME)
    save_dataframe_to_csv(
        found_persons_df, 
        found_persons_file_path, 
        separator=CSV_SEPARATOR, 
        encoding=CSV_ENCODING
    )


if __name__ == "__main__":
    main_scraping_workflow()
