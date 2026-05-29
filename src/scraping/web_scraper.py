"""
Web scraping module for missing persons data
Handles data extraction from police website pages
"""

import requests
import urllib3
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm
from typing import List, Dict, Tuple, Any
from .config import (
    REQUEST_HEADERS, MISSING_ADULTS_URL, MISSING_MINORS_URL, 
    FOUND_PERSONS_URL, BASE_URL, PHOTO_CSS_CLASS,
    DETAIL_SECTION_CLASS, AGENCY_SECTION_STYLE, PERSON_DATA_STYLE,
    BORDER_DIV_STYLE, ADDITIONAL_INFO_STYLE
)

# Disable SSL warnings (reproducing original)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_page_soup(url: str) -> BeautifulSoup:
    """
    Fetch and parse webpage content
    
    Args:
        url: URL to fetch
    
    Returns:
        BeautifulSoup object of parsed HTML
    """
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, verify=False)
        content = response.content.decode('utf-8')
        return BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        raise


def extract_case_links_from_main_page(main_page_soup: BeautifulSoup) -> List[str]:
    """
    Extract individual case links from main listing page
    
    Args:
        main_page_soup: BeautifulSoup object of main page
    
    Returns:
        List of full URLs to individual case pages
    """
    case_links = []
    
    # Reproduce original logic: enlaces_menores = ['https://...' + enlace.get('href') ...]
    for link_element in main_page_soup.find_all('a', href=True):
        href_value = link_element.get('href')
        if href_value and href_value.startswith('/Desaparecidos/nota_alerta_menor/'):
            full_case_url = BASE_URL + href_value
            case_links.append(full_case_url)
    
    return case_links


def extract_photo_urls_from_main_page(main_page_soup: BeautifulSoup) -> List[str]:
    """
    Extract photo URLs from main listing page
    
    Args:
        main_page_soup: BeautifulSoup object of main page
    
    Returns:
        List of photo URLs
    """
    # Reproduce: Fotos_Menores = [b.get('src') for b in menores.find_all('img', {'class': 'adaptive-image foto-desa'})]
    photo_urls = [
        img.get('src') 
        for img in main_page_soup.find_all('img', {'class': PHOTO_CSS_CLASS})
    ]
    
    return photo_urls


def extract_case_data_from_detail_page(case_url: str) -> List[str]:
    """
    Extract detailed information from individual case page
    
    Args:
        case_url: URL of individual case page
    
    Returns:
        List of extracted data fields
    """
    try:
        case_soup = fetch_page_soup(case_url)
        
        # Reproduce original: div_general_datos = sopa.find_all('p', {'class': 'detalle-desaparecidos-p1'})
        detail_sections = case_soup.find_all('p', {'class': DETAIL_SECTION_CLASS})
        
        if len(detail_sections) < 2:
            print(f"Insufficient data sections in {case_url}")
            return []
        
        agency_data_section = detail_sections[0]  # div_datos_dependencia
        person_data_section = detail_sections[1]  # div_datos_persona
        
        # Reproduce original: a1 = sopa.find_all('div',{'style':'border: 1px solid #949393; margin-bottom: 15px;'})
        border_divs = case_soup.find_all('div', {'style': BORDER_DIV_STYLE})
        additional_info_section = border_divs[1] if len(border_divs) > 1 else None  # div_info_adicional
        
        # Reproduce original: tablas = sopa.find_all('table')
        all_tables = case_soup.find_all('table')
        characteristics_table = all_tables[2] if len(all_tables) > 2 else None
        distinctive_marks_table = all_tables[3] if len(all_tables) > 3 else None
        
        # Extract agency data (reproducing datos_dependencia)
        agency_data = [
            info.text.strip() 
            for info in agency_data_section.find_all('b', {'style': AGENCY_SECTION_STYLE})
        ]
        
        # Extract personal data (reproducing datos_personal)
        personal_data = [
            data.text.strip() 
            for data in person_data_section.find_all('b', {'style': PERSON_DATA_STYLE})
        ]
        
        # Extract characteristics data (reproducing datos_caracteristicas)
        characteristics_data = []
        if characteristics_table:
            characteristics_data = [
                b.text.strip() 
                for tr in characteristics_table.find_all('tr') 
                for td in tr.find_all('td') 
                for b in td.find_all('b') 
                if 'color: #174e75;' in b.get('style', '')
            ]
        
        # Extract distinctive marks (reproducing datos_señas_particulares)
        distinctive_marks_data = []
        if distinctive_marks_table:
            distinctive_marks_data = [
                td.text.strip() 
                for td in distinctive_marks_table.find_all('td', {'style': PERSON_DATA_STYLE})
            ]
        
        # Extract additional information (reproducing datos_info_adicional)
        additional_info_data = []
        if additional_info_section:
            additional_info_data = [
                info.text.strip(' : ') 
                for info in additional_info_section.find_all('b', {'style': ADDITIONAL_INFO_STYLE})
            ]
        
        # Combine all extracted data (reproducing info_men/info_may combination)
        combined_case_data = (agency_data + personal_data + characteristics_data + 
                             distinctive_marks_data + additional_info_data)
        
        return combined_case_data
        
    except Exception as e:
        print(f"Error extracting data from {case_url}: {e}")
        return []


def scrape_missing_persons_text_data(category_url: str, category_name: str) -> Tuple[List[List[str]], List[str], List[str]]:
    """
    Scrape all text data from a specific category (minors or adults)
    
    Args:
        category_url: URL of the category page
        category_name: Name for progress tracking
    
    Returns:
        Tuple of (case_data_list, case_links, photo_urls)
    """
    print(f"Scraping {category_name} cases...")
    
    # Fetch main category page (reproducing original menores/mayores = bs(...))
    main_page_soup = fetch_page_soup(category_url)
    
    # Extract case links (reproducing enlaces_menores/enlaces_mayores)
    case_links = extract_case_links_from_main_page(main_page_soup)
    
    # Extract photo URLs (reproducing Fotos_Menores/Fotos_Mayores)
    photo_urls = extract_photo_urls_from_main_page(main_page_soup)
    
    print(f"Found {len(case_links)} {category_name} cases to process")
    
    # Extract detailed data from each case (reproducing Info_menores/Info_mayores loop)
    all_case_data = []
    
    for i in tqdm(range(len(case_links)), desc=f"Processing {category_name}"):
        case_data = extract_case_data_from_detail_page(case_links[i])
        
        if case_data:
            all_case_data.append(case_data)
        else:
            print(f"No data extracted for case {i+1}: {case_links[i]}")
        
        # Rate limiting (reproducing original time.sleep(1))
        time.sleep(1)
    
    return all_case_data, case_links, photo_urls


def scrape_found_persons_data() -> List[List[str]]:
    """
    Scrape data about found persons
    
    Returns:
        List of [name, date, photo_url] for each found person
    """
    print("Scraping found persons data...")
    
    # Fetch found persons page (reproducing ubicados = bs(...))
    found_page_soup = fetch_page_soup(FOUND_PERSONS_URL)
    
    # Extract data elements (reproducing original extraction)
    found_names = found_page_soup.find_all('h5')  # nombres
    found_dates = found_page_soup.find_all('p')   # hora
    found_photos = found_page_soup.find_all('img', {'class': PHOTO_CSS_CLASS})  # foto
    
    # Process found persons data (reproducing Info_Ubicados loop)
    found_persons_data = []
    
    for i in range(len(found_names)):
        person_name = found_names[i].text
        occurrence_date = found_dates[i].text.strip('Hecho ocurrido el:')
        photo_source = found_photos[i].get('src')
        
        found_persons_data.append([person_name, occurrence_date, photo_source])
    
    print(f"Found {len(found_persons_data)} records of found persons")
    
    return found_persons_data


def get_column_structure_from_sample_case(sample_category_url: str) -> List[str]:
    """
    Extract column names from a sample case page
    
    Args:
        sample_category_url: URL of category to sample from
    
    Returns:
        List of column names for DataFrame creation
    """
    main_page_soup = fetch_page_soup(sample_category_url)
    case_links = extract_case_links_from_main_page(main_page_soup)
    
    if not case_links:
        raise ValueError(f"No case links found in {sample_category_url}")
    
    # Use first case as sample (reproducing obtener_col = enlaces_menores[1])
    sample_case_url = case_links[0]  # Using index 0 for safety
    sample_case_soup = fetch_page_soup(sample_case_url)
    
    # Extract column structure directly (function is in same file)
    return extract_dataframe_columns_from_sample(sample_case_soup)


def extract_dataframe_columns_from_sample(soup_sample) -> List[str]:
    """
    Extract column names from a sample page structure
    
    Args:
        soup_sample: BeautifulSoup object of sample page
    
    Returns:
        List of column names for DataFrame creation
    """
    from .config import (DETAIL_SECTION_CLASS, AGENCY_SECTION_STYLE, 
                       BORDER_DIV_STYLE, ADDITIONAL_INFO_STYLE, AGENCY_HEADER_STYLE)
    
    # Extract main data sections (reproducing original div_general)
    detail_sections = soup_sample.find_all('p', {'class': DETAIL_SECTION_CLASS})
    
    if len(detail_sections) < 3:
        # Try to handle case with only 2 sections
        if len(detail_sections) >= 2:
            detail_sections.append(None)  # Add placeholder for missing section
        else:
            raise ValueError("Insufficient page structure for column extraction")
    
    agency_info_section = detail_sections[0]  # div_col_dependencia
    person_info_section = detail_sections[1]  # div_col_persona
    additional_info_section = detail_sections[2]  # div_info_adicional_col
    
    # Extract tables (reproducing original tablas_col)
    all_tables = soup_sample.find_all('table')
    if len(all_tables) < 4:
        print(f"Warning: Only found {len(all_tables)} tables, expected at least 4")
        # Pad with None values if not enough tables
        while len(all_tables) < 4:
            all_tables.append(None)
    
    characteristics_table = all_tables[2] if all_tables[2] is not None else None  # caracteristicas_col
    distinctive_marks_table = all_tables[3] if all_tables[3] is not None else None  # señas_particulares_col
    
    # Extract border divs (reproducing original 'a')
    border_divs = soup_sample.find_all('div', {'style': BORDER_DIV_STYLE})
    
    # Extract agency information columns (reproducing col_dependencia)
    agency_columns = [
        col.text.strip(' : ').strip() 
        for col in agency_info_section.find_all('b', {'style': 'font-family: arial; font-size: 20px; color: #000000; text-transform: uppercase;'})
    ]
    
    # Extract person data columns (reproducing col_datos_persona)
    person_data_columns = [
        col.text.strip(':').strip() 
        for col in person_info_section.find_all('b') 
        if ':' in col.text and ':00' not in col.text
    ]
    
    # Extract characteristics columns (reproducing col_caracteristicas)
    characteristics_columns = []
    if characteristics_table is not None:
        characteristics_columns = [
            td.text.strip(':').strip() 
            for tr in characteristics_table.find_all('tr') 
            for td in tr.find_all('td') 
            if ':' in td.text
        ]
    
    # Extract distinctive marks columns (reproducing col_señas_particulares)
    distinctive_marks_columns = []
    if distinctive_marks_table is not None:
        distinctive_marks_columns = [
            td.text.strip(':').strip() 
            for tr in distinctive_marks_table.find_all('tr') 
            for td in tr.find_all('td') 
            if ':' in td.text
        ]
    
    # Handle special case for distinctive marks (reproducing original logic)
    if len(distinctive_marks_columns) > 3:
        distinctive_marks_columns = [
            distinctive_marks_columns[0],
            distinctive_marks_columns[1], 
            distinctive_marks_columns[-1]
        ]
    
    # Extract additional info columns (reproducing col_info_adicional)
    additional_info_columns = []
    if len(border_divs) > 1 and border_divs[1] is not None:
        additional_info_columns = [
            text.text.strip(' : ') 
            for text in border_divs[1].find_all('b') 
            if ':' in text.text
        ]
    
    # Combine all columns (reproducing columnas_df)
    all_column_names = (agency_columns + person_data_columns + characteristics_columns + 
                       distinctive_marks_columns + additional_info_columns + 
                       ['img', 'url'])
    
    return all_column_names
