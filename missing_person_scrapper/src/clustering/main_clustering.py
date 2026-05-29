"""
Main clustering script for missing persons analysis
Orchestrates the complete clustering workflow including multimodal embeddings and GMM optimization
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import json

# Local imports
from .config import (
    INPUT_DATASET_PATH, CLUSTERING_RESULTS_DIR, OUTPUT_FILES,
    CLUSTERING_FIGURES_DIR, CLUSTERING_MODELS_DIR
)
from .feature_processor import StructuredFeatureProcessor, load_and_validate_dataset
from .multimodal_embeddings import MultimodalEmbeddingExtractor, check_device_availability, optimize_memory_usage
from .clustering_models import ClusteringPipeline
from .visualization import ClusteringVisualizer, create_clustering_report


def main_clustering_workflow() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    
    
    Returns:
        Tuple of (results_dataframe, workflow_info)
    """
    print("=== Missing Persons Clustering Analysis Started ===")
    
    try:
        # Setup
        create_output_directories()
        check_device_availability()
        optimize_memory_usage()
        
        # Step 1: Load and validate dataset
        print("\n1. Loading and validating dataset...")
        if not os.path.exists(INPUT_DATASET_PATH):
            raise FileNotFoundError(f"Input dataset not found: {INPUT_DATASET_PATH}")
        
        missing_persons_df = load_and_validate_dataset(INPUT_DATASET_PATH)
        
        # Step 2: Process structured features
        print("\n2. Processing structured features...")
        feature_processor = StructuredFeatureProcessor()
        
        (structured_train, structured_test, y_train, y_test, 
         top_feature_names, validation_metrics) = feature_processor.process_structured_features(missing_persons_df)
        
        # Get train/test DataFrames for embedding extraction
        df_with_target = feature_processor.create_target_variable(missing_persons_df)
        train_df, test_df = feature_processor.perform_train_test_split(df_with_target)
        
        # Step 3: Extract multimodal embeddings
        print("\n3. Extracting multimodal embeddings...")
        embedding_extractor = MultimodalEmbeddingExtractor()
        
        embeddings = embedding_extractor.extract_all_embeddings(train_df, test_df)
        
        # Validate embeddings
        embedding_validation = embedding_extractor.validate_embeddings(embeddings)
        print("Embedding validation results:")
        for modality, validation_info in embedding_validation.items():
            print(f"  {modality}: {validation_info['train_shape']} -> {validation_info['test_shape']}")
        
        # Step 4: Run clustering analysis
        print("\n4. Running clustering analysis...")
        clustering_pipeline = ClusteringPipeline()
        
        results_df, clustering_info = clustering_pipeline.run_complete_clustering_analysis(
            (structured_train, structured_test),
            embeddings['image'],
            embeddings['text']
        )
        
        # Step 5: Create visualizations
        print("\n5. Creating visualizations...")
        visualizer = ClusteringVisualizer()
        figures = visualizer.create_all_visualizations(results_df, save_plots=True)
        
        # Step 6: Save results and create report
        print("\n6. Saving results and creating report...")
        save_all_results(results_df, clustering_info, embedding_validation, validation_metrics)
        
        # Create and save text report
        text_report = create_clustering_report(results_df, clustering_info)
        report_path = os.path.join(CLUSTERING_RESULTS_DIR, "clustering_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        print(f"Text report saved: {report_path}")
        
        # Step 7: Display summary
        print("\n=== Clustering Analysis Summary ===")
        display_clustering_summary(results_df, clustering_info)
        
        # Prepare workflow info
        workflow_info = {
            'validation_metrics': validation_metrics,
            'embedding_validation': embedding_validation,
            'clustering_info': clustering_info,
            'feature_summary': feature_processor.get_feature_summary(),
            'top_feature_names': top_feature_names,
            'figures': figures
        }
        
        print("\n=== Clustering Analysis Completed Successfully ===")
        
        return results_df, workflow_info
        
    except Exception as e:
        print(f"\nError during clustering analysis: {e}")
        print("Please check the logs above for specific error details.")
        sys.exit(1)


def create_output_directories() -> None:
    """Create necessary output directories"""
    directories = [
        CLUSTERING_RESULTS_DIR,
        CLUSTERING_FIGURES_DIR,
        CLUSTERING_MODELS_DIR
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")


def save_all_results(results_df: pd.DataFrame, clustering_info: Dict[str, Any], 
                    embedding_validation: Dict[str, Dict], validation_metrics: Dict[str, float]) -> None:
    """
    Save all clustering results to files
    
    Args:
        results_df: Clustering results DataFrame
        clustering_info: Additional clustering information
        embedding_validation: Embedding validation results
        validation_metrics: Feature validation metrics
    """
    print("Saving clustering results...")
    
    # Save main results DataFrame
    results_path = os.path.join(CLUSTERING_RESULTS_DIR, OUTPUT_FILES['clustering_results'])
    results_df.to_csv(results_path, index=False, encoding='utf-8-sig')
    print(f"Saved clustering results: {results_path}")
    
    # Save feature importance if available
    if 'feature_importance_scores' in clustering_info.get('models', {}):
        feature_importance_path = os.path.join(CLUSTERING_RESULTS_DIR, OUTPUT_FILES['feature_importance'])
        feature_importance_df = pd.DataFrame({
            'feature': clustering_info['feature_importance_scores'].keys(),
            'importance': clustering_info['feature_importance_scores'].values()
        }).sort_values('importance', ascending=False)
        feature_importance_df.to_csv(feature_importance_path, index=False)
        print(f"Saved feature importance: {feature_importance_path}")
    
    # Save evaluation metrics as JSON
    evaluation_metrics = {
        'clustering_results': results_df.to_dict('records'),
        'embedding_validation': embedding_validation,
        'validation_metrics': validation_metrics,
        'best_modality': {
            'name': results_df.loc[results_df['Sil_test'].idxmax(), 'Modalidad'],
            'silhouette_score': results_df['Sil_test'].max(),
            'davies_bouldin': results_df.loc[results_df['Sil_test'].idxmax(), 'DB_test']
        }
    }
    
    metrics_path = os.path.join(CLUSTERING_RESULTS_DIR, OUTPUT_FILES['evaluation_metrics'])
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_metrics, f, indent=2, default=str)
    print(f"Saved evaluation metrics: {metrics_path}")


def display_clustering_summary(results_df: pd.DataFrame, clustering_info: Dict[str, Any]) -> None:
    """
    Display summary of clustering analysis
    
    Args:
        results_df: Clustering results DataFrame
        clustering_info: Additional clustering information
    """
    print(f"Total modalities analyzed: {len(results_df)}")
    print(f"Modalities: {', '.join(results_df['Modalidad'].tolist())}")
    
    # Best performing modality
    best_idx = results_df['Sil_test'].idxmax()
    best_modality = results_df.loc[best_idx]
    
    print(f"\nBest performing modality: {best_modality['Modalidad']}")
    print(f"  - Optimal clusters: {best_modality['k_opt']}")
    print(f"  - Covariance type: {best_modality['cov_opt']}")
    print(f"  - Test silhouette score: {best_modality['Sil_test']:.4f}")
    print(f"  - Davies-Bouldin index: {best_modality['DB_test']:.4f}")
    
    # Summary statistics
    print(f"\nSummary statistics:")
    print(f"  - Average test silhouette: {results_df['Sil_test'].mean():.4f}")
    print(f"  - Standard deviation: {results_df['Sil_test'].std():.4f}")
    print(f"  - Average Davies-Bouldin: {results_df['DB_test'].mean():.4f}")
    
    # Cluster distribution
    cluster_counts = results_df['k_opt'].value_counts().sort_index()
    print(f"\nOptimal cluster distribution:")
    for k, count in cluster_counts.items():
        print(f"  - {k} clusters: {count} modalities")
    
    # Covariance type distribution
    cov_counts = results_df['cov_opt'].value_counts()
    print(f"\nCovariance type distribution:")
    for cov_type, count in cov_counts.items():
        print(f"  - {cov_type}: {count} modalities")


def load_previous_results(results_path: str) -> Tuple[pd.DataFrame, bool]:
    """
    Load previous clustering results if available
    
    Args:
        results_path: Path to previous results file
        
    Returns:
        Tuple of (results_df, results_loaded)
    """
    if os.path.exists(results_path):
        try:
            results_df = pd.read_csv(results_path)
            print(f"Loaded previous results from: {results_path}")
            return results_df, True
        except Exception as e:
            print(f"Error loading previous results: {e}")
            return pd.DataFrame(), False
    else:
        return pd.DataFrame(), False


def validate_clustering_results(results_df: pd.DataFrame) -> bool:
    """
    Validate clustering results meet expected criteria
    
    Args:
        results_df: DataFrame with clustering results
        
    Returns:
        True if validation passes, False otherwise
    """
    validation_checks = []
    
    # Check required columns
    required_columns = ['Modalidad', 'k_opt', 'cov_opt', 'Sil_train', 'Sil_test', 'DB_test']
    missing_columns = [col for col in required_columns if col not in results_df.columns]
    
    if missing_columns:
        print(f"Validation failed: Missing required columns: {missing_columns}")
        validation_checks.append(False)
    else:
        validation_checks.append(True)
    
    # Check data ranges
    if 'Sil_test' in results_df.columns:
        if (results_df['Sil_test'] < -1).any() or (results_df['Sil_test'] > 1).any():
            print("Validation warning: Silhouette scores outside valid range [-1, 1]")
    
    if 'k_opt' in results_df.columns:
        if (results_df['k_opt'] < 2).any() or (results_df['k_opt'] > 10).any():
            print("Validation warning: Cluster counts outside reasonable range [2, 10]")
    
    # Check for reasonable performance
    if 'Sil_test' in results_df.columns:
        if results_df['Sil_test'].max() < 0.1:
            print("Validation warning: All silhouette scores are very low (< 0.1)")
    
    return all(validation_checks)


def run_clustering_comparison_analysis(results_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Run additional comparison analysis between modalities
    
    Args:
        results_df: DataFrame with clustering results
        
    Returns:
        Dictionary with comparison analysis results
    """
    print("Running modality comparison analysis...")
    
    comparison_analysis = {}
    
    # Rank modalities by different metrics
    comparison_analysis['silhouette_ranking'] = results_df.nlargest(5, 'Sil_test')[['Modalidad', 'Sil_test']].to_dict('records')
    comparison_analysis['davies_bouldin_ranking'] = results_df.nsmallest(5, 'DB_test')[['Modalidad', 'DB_test']].to_dict('records')
    
    # Stability analysis (train vs test silhouette)
    results_df['silhouette_stability'] = abs(results_df['Sil_train'] - results_df['Sil_test'])
    comparison_analysis['most_stable'] = results_df.nsmallest(3, 'silhouette_stability')[['Modalidad', 'silhouette_stability']].to_dict('records')
    
    # Modality complexity (number of features)
    modality_complexity = {
        'A_Structured': 'Low',
        'B_Structured_Text': 'Medium',
        'C_Structured_Image': 'High',
        'D_Text_Image': 'High',
        'E_All_Modalities': 'Very High'
    }
    
    results_df['complexity'] = results_df['Modalidad'].map(modality_complexity)
    comparison_analysis['complexity_performance'] = results_df.groupby('complexity')['Sil_test'].mean().to_dict()
    
    return comparison_analysis


if __name__ == "__main__":
    # Run main clustering workflow
    results, workflow_info = main_clustering_workflow()
    
    # Validate results
    if validate_clustering_results(results):
        print("✓ Clustering validation passed")
        
        # Run additional comparison analysis
        comparison_analysis = run_clustering_comparison_analysis(results)
        print("\n=== Modality Comparison Analysis ===")
        print(f"Best silhouette performer: {comparison_analysis['silhouette_ranking'][0]['Modalidad']}")
        print(f"Most stable modality: {comparison_analysis['most_stable'][0]['Modalidad']}")
        
    else:
        print("✗ Clustering validation failed")
        sys.exit(1)
