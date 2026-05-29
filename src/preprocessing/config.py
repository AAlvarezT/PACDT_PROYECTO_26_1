"""
Configuration file for missing persons data preprocessing
Contains paths, column mappings, and processing parameters
"""

import os
from datetime import datetime

# Base directories - relative paths for portability
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

# Input data directories
MISSING_PERSONS_RAW_DIR = os.path.join(RAW_DATA_DIR, "missing_persons")
FOUND_PERSONS_RAW_DIR = os.path.join(RAW_DATA_DIR, "found_persons")

# Output files
CONSOLIDATED_MISSING_FILENAME = "consolidated_missing_persons.csv"
CONSOLIDATED_FOUND_FILENAME = "consolidated_found_persons.csv"
FINAL_ANALYSIS_FILENAME = "final_analysis_dataset.csv"
GEOCODED_FILENAME = "datos_combinados_geocodificados.csv"

# CSV processing parameters
CSV_DELIMITER = ';'
CSV_ENCODING = 'utf-8-sig'

# Column name mappings (original -> standardized)
COLUMN_MAPPINGS = {
    # Personal information
    'NOMBRES': 'first_names',
    'APELLIDOS': 'last_names', 
    'EDAD': 'age_raw',
    'ESTATURA': 'height_raw',
    'SEXO': 'gender',
    'ESTADO CIVIL': 'marital_status',
    
    # Dates and times
    'Fecha': 'report_datetime_raw',
    'F./ NACIMIENTO': 'birth_datetime_raw', 
    'FECHA DEL HECHO': 'incident_datetime_raw',
    
    # Location information
    'DEPARTAMENTO': 'department',
    'PROVINCIA': 'province',
    'DISTRITO': 'district',
    'LUGAR DEL HECHO': 'incident_location',
    
    # Physical characteristics
    'CONTEXTURA': 'build',
    'TALLA': 'size',
    'PESO': 'weight_raw',
    'COLOR DE CABELLO': 'hair_color',
    'COLOR DE OJOS': 'eye_color',
    'TIPO DE CABELLO': 'hair_type',
    
    # Additional information
    'SEÑAS PARTICULARES': 'distinctive_marks',
    'VESTIMENTA': 'clothing',
    'OBSERVACIONES': 'observations',
    
    # Technical fields
    'url': 'photo_url',
    'img_serializada': 'serialized_image'
}

# Found persons column mappings
FOUND_PERSONS_COLUMNS = {
    'Nombre': 'full_name',
    'Fecha': 'found_datetime_raw', 
    'Img': 'photo_url'
}

# Data cleaning parameters
CLEANING_CONFIG = {
    'age_pattern': r'(\d+)',
    'height_pattern': r'(\d+\.?\d*)',
    'weight_pattern': r'(\d+\.?\d*)',
    'time_format_12h': '%I:%M:%S %p',
    'date_format': '%d/%m/%Y',
    'time_replacements': {
        'a.m.': 'AM',
        'p.m.': 'PM'
    },
    'columns_to_drop': ['last_names', 'report_datetime_raw', 'birth_datetime_raw', 'incident_datetime_raw']
}

# Feature engineering parameters
FEATURE_CONFIG = {
    'date_columns': [
        'incident_date',
        'report_date',
        'birth_date',
        'found_date'
    ],
    'time_columns': [
        'incident_time',
        'report_time',
        'birth_time',
        'found_time'
    ],
    'calculated_features': [
        'hours_to_appear',
        'hours_to_report',
        'appeared_status'
    ]
}

# Validation parameters
VALIDATION_CONFIG = {
    'required_columns': ['full_name', 'age_cleaned', 'gender'],
    'max_age': 120,
    'min_age': 0,
    'max_height': 250,
    'min_height': 50
}

# Geocoding parameters
GEOCODING_CONFIG = {
    'photon_api_url': 'https://photon.komoot.io/api/',
    'request_delay': 5,
    'max_retries': 3,
    'abreviaturas': {
        "URB": "Urbanización",
        "CPM": "Centro Poblado Menor",
        "IE": "Institución Educativa",
        "PSJ": "Pasaje",
        "ASENT": "Asentamiento",
        "H": "Humano",
        "MZ": "Manzana",
        "LT": "Lote",
        "AAHH": "Asentamiento Humano",
        "AV": "Avenida",
        "CDRA": "Cuadra",
        "N": "Número",
        "SN": "Sin Número"
    },
    'failed_addresses_filename': 'direcciones_no_encontradas.txt',
    'expected_shapefile_names': [
        'per_admbnda_adm3_ign_20200714.shp',
        'peru_distritos.shp',
        'peru_districts.shp'
    ]
}