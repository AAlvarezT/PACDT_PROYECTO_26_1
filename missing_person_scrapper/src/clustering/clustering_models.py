"""
Clustering models module for missing persons analysis
Implements Gaussian Mixture Models with hyperparameter optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from tqdm import tqdm
import joblib
import os

from .config import (
    GMM_CONFIG, MODALITY_COMBINATIONS, EVALUATION_METRICS,
    DATA_PREPROCESSING, CLUSTERING_MODELS_DIR
)


class ModalityProcessor:
    """
    Processes and combines different data modalities for clustering
    Reproduces the original modality combination logic
    """
    
    def __init__(self):
        self.scalers = {}
        self.modality_combinations = MODALITY_COMBINATIONS
    
    def scale_modalities(self, structured_features: Tuple[np.ndarray, np.ndarray],
                        image_embeddings: Tuple[np.ndarray, np.ndarray],
                        text_embeddings: Tuple[np.ndarray, np.ndarray]) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """
        Scale all modalities using StandardScaler
        Reproduces the original scaling logic: StandardScaler().fit_transform(...)
        
        Args:
            structured_features: Tuple of (train, test) structured features
            image_embeddings: Tuple of (train, test) image embeddings
            text_embeddings: Tuple of (train, test) text embeddings
            
        Returns:
            Dictionary with scaled modalities
        """
        print("Scaling modalities...")
        
        struct_train, struct_test = structured_features
        img_train, img_test = image_embeddings
        text_train, text_test = text_embeddings
        
        # Reproduce original scaling logic
        # sc_struct = StandardScaler().fit(struct_train)
        scaler_struct = StandardScaler().fit(struct_train)
        scaler_img = StandardScaler().fit(img_train)
        scaler_text = StandardScaler().fit(text_train)
        
        # Store scalers for later use
        self.scalers = {
            'structured': scaler_struct,
            'image': scaler_img,
            'text': scaler_text
        }
        
        # Apply scaling (reproduce original transform logic)
        scaled_struct_train = scaler_struct.transform(struct_train)
        scaled_img_train = scaler_img.transform(img_train)
        scaled_text_train = scaler_text.transform(text_train)
        
        scaled_struct_test = scaler_struct.transform(struct_test)
        scaled_img_test = scaler_img.transform(img_test)
        scaled_text_test = scaler_text.transform(text_test)
        
        scaled_modalities = {
            'structured': (scaled_struct_train, scaled_struct_test),
            'image': (scaled_img_train, scaled_img_test),
            'text': (scaled_text_train, scaled_text_test)
        }
        
        print("Modality scaling complete")
        return scaled_modalities
    
    def combine_modalities(self, scaled_modalities: Dict[str, Tuple[np.ndarray, np.ndarray]]) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """
        Combine modalities according to predefined combinations
        Reproduces the original modalidades dictionary creation
        
        Args:
            scaled_modalities: Dictionary with scaled modalities
            
        Returns:
            Dictionary with combined modalities
        """
        print("Combining modalities...")
        
        struct_train, struct_test = scaled_modalities['structured']
        img_train, img_test = scaled_modalities['image']
        text_train, text_test = scaled_modalities['text']
        
        # Reproduce original modalidades dictionary
        combined_modalities = {}
        
        for combination_name, modality_list in self.modality_combinations.items():
            train_parts = []
            test_parts = []
            
            for modality in modality_list:
                if modality == 'structured':
                    train_parts.append(struct_train)
                    test_parts.append(struct_test)
                elif modality == 'image':
                    train_parts.append(img_train)
                    test_parts.append(img_test)
                elif modality == 'text':
                    train_parts.append(text_train)
                    test_parts.append(text_test)
            
            # Combine using np.hstack (reproduce original logic)
            if len(train_parts) == 1:
                combined_train = train_parts[0]
                combined_test = test_parts[0]
            else:
                combined_train = np.hstack(train_parts)
                combined_test = np.hstack(test_parts)
            
            combined_modalities[combination_name] = (combined_train, combined_test)
        
        print(f"Created {len(combined_modalities)} modality combinations")
        return combined_modalities
    
    def handle_missing_values(self, combined_modalities: Dict[str, Tuple[np.ndarray, np.ndarray]]) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """
        Handle missing values in combined modalities
        Reproduces: np.nan_to_num(X_tr, nan=0.0)
        
        Args:
            combined_modalities: Dictionary with combined modalities
            
        Returns:
            Dictionary with cleaned modalities
        """
        print("Handling missing values...")
        
        cleaned_modalities = {}
        
        for name, (X_train, X_test) in combined_modalities.items():
            # Reproduce original: np.nan_to_num(X_tr, nan=0.0)
            cleaned_train = np.nan_to_num(X_train, nan=DATA_PREPROCESSING['nan_replacement'])
            cleaned_test = np.nan_to_num(X_test, nan=DATA_PREPROCESSING['nan_replacement'])
            
            cleaned_modalities[name] = (cleaned_train, cleaned_test)
        
        print("Missing value handling complete")
        return cleaned_modalities


class GMMClusteringOptimizer:
    """
    Optimizes Gaussian Mixture Model hyperparameters for each modality
    Reproduces the original GMM optimization logic
    """
    
    def __init__(self):
        self.n_components_range = GMM_CONFIG['n_components_range']
        self.covariance_types = GMM_CONFIG['covariance_types']
        self.random_state = GMM_CONFIG['random_state']
        self.best_models = {}
    
    def optimize_single_modality(self, X_train: np.ndarray, modality_name: str) -> Dict[str, Any]:
        """
        Optimize GMM hyperparameters for a single modality
        Reproduces the original nested loop optimization logic
        
        Args:
            X_train: Training data for the modality
            modality_name: Name of the modality
            
        Returns:
            Dictionary with best parameters and score
        """
        print(f"Optimizing GMM for {modality_name}...")
        
        # Reproduce original: best = {'sil':-1, 'k':None, 'cov':None}
        best_config = {
            'silhouette_score': -1,
            'n_components': None,
            'covariance_type': None,
            'model': None
        }
        
        # Reproduce original nested loops: for k in [2,3,4,5]: for cov in [...]
        for n_components in self.n_components_range:
            for covariance_type in self.covariance_types:
                try:
                    # Create and fit GMM (reproduce original)
                    gmm = GaussianMixture(
                        n_components=n_components,
                        covariance_type=covariance_type,
                        random_state=self.random_state,
                        max_iter=GMM_CONFIG['max_iter'],
                        init_params=GMM_CONFIG['init_params']
                    )
                    
                    # Fit and predict (reproduce original: gmm.fit_predict(X_tr))
                    cluster_labels = gmm.fit_predict(X_train)
                    
                    # Calculate silhouette score (reproduce original)
                    if len(np.unique(cluster_labels)) > 1:  # Need at least 2 clusters
                        silhouette_avg = silhouette_score(X_train, cluster_labels)
                        
                        # Update best if better (reproduce original: if sil > best['sil'])
                        if silhouette_avg > best_config['silhouette_score']:
                            best_config.update({
                                'silhouette_score': silhouette_avg,
                                'n_components': n_components,
                                'covariance_type': covariance_type,
                                'model': gmm
                            })
                    
                except Exception as e:
                    print(f"Warning: Failed to fit GMM with k={n_components}, cov={covariance_type}: {e}")
                    continue
        
        if best_config['model'] is None:
            raise ValueError(f"Failed to find valid GMM configuration for {modality_name}")
        
        print(f"Best config for {modality_name}: k={best_config['n_components']}, "
              f"cov={best_config['covariance_type']}, sil={best_config['silhouette_score']:.4f}")
        
        return best_config
    
    def optimize_all_modalities(self, combined_modalities: Dict[str, Tuple[np.ndarray, np.ndarray]]) -> Dict[str, Dict[str, Any]]:
        """
        Optimize GMM hyperparameters for all modalities
        Reproduces the original optimization loop with tqdm
        
        Args:
            combined_modalities: Dictionary with all modality combinations
            
        Returns:
            Dictionary with best configurations for each modality
        """
        print("=== Starting GMM Hyperparameter Optimization ===")
        
        best_configurations = {}
        
        # Reproduce original: for name, (X_tr, X_te) in tqdm(modalidades.items(), desc="Clustering")
        for modality_name, (X_train, X_test) in tqdm(combined_modalities.items(), desc="Clustering"):
            try:
                best_config = self.optimize_single_modality(X_train, modality_name)
                best_configurations[modality_name] = best_config
                
                # Store best model for later use
                self.best_models[modality_name] = best_config['model']
                
            except Exception as e:
                print(f"Error optimizing {modality_name}: {e}")
                continue
        
        print("=== GMM Hyperparameter Optimization Complete ===")
        return best_configurations


class ClusteringEvaluator:
    """
    Evaluates clustering results using multiple metrics
    Reproduces the original evaluation logic
    """
    
    def __init__(self):
        self.evaluation_metrics = EVALUATION_METRICS
    
    def evaluate_clustering(self, X_train: np.ndarray, X_test: np.ndarray, 
                          best_model: GaussianMixture, modality_name: str) -> Dict[str, float]:
        """
        Evaluate clustering using multiple metrics
        Reproduces the original evaluation logic
        
        Args:
            X_train: Training data
            X_test: Test data
            best_model: Trained GMM model
            modality_name: Name of the modality
            
        Returns:
            Dictionary with evaluation metrics
        """
        evaluation_results = {}
        
        try:
            # Get cluster labels (reproduce original: gmm_best.predict)
            train_labels = best_model.predict(X_train)
            test_labels = best_model.predict(X_test)
            
            # Calculate silhouette scores (reproduce original)
            if len(np.unique(train_labels)) > 1:
                train_silhouette = silhouette_score(X_train, train_labels)
                evaluation_results['silhouette_train'] = train_silhouette
            else:
                evaluation_results['silhouette_train'] = -1
            
            if len(np.unique(test_labels)) > 1:
                test_silhouette = silhouette_score(X_test, test_labels)
                evaluation_results['silhouette_test'] = test_silhouette
            else:
                evaluation_results['silhouette_test'] = -1
            
            # Calculate Davies-Bouldin score (reproduce original)
            if len(np.unique(test_labels)) > 1:
                db_score = davies_bouldin_score(X_test, test_labels)
                evaluation_results['davies_bouldin_test'] = db_score
            else:
                evaluation_results['davies_bouldin_test'] = float('inf')
            
            # Additional metric: Calinski-Harabasz score
            if len(np.unique(test_labels)) > 1:
                ch_score = calinski_harabasz_score(X_test, test_labels)
                evaluation_results['calinski_harabasz_test'] = ch_score
            else:
                evaluation_results['calinski_harabasz_test'] = 0
            
        except Exception as e:
            print(f"Error evaluating {modality_name}: {e}")
            # Return default values in case of error
            evaluation_results = {
                'silhouette_train': -1,
                'silhouette_test': -1,
                'davies_bouldin_test': float('inf'),
                'calinski_harabasz_test': 0
            }
        
        return evaluation_results
    
    def create_results_dataframe(self, best_configurations: Dict[str, Dict[str, Any]], 
                                combined_modalities: Dict[str, Tuple[np.ndarray, np.ndarray]]) -> pd.DataFrame:
        """
        Create results DataFrame combining optimization and evaluation results
        Reproduces the original results DataFrame creation
        
        Args:
            best_configurations: Best configurations for each modality
            combined_modalities: Combined modality data
            
        Returns:
            DataFrame with clustering results
        """
        print("Creating results DataFrame...")
        
        results_list = []
        
        for modality_name, best_config in best_configurations.items():
            if modality_name in combined_modalities:
                X_train, X_test = combined_modalities[modality_name]
                best_model = best_config['model']
                
                # Evaluate clustering
                evaluation_metrics = self.evaluate_clustering(X_train, X_test, best_model, modality_name)
                
                # Reproduce original results structure
                result_row = {
                    'Modalidad': modality_name,
                    'k_opt': best_config['n_components'],
                    'cov_opt': best_config['covariance_type'],
                    'Sil_train': evaluation_metrics['silhouette_train'],
                    'Sil_test': evaluation_metrics['silhouette_test'],
                    'DB_test': evaluation_metrics['davies_bouldin_test'],
                    'CH_test': evaluation_metrics.get('calinski_harabasz_test', 0)
                }
                
                results_list.append(result_row)
        
        # Create DataFrame (reproduce original: res_df = pd.DataFrame(results))
        results_df = pd.DataFrame(results_list)
        
        print(f"Results DataFrame created with {len(results_df)} rows")
        return results_df
    
    def save_models(self, best_models: Dict[str, GaussianMixture], output_dir: str) -> None:
        """
        Save trained clustering models
        
        Args:
            best_models: Dictionary with best models for each modality
            output_dir: Directory to save models
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for modality_name, model in best_models.items():
            model_path = os.path.join(output_dir, f'gmm_{modality_name}.pkl')
            try:
                joblib.dump(model, model_path)
                print(f"Saved model for {modality_name}: {model_path}")
            except Exception as e:
                print(f"Error saving model for {modality_name}: {e}")


class ClusteringPipeline:
    """
    Main clustering pipeline that coordinates all components
    Reproduces the complete original clustering workflow
    """
    
    def __init__(self):
        self.modality_processor = ModalityProcessor()
        self.gmm_optimizer = GMMClusteringOptimizer()
        self.evaluator = ClusteringEvaluator()
    
    def run_complete_clustering_analysis(self, structured_features: Tuple[np.ndarray, np.ndarray],
                                       image_embeddings: Tuple[np.ndarray, np.ndarray],
                                       text_embeddings: Tuple[np.ndarray, np.ndarray]) -> Tuple[pd.DataFrame, Dict]:
        """
        Run complete clustering analysis pipeline
        Reproduces the entire original clustering workflow
        
        Args:
            structured_features: Tuple of (train, test) structured features
            image_embeddings: Tuple of (train, test) image embeddings  
            text_embeddings: Tuple of (train, test) text embeddings
            
        Returns:
            Tuple of (results_dataframe, additional_info)
        """
        print("=== Starting Complete Clustering Analysis ===")
        
        # Step 1: Scale modalities
        scaled_modalities = self.modality_processor.scale_modalities(
            structured_features, image_embeddings, text_embeddings
        )
        
        # Step 2: Combine modalities
        combined_modalities = self.modality_processor.combine_modalities(scaled_modalities)
        
        # Step 3: Handle missing values
        cleaned_modalities = self.modality_processor.handle_missing_values(combined_modalities)
        
        # Step 4: Optimize GMM hyperparameters
        best_configurations = self.gmm_optimizer.optimize_all_modalities(cleaned_modalities)
        
        # Step 5: Create results DataFrame
        results_df = self.evaluator.create_results_dataframe(best_configurations, cleaned_modalities)
        
        # Step 6: Save models
        if CLUSTERING_MODELS_DIR:
            self.evaluator.save_models(self.gmm_optimizer.best_models, CLUSTERING_MODELS_DIR)
        
        # Prepare additional information
        additional_info = {
            'best_configurations': best_configurations,
            'modality_combinations': self.modality_processor.modality_combinations,
            'scalers': self.modality_processor.scalers,
            'models': self.gmm_optimizer.best_models
        }
        
        print("=== Complete Clustering Analysis Finished ===")
        
        return results_df, additional_info