"""
Regression module for missing persons analysis
Contains multimodal regression analysis using structured data and face images
"""

from .target_generator import (
    SemanticTargetGenerator,
    filter_valid_data,
    load_and_prepare_regression_data
)

from .face_processor import (
    FaceProcessor,
    check_mtcnn_requirements,
    optimize_face_processing_memory
)

from .multimodal_model import (
    ResidualBlock,
    FaceFeatureExtractor,
    StructuredDataProcessor,
    MultimodalAttentionFusion,
    PredictionHead,
    MMReg,
    create_mmreg_model,
    count_model_parameters
)

from .data_handler import (
    StructuredFeatureProcessor,
    MultimodalDataset,
    MultimodalDataHandler,
    validate_data_consistency
)

from .trainer import (
    MultimodalTrainer,
    create_trainer,
    resume_training
)

from .evaluator import (
    RegressionEvaluator,
    evaluate_model_comprehensive
)

from .main_regression import (
    main_regression_workflow,
    create_output_directories,
    check_system_requirements
)

__all__ = [
    'main_regression_workflow',
    'SemanticTargetGenerator',
    'FaceProcessor',
    'MMReg',
    'MultimodalTrainer',
    'RegressionEvaluator',
    'create_mmreg_model',
    'create_trainer',
    'load_and_prepare_regression_data'
]

__version__ = "1.0.0"
__author__ = "Missing Persons Analysis Project"
__description__ = "Multimodal regression analysis module for missing persons intentionality prediction"