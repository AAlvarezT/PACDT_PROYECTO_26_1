"""
Feature engineering module for missing persons preprocessing
Handles creation of target variables and advanced features
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .temporal_processor import TemporalProcessor


class FeatureEngineer:
    """
    Handles feature engineering operations including target variable creation
    """
    
    def __init__(self):
        self.temporal_processor = TemporalProcessor()
    
    def create_appeared_status(self, missing_df: pd.DataFrame, found_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create appeared status based on name and photo URL matching
        
        Args:
            missing_df: Missing persons DataFrame
            found_df: Found persons DataFrame
            
        Returns:
            DataFrame with appeared_status column added
        """
        if found_df.empty:
            print("Warning: No found persons data available, setting all appeared_status to False")
            missing_df_with_status = missing_df.copy()
            missing_df_with_status['appeared_status'] = False
            return missing_df_with_status
        
        print("Creating appeared status based on name and photo matching...")
        
        missing_df_with_status = missing_df.copy()
        

        
        name_matches = missing_df_with_status['full_name'].isin(found_df['full_name'])
        photo_matches = missing_df_with_status['photo_url'].isin(found_df['photo_url'])
        
        missing_df_with_status['appeared_status'] = name_matches & photo_matches
        
        # Summary statistics
        total_appeared = missing_df_with_status['appeared_status'].sum()
        appearance_rate = (total_appeared / len(missing_df_with_status)) * 100
        
        print(f"Found {total_appeared} persons who appeared ({appearance_rate:.2f}% of total)")
        
        return missing_df_with_status
    
    def add_found_persons_temporal_data(self, missing_df: pd.DataFrame, found_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add temporal data from found persons to missing persons DataFrame
        
        Args:
            missing_df: Missing persons DataFrame with appeared_status
            found_df: Found persons DataFrame with temporal data
            
        Returns:
            DataFrame with found temporal data added
        """
        if found_df.empty:
            print("Warning: No found persons data to merge")
            missing_df_enhanced = missing_df.copy()
            missing_df_enhanced['found_date'] = pd.NaT
            missing_df_enhanced['found_time'] = None
            return missing_df_enhanced
        
        print("Adding found persons temporal data to missing persons records...")
        
        missing_df_enhanced = missing_df.copy()
        
        # Process found persons temporal data first
        found_df_processed = self.temporal_processor.process_found_persons_temporal_data(found_df)
        
        # Initialize found temporal columns with NaN/None
        missing_df_enhanced['found_date'] = pd.NaT
        missing_df_enhanced['found_time'] = None
        
        # Get subset of found persons whose names are in missing persons
        matching_found = found_df_processed[found_df_processed['full_name'].isin(missing_df_enhanced['full_name'])]
        
        if len(matching_found) > 0:
            # Create mapping from name to found date/time
            name_to_found_date = dict(zip(matching_found['full_name'], matching_found['found_date']))
            name_to_found_time = dict(zip(matching_found['full_name'], matching_found['found_time']))
            
            # Apply mapping to all missing persons (not just appeared ones initially)
            for idx, row in missing_df_enhanced.iterrows():
                person_name = row['full_name']
                if person_name in name_to_found_date:
                    missing_df_enhanced.loc[idx, 'found_date'] = name_to_found_date[person_name]
                if person_name in name_to_found_time:
                    missing_df_enhanced.loc[idx, 'found_time'] = name_to_found_time[person_name]
        
        # Count successful mappings
        found_dates_added = missing_df_enhanced['found_date'].notna().sum()
        found_times_added = missing_df_enhanced['found_time'].notna().sum()
        
        print(f"Added found dates for {found_dates_added} records")
        print(f"Added found times for {found_times_added} records")
        
        return missing_df_enhanced
    
    def calculate_hours_to_appear(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate hours from incident to appearance

        Args:
            df: DataFrame with incident and found temporal data
            
        Returns:
            DataFrame with hours_to_appear column added
        """
        print("Calculating hours from incident to appearance...")
        
        df_with_calculation = df.copy()
        
        required_columns = ['found_date', 'found_time']  # equivalent to 'Fecha de Aparición', 'Hora de Aparición'
        subset_for_calculation = df_with_calculation.dropna(subset=required_columns).copy()
        
        if len(subset_for_calculation) == 0:
            print("Warning: No records with found date and time information")
            df_with_calculation['hours_to_appear'] = np.nan
            return df_with_calculation
        
        # We also need incident data for the calculation
        subset_with_incident = subset_for_calculation.dropna(subset=['incident_date', 'incident_time']).copy()
        
        if len(subset_with_incident) == 0:
            print("Warning: No records with complete incident and found datetime information")
            df_with_calculation['hours_to_appear'] = np.nan
            return df_with_calculation
        
        subset_with_incident['hours_to_appear'] = subset_with_incident.apply(
            lambda row: self.temporal_processor.calculate_hours_elapsed(
                row, 'incident_date', 'incident_time', 'found_date', 'found_time'
            ),
            axis=1
        )
        
        df_with_calculation['hours_to_appear'] = np.nan
        df_with_calculation.loc[subset_with_incident.index, 'hours_to_appear'] = subset_with_incident['hours_to_appear']
        
        valid_calculations = subset_with_incident['hours_to_appear'].notna().sum()
        print(f"Calculated hours to appear for {valid_calculations} records")
        
        return df_with_calculation
    
    def calculate_hours_to_report(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate hours from incident to report (MISSING from original implementation!)

        Args:
            df: DataFrame with incident and report temporal data
            
        Returns:
            DataFrame with hours_to_report column added
        """
        print("Calculating hours from incident to report...")
        
        df_with_calculation = df.copy()
        
        required_columns = ['incident_date', 'incident_time', 'report_date', 'report_time']
        subset_for_calculation = df_with_calculation.dropna(subset=required_columns).copy()
        
        if len(subset_for_calculation) == 0:
            print("Warning: No records with complete incident and report datetime information")
            df_with_calculation['hours_to_report'] = np.nan
            return df_with_calculation
        
        subset_for_calculation['hours_to_report'] = subset_for_calculation.apply(
            lambda row: self.temporal_processor.calculate_hours_elapsed(
                row, 'incident_date', 'incident_time', 'report_date', 'report_time'
            ),
            axis=1
        )
        
        df_with_calculation['hours_to_report'] = np.nan
        df_with_calculation.loc[subset_for_calculation.index, 'hours_to_report'] = subset_for_calculation['hours_to_report']
        
        valid_calculations = subset_for_calculation['hours_to_report'].notna().sum()
        print(f"Calculated hours to report for {valid_calculations} records")
        
        return df_with_calculation
    
    def create_demographic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create additional demographic and categorical features
        
        Args:
            df: DataFrame to enhance with demographic features
            
        Returns:
            DataFrame with additional demographic features
        """
        print("Creating demographic features...")
        
        df_enhanced = df.copy()
        
        # Age categories
        if 'age_cleaned' in df.columns:
            df_enhanced['age_category'] = pd.cut(
                df_enhanced['age_cleaned'],
                bins=[0, 12, 18, 30, 50, 65, 100],
                labels=['Child', 'Adolescent', 'Young Adult', 'Adult', 'Middle Aged', 'Senior'],
                right=False
            )
        
        # Height categories  
        if 'height_cleaned' in df.columns:
            df_enhanced['height_category'] = pd.cut(
                df_enhanced['height_cleaned'],
                bins=[0, 150, 160, 170, 180, 250],
                labels=['Very Short', 'Short', 'Average', 'Tall', 'Very Tall'],
                right=False
            )
        
        # Time-based features from incident date
        if 'incident_date' in df.columns:
            df_enhanced['incident_year'] = df_enhanced['incident_date'].dt.year
            df_enhanced['incident_month'] = df_enhanced['incident_date'].dt.month
            df_enhanced['incident_day_of_week'] = df_enhanced['incident_date'].dt.day_name()
            df_enhanced['incident_quarter'] = df_enhanced['incident_date'].dt.quarter
        
        # Binary features for data availability
        df_enhanced['has_photo'] = df_enhanced['photo_url'].notna() & (df_enhanced['photo_url'] != '')
        df_enhanced['has_distinctive_marks'] = df_enhanced.get('distinctive_marks', pd.Series()).notna()
        df_enhanced['has_complete_temporal_data'] = (
            df_enhanced['incident_date'].notna() & 
            df_enhanced['incident_time'].notna() &
            df_enhanced['report_date'].notna() & 
            df_enhanced['report_time'].notna()
        )
        
        print("Demographic features created successfully")
        
        return df_enhanced
    
    def apply_feature_engineering(self, missing_df: pd.DataFrame, found_df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply complete feature engineering workflow
        
        Args:
            missing_df: Missing persons DataFrame
            found_df: Found persons DataFrame
            
        Returns:
            DataFrame with all engineered features
        """
        print("=== Starting Feature Engineering ===")
        
        # Step 1: Create appeared status
        df_with_status = self.create_appeared_status(missing_df, found_df)
        
        # Step 2: Add found persons temporal data
        df_with_found_data = self.add_found_persons_temporal_data(df_with_status, found_df)
        
        # Step 3: Calculate hours to appear (Horas para Aparecer)
        df_with_hours_to_appear = self.calculate_hours_to_appear(df_with_found_data)
        
        # Step 4: Calculate hours to report (Horas para Denunciar) - WAS MISSING!
        df_with_hours_to_report = self.calculate_hours_to_report(df_with_hours_to_appear)
        
        # Step 5: Create additional demographic features
        df_final = self.create_demographic_features(df_with_hours_to_report)
        
        print("=== Feature Engineering Complete ===")
        
        return df_final
    
    def get_feature_engineering_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary of feature engineering operations
        
        Args:
            df: DataFrame with engineered features
            
        Returns:
            Dictionary with feature engineering summary
        """
        summary = {
            'target_variable': {},
            'temporal_features': {},
            'demographic_features': {},
            'data_quality_features': {}
        }
        
        # Target variable analysis
        if 'appeared_status' in df.columns:
            appeared_count = df['appeared_status'].sum()
            total_count = len(df)
            summary['target_variable'] = {
                'total_cases': total_count,
                'appeared_cases': appeared_count,
                'missing_cases': total_count - appeared_count,
                'appearance_rate': (appeared_count / total_count) * 100
            }
        
        # Temporal features analysis (now includes both!)
        temporal_features = ['hours_to_appear', 'hours_to_report']
        for feature in temporal_features:
            if feature in df.columns:
                valid_values = df[feature].notna().sum()
                summary['temporal_features'][feature] = {
                    'valid_calculations': valid_values,
                    'coverage_percentage': (valid_values / len(df)) * 100,
                    'mean_hours': df[feature].mean() if valid_values > 0 else None,
                    'median_hours': df[feature].median() if valid_values > 0 else None
                }
        
        # Demographic features analysis
        demographic_features = ['age_category', 'height_category', 'incident_day_of_week']
        for feature in demographic_features:
            if feature in df.columns:
                summary['demographic_features'][feature] = df[feature].value_counts().to_dict()
        
        # Data quality features
        quality_features = ['has_photo', 'has_distinctive_marks', 'has_complete_temporal_data']
        for feature in quality_features:
            if feature in df.columns:
                summary['data_quality_features'][feature] = {
                    'count': df[feature].sum(),
                    'percentage': (df[feature].sum() / len(df)) * 100
                }
        
        return summary
