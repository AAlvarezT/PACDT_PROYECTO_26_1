"""
Model evaluation module for multimodal regression
Simple wrapper that uses the trainer's evaluation method
"""

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from typing import Dict, Optional, Any
import json
import os

from .config import DEVICE, REGRESSION_RESULTS_DIR, OUTPUT_FILES
from .multimodal_model import MMReg


class RegressionEvaluator:
    """
    Simple evaluator that uses trainer's evaluation method
    """
    
    def __init__(self, model: MMReg):
        self.model = model.to(DEVICE)
        self.device = DEVICE
    
    def evaluate_model(self, test_loader: DataLoader) -> Dict[str, float]:
        """
        Simple evaluation using the exact notebook code
        """
        print("=== Starting Model Evaluation ===")
        
        # Load best model
        best_model_path = os.path.join(REGRESSION_RESULTS_DIR, "models", OUTPUT_FILES['best_model'])
        if os.path.exists(best_model_path):
            self.model.load_state_dict(torch.load(best_model_path, map_location=self.device))
            print(f"Best model loaded from: {best_model_path}")
        
        # Use exact notebook evaluation code
        from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
        
        self.model.eval()
        preds, ys = [], []
        
        with torch.no_grad():
            for b in test_loader:
                preds.append(self.model(b['s'].to(self.device), b['f'].to(self.device)).cpu())
                ys.append(b['y'])
        
        preds = np.concatenate(preds).ravel()
        ys = np.concatenate(ys).ravel()
        
        mse = mean_squared_error(ys, preds)
        rmse = np.sqrt(mse)
        mape = mean_absolute_percentage_error(ys, preds)
        
        print(f"\n► MSE  : {mse:.6f}")
        print(f"► RMSE : {rmse:.6f}")
        print(f"► MAPE : {mape:.6%}")
        
        print("=== Model Evaluation Complete ===")
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mape': mape,
            'predictions': preds.tolist(),
            'targets': ys.tolist()
        }


def evaluate_model_comprehensive(model: MMReg, test_loader: DataLoader, 
                                output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Comprehensive model evaluation function
    """
    evaluator = RegressionEvaluator(model)
    
    # Get evaluation results
    results = evaluator.evaluate_model(test_loader)
    
    # Create summary
    summary = {
        'model_performance': {
            'rmse': results['rmse'],
            'mape_percentage': results['mape'] * 100,
            'r2_score': 0.0,  # Placeholder
            'correlation': 0.0  # Placeholder
        },
        'accuracy_metrics': {
            'within_5_percent': 0.0,  # Placeholder
            'within_10_percent': 0.0  # Placeholder
        },
        'overall_grade': 'Good'  # Placeholder
    }
    
    return {
        'summary': summary,
        'full_results': results
    }