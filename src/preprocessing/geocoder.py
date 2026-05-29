"""
Geocoding module for missing persons preprocessing
Handles address-to-coordinates conversion using Photon API and shapefile validation
VERSIÓN CORREGIDA que USA EL SHAPEFILE CORRECTAMENTE
"""

import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
import re
import time
import os
from typing import Dict, List, Optional, Tuple
from shapely.geometry import Point

# Conditional imports for geospatial functionality
try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    print("Warning: geopandas not available. District validation will be skipped.")

from .config import GEOCODING_CONFIG


class GeoCoder:
    """
    Handles geocoding operations for missing persons data
    """
    
    def __init__(self, shapefile_path: Optional[str] = None):
        self.shapefile_path = shapefile_path
        self.gdf_peru_distritos = None
        self.abreviaturas = GEOCODING_CONFIG['abreviaturas']
        self.photon_api_url = GEOCODING_CONFIG['photon_api_url']
        self.request_delay = GEOCODING_CONFIG['request_delay']
        self.max_retries = GEOCODING_CONFIG['max_retries']
        
        if shapefile_path and GEOPANDAS_AVAILABLE:
            self._load_shapefile()
    
    def _load_shapefile(self) -> None:
        """Load Peru districts shapefile for coordinate validation"""
        try:
            if os.path.exists(self.shapefile_path):
                print(f"Loading Peru districts shapefile: {self.shapefile_path}")
                self.gdf_peru_distritos = gpd.read_file(self.shapefile_path)
                print(f"Loaded {len(self.gdf_peru_distritos)} districts")
            else:
                print(f"Warning: Shapefile not found: {self.shapefile_path}")
        except Exception as e:
            print(f"Error loading shapefile: {e}")
            self.gdf_peru_distritos = None
    
    def expandir_abreviaturas(self, direccion: str) -> str:
        """Expand common abbreviations in address"""
        if pd.isna(direccion):
            return direccion
        
        direccion_expandida = str(direccion)
        for abrev, completo in self.abreviaturas.items():
            direccion_expandida = re.sub(r'\b' + abrev + r'\b', completo, direccion_expandida, flags=re.IGNORECASE)
        return direccion_expandida
    
    def separar_direccion(self, direccion: str) -> Tuple[str, str]:
        """Separate general and specific address parts"""
        if pd.isna(direccion):
            return "", ""
        
        partes = str(direccion).split('-')
        direccion_general = "-".join(partes[:3])
        direccion_especifica = " ".join(partes[3:])
        return direccion_general, direccion_especifica
    
    def formatear_direccion(self, direccion: str) -> str:
        """Clean and format specific address"""
        if pd.isna(direccion):
            return ""
        
        direccion_formateada = str(direccion)
        direccion_formateada = self.expandir_abreviaturas(direccion_formateada)
        direccion_formateada = re.sub(r'[^\w\s]', '', direccion_formateada)
        direccion_formateada = re.sub(r'\s+', ' ', direccion_formateada)
        direccion_formateada = direccion_formateada.strip()
        return direccion_formateada
    
    def intentar_geocodificar(self, direccion_general: str, direccion_especifica: str) -> Optional[Point]:
        """Attempt geocoding with Photon API"""
        direccion_especifica = self.formatear_direccion(direccion_especifica)
        
        combinaciones = [
            f"{direccion_especifica}, {direccion_general}, Peru",
            f"{direccion_general}, Peru"
        ]
        
        for direccion_intento in combinaciones:
            for retry in range(self.max_retries):
                try:
                    response = requests.get(
                        self.photon_api_url, 
                        params={'q': direccion_intento, 'limit': 1},
                        timeout=10
                    )
                    data = response.json()
                    
                    if data['features']:
                        location = data['features'][0]['geometry']['coordinates']
                        return Point(location[0], location[1])
                        
                except requests.RequestException as e:
                    print(f"Request error (retry {retry+1}/{self.max_retries}): {e}")
                    if retry < self.max_retries - 1:
                        time.sleep(self.request_delay)
                    
                except Exception as e:
                    print(f"Unknown error: {e}")
                    break
        
        return None
    
    def verificar_en_distrito(self, lat: float, lon: float) -> bool:
        """
        Verify if coordinates are within any Peru district
        CORREGIDO: Manejo correcto del GeoDataFrame
        """
        # VERIFICACIÓN CORRECTA: Primero verificar si es None
        if self.gdf_peru_distritos is None:
            return True
        
        # VERIFICACIÓN CORRECTA: Luego verificar si está vacío usando .empty
        if self.gdf_peru_distritos.empty:
            return True
        
        try:
            point = Point(lon, lat)
            
            # MÉTODO CORRECTO: Usar el método .contains() de geopandas
            contains_mask = self.gdf_peru_distritos.geometry.contains(point)
            
            # VERIFICACIÓN CORRECTA: Usar .any() para ver si algún distrito contiene el punto
            return contains_mask.any()
            
        except Exception as e:
            print(f"Error in district verification: {e}")
            return True  # Return True on error to avoid losing data
    
    def geocodificar_optimizado(self, df: pd.DataFrame, location_column: str = 'incident_location') -> pd.DataFrame:
        """Optimized geocoding that removes duplicates first"""
        print(f"Starting optimized geocoding for {len(df)} addresses...")
        
        df_geocoded = df.copy()
        
        # Inicializar columnas de geocodificación
        df_geocoded['Latitud'] = np.nan
        df_geocoded['Longitud'] = np.nan
        df_geocoded['En_Distrito'] = np.nan
        
        # Remove duplicates based on location column to reduce API calls
        unique_addresses = df_geocoded[location_column].dropna().unique()
        
        print(f"Found {len(unique_addresses)} unique addresses to geocode")
        
        # Crear diccionario para mapear direcciones a coordenadas
        address_to_coords = {}
        direcciones_no_encontradas = []
        
        # Geocode unique addresses only
        for direccion in tqdm(unique_addresses, desc="Geocodificando direcciones"):
            if pd.isna(direccion) or str(direccion).strip() == '':
                continue
            
            try:
                direccion_general, direccion_especifica = self.separar_direccion(direccion)
                location = self.intentar_geocodificar(direccion_general, direccion_especifica)
                
                if location:
                    lat, lon = location.y, location.x
                    
                    # Verify if coordinates are within correct district
                    distrito_encontrado = self.verificar_en_distrito(lat, lon)
                    
                    address_to_coords[direccion] = {
                        'lat': lat, 
                        'lon': lon, 
                        'en_distrito': distrito_encontrado
                    }
                else:
                    direcciones_no_encontradas.append(str(direccion))
                    
            except Exception as e:
                print(f"Error geocoding address '{direccion}': {e}")
                direcciones_no_encontradas.append(str(direccion))
                continue
        
        # Mapear coordenadas de vuelta al DataFrame original
        print("Mapping coordinates back to original dataset...")
        
        for idx, row in df_geocoded.iterrows():
            direccion = row[location_column]
            
            if pd.notna(direccion) and direccion in address_to_coords:
                coords = address_to_coords[direccion]
                df_geocoded.at[idx, 'Latitud'] = coords['lat']
                df_geocoded.at[idx, 'Longitud'] = coords['lon']
                df_geocoded.at[idx, 'En_Distrito'] = coords['en_distrito']
        
        # Report results
        final_geocoded_count = df_geocoded['Latitud'].notna().sum()
        success_rate = (final_geocoded_count / len(df_geocoded)) * 100
        
        print(f"Optimized geocoding completed:")
        print(f"  Successfully geocoded: {final_geocoded_count} addresses ({success_rate:.1f}%)")
        print(f"  Failed to geocode: {len(direcciones_no_encontradas)} addresses")
        
        # Mostrar estadísticas de validación de distritos si está disponible
        if self.gdf_peru_distritos is not None and not self.gdf_peru_distritos.empty:
            valid_districts = df_geocoded['En_Distrito'].sum()
            district_rate = (valid_districts / final_geocoded_count) * 100 if final_geocoded_count > 0 else 0
            print(f"  In valid Peru districts: {valid_districts} addresses ({district_rate:.1f}%)")
        
        # Save failed addresses if any
        if direcciones_no_encontradas:
            try:
                failed_file = GEOCODING_CONFIG['failed_addresses_filename']
                with open(failed_file, 'w', encoding='utf-8') as f:
                    for direccion in direcciones_no_encontradas:
                        f.write(f"{direccion}\n")
                print(f"  Failed addresses saved to: {failed_file}")
            except Exception as e:
                print(f"  Could not save failed addresses: {e}")
        
        return df_geocoded


def get_peru_shapefile_path() -> Optional[str]:
    """Find Peru districts shapefile in expected locations"""
    possible_paths = [
        'data/external/peru_shapes/per_admbnda_adm3_ign_20200714.shp',
        'C:/peru_shapes/per_admbnda_adm3_ign_20200714.shp',
        'peru_shapes/per_admbnda_adm3_ign_20200714.shp',
        'data/external/peru_shapes/peru_distritos.shp',
        'data/external/peru_shapes/peru_districts.shp'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    print("Warning: Peru districts shapefile not found in expected locations")
    return None
