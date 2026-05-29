 
"""
Clustering module for missing persons analysis
Contains multimodal clustering analysis using Gaussian Mixture Models
"""

from .feature_processor import (
    StructuredFeatureProcessor,
    load_and_validate_dataset
)

from .multimodal_embeddings import (
    ImageEmbeddingExtractor,
    TextEmbeddingExtractor,
    MultimodalEmbeddingExtractor,
    check_device_availability,
    optimize_memory_usage
)

from .clustering_models import (
    ModalityProcessor,
    GMMClusteringOptimizer,
    ClusteringEvaluator,
    ClusteringPipeline
)

from .visualization import (
    ClusteringVisualizer,
    create_clustering_report
)

from .config import (
    PROJECT_ROOT,
    PROCESSED_DATA_DIR,
    CLUSTERING_RESULTS_DIR,
    CLUSTERING_FIGURES_DIR,
    CLUSTERING_MODELS_DIR,
    INPUT_DATASET_FILENAME,
    INPUT_DATASET_PATH,
    DEVICE,
    TRAIN_TEST_CONFIG,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    TEXT_FEATURES,
    IMAGE_FEATURE,
    COLUMN_MAPPINGS,
    RANDOM_FOREST_CONFIG,
    BEST_RF_PARAMS,
    TOP_STRUCTURAL_FEATURES,
    IMAGE_EMBEDDING_CONFIG,
    TEXT_EMBEDDING_CONFIG,
    MODALITY_COMBINATIONS,
    GMM_CONFIG,
    EVALUATION_METRICS,
    VISUALIZATION_CONFIG,
    OUTPUT_FILES,
    DATA_PREPROCESSING,
    REGEX_PATTERNS,
    VALIDATION_CONFIG
)

from .main_clustering import (
    main_clustering_workflow,
    create_output_directories,
    save_all_results,
    display_clustering_summary,
    load_previous_results,
    validate_clustering_results,
    run_clustering_comparison_analysis
)

__all__ = [
    # Main classes
    'StructuredFeatureProcessor',
    'ImageEmbeddingExtractor', 
    'TextEmbeddingExtractor',
    'MultimodalEmbeddingExtractor',
    'ModalityProcessor',
    'GMMClusteringOptimizer',
    'ClusteringEvaluator',
    'ClusteringPipeline',
    'ClusteringVisualizer',
    
    # Main workflow functions
    'main_clustering_workflow',
    'create_output_directories',
    'save_all_results',
    'display_clustering_summary',
    'load_previous_results',
    'validate_clustering_results',
    'run_clustering_comparison_analysis',
    
    # Utility functions
    'load_and_validate_dataset',
    'check_device_availability',
    'optimize_memory_usage',
    'create_clustering_report',
    
    # Configuration constants
    'PROJECT_ROOT',
    'PROCESSED_DATA_DIR',
    'CLUSTERING_RESULTS_DIR',
    'CLUSTERING_FIGURES_DIR',
    'CLUSTERING_MODELS_DIR',
    'INPUT_DATASET_FILENAME',
    'INPUT_DATASET_PATH',
    'DEVICE',
    'TRAIN_TEST_CONFIG',
    'NUMERIC_FEATURES',
    'CATEGORICAL_FEATURES',
    'TEXT_FEATURES',
    'IMAGE_FEATURE',
    'COLUMN_MAPPINGS',
    'RANDOM_FOREST_CONFIG',
    'BEST_RF_PARAMS',
    'TOP_STRUCTURAL_FEATURES',
    'IMAGE_EMBEDDING_CONFIG',
    'TEXT_EMBEDDING_CONFIG',
    'MODALITY_COMBINATIONS',
    'GMM_CONFIG',
    'EVALUATION_METRICS',
    'VISUALIZATION_CONFIG',
    'OUTPUT_FILES',
    'DATA_PREPROCESSING',
    'REGEX_PATTERNS',
    'VALIDATION_CONFIG'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Missing Persons Analysis Project"
__description__ = "Multimodal clustering analysis module for missing persons data"

# Clustering workflow example usage:
"""
Example usage:

from src.clustering import main_clustering_workflow

# Run complete clustering analysis
results_df, workflow_info = main_clustering_workflow()

# Results will be saved to results/clustering/ directory
# Visualizations will be saved to results/figures/clustering/
"""