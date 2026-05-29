"""
Configuration file for missing persons clustering analysis
"""

import os
import torch

# Base directories
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
CLUSTERING_RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "clustering")
CLUSTERING_FIGURES_DIR = os.path.join(PROJECT_ROOT, "results", "figures", "clustering")
CLUSTERING_MODELS_DIR = os.path.join(PROJECT_ROOT, "results", "models", "clustering")

# Dataset configuration - CORREGIDO
INPUT_DATASET_FILENAME = "datos_combinados_geocodificados.csv"
INPUT_DATASET_PATH = os.path.join(PROCESSED_DATA_DIR, INPUT_DATASET_FILENAME)

# Device configuration for deep learning
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Train/test split parameters - CORREGIDO: usar el nombre correcto de la columna
TRAIN_TEST_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'stratify_column': 'appeared_status_binary'  # Se crea en el procesamiento
}

# Feature definitions - CORREGIDO: usar nombres reales del dataset actual
NUMERIC_FEATURES = [
    'age_cleaned',      # Del preprocessing (antes EDAD)
    'height_cleaned',   # Del preprocessing (antes Estatura)
    'hours_to_report',  # Del preprocessing (antes Horas para Denunciar)
    'hours_to_appear',  # Del preprocessing (antes Horas para Aparecer)
    'Latitud',          # Del geocoding
    'Longitud'          # Del geocoding
]

CATEGORICAL_FEATURES = [
    'Dependencia Policial',    # Del dataset actual
    'PAIS DE NACIMIENTO',      # Del dataset actual
    'incident_location',       # Del dataset actual (antes Lugar Hecho)
    'TEZ',                     # Del dataset actual (antes Tez)
    'FENOTIPO',               # Del dataset actual (antes Fenotipo)
    'OJOS',                   # Del dataset actual (antes Ojos)
    'SANGRE',                 # Del dataset actual (antes Sangre)
    'BOCA',                   # Del dataset actual (antes Boca)
    'NARIZ',                  # Del dataset actual (antes Nariz)
    'CABELLO',                # Del dataset actual (antes Cabello)
    'build'                   # Del dataset actual (antes Contextura)
    # Nota: 'sexo' no está en el dataset actual
]

# Text features for embedding - CORREGIDO: usar nombres reales del dataset
TEXT_FEATURES = {
    'clothing_description': 'clothing',              # Antes Vestimenta
    'other_observations': 'OTRAS OBSERVACIONES',     # Igual nombre
    'circumstances': 'CIRCUNSTANCIAS'                # Antes Circunstancias
}

# Image feature - CORREGIDO: usar nombre real del dataset
IMAGE_FEATURE = 'serialized_image'  # Antes photo_matrix

# Column mappings for backwards compatibility
COLUMN_MAPPINGS = {
    'Aparecido': 'appeared_status',
    'EDAD': 'age_cleaned',
    'Estatura': 'height_cleaned',
    'Horas para Denunciar': 'hours_to_report',
    'Horas para Aparecer': 'hours_to_appear',
    'Lugar Hecho': 'incident_location',
    'Tez': 'TEZ',
    'Fenotipo': 'FENOTIPO',
    'Ojos': 'OJOS',
    'Sangre': 'SANGRE',
    'Boca': 'BOCA',
    'Nariz': 'NARIZ',
    'Cabello': 'CABELLO',
    'Contextura': 'build',
    'Vestimenta': 'clothing',
    'Otras observaciones': 'OTRAS OBSERVACIONES',
    'Circunstancias': 'CIRCUNSTANCIAS',
    'photo_matrix': 'serialized_image'
}

# Random Forest configuration - CORREGIDO: hacer grid search opcional
RANDOM_FOREST_CONFIG = {
    'enabled': False,  # Por defecto usar parámetros fijos (más rápido)
    'param_grid': {
        'n_estimators': list(range(50, 201, 50)),
        'max_depth': list(range(5, 21, 5)),
        'min_samples_split': list(range(5, 21, 5)),
        'min_samples_leaf': list(range(5, 21, 5)),
        'max_features': [None, 'sqrt', 'log2'],
        'criterion': ['gini', 'entropy']
    },
    'cv_folds': 3,
    'scoring': 'accuracy',
    'n_jobs': -1,
    'random_state': 42,
    'top_features_count': 10
}

# Best RF parameters from grid search - ESTOS SON LOS RESULTADOS DEL GRID SEARCH
BEST_RF_PARAMS = {
    'criterion': 'entropy',
    'max_depth': 10,
    'max_features': None,
    'min_samples_leaf': 5,
    'min_samples_split': 5,
    'n_estimators': 100,
    'random_state': 42
}

# Top structural features from grid search - ESTOS SON LOS TOP FEATURES DEL CÓDIGO ORIGINAL
TOP_STRUCTURAL_FEATURES = [
    'hours_to_report',                                    # Antes Horas_para_Denunciar
    'Longitud',
    'Latitud',
    'age_cleaned',                                        # Antes EDAD_num
    'hours_to_appear',                                    # Antes Horas_para_Aparecer
    'height_cleaned',                                     # Antes Estatura_num
    'Dependencia Policial_REGPOL - CUSCO - DEPINCRI CUSCO',
    'NARIZ_RECTO',                                        # Antes Nariz_RECTO
    'TEZ_TRIGUEÑA',                                       # Antes Tez_TRIGUEÑA
    'TEZ_MESTIZO'                                         # Antes Tez_MESTIZO
]

# Image embedding config - DEL CÓDIGO ORIGINAL
IMAGE_EMBEDDING_CONFIG = {
    'model_name': 'resnet50',
    'pretrained': True,
    'embedding_size': 2048,
    'input_size': (224, 224),
    'normalization_mean': [0.485, 0.456, 0.406],
    'normalization_std': [0.229, 0.224, 0.225]
}

# Text embedding config - DEL CÓDIGO ORIGINAL
TEXT_EMBEDDING_CONFIG = {
    'model_name': 'paraphrase-multilingual-MiniLM-L12-v2',
    'embedding_size': 384,
    'show_progress': True
}

# Modality combinations - DEL CÓDIGO ORIGINAL
MODALITY_COMBINATIONS = {
    'A_Estructurada': ['structured'],                     # Antes A_Estructurada
    'B_Estruct_Texto': ['structured', 'text'],           # Antes B_Estruct_Texto
    'C_Estruct_Imagen': ['structured', 'image'],         # Antes C_Estruct_Imagen
    'D_Texto_Imagen': ['text', 'image'],                 # Antes D_Texto_Imagen
    'E_Todas_modalidades': ['structured', 'text', 'image'] # Antes E_Todas_modalidades
}

# GMM parameters - DEL CÓDIGO ORIGINAL
GMM_CONFIG = {
    'n_components_range': [2, 3, 4, 5],
    'covariance_types': ['full', 'diag', 'tied', 'spherical'],
    'random_state': 42,
    'max_iter': 100,
    'init_params': 'kmeans'
}

# Evaluation metrics
EVALUATION_METRICS = [
    'silhouette_score',
    'davies_bouldin_score',
    'calinski_harabasz_score'
]

# Data preprocessing - DEL CÓDIGO ORIGINAL
DATA_PREPROCESSING = {
    'missing_value_strategy': {
        'numeric': 0,
        'categorical': 'Desconocido',  # Del código original
        'text': ''
    },
    'nan_replacement': 0.0
}

# Regex patterns - DEL CÓDIGO ORIGINAL
REGEX_PATTERNS = {
    'age_extraction': r'(\d+)',        # Del código original
    'height_extraction': r'(\d+\.?\d*)', # Del código original (corregido)
    'numeric_extraction': r'(\d+\.?\d*)'
}

# Visualization config
VISUALIZATION_CONFIG = {
    'figure_size': (1200, 500),
    'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
    'save_formats': ['html', 'png'],
    'dpi': 300
}

# Output files
OUTPUT_FILES = {
    'clustering_results': 'clustering_results.csv',
    'feature_importance': 'feature_importance.csv',
    'evaluation_metrics': 'evaluation_metrics.json',
    'embeddings': 'embeddings.npz'
}

# Validation config
VALIDATION_CONFIG = {
    'min_silhouette_score': -1.0,
    'max_silhouette_score': 1.0,
    'min_clusters': 2,
    'max_clusters': 10,
    'warning_threshold_silhouette': 0.1
}
