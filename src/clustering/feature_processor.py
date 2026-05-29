"""
Feature processing module for clustering analysis
Handles structured data preparation, feature extraction, and encoding
"""

import pandas as pd
import numpy as np
import re
from typing import Tuple, List, Dict, Optional
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, ParameterGrid
from sklearn.metrics import accuracy_score
from tqdm import tqdm

from .config import (
    TRAIN_TEST_CONFIG, NUMERIC_FEATURES, CATEGORICAL_FEATURES,
    COLUMN_MAPPINGS, RANDOM_FOREST_CONFIG, BEST_RF_PARAMS,
    TOP_STRUCTURAL_FEATURES, REGEX_PATTERNS, DATA_PREPROCESSING
)


class StructuredFeatureProcessor:
    """
    Processes structured features for clustering analysis
    Reproduces the original feature preparation logic with correct column names
    """
    
    def __init__(self):
        self.numeric_features = NUMERIC_FEATURES.copy()
        self.categorical_features = CATEGORICAL_FEATURES.copy()
        self.column_mappings = COLUMN_MAPPINGS
        self.feature_importance_scores = None
        self.top_features = None
        
    def create_target_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create binary target variable from appeared_status
        Reproduces: df['Aparecido_bin'] = df['Aparecido'].astype(bool).astype(int)
        
        Args:
            df: DataFrame with appeared_status column
            
        Returns:
            DataFrame with appeared_status_binary column added
        """
        df_with_target = df.copy()
        
        if 'appeared_status' in df.columns:
            # Reproduce original logic: .astype(bool).astype(int)
            df_with_target['appeared_status_binary'] = (
                df_with_target['appeared_status'].astype(bool).astype(int)
            )
            print(f"Created binary target variable. Distribution:")
            print(df_with_target['appeared_status_binary'].value_counts())
        else:
            raise ValueError("appeared_status column not found in DataFrame")
        
        return df_with_target
    
    def perform_train_test_split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Perform stratified train/test split
        Reproduces the original train_test_split with stratification
        
        Args:
            df: DataFrame with target variable
            
        Returns:
            Tuple of (train_df, test_df)
        """
        print("Performing stratified train/test split...")
        
        # Reproduce original split parameters
        train_df, test_df = train_test_split(
            df,
            test_size=TRAIN_TEST_CONFIG['test_size'],
            stratify=df[TRAIN_TEST_CONFIG['stratify_column']],
            random_state=TRAIN_TEST_CONFIG['random_state']
        )
        
        print(f"Train/Test shapes: {train_df.shape}, {test_df.shape}")
        
        # Verify stratification worked
        train_dist = train_df['appeared_status_binary'].value_counts(normalize=True)
        test_dist = test_df['appeared_status_binary'].value_counts(normalize=True)
        print(f"Train distribution: {train_dist.to_dict()}")
        print(f"Test distribution: {test_dist.to_dict()}")
        
        return train_df, test_df
    
    def extract_numeric_features(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Extract numeric features from text columns
        Reproduces the original numeric feature extraction logic
        
        Args:
            train_df: Training DataFrame
            test_df: Test DataFrame
            
        Returns:
            Tuple of processed (train_df, test_df)
        """
        print("Extracting numeric features...")
        
        # Process both dataframes
        for df_name, df_subset in [("train", train_df), ("test", test_df)]:
            print(f"Processing {df_name} set...")
            
            # Age extraction (reproduce original logic) - CORREGIDO: usar age_cleaned
            if 'age_cleaned' in df_subset.columns:
                df_subset['age_numeric'] = pd.to_numeric(
                    df_subset['age_cleaned'].astype(str).str.extract(REGEX_PATTERNS['age_extraction'])[0],
                    errors='coerce'
                ).fillna(DATA_PREPROCESSING['missing_value_strategy']['numeric'])
            
            # Height extraction (reproduce original logic) - CORREGIDO: usar height_cleaned
            if 'height_cleaned' in df_subset.columns:
                df_subset['height_numeric'] = pd.to_numeric(
                    df_subset['height_cleaned'].astype(str).str.extract(REGEX_PATTERNS['height_extraction'])[0],
                    errors='coerce'
                ).fillna(DATA_PREPROCESSING['missing_value_strategy']['numeric'])
            
            # Hours to report (reproduce original logic) - CORREGIDO: nombre correcto
            if 'hours_to_report' in df_subset.columns:
                df_subset['hours_to_report_numeric'] = pd.to_numeric(
                    df_subset['hours_to_report'],
                    errors='coerce'
                ).fillna(DATA_PREPROCESSING['missing_value_strategy']['numeric'])
            
            # Hours to appear (reproduce original logic) - CORREGIDO: nombre correcto
            if 'hours_to_appear' in df_subset.columns:
                df_subset['hours_to_appear_numeric'] = pd.to_numeric(
                    df_subset['hours_to_appear'],
                    errors='coerce'
                ).fillna(DATA_PREPROCESSING['missing_value_strategy']['numeric'])
        
        return train_df, test_df
    
    def prepare_categorical_features(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepare categorical features by filling missing values
        Reproduces: df_[c] = df_[c].fillna('Desconocido')
        
        Args:
            train_df: Training DataFrame
            test_df: Test DataFrame
            
        Returns:
            Tuple of processed (train_df, test_df)
        """
        print("Preparing categorical features...")
        
        # Get available categorical features in the data
        available_categorical_features = [
            col for col in self.categorical_features 
            if col in train_df.columns
        ]
        
        if not available_categorical_features:
            print("Warning: No categorical features found in the data")
            return train_df, test_df
        
        # Process both dataframes (reproduce original loop)
        for df_subset in [train_df, test_df]:
            for feature_col in available_categorical_features:
                # Reproduce original: df_[c] = df_[c].fillna('Desconocido')
                df_subset[feature_col] = df_subset[feature_col].fillna(
                    DATA_PREPROCESSING['missing_value_strategy']['categorical']
                )
        
        print(f"Processed {len(available_categorical_features)} categorical features")
        return train_df, test_df
    
    def create_one_hot_encoding(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create one-hot encoded features
        Reproduces the original pd.get_dummies and align logic
        
        Args:
            train_df: Training DataFrame
            test_df: Test DataFrame
            
        Returns:
            Tuple of (X_train_encoded, X_test_encoded)
        """
        print("Creating one-hot encoded features...")
        
        # Get available features for encoding
        available_numeric = [col for col in self.numeric_features if col in train_df.columns]
        available_categorical = [col for col in self.categorical_features if col in train_df.columns]
        
        all_features_for_encoding = available_numeric + available_categorical
        
        print(f"Features for encoding: {len(available_numeric)} numeric, {len(available_categorical)} categorical")
        
        # Reproduce original: pd.get_dummies with drop_first=True
        X_train_encoded = pd.get_dummies(
            train_df[all_features_for_encoding],
            drop_first=True
        )
        
        X_test_encoded = pd.get_dummies(
            test_df[all_features_for_encoding],
            drop_first=True
        )
        
        # Reproduce original: align with join='left'
        X_train_encoded, X_test_encoded = X_train_encoded.align(
            X_test_encoded,
            join='left',
            axis=1,
            fill_value=0
        )
        
        print(f"Encoded features -> Train: {X_train_encoded.shape}, Test: {X_test_encoded.shape}")
        
        return X_train_encoded, X_test_encoded
    
    def perform_feature_selection(self, X_train: pd.DataFrame, y_train: pd.Series, 
                                 X_test: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Perform feature selection using Random Forest
        Grid Search es OPCIONAL según configuración
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            
        Returns:
            Tuple of (selected_train_features, selected_test_features, top_feature_names)
        """
        print("Performing feature selection with Random Forest...")
        
        if RANDOM_FOREST_CONFIG['enabled']:
            # Hacer Grid Search (toma más tiempo)
            print("Grid Search enabled - this will take longer...")
            return self._perform_grid_search_feature_selection(X_train, y_train, X_test)
        else:
            # Usar parámetros pre-determinados (más rápido)
            print("Using pre-determined parameters for faster execution...")
            return self._perform_fixed_feature_selection(X_train, y_train, X_test)
    
    def _perform_grid_search_feature_selection(self, X_train: pd.DataFrame, y_train: pd.Series, 
                                             X_test: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Perform feature selection using Grid Search (reproduce original grid search)
        """
        # Setup Random Forest and Grid Search (reproduce original)
        rf_classifier = RandomForestClassifier(random_state=RANDOM_FOREST_CONFIG['random_state'])
        
        grid_search = GridSearchCV(
            rf_classifier,
            RANDOM_FOREST_CONFIG['param_grid'],
            cv=RANDOM_FOREST_CONFIG['cv_folds'],
            scoring=RANDOM_FOREST_CONFIG['scoring'],
            n_jobs=RANDOM_FOREST_CONFIG['n_jobs'],
            verbose=0
        )
        
        # Calculate total fits for progress bar (reproduce original)
        n_candidates = len(list(ParameterGrid(RANDOM_FOREST_CONFIG['param_grid'])))
        total_fits = n_candidates * RANDOM_FOREST_CONFIG['cv_folds']
        
        print(f"Starting GridSearchCV with {total_fits} total fits...")
        
        # Fit with progress tracking
        try:
            from tqdm_joblib import tqdm_joblib
            with tqdm_joblib(tqdm(desc="GridSearchCV fits", total=total_fits)):
                grid_search.fit(X_train, y_train)
        except ImportError:
            print("tqdm_joblib not available, running without progress bar")
            grid_search.fit(X_train, y_train)
        
        # Get best model and feature importances
        best_rf_model = grid_search.best_estimator_
        print(f"Best hyperparameters: {grid_search.best_params_}")
        
        return self._extract_top_features(best_rf_model, X_train, X_test)
    
    def _perform_fixed_feature_selection(self, X_train: pd.DataFrame, y_train: pd.Series, 
                                       X_test: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Perform feature selection using fixed parameters (reproduce original fixed model)
        """
        # Use best parameters from grid search results (reproduce original fixed model)
        rf_final = RandomForestClassifier(**BEST_RF_PARAMS)
        rf_final.fit(X_train, y_train)
        
        print(f"Using fixed parameters: {BEST_RF_PARAMS}")
        
        return self._extract_top_features(rf_final, X_train, X_test)
    
    def _extract_top_features(self, rf_model: RandomForestClassifier, X_train: pd.DataFrame, 
                            X_test: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Extract top features from trained Random Forest model
        """
        # Calculate feature importances (reproduce original)
        feature_importances = pd.Series(
            rf_model.feature_importances_,
            index=X_train.columns
        ).sort_values(ascending=False)
        
        print("Feature importances (top 10):")
        print(feature_importances.head(10))
        
        # Select top features (reproduce original)
        top_feature_names = feature_importances.head(RANDOM_FOREST_CONFIG['top_features_count']).index.tolist()
        print(f"Top {len(top_feature_names)} features selected: {top_feature_names}")
        
        # Store for later use
        self.feature_importance_scores = feature_importances
        self.top_features = top_feature_names
        
        # Extract selected features as numpy arrays (reproduce original)
        selected_train_features = X_train[top_feature_names].values
        selected_test_features = X_test[top_feature_names].values
        
        print(f"Selected features shape -> Train: {selected_train_features.shape}, Test: {selected_test_features.shape}")
        
        return selected_train_features, selected_test_features, top_feature_names
    
    def use_predefined_features(self, X_train: pd.DataFrame, X_test: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Use predefined top features from previous analysis
        Útil cuando ya conocemos las mejores features del grid search anterior
        
        Args:
            X_train: Training features
            X_test: Test features
            
        Returns:
            Tuple of (selected_train_features, selected_test_features, top_feature_names)
        """
        print("Using predefined top features from previous analysis...")
        
        # Mapear features predefinidas a las disponibles en los datos actuales
        available_top_features = []
        
        for feature_name in TOP_STRUCTURAL_FEATURES:
            # Buscar features similares en los datos actuales
            if feature_name in X_train.columns:
                available_top_features.append(feature_name)
            else:
                # Buscar features que contengan partes del nombre original
                similar_features = [col for col in X_train.columns if any(part in col for part in feature_name.split('_'))]
                if similar_features:
                    print(f"Feature '{feature_name}' not found, using similar: {similar_features[0]}")
                    available_top_features.append(similar_features[0])
                else:
                    print(f"Warning: Feature '{feature_name}' not found and no similar feature detected")
        
        if not available_top_features:
            print("Warning: No predefined features found, falling back to feature selection")
            return self.perform_feature_selection(X_train, pd.Series([0]*len(X_train)), X_test)
        
        print(f"Using {len(available_top_features)} predefined features: {available_top_features}")
        
        # Extract selected features as numpy arrays
        selected_train_features = X_train[available_top_features].values
        selected_test_features = X_test[available_top_features].values
        
        self.top_features = available_top_features
        
        print(f"Predefined features shape -> Train: {selected_train_features.shape}, Test: {selected_test_features.shape}")
        
        return selected_train_features, selected_test_features, available_top_features
    
    def validate_feature_selection(self, X_train: pd.DataFrame, y_train: pd.Series, 
                                  X_test: pd.DataFrame, y_test: pd.Series, 
                                  top_features: List[str]) -> Dict[str, float]:
        """
        Validate feature selection by training final model
        Reproduces the fixed Random Forest validation
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features  
            y_test: Test target
            top_features: Selected feature names
            
        Returns:
            Dictionary with train and test accuracies
        """
        print("Validating feature selection...")
        
        # Use best parameters (reproduce original fixed model)
        rf_final = RandomForestClassifier(**BEST_RF_PARAMS)
        rf_final.fit(X_train[top_features], y_train)
        
        # Calculate accuracies
        train_accuracy = accuracy_score(y_train, rf_final.predict(X_train[top_features]))
        test_accuracy = accuracy_score(y_test, rf_final.predict(X_test[top_features]))
        
        print(f"Validation results:")
        print(f"Train accuracy: {train_accuracy:.4f}")
        print(f"Test accuracy: {test_accuracy:.4f}")
        
        return {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy
        }
    
    def process_structured_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, pd.Series, pd.Series, List[str], Dict]:
        """
        Complete structured feature processing pipeline
        Reproduces the entire original workflow
        
        Args:
            df: Input DataFrame from preprocessing
            
        Returns:
            Tuple of (train_features, test_features, y_train, y_test, feature_names, validation_metrics)
        """
        print("=== Starting Structured Feature Processing ===")
        
        # Step 1: Create binary target variable
        df_with_target = self.create_target_variable(df)
        
        # Step 2: Train/test split
        train_df, test_df = self.perform_train_test_split(df_with_target)
        
        # Step 3: Extract numeric features
        train_df, test_df = self.extract_numeric_features(train_df, test_df)
        
        # Step 4: Prepare categorical features
        train_df, test_df = self.prepare_categorical_features(train_df, test_df)
        
        # Step 5: Create one-hot encoding
        X_train_encoded, X_test_encoded = self.create_one_hot_encoding(train_df, test_df)
        
        # Step 6: Extract target variables
        y_train = train_df['appeared_status_binary']
        y_test = test_df['appeared_status_binary']
        
        # Step 7: Feature selection (grid search opcional)
        selected_train_features, selected_test_features, top_feature_names = self.perform_feature_selection(
            X_train_encoded, y_train, X_test_encoded
        )
        
        # Step 8: Validate feature selection
        validation_metrics = self.validate_feature_selection(
            X_train_encoded, y_train, X_test_encoded, y_test, top_feature_names
        )
        
        print("=== Structured Feature Processing Complete ===")
        
        return (selected_train_features, selected_test_features, 
                y_train, y_test, top_feature_names, validation_metrics)
    
    def get_feature_summary(self) -> Dict:
        """
        Get summary of feature processing results
        
        Returns:
            Dictionary with feature processing summary
        """
        summary = {
            'total_features_after_encoding': len(self.feature_importance_scores) if self.feature_importance_scores is not None else 0,
            'top_features_selected': len(self.top_features) if self.top_features is not None else 0,
            'top_feature_names': self.top_features,
            'feature_importance_scores': self.feature_importance_scores.to_dict() if self.feature_importance_scores is not None else {},
            'grid_search_enabled': RANDOM_FOREST_CONFIG['enabled']
        }
        
        return summary


def load_and_validate_dataset(file_path: str) -> pd.DataFrame:
    """
    Load and validate the input dataset
    
    Args:
        file_path: Path to the dataset file
        
    Returns:
        Loaded and validated DataFrame
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"Loaded dataset: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Basic validation
        if 'appeared_status' not in df.columns:
            raise ValueError("appeared_status column not found in dataset")
        
        # Check for required columns
        required_cols = ['appeared_status', 'serialized_image']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"Warning: Missing columns: {missing_cols}")
        
        return df
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        raise
