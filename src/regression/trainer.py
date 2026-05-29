"""
Training module for multimodal regression model
Reproduces EXACTLY the notebook training code
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

from .config import TRAINING_CONFIG, DEVICE, REGRESSION_MODELS_DIR, OUTPUT_FILES
from .multimodal_model import MMReg


class MultimodalTrainer:
    """
    Handles training of multimodal regression model
    Reproduces EXACTLY the original notebook training code
    """
    
    def __init__(self, model: MMReg, train_loader: DataLoader, test_loader: DataLoader):
        self.model = model.to(DEVICE)
        self.train_loader = train_loader
        self.test_loader = test_loader
        
        self.epochs = TRAINING_CONFIG['epochs']
        self.device = DEVICE
        
        # Reproduce EXACTLY: opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=2e-4)
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(), 
            lr=TRAINING_CONFIG['optimizer']['lr'], 
            weight_decay=TRAINING_CONFIG['optimizer']['weight_decay']
        )
        
        # Reproduce EXACTLY: sched = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, factor=0.5, patience=3)
        # FIXED: Remove verbose parameter that doesn't exist
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, 
            factor=TRAINING_CONFIG['scheduler']['factor'], 
            patience=TRAINING_CONFIG['scheduler']['patience']
        )
        
        # Reproduce EXACTLY: loss_fn = nn.MSELoss()
        self.loss_function = nn.MSELoss()
        
        self.best_rmse = np.inf
        self.training_history = {
            'train_mse': [],
            'val_rmse': [],
            'learning_rates': []
        }
        
        self.checkpoint_dir = REGRESSION_MODELS_DIR
        self.best_model_path = os.path.join(self.checkpoint_dir, OUTPUT_FILES['best_model'])
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        print(f"Trainer initialized for {self.epochs} epochs")
        print(f"Best model will be saved to: {self.best_model_path}")
    
    def train(self) -> Dict[str, Any]:
        """
        Execute complete training loop
        Reproduces EXACTLY the original notebook training code
        """
        print("=== Starting Model Training ===")
        print(f"Training on device: {self.device}")
        print(f"Train batches: {len(self.train_loader)}")
        print(f"Test batches: {len(self.test_loader)}")
        
        # Reproduce EXACTLY: EPOCHS=25; best_rmse=np.inf; for ep in range(1,EPOCHS+1):
        EPOCHS = self.epochs
        best_rmse = np.inf
        
        for ep in range(1, EPOCHS + 1):
            # Reproduce EXACTLY: model.train(); run=0.
            self.model.train()
            run = 0.0
            
            # Reproduce EXACTLY: for b in tqdm(tr_dl, desc=f"Epoch {ep}/{EPOCHS}"):
            for b in tqdm(self.train_loader, desc=f"Epoch {ep}/{EPOCHS}"):
                # Reproduce EXACTLY: pred=model(b['s'].to(device), b['f'].to(device))
                pred = self.model(b['s'].to(self.device), b['f'].to(self.device))
                
                # Reproduce EXACTLY: loss=loss_fn(pred, b['y'].to(device))
                loss = self.loss_function(pred, b['y'].to(self.device))
                
                # Reproduce EXACTLY: opt.zero_grad(); loss.backward(); opt.step()
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                # Reproduce EXACTLY: run+=loss.item()*len(pred)
                run += loss.item() * len(pred)
            
            # Reproduce EXACTLY: train_mse=run/len(tr_dl.dataset)
            train_mse = run / len(self.train_loader.dataset)
            
            # Reproduce EXACTLY: model.eval(); yhat,yt=[] ,[]
            self.model.eval()
            yhat, yt = [], []
            
            # Reproduce EXACTLY: with torch.no_grad(): for b in te_dl:
            with torch.no_grad():
                for b in self.test_loader:
                    # Reproduce EXACTLY: yhat.append(model(b['s'].to(device),b['f'].to(device)).cpu())
                    yhat.append(self.model(b['s'].to(self.device), b['f'].to(self.device)).cpu())
                    # Reproduce EXACTLY: yt.append(b['y'])
                    yt.append(b['y'])
            
            # Reproduce EXACTLY: yhat=np.concatenate(yhat).ravel(); yt=np.concatenate(yt).ravel()
            yhat = np.concatenate(yhat).ravel()
            yt = np.concatenate(yt).ravel()
            
            # Reproduce EXACTLY: rmse=np.sqrt(mean_squared_error(yt,yhat))
            rmse = np.sqrt(mean_squared_error(yt, yhat))
            
            # Reproduce EXACTLY: sched.step(rmse)
            self.scheduler.step(rmse)
            
            # Store training history
            self.training_history['train_mse'].append(train_mse)
            self.training_history['val_rmse'].append(rmse)
            self.training_history['learning_rates'].append(self.optimizer.param_groups[0]['lr'])
            
            # Reproduce EXACTLY: print(f"Epoch {ep:02d} | Train MSE {train_mse:.5f} | Val RMSE {rmse:.5f}")
            print(f"Epoch {ep:02d} | Train MSE {train_mse:.5f} | Val RMSE {rmse:.5f}")
            
            # Reproduce EXACTLY: if rmse<best_rmse: best_rmse=rmse; torch.save(model.state_dict(),"best_mmreg.pt")
            if rmse < best_rmse:
                best_rmse = rmse
                torch.save(self.model.state_dict(), self.best_model_path)
        
        # Store best rmse
        self.best_rmse = best_rmse
        
        print("=== Training Complete ===")
        print(f"Best validation RMSE: {self.best_rmse:.6f}")
        
        return {
            'best_rmse': self.best_rmse,
            'training_history': self.training_history,
            'final_predictions': yhat,
            'final_targets': yt
        }
    
    def evaluate_final_model(self) -> Dict[str, float]:
        """
        Reproduce EXACTLY the final evaluation from notebook
        """
        print("=== Final Evaluation ===")
        
        # Reproduce EXACTLY: model.load_state_dict(torch.load("best_mmreg.pt"))
        self.model.load_state_dict(torch.load(self.best_model_path, map_location=self.device))
        
        # Reproduce EXACTLY: model.eval(); preds,ys=[],[]
        self.model.eval()
        preds, ys = [], []
        
        # Reproduce EXACTLY: with torch.no_grad(): for b in te_dl:
        with torch.no_grad():
            for b in self.test_loader:
                # Reproduce EXACTLY: preds.append(model(b['s'].to(device),b['f'].to(device)).cpu())
                preds.append(self.model(b['s'].to(self.device), b['f'].to(self.device)).cpu())
                # Reproduce EXACTLY: ys.append(b['y'])
                ys.append(b['y'])
        
        # Reproduce EXACTLY: preds=np.concatenate(preds).ravel(); ys=np.concatenate(ys).ravel()
        preds = np.concatenate(preds).ravel()
        ys = np.concatenate(ys).ravel()
        
        # Reproduce EXACTLY: mse = mean_squared_error(ys,preds); rmse = np.sqrt(mse); mape = mean_absolute_percentage_error(ys,preds)
        mse = mean_squared_error(ys, preds)
        rmse = np.sqrt(mse)
        mape = mean_absolute_percentage_error(ys, preds)
        
        # Reproduce EXACTLY the print format:
        print(f"\n► MSE  : {mse:.6f}")
        print(f"► RMSE : {rmse:.6f}")
        print(f"► MAPE : {mape:.6%}")
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mape': mape,
            'predictions': preds.tolist(),
            'targets': ys.tolist()
        }
    
    def save_training_history(self, output_path: Optional[str] = None):
        """Save training history to JSON file"""
        if output_path is None:
            output_path = os.path.join(self.checkpoint_dir, OUTPUT_FILES['training_history'])
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.training_history, f, indent=2)
            print(f"Training history saved to: {output_path}")
        except Exception as e:
            print(f"Error saving training history: {e}")


def create_trainer(model: MMReg, train_loader: DataLoader, 
                  test_loader: DataLoader) -> MultimodalTrainer:
    """Factory function to create configured trainer"""
    trainer = MultimodalTrainer(model, train_loader, test_loader)
    return trainer


def resume_training(checkpoint_path: str, model: MMReg, 
                   train_loader: DataLoader, test_loader: DataLoader) -> MultimodalTrainer:
    """Resume training from checkpoint"""
    trainer = MultimodalTrainer(model, train_loader, test_loader)
    
    try:
        checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
        
        trainer.model.load_state_dict(checkpoint['model_state_dict'])
        trainer.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        trainer.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        trainer.best_rmse = checkpoint['rmse']
        trainer.training_history = checkpoint['training_history']
        
        print(f"Training resumed from checkpoint")
        
    except Exception as e:
        print(f"Error loading checkpoint: {e}")
        print("Starting fresh training...")
    
    return trainer