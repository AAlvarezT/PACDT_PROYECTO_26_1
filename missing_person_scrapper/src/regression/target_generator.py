import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
import warnings
import json

warnings.filterwarnings('ignore')

# Keywords for target generation
TARGET_KEYWORDS = {
    'intentional': [
        "fugó", "se fugó", "se marchó", "abandono voluntario", "huida",
        "decidió irse", "salió de su casa", "salió por voluntad propia",
        "abandono", "abandono del hogar", "retiro", "reubicación voluntaria",
        "se alejó", "partió", "renunció"
    ],
    'non_intentional': [
        "desapareció", "sin paradero", "no regresó", "no volvió",
        "destino desconocido", "búsqueda", "alerta de búsqueda",
        "secuestrado", "secuestrada", "raptado", "raptada",
        "trata de personas", "privado de libertad", "se perdió", "extraviado"
    ]
}

TARGET_TEXT_COLUMNS = ['OTRAS OBSERVACIONES', 'CIRCUNSTANCIAS']


class SemanticTargetGenerator:
    def __init__(self):
        try:
            import torch
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        except:
            self.device = 'cpu'
            
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=self.device)
        self.intentional_centroid = self._compute_centroid(TARGET_KEYWORDS['intentional'])
        self.non_intentional_centroid = self._compute_centroid(TARGET_KEYWORDS['non_intentional'])
    
    def _compute_centroid(self, keyword_list):
        embeddings = self.model.encode(keyword_list, convert_to_numpy=True)
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings.mean(axis=0, keepdims=True)
    
    def compute_intentionality_score(self, text1, text2):
        embeddings = self.model.encode([str(text1), str(text2)], convert_to_numpy=True)
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        embedding_mean = embeddings.mean(axis=0, keepdims=True)
        
        similarity_intentional = float(embedding_mean @ self.intentional_centroid.T)
        similarity_non_intentional = float(embedding_mean @ self.non_intentional_centroid.T)
        
        return (similarity_intentional - similarity_non_intentional) / 2 + 0.5
    
    def generate_target_variable(self, df, text_columns=None):
        print("Generating regression target variable...")
        
        if text_columns is None:
            text_columns = []
            for target_col in TARGET_TEXT_COLUMNS:
                if target_col in df.columns:
                    text_columns.append(target_col)
        
        if len(text_columns) < 2:
            alternative_columns = ['clothing', 'OTRAS OBSERVACIONES', 'CIRCUNSTANCIAS']
            available_alternatives = [col for col in alternative_columns if col in df.columns]
            
            if len(available_alternatives) >= 2:
                text_columns = available_alternatives[:2]
            else:
                raise ValueError(f"Need at least 2 text columns. Available: {df.columns.tolist()}")
        
        print(f"Using text columns: {text_columns}")
        
        df_with_target = df.copy()
        
        tqdm.pandas(desc="→ Target Generation")
        
        def compute_row_score(row):
            text1 = str(row[text_columns[0]]) if pd.notna(row[text_columns[0]]) else ""
            text2 = str(row[text_columns[1]]) if pd.notna(row[text_columns[1]]) else ""
            return self.compute_intentionality_score(text1, text2)
        
        df_with_target['target_regression'] = df_with_target.progress_apply(
            compute_row_score, axis=1
        ).astype(np.float32)
        
        target_stats = df_with_target['target_regression'].describe()
        print(f"Target variable statistics:")
        print(f"  Mean: {target_stats['mean']:.4f}")
        print(f"  Std:  {target_stats['std']:.4f}")
        print(f"  Min:  {target_stats['min']:.4f}")
        print(f"  Max:  {target_stats['max']:.4f}")
        
        return df_with_target


def filter_valid_data(df, image_column='serialized_image'):
    print("Filtering data for valid image content...")
    
    def is_valid_json(json_string):
        try:
            json.loads(json_string)
            return True
        except:
            return False
    
    initial_count = len(df)
    
    df_filtered = df[df[image_column].notna()].copy()
    df_filtered = df_filtered[
        df_filtered[image_column].astype(str).apply(is_valid_json)
    ].reset_index(drop=True)
    
    final_count = len(df_filtered)
    removed_count = initial_count - final_count
    
    print(f"Filtered dataset: {initial_count} → {final_count} records")
    print(f"Removed {removed_count} records with invalid image data ({(removed_count/initial_count)*100:.1f}%)")
    
    return df_filtered


def load_and_prepare_regression_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"Loaded dataset: {df.shape}")
        
        df_filtered = filter_valid_data(df)
        
        target_generator = SemanticTargetGenerator()
        df_with_target = target_generator.generate_target_variable(df_filtered)
        
        return df_with_target
        
    except Exception as e:
        print(f"Error loading and preparing regression data: {e}")
        raise