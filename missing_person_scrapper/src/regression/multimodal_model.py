"""
Multimodal regression model architecture
Implements the MMReg model combining structured data and face images with attention
"""

import torch
import torch.nn as nn
from torchvision import models
from typing import Tuple, Dict, Optional
import numpy as np

from .config import MODEL_CONFIG


class ResidualBlock(nn.Module):
    """
    Residual block for structured data processing
    Reproduces the original ResBlock class exactly
    """
    
    def __init__(self, hidden_dim: int):
        """
        Initialize residual block
        
        Args:
            hidden_dim: Hidden dimension size
        """
        super().__init__()
        
        # Reproduce original: nn.Sequential(nn.Linear(d,d),nn.ReLU(),nn.Linear(d,d))
        self.sequence = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with residual connection
        Reproduces: return torch.relu(x+self.seq(x))
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor with residual connection
        """
        return torch.relu(x + self.sequence(x))


class FaceFeatureExtractor(nn.Module):
    """
    Face feature extraction using fine-tuned ResNet50
    Reproduces the original ResNet50 backbone with selective fine-tuning
    """
    
    def __init__(self):
        super().__init__()
        
        # Load pretrained ResNet50 (reproduce original: models.resnet50(weights=...))
        base_resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        
        # Extract backbone without final classification layer
        # Reproduce original: nn.Sequential(*list(base.children())[:-1])
        self.backbone = nn.Sequential(*list(base_resnet.children())[:-1])
        
        # Configure trainable parameters (reproduce original layer freezing logic)
        self._configure_trainable_layers()
        
        # Feature projection network
        self.feature_projection = self._create_face_projection()
    
    def _configure_trainable_layers(self):
        """
        Configure which layers are trainable
        Reproduces: p.requires_grad = name.split('.')[0] in {'6','7'}
        """
        trainable_layers = MODEL_CONFIG['resnet_config']['trainable_layers']
        
        for name, param in self.backbone.named_parameters():
            layer_index = name.split('.')[0]
            # Only train specified layers (layer3=6, layer4=7 in original)
            param.requires_grad = layer_index in trainable_layers
        
        # Count trainable parameters
        trainable_params = sum(p.numel() for p in self.backbone.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.backbone.parameters())
        
        print(f"ResNet50 backbone: {trainable_params:,} / {total_params:,} parameters trainable")
    
    def _create_face_projection(self) -> nn.Module:
        """Create face feature projection network"""
        config = MODEL_CONFIG['face_projection']
        
        # Reproduce original face projection architecture
        return nn.Sequential(
            nn.Linear(config['input_size'], config['hidden_size']),
            nn.BatchNorm1d(config['hidden_size']) if config['use_batch_norm'] else nn.Identity(),
            nn.ReLU(),
            nn.Dropout(config['dropout_rate']),
            nn.Linear(config['hidden_size'], config['output_size'])
        )
    
    def forward(self, face_images: torch.Tensor) -> torch.Tensor:
        """
        Extract features from face images
        
        Args:
            face_images: Batch of face images [B, 3, 160, 160]
            
        Returns:
            Face feature embeddings [B, 128]
        """
        # Extract backbone features (reproduce original: torch.flatten(self.bb(f_img),1))
        backbone_features = torch.flatten(self.backbone(face_images), 1)  # [B, 2048]
        
        # Project to final feature space (reproduce original: self.face_proj(x))
        face_embeddings = self.feature_projection(backbone_features)  # [B, 128]
        
        return face_embeddings


class StructuredDataProcessor(nn.Module):
    """
    Structured data processing with residual connections
    Reproduces the original structured data processing pipeline
    """
    
    def __init__(self, input_dim: int):
        super().__init__()
        
        hidden_size = MODEL_CONFIG['structured_projection']['hidden_size']
        
        # Initial projection (reproduce original: self.s_proj)
        projection_layers = [nn.Linear(input_dim, hidden_size)]
        if MODEL_CONFIG['structured_projection']['use_batch_norm']:
            projection_layers.append(nn.BatchNorm1d(hidden_size))
        projection_layers.append(nn.ReLU())
        
        self.structured_projection = nn.Sequential(*projection_layers)
        
        # Residual processing (reproduce original: self.s_res)
        self.residual_processor = self._create_residual_processor()
    
    def _create_residual_processor(self) -> nn.Module:
        """Create residual processing blocks"""
        config = MODEL_CONFIG['residual_blocks']
        
        # Reproduce original: nn.Sequential(ResBlock(128),nn.Dropout(0.3),ResBlock(128))
        layers = []
        for i in range(config['num_blocks']):
            layers.append(ResidualBlock(config['hidden_size']))
            if i < config['num_blocks'] - 1:  # Don't add dropout after last block
                layers.append(nn.Dropout(config['dropout_rate']))
        
        return nn.Sequential(*layers)
    
    def forward(self, structured_data: torch.Tensor) -> torch.Tensor:
        """
        Process structured data
        
        Args:
            structured_data: Batch of structured features [B, input_dim]
            
        Returns:
            Processed structured embeddings [B, 128]
        """
        # Project to hidden space (reproduce original: self.s_proj(s))
        projected = self.structured_projection(structured_data)
        
        # Apply residual processing (reproduce original: self.s_res(...))
        processed = self.residual_processor(projected)
        
        return processed


class MultimodalAttentionFusion(nn.Module):
    """
    Attention-based fusion of structured and face features
    Reproduces the original multi-head attention mechanism
    """
    
    def __init__(self):
        super().__init__()
        
        config = MODEL_CONFIG['attention_config']
        
        # Reproduce original: nn.MultiheadAttention(128,4,batch_first=True,dropout=0.2)
        self.attention = nn.MultiheadAttention(
            embed_dim=config['embed_dim'],
            num_heads=config['num_heads'],
            dropout=config['dropout'],
            batch_first=config['batch_first']
        )
    
    def forward(self, structured_features: torch.Tensor, 
                face_features: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Apply attention mechanism between structured and face features
        
        Args:
            structured_features: Structured data embeddings [B, 128]
            face_features: Face feature embeddings [B, 128]
            
        Returns:
            Tuple of (structured_features, attended_face_features)
        """
        # Reproduce original attention mechanism:
        # q=s.unsqueeze(1); k=v=f.unsqueeze(1)
        # att,_ = self.att(q,k,v); att=att.squeeze(1)
        
        query = structured_features.unsqueeze(1)      # [B, 1, 128] - structured as query
        key = value = face_features.unsqueeze(1)      # [B, 1, 128] - face as key and value
        
        attended_features, attention_weights = self.attention(query, key, value)
        attended_features = attended_features.squeeze(1)  # [B, 128]
        
        return structured_features, attended_features


class PredictionHead(nn.Module):
    """
    Final prediction head for regression output
    Reproduces the original prediction head architecture
    """
    
    def __init__(self):
        super().__init__()
        
        config = MODEL_CONFIG['prediction_head']
        
        # Reproduce original: nn.Sequential(nn.Linear(256,64),nn.ReLU(),nn.Dropout(0.3),nn.Linear(64,1),nn.Sigmoid())
        layers = [
            nn.Linear(config['input_size'], config['hidden_size']),
            nn.ReLU(),
            nn.Dropout(config['dropout_rate']),
            nn.Linear(config['hidden_size'], 1)
        ]
        
        if config['use_sigmoid']:
            layers.append(nn.Sigmoid())
        
        self.prediction_network = nn.Sequential(*layers)
    
    def forward(self, fused_features: torch.Tensor) -> torch.Tensor:
        """
        Generate final predictions
        
        Args:
            fused_features: Concatenated features [B, 256]
            
        Returns:
            Predictions [B, 1]
        """
        return self.prediction_network(fused_features)


class MMReg(nn.Module):
    """
    Multimodal Regression model combining structured data and face images
    Reproduces the original MMReg class architecture exactly
    """
    
    def __init__(self, structured_input_dim: int):
        """
        Initialize multimodal regression model
        
        Args:
            structured_input_dim: Dimension of structured input features
        """
        super().__init__()
        
        print(f"Initializing MMReg with structured input dim: {structured_input_dim}")
        
        # Initialize all components
        self.face_extractor = FaceFeatureExtractor()
        self.structured_processor = StructuredDataProcessor(structured_input_dim)
        self.attention_fusion = MultimodalAttentionFusion()
        self.prediction_head = PredictionHead()
        
        # Store configuration for logging
        self.config = MODEL_CONFIG
        self.structured_input_dim = structured_input_dim
        
        self._print_model_summary()
    
    def forward(self, structured_data: torch.Tensor, 
                face_images: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through multimodal model
        Reproduces the original forward method exactly
        
        Args:
            structured_data: Structured features [B, structured_dim]
            face_images: Face images [B, 3, 160, 160]
            
        Returns:
            Regression predictions [B, 1]
        """
        # Process structured data (reproduce original: s = self.s_res(self.s_proj(s)))
        structured_features = self.structured_processor(structured_data)  # [B, 128]
        
        # Extract face features (reproduce original face processing)
        face_features = self.face_extractor(face_images)  # [B, 128]
        
        # Apply attention fusion (reproduce original attention mechanism)
        structured_out, attended_face = self.attention_fusion(structured_features, face_features)
        
        # Concatenate features (reproduce original: torch.cat([s,att],dim=1))
        fused_features = torch.cat([structured_out, attended_face], dim=1)  # [B, 256]
        
        # Generate predictions (reproduce original: self.head(...))
        predictions = self.prediction_head(fused_features)  # [B, 1]
        
        return predictions
    
    def _print_model_summary(self):
        """Print model architecture summary"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        print(f"\n=== MMReg Model Summary ===")
        print(f"Structured input dimension: {self.structured_input_dim}")
        print(f"Total parameters: {total_params:,}")
        print(f"Trainable parameters: {trainable_params:,}")
        print(f"Parameter efficiency: {(trainable_params/total_params)*100:.1f}%")
        
        # Component-wise parameter counts
        component_params = {
            'Face Extractor': sum(p.numel() for p in self.face_extractor.parameters()),
            'Structured Processor': sum(p.numel() for p in self.structured_processor.parameters()),
            'Attention Fusion': sum(p.numel() for p in self.attention_fusion.parameters()),
            'Prediction Head': sum(p.numel() for p in self.prediction_head.parameters())
        }
        
        print(f"\nComponent-wise parameters:")
        for component, params in component_params.items():
            print(f"  {component}: {params:,}")
        print("=" * 30)
    
    def get_attention_weights(self, structured_data: torch.Tensor, 
                             face_images: torch.Tensor) -> torch.Tensor:
        """
        Extract attention weights for interpretability
        
        Args:
            structured_data: Structured features
            face_images: Face images
            
        Returns:
            Attention weights
        """
        with torch.no_grad():
            structured_features = self.structured_processor(structured_data)
            face_features = self.face_extractor(face_images)
            
            query = structured_features.unsqueeze(1)
            key = value = face_features.unsqueeze(1)
            
            _, attention_weights = self.attention_fusion.attention(query, key, value)
            
        return attention_weights
    
    def get_feature_embeddings(self, structured_data: torch.Tensor, 
                              face_images: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Extract intermediate feature embeddings for analysis
        
        Args:
            structured_data: Structured features
            face_images: Face images
            
        Returns:
            Dictionary with intermediate embeddings
        """
        with torch.no_grad():
            structured_features = self.structured_processor(structured_data)
            face_features = self.face_extractor(face_images)
            structured_out, attended_face = self.attention_fusion(structured_features, face_features)
            
        return {
            'structured_embeddings': structured_features,
            'face_embeddings': face_features,
            'attended_face_embeddings': attended_face,
            'final_structured_embeddings': structured_out
        }
    
    def freeze_backbone(self):
        """Freeze ResNet backbone for faster training"""
        for param in self.face_extractor.backbone.parameters():
            param.requires_grad = False
        print("ResNet backbone frozen")
    
    def unfreeze_backbone(self):
        """Unfreeze ResNet backbone for fine-tuning"""
        trainable_layers = MODEL_CONFIG['resnet_config']['trainable_layers']
        
        for name, param in self.face_extractor.backbone.named_parameters():
            layer_index = name.split('.')[0]
            param.requires_grad = layer_index in trainable_layers
        print(f"ResNet backbone unfrozen (layers {trainable_layers})")


def create_mmreg_model(structured_input_dim: int, device: torch.device) -> MMReg:
    """
    Factory function to create and initialize MMReg model
    
    Args:
        structured_input_dim: Dimension of structured input features
        device: Device to place model on
        
    Returns:
        Initialized MMReg model
    """
    model = MMReg(structured_input_dim)
    model = model.to(device)
    
    # Initialize weights if needed
    def init_weights(m):
        if isinstance(m, nn.Linear):
            torch.nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                torch.nn.init.zeros_(m.bias)
    
    # Apply weight initialization to new components (not pretrained ResNet)
    model.structured_processor.apply(init_weights)
    model.attention_fusion.apply(init_weights)  
    model.prediction_head.apply(init_weights)
    
    return model


def count_model_parameters(model: nn.Module) -> Dict[str, int]:
    """
    Count model parameters by component
    
    Args:
        model: PyTorch model
        
    Returns:
        Dictionary with parameter counts
    """
    param_counts = {
        'total': sum(p.numel() for p in model.parameters()),
        'trainable': sum(p.numel() for p in model.parameters() if p.requires_grad),
        'frozen': sum(p.numel() for p in model.parameters() if not p.requires_grad)
    }
    
    if hasattr(model, 'face_extractor'):
        param_counts['face_extractor'] = sum(p.numel() for p in model.face_extractor.parameters())
        param_counts['face_extractor_trainable'] = sum(p.numel() for p in model.face_extractor.parameters() if p.requires_grad)
    
    return param_counts