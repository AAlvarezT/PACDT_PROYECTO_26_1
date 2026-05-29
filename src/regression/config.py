"""
Configuration file for missing persons regression analysis
Contains model parameters, keywords for target generation, and training settings
FIXED: Completely removed any verbose parameters
"""

import os
import torch

# Base directories
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
REGRESSION_RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "regression")
REGRESSION_FIGURES_DIR = os.path.join(PROJECT_ROOT, "results", "figures", "regression")
REGRESSION_MODELS_DIR = os.path.join(PROJECT_ROOT, "results", "models", "regression")

# Input data file
INPUT_DATASET_FILENAME = "datos_combinados_geocodificados.csv"
INPUT_DATASET_PATH = os.path.join(PROCESSED_DATA_DIR, INPUT_DATASET_FILENAME)

# Device configuration
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {DEVICE}")
if DEVICE.type == 'cuda':
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Target variable generation using semantic analysis
TARGET_KEYWORDS = {
    # Keywords indicating INTENTIONAL disappearance (voluntary)
    'intentional': [
        "fugó", "se fugó", "se marchó", "abandono voluntario", "huida",
        "decidió irse", "salió de su casa", "salió por voluntad propia",
        "abandono", "abandono del hogar", "retiro", "reubicación voluntaria",
        "se alejó", "partió", "renunció"
    ],
    
    # Keywords indicating NON-INTENTIONAL disappearance (involuntary)  
    'non_intentional': [
        "desapareció", "sin paradero", "no regresó", "no volvió",
        "destino desconocido", "búsqueda", "alerta de búsqueda",
        "secuestrado", "secuestrada", "raptado", "raptada",
        "trata de personas", "privado de libertad", "se perdió", "extraviado"
    ]
}

# Verify balanced keywords (reproduce original assertion)
assert len(TARGET_KEYWORDS['intentional']) == len(TARGET_KEYWORDS['non_intentional']) == 15, \
    "Keyword lists are unbalanced"

# Text columns for target generation
TARGET_TEXT_COLUMNS = [
    'OTRAS OBSERVACIONES',
    'CIRCUNSTANCIAS'
]

# Structured features configuration
STRUCTURED_FEATURES = {
    'numeric_columns': [
        'age_numeric',
        'height_numeric',
        'hours_to_report_numeric',
        'hours_to_appear_numeric',
        'latitude',
        'longitude'
    ],
    
    'excluded_columns': [
        'serialized_image',
        'target_regression',
        'OTRAS OBSERVACIONES',
        'CIRCUNSTANCIAS'
    ]
}

# Column name mappings
COLUMN_MAPPINGS = {
    'age_cleaned': 'age_numeric',
    'height_cleaned': 'height_numeric', 
    'hours_to_report': 'hours_to_report_numeric',
    'hours_to_appear': 'hours_to_appear_numeric',
    'Latitud': 'latitude',
    'Longitud': 'longitude',
    'OTRAS OBSERVACIONES': 'other_observations',
    'CIRCUNSTANCIAS': 'circumstances',
    'serialized_image': 'serialized_image'
}

# SentenceTransformer configuration for target generation
SENTENCE_TRANSFORMER_CONFIG = {
    'model_name': 'paraphrase-multilingual-MiniLM-L12-v2',
    'embedding_size': 384,
    'normalize_embeddings': True
}

# Face detection and processing configuration
FACE_PROCESSING_CONFIG = {
    'mtcnn_params': {
        'image_size': 160,
        'margin': 20,
        'post_process': True
    },
    'default_face_tensor_shape': (3, 160, 160),
    'batch_size_face_processing': 32
}

# Model architecture configuration
MODEL_CONFIG = {
    'resnet_config': {
        'weights': 'DEFAULT',
        'trainable_layers': ['6', '7'],
        'feature_size': 2048
    },
    
    'face_projection': {
        'input_size': 2048,
        'hidden_size': 256,
        'output_size': 128,
        'dropout_rate': 0.3,
        'use_batch_norm': True
    },
    
    'structured_projection': {
        'hidden_size': 128,
        'use_batch_norm': True
    },
    
    'residual_blocks': {
        'num_blocks': 2,
        'hidden_size': 128,
        'dropout_rate': 0.3
    },
    
    'attention_config': {
        'embed_dim': 128,
        'num_heads': 4,
        'dropout': 0.2,
        'batch_first': True
    },
    
    'prediction_head': {
        'input_size': 256,
        'hidden_size': 64,
        'dropout_rate': 0.3,
        'use_sigmoid': True
    }
}

# Training configuration - COMPLETELY CLEAN
TRAINING_CONFIG = {
    'batch_size': 16,
    'epochs': 25,
    'test_size': 0.2,
    'random_state': 42,
    
    'optimizer': {
        'type': 'AdamW',
        'lr': 3e-4,
        'weight_decay': 2e-4
    },
    
    # FIXED: Scheduler config without ANY verbose parameter
    'scheduler': {
        'type': 'ReduceLROnPlateau',
        'factor': 0.5,
        'patience': 3,
        'monitor': 'val_rmse'
    },
    
    'loss_function': 'MSELoss',
    
    'early_stopping': {
        'patience': 5,
        'monitor': 'val_rmse',
        'min_delta': 1e-6
    }
}

# Data preprocessing configuration
DATA_PREPROCESSING = {
    'missing_value_strategy': {
        'numeric': 0,
        'categorical': 'Desconocido'
    },
    'scaling_method': 'StandardScaler',
    'categorical_encoding': 'one_hot',
    'drop_first_dummy': True
}

# Evaluation metrics
EVALUATION_METRICS = [
    'mse',
    'rmse',
    'mape',
    'mae',
    'r2_score'
]

# Validation configuration
VALIDATION_CONFIG = {
    'cross_validation': {
        'cv_folds': 5,
        'cv_scoring': 'neg_mean_squared_error'
    },
    'target_range': {
        'min_value': 0.0,
        'max_value': 1.0
    },
    'required_columns': [
        'OTRAS OBSERVACIONES',
        'CIRCUNSTANCIAS', 
        'serialized_image'
    ]
}

# Output files configuration
OUTPUT_FILES = {
    'best_model': 'best_mmreg_model.pt',
    'training_history': 'training_history.json',
    'evaluation_results': 'evaluation_results.json',
    'predictions': 'test_predictions.csv',
    'feature_importance': 'feature_importance.csv',
    'model_architecture': 'model_summary.txt'
}

# Visualization configuration
VISUALIZATION_CONFIG = {
    'figure_size': (12, 8),
    'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
    'save_formats': ['png', 'pdf', 'svg'],
    'dpi': 300,
    'plot_types': [
        'training_curves',
        'prediction_scatter',
        'residual_plots',
        'target_distribution',
        'feature_importance'
    ]
}

# Regex patterns for feature extraction
REGEX_PATTERNS = {
    'age_extraction': r'(\d+)',
    'height_extraction': r'(\d+\.?\d*)',
    'numeric_extraction': r'(\d+\.?\d*)'
}

# Model checkpointing configuration
CHECKPOINTING = {
    'save_best_only': True,
    'monitor': 'val_rmse',
    'mode': 'min',
    'save_frequency': 'epoch'
}

# Debugging and logging configuration
DEBUG_CONFIG = {
    'log_level': 'INFO',
    'save_intermediate_results': True,
    'plot_training_progress': True,
    'validate_data_quality': True
}