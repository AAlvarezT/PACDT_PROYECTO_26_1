"""
Data handling module for regression analysis
Handles dataset preparation, feature processing, and DataLoader creation
"""

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Tuple, Dict, List, Optional, Any
import warnings

from .config import (
    STRUCTURED_FEATURES, COLUMN_MAPPINGS, DATA_PREPROCESSING, 
    TRAINING_CONFIG, REGEX_PATTERNS
)

warnings.filterwarnings('ignore')


class StructuredFeatureProcessor:
    """
    Processes structured features for regression modeling
    Reproduces the original structured data processing logic
    """
    
    def __init__(self):
        self.scaler = None
        self.feature_columns = None
        self.numeric_columns = STRUCTURED_FEATURES['numeric_columns']
        self.excluded_columns = STRUCTURED_FEATURES['excluded_columns']
    
    def extract_numeric_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract and clean numeric features
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with processed numeric features
        """
        print("Extracting numeric features...")
        
        df_processed = df.copy()
        
        # Age extraction - CORRECTED: use actual column name
        if 'age_cleaned' in df.columns:
            df_processed['age_numeric'] = pd.to_numeric(
                df_processed['age_cleaned'].astype(str).str.extract(REGEX_PATTERNS['age_extraction'])[0],
                errors='coerce'
            ).fillna(DATA_PREPROCESSING['missing_value_strategy']['numeric'])
        
        # Height extraction - CORRECTED: use actual column name
        if 'height_cleaned' in df.columns:
            df_processed['height_numeric'] = pd.to_numeric(
                df_processed['height_cleaned'].astype(str).str.extract(REGEX_PATTERNS['height_extraction'])[0],
                errors='coerce'
            ).fillna(DATA_PREPROCESSING['missing_value_strategy']['numeric'])
        
        # Hours to report - CORRECTED: use actual column name
        if 'hours_to_report' in df.columns:
            df_processed['hours_to_report_numeric'] = pd.to_numeric(
                df_processed['hours_to_report'].astype(str),
                errors='coerce'
            ).fillna(DATA_PREPROCESSING['missing_value_strategy']['numeric'])
        
        # Hours to appear - CORRECTED: use actual column name
        if 'hours_to_appear' in df.columns:
            df_processed['hours_to_appear_numeric'] = pd.to_numeric(
                df_processed['hours_to_appear'].astype(str),
                errors='coerce'
            ).fillna(DATA_PREPROCESSING['missing_value_strategy']['numeric'])
        
        # Geographic coordinates - CORRECTED: use actual column names
        if 'Latitud' in df.columns:
            df_processed['latitude'] = pd.to_numeric(
                df_processed['Latitud'].astype(str),
                errors='coerce'
            ).fillna(DATA_PREPROCESSING['missing_value_strategy']['numeric'])
        
        if 'Longitud' in df.columns:
            df_processed['longitude'] = pd.to_numeric(
                df_processed['Longitud'].astype(str),
                errors='coerce'
            ).fillna(DATA_PREPROCESSING['missing_value_strategy']['numeric'])
        
        return df_processed
    
    def prepare_categorical_features(self, df: pd.DataFrame) -> Tuple[List[str], pd.DataFrame]:
        """
        Identify and prepare categorical features
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (categorical_column_names, processed_dataframe)
        """
        print("Preparing categorical features...")
        
        df_processed = df.copy()
        
        # Identify categorical columns (reproduce original logic)
        # cat_cols = [c for c in df.columns if c not in num_cols and c not in excluded_cols]
        available_numeric_cols = [col for col in self.numeric_columns if col in df.columns]
        
        categorical_columns = [
            col for col in df.columns 
            if col not in available_numeric_cols and col not in self.excluded_columns
        ]
        
        print(f"Found {len(categorical_columns)} categorical columns")
        
        # Fill missing values (reproduce original: df[cat_cols] = df[cat_cols].fillna('Desconocido'))
        if categorical_columns:
            df_processed[categorical_columns] = df_processed[categorical_columns].fillna(
                DATA_PREPROCESSING['missing_value_strategy']['categorical']
            )
        
        return categorical_columns, df_processed
    
    def create_structured_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Create final structured feature matrix
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Structured feature matrix
        """
        print("Creating structured feature matrix...")
        
        # Extract numeric features
        df_processed = self.extract_numeric_features(df)
        
        # Get available numeric columns
        available_numeric_cols = [col for col in self.numeric_columns if col in df_processed.columns]
        
        # Get categorical features
        categorical_columns, df_processed = self.prepare_categorical_features(df_processed)
        
        # Create dummy variables (reproduce original: pd.get_dummies(df[cat_cols], drop_first=True))
        if categorical_columns:
            categorical_dummies = pd.get_dummies(
                df_processed[categorical_columns],
                drop_first=DATA_PREPROCESSING['drop_first_dummy']
            )
        else:
            categorical_dummies = pd.DataFrame()
        
        # Combine numeric and categorical features (reproduce original: pd.concat([df[num_cols], dummies], axis=1))
        if available_numeric_cols:
            numeric_features = df_processed[available_numeric_cols]
            if not categorical_dummies.empty:
                structured_features = pd.concat([numeric_features, categorical_dummies], axis=1)
            else:
                structured_features = numeric_features
        else:
            structured_features = categorical_dummies
        
        # Convert to float32 (reproduce original: .astype(np.float32))
        structured_matrix = structured_features.astype(np.float32).values
        
        # Store feature columns for later reference
        self.feature_columns = structured_features.columns.tolist()
        
        print(f"Structured feature matrix shape: {structured_matrix.shape}")
        print(f"Feature columns: {len(self.feature_columns)}")
        
        return structured_matrix
    
    def fit_scaler(self, X_train: np.ndarray) -> 'StructuredFeatureProcessor':
        """
        Fit scaler on training data
        
        Args:
            X_train: Training feature matrix
            
        Returns:
            Self for method chaining
        """
        print("Fitting feature scaler...")
        
        # Reproduce original: StandardScaler().fit(X_struct)
        self.scaler = StandardScaler().fit(X_train)
        
        print("Feature scaler fitted successfully")
        return self
    
    def transform_features(self, X: np.ndarray) -> np.ndarray:
        """
        Transform features using fitted scaler
        
        Args:
            X: Feature matrix to transform
            
        Returns:
            Scaled feature matrix
        """
        if self.scaler is None:
            raise ValueError("Scaler not fitted. Call fit_scaler() first.")
        
        # Reproduce original: scaler.transform(X_struct)
        return self.scaler.transform(X)
    
    def get_feature_info(self) -> Dict[str, Any]:
        """
        Get information about processed features
        
        Returns:
            Dictionary with feature information
        """
        return {
            'feature_columns': self.feature_columns,
            'num_features': len(self.feature_columns) if self.feature_columns else 0,
            'numeric_columns': self.numeric_columns,
            'scaler_fitted': self.scaler is not None,
            'scaler_mean': self.scaler.mean_.tolist() if self.scaler is not None else None,
            'scaler_scale': self.scaler.scale_.tolist() if self.scaler is not None else None
        }


class MultimodalDataset(Dataset):
    """
    Custom dataset for multimodal regression
    """
    
    def __init__(self, structured_features: np.ndarray, face_tensors: torch.Tensor, 
                 targets: np.ndarray):
        """
        Initialize multimodal dataset
        
        Args:
            structured_features: Structured feature matrix [N, feature_dim]
            face_tensors: Face image tensors [N, 3, 160, 160]
            targets: Target values [N, 1]
        """
        # Reproduce original initialization logic
        self.structured_features = structured_features.astype(np.float32)
        self.face_tensors = face_tensors
        self.targets = targets.astype(np.float32)
        
        # Validate data consistency
        assert len(self.structured_features) == len(self.face_tensors) == len(self.targets), \
            "All inputs must have the same number of samples"
        
        print(f"Dataset initialized with {len(self)} samples")
        print(f"  Structured features shape: {self.structured_features.shape}")
        print(f"  Face tensors shape: {self.face_tensors.shape}")
        print(f"  Targets shape: {self.targets.shape}")
    
    def __len__(self) -> int:
        """
        Get dataset length
        """
        return len(self.targets)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get single sample
        
        Args:
            idx: Sample index
            
        Returns:
            Dictionary with sample data
        """
        return {
            's': torch.from_numpy(self.structured_features[idx]),  # Structured features
            'f': self.face_tensors[idx],                          # Face tensor
            'y': torch.tensor(self.targets[idx])                  # Target value
        }
    
    def get_sample_info(self, idx: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific sample
        
        Args:
            idx: Sample index
            
        Returns:
            Dictionary with sample information
        """
        sample = self[idx]
        
        return {
            'index': idx,
            'structured_shape': sample['s'].shape,
            'face_shape': sample['f'].shape,
            'target_value': sample['y'].item(),
            'structured_stats': {
                'mean': sample['s'].mean().item(),
                'std': sample['s'].std().item(),
                'min': sample['s'].min().item(),
                'max': sample['s'].max().item()
            },
            'face_stats': {
                'mean': sample['f'].mean().item(),
                'std': sample['f'].std().item(),
                'min': sample['f'].min().item(),
                'max': sample['f'].max().item()
            }
        }


class MultimodalDataHandler:
    """
    Handles complete data preparation workflow for multimodal regression
    """
    
    def __init__(self):
        self.feature_processor = StructuredFeatureProcessor()
        self.train_dataset = None
        self.test_dataset = None
        self.train_indices = None
        self.test_indices = None
    
    def prepare_data_splits(self, df: pd.DataFrame, face_tensors: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create train/test splits
        
        Args:
            df: DataFrame with target variable
            face_tensors: All face tensors
            
        Returns:
            Tuple of (train_indices, test_indices)
        """
        print("Creating train/test splits...")
        
        # Reproduce original: idx_tr, idx_te = train_test_split(np.arange(len(df)), test_size=0.2, random_state=42)
        train_indices, test_indices = train_test_split(
            np.arange(len(df)),
            test_size=TRAINING_CONFIG['test_size'],
            random_state=TRAINING_CONFIG['random_state']
        )
        
        print(f"Train split: {len(train_indices)} samples")
        print(f"Test split: {len(test_indices)} samples")
        
        self.train_indices = train_indices
        self.test_indices = test_indices
        
        return train_indices, test_indices
    
    def create_datasets(self, df: pd.DataFrame, face_tensors: torch.Tensor) -> Tuple[MultimodalDataset, MultimodalDataset]:
        """
        Create train and test datasets
        
        Args:
            df: DataFrame with features and targets
            face_tensors: Face tensors for all samples
            
        Returns:
            Tuple of (train_dataset, test_dataset)
        """
        print("=== Creating Multimodal Datasets ===")
        
        # Validate required columns
        if 'target_regression' not in df.columns:
            raise ValueError("target_regression column not found in DataFrame")
        
        # Create structured features
        structured_features = self.feature_processor.create_structured_features(df)
        
        # Create train/test splits
        train_indices, test_indices = self.prepare_data_splits(df, face_tensors)
        
        # Split structured features (reproduce original: S_tr,S_te = X_struct[idx_tr], X_struct[idx_te])
        structured_train = structured_features[train_indices]
        structured_test = structured_features[test_indices]
        
        # Fit scaler on training data and transform both sets
        self.feature_processor.fit_scaler(structured_train)
        structured_train_scaled = self.feature_processor.transform_features(structured_train)
        structured_test_scaled = self.feature_processor.transform_features(structured_test)
        
        # Split targets (reproduce original: y_tr,y_te = df['y_reg'].values[idx_tr,None], df['y_reg'].values[idx_te,None])
        targets_train = df['target_regression'].values[train_indices, None]
        targets_test = df['target_regression'].values[test_indices, None]
        
        # Split face tensors (F_tr, F_te will be passed separately)
        face_tensors_train = face_tensors[train_indices]
        face_tensors_test = face_tensors[test_indices]
        
        # Create datasets (reproduce original: DS(S_tr,F_tr,y_tr))
        train_dataset = MultimodalDataset(structured_train_scaled, face_tensors_train, targets_train)
        test_dataset = MultimodalDataset(structured_test_scaled, face_tensors_test, targets_test)
        
        self.train_dataset = train_dataset
        self.test_dataset = test_dataset
        
        print("=== Dataset Creation Complete ===")
        
        return train_dataset, test_dataset
    
    def create_data_loaders(self, train_dataset: MultimodalDataset, 
                           test_dataset: MultimodalDataset) -> Tuple[DataLoader, DataLoader]:
        """
        Create DataLoaders for training and testing
        
        Args:
            train_dataset: Training dataset
            test_dataset: Test dataset
            
        Returns:
            Tuple of (train_loader, test_loader)
        """
        print("Creating DataLoaders...")
        
        batch_size = TRAINING_CONFIG['batch_size']
        
        # Reproduce original: DataLoader(DS(...),batch_size=BATCH,shuffle=True)
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,  # Shuffle training data
            num_workers=0,  # Set to 0 to avoid multiprocessing issues
            pin_memory=torch.cuda.is_available()
        )
        
        # Reproduce original: DataLoader(DS(...),batch_size=BATCH) (no shuffle for test)
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,  # Don't shuffle test data
            num_workers=0,
            pin_memory=torch.cuda.is_available()
        )
        
        print(f"Train loader: {len(train_loader)} batches")
        print(f"Test loader: {len(test_loader)} batches")
        
        return train_loader, test_loader
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of data preparation
        
        Returns:
            Dictionary with data summary
        """
        summary = {
            'feature_info': self.feature_processor.get_feature_info(),
            'split_info': {
                'train_size': len(self.train_indices) if self.train_indices is not None else 0,
                'test_size': len(self.test_indices) if self.test_indices is not None else 0,
                'test_ratio': TRAINING_CONFIG['test_size']
            }
        }
        
        if self.train_dataset is not None:
            summary['train_dataset'] = {
                'size': len(self.train_dataset),
                'structured_dim': self.train_dataset.structured_features.shape[1],
                'face_shape': list(self.train_dataset.face_tensors.shape[1:]),
                'target_stats': {
                    'mean': float(self.train_dataset.targets.mean()),
                    'std': float(self.train_dataset.targets.std()),
                    'min': float(self.train_dataset.targets.min()),
                    'max': float(self.train_dataset.targets.max())
                }
            }
        
        if self.test_dataset is not None:
            summary['test_dataset'] = {
                'size': len(self.test_dataset),
                'target_stats': {
                    'mean': float(self.test_dataset.targets.mean()),
                    'std': float(self.test_dataset.targets.std()),
                    'min': float(self.test_dataset.targets.min()),
                    'max': float(self.test_dataset.targets.max())
                }
            }
        
        return summary


def validate_data_consistency(df: pd.DataFrame, face_tensors: torch.Tensor) -> bool:
    """
    Validate consistency between DataFrame and face tensors
    
    Args:
        df: DataFrame with features and targets
        face_tensors: Face tensors
        
    Returns:
        True if data is consistent, False otherwise
    """
    validation_checks = []
    
    # Check length consistency
    if len(df) != len(face_tensors):
        print(f"Length mismatch: DataFrame {len(df)} vs Face tensors {len(face_tensors)}")
        validation_checks.append(False)
    else:
        validation_checks.append(True)
    
    # Check target variable presence
    if 'target_regression' not in df.columns:
        print("Missing target_regression column")
        validation_checks.append(False)
    else:
        validation_checks.append(True)
    
    # Check target value range
    if 'target_regression' in df.columns:
        target_min, target_max = df['target_regression'].min(), df['target_regression'].max()
        if target_min < 0 or target_max > 1:
            print(f"Target values outside [0,1] range: [{target_min:.4f}, {target_max:.4f}]")
            validation_checks.append(False)
        else:
            validation_checks.append(True)
    
    # Check face tensor format
    expected_face_shape = (3, 160, 160)
    if face_tensors.shape[1:] != expected_face_shape:
        print(f"Unexpected face tensor shape: {face_tensors.shape[1:]} vs {expected_face_shape}")
        validation_checks.append(False)
    else:
        validation_checks.append(True)
    
    return all(validation_checks)
