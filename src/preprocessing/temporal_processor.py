"""
Temporal data processing module for missing persons preprocessing
Handles date/time conversions and temporal calculations
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
from typing import Optional, Tuple, Dict

from .config import CLEANING_CONFIG


class TemporalProcessor:
    """
    Handles all temporal data processing operations
    """
    
    def __init__(self):
        self.date_format = CLEANING_CONFIG['date_format']
        self.time_format_12h = CLEANING_CONFIG['time_format_12h']
        self.time_replacements = CLEANING_CONFIG['time_replacements']
    
    def convert_time_format(self, time_str: str) -> Optional[time]:
        """
        Convert time string to time object
        
        Args:
            time_str: Time string to convert
            
        Returns:
            time object or None if conversion fails
        """
        if pd.isnull(time_str) or time_str == '':
            return None
        
        time_str_cleaned = str(time_str)
        time_str_cleaned = time_str_cleaned.replace('a.m.', 'AM').replace('p.m.', 'PM')
        
        try:
            datetime_obj = pd.to_datetime(time_str_cleaned, format=self.time_format_12h)
            return datetime_obj.time()
        except:
            return None
    
    def convert_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert date columns to datetime format

        Args:
            df: DataFrame with date columns to convert
            
        Returns:
            DataFrame with converted date columns
        """
        df_converted = df.copy()
        
        date_columns_to_convert = [
            'incident_date',     # equivalent to 'Fecha del Hecho'
            'report_date',       # equivalent to 'Fecha de Denuncia'
            'birth_date'         # equivalent to 'Fecha de Nacimiento'
        ]
        
        for date_col in date_columns_to_convert:
            if date_col in df.columns:
                print(f"Converting {date_col} to datetime format...")
                
                df_converted[date_col] = pd.to_datetime(
                    df_converted[date_col], 
                    errors='coerce', 
                    format=self.date_format
                )
                
                # Count successful conversions
                valid_dates = df_converted[date_col].notna().sum()
                print(f"  Converted {valid_dates} valid dates")
            else:
                print(f"Warning: {date_col} column not found for conversion")
        
        return df_converted
    
    def convert_time_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert time columns using the time format converter

        Args:
            df: DataFrame with time columns to convert
            
        Returns:
            DataFrame with converted time columns
        """
        df_converted = df.copy()
        
        time_columns_to_convert = [
            'incident_time',     # equivalent to 'Hora del Hecho'
            'report_time',       # equivalent to 'Hora de Denuncia'
            'birth_time'         # equivalent to 'Hora de Nacimiento'
        ]
        
        for time_col in time_columns_to_convert:
            if time_col in df.columns:
                print(f"Converting {time_col} to time format...")
                
                df_converted[time_col] = df_converted[time_col].apply(self.convert_time_format)
                
                # Count successful conversions
                valid_times = df_converted[time_col].notna().sum()
                print(f"  Converted {valid_times} valid times")
            else:
                print(f"Warning: {time_col} column not found for conversion")
        
        return df_converted
    
    def calculate_hours_elapsed(self, row: pd.Series, start_date_col: str, start_time_col: str, 
                               end_date_col: str, end_time_col: str) -> Optional[float]:
        """
        Calculate hours elapsed between two datetime points
        
        Args:
            row: DataFrame row with datetime information
            start_date_col: Column name for start date
            start_time_col: Column name for start time
            end_date_col: Column name for end date
            end_time_col: Column name for end time
            
        Returns:
            Hours elapsed as float, or None if calculation not possible
        """
        try:
            # Check if all required values are present
            start_date = row[start_date_col]
            start_time = row[start_time_col]
            end_date = row[end_date_col]
            end_time = row[end_time_col]
            
            if pd.isnull(start_date) or pd.isnull(start_time) or pd.isnull(end_date) or pd.isnull(end_time):
                return None
            
            datetime_inicio = datetime.combine(start_date.date(), start_time)
            datetime_fin = datetime.combine(end_date.date(), end_time)
            
            horas_transcurridas = (datetime_fin - datetime_inicio).total_seconds() / 3600
            
            return horas_transcurridas
            
        except Exception as e:
            return None
    
    def process_found_persons_temporal_data(self, found_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process temporal data for found persons
        
        Args:
            found_df: Found persons DataFrame
            
        Returns:
            DataFrame with processed temporal data
        """
        if found_df.empty:
            return found_df
        
        df_processed = found_df.copy()
        
        print("Processing found persons temporal data...")
        
        # Split found datetime into date and time components
        if 'found_datetime_raw' in df_processed.columns:
            split_result = df_processed['found_datetime_raw'].astype(str).str.split(' ', n=1, expand=True)
            
            if split_result.shape[1] >= 2:
                df_processed['found_date_raw'] = split_result[0]
                df_processed['found_time_raw'] = split_result[1]
            else:
                df_processed['found_date_raw'] = split_result[0]
                df_processed['found_time_raw'] = np.nan
            
            # Convert to proper formats using EXACT same logic as missing persons
            df_processed['found_date'] = pd.to_datetime(
                df_processed['found_date_raw'], 
                errors='coerce', 
                format=self.date_format
            )
            
            df_processed['found_time'] = df_processed['found_time_raw'].apply(self.convert_time_format)
            
            print(f"Processed temporal data for {len(df_processed)} found persons records")
        
        return df_processed
    
    def apply_temporal_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all temporal processing operations
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with all temporal processing applied
        """
        print("=== Starting Temporal Data Processing ===")
        
        df_processed = self.convert_date_columns(df)
        
        df_processed = self.convert_time_columns(df_processed)
        
        print("=== Temporal Data Processing Complete ===")
        
        return df_processed
    
    def get_temporal_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary of temporal data processing
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dictionary with temporal processing summary
        """
        summary = {
            'date_columns_processed': [],
            'time_columns_processed': [],
            'calculated_features': [],
            'temporal_coverage': {}
        }
        
        # Check processed date columns
        date_columns = ['incident_date', 'report_date', 'birth_date', 'found_date']
        for col in date_columns:
            if col in df.columns:
                valid_dates = df[col].notna().sum()
                summary['date_columns_processed'].append({
                    'column': col,
                    'valid_dates': valid_dates,
                    'coverage_percentage': (valid_dates / len(df)) * 100
                })
        
        # Check processed time columns
        time_columns = ['incident_time', 'report_time', 'birth_time', 'found_time']
        for col in time_columns:
            if col in df.columns:
                valid_times = df[col].notna().sum()
                summary['time_columns_processed'].append({
                    'column': col,
                    'valid_times': valid_times,
                    'coverage_percentage': (valid_times / len(df)) * 100
                })
        
        # Check calculated features
        calculated_features = ['hours_to_report', 'hours_to_appear']
        for col in calculated_features:
            if col in df.columns:
                valid_calculations = df[col].notna().sum()
                summary['calculated_features'].append({
                    'feature': col,
                    'valid_calculations': valid_calculations,
                    'coverage_percentage': (valid_calculations / len(df)) * 100
                })
        
        return summary
