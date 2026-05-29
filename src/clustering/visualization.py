"""
Visualization module for clustering analysis results
Creates interactive plots and charts using Plotly
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Optional, Tuple, Any
import os

from .config import VISUALIZATION_CONFIG, CLUSTERING_FIGURES_DIR


class ClusteringVisualizer:
    """
    Creates visualizations for clustering analysis results
    Reproduces the original Plotly visualizations
    """
    
    def __init__(self):
        self.figure_size = VISUALIZATION_CONFIG['figure_size']
        self.color_palette = VISUALIZATION_CONFIG['color_palette']
        self.save_formats = VISUALIZATION_CONFIG['save_formats']
        self.dpi = VISUALIZATION_CONFIG['dpi']
    
    def create_metrics_comparison_plot(self, results_df: pd.DataFrame) -> go.Figure:
        """
        Create comparison plot of clustering metrics across modalities
        Reproduces the original Plotly subplot visualization
        
        Args:
            results_df: DataFrame with clustering results
            
        Returns:
            Plotly Figure object
        """
        print("Creating metrics comparison plot...")
        
        # Reproduce original: make_subplots with three columns
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=(
                "Silhouette Score (Train)",
                "Silhouette Score (Test)", 
                "Davies–Bouldin Index (Test)"
            )
        )
        
        # Get modality names (reproduce original: modalidades = res_df['Modalidad'].tolist())
        modality_names = results_df['Modalidad'].tolist()
        
        # Add traces (reproduce original bar charts)
        fig.add_trace(
            go.Bar(
                x=modality_names, 
                y=results_df['Sil_train'], 
                name="Train",
                marker_color=self.color_palette[0]
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=modality_names, 
                y=results_df['Sil_test'], 
                name="Test",
                marker_color=self.color_palette[1]
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=modality_names, 
                y=results_df['DB_test'], 
                name="DB Index",
                marker_color=self.color_palette[2]
            ),
            row=1, col=3
        )
        
        # Update layout (reproduce original layout settings)
        fig.update_layout(
            title_text="Comparación de Métricas de Clustering",
            height=self.figure_size[1],
            width=self.figure_size[0],
            showlegend=False
        )
        
        # Update axes and labels (reproduce original)
        axis_labels = [
            'Silhouette Train',
            'Silhouette Test', 
            'Davies–Bouldin Test'
        ]
        
        for i, ylabel in enumerate(axis_labels, start=1):
            fig.update_yaxes(title_text=ylabel, row=1, col=i)
            fig.update_xaxes(tickangle=45, row=1, col=i)  # Rotate x-axis labels
        
        print("Metrics comparison plot created successfully")
        return fig
    
    def create_detailed_metrics_table(self, results_df: pd.DataFrame) -> go.Figure:
        """
        Create detailed table with all clustering metrics
        
        Args:
            results_df: DataFrame with clustering results
            
        Returns:
            Plotly Figure with table
        """
        print("Creating detailed metrics table...")
        
        # Prepare table data
        table_data = results_df.round(4)
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(table_data.columns),
                fill_color='lightblue',
                align='center',
                font_size=12,
                height=40
            ),
            cells=dict(
                values=[table_data[col] for col in table_data.columns],
                fill_color='white',
                align='center',
                font_size=11,
                height=30
            )
        )])
        
        fig.update_layout(
            title="Detailed Clustering Results",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_optimal_clusters_plot(self, results_df: pd.DataFrame) -> go.Figure:
        """
        Create plot showing optimal number of clusters for each modality
        
        Args:
            results_df: DataFrame with clustering results
            
        Returns:
            Plotly Figure object
        """
        print("Creating optimal clusters plot...")
        
        fig = go.Figure()
        
        # Bar chart of optimal k values
        fig.add_trace(go.Bar(
            x=results_df['Modalidad'],
            y=results_df['k_opt'],
            text=results_df['k_opt'],
            textposition='auto',
            marker_color=self.color_palette[3],
            name='Optimal k'
        ))
        
        fig.update_layout(
            title="Número Óptimo de Clusters por Modalidad",
            xaxis_title="Modalidad",
            yaxis_title="Número de Clusters (k)",
            height=400,
            width=800
        )
        
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    def create_covariance_type_plot(self, results_df: pd.DataFrame) -> go.Figure:
        """
        Create plot showing optimal covariance types
        
        Args:
            results_df: DataFrame with clustering results
            
        Returns:
            Plotly Figure object
        """
        print("Creating covariance type plot...")
        
        # Count occurrences of each covariance type
        cov_counts = results_df['cov_opt'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=cov_counts.index,
            values=cov_counts.values,
            hole=0.4,
            marker_colors=self.color_palette[:len(cov_counts)]
        )])
        
        fig.update_layout(
            title="Distribución de Tipos de Covarianza Óptimos",
            height=400,
            width=500
        )
        
        return fig
    
    def create_silhouette_heatmap(self, results_df: pd.DataFrame) -> go.Figure:
        """
        Create heatmap comparing silhouette scores
        
        Args:
            results_df: DataFrame with clustering results
            
        Returns:
            Plotly Figure object
        """
        print("Creating silhouette heatmap...")
        
        # Prepare data for heatmap
        heatmap_data = results_df.set_index('Modalidad')[['Sil_train', 'Sil_test']]
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values.T,
            x=heatmap_data.index,
            y=['Train', 'Test'],
            colorscale='Viridis',
            text=np.round(heatmap_data.values.T, 3),
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Silhouette Scores por Modalidad y Conjunto",
            xaxis_title="Modalidad",
            yaxis_title="Conjunto de Datos",
            height=300,
            width=800
        )
        
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    def create_comprehensive_dashboard(self, results_df: pd.DataFrame) -> go.Figure:
        """
        Create comprehensive dashboard with multiple visualizations
        
        Args:
            results_df: DataFrame with clustering results
            
        Returns:
            Plotly Figure with subplots
        """
        print("Creating comprehensive dashboard...")
        
        # Create subplots with different types
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Silhouette Scores Comparison",
                "Davies-Bouldin Index",
                "Optimal Clusters",
                "Covariance Types"
            ),
            specs=[
                [{"type": "xy"}, {"type": "xy"}],
                [{"type": "xy"}, {"type": "domain"}]
            ]
        )
        
        # Silhouette comparison
        fig.add_trace(
            go.Bar(x=results_df['Modalidad'], y=results_df['Sil_train'], 
                   name='Train', marker_color=self.color_palette[0]),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=results_df['Modalidad'], y=results_df['Sil_test'], 
                   name='Test', marker_color=self.color_palette[1]),
            row=1, col=1
        )
        
        # Davies-Bouldin Index
        fig.add_trace(
            go.Bar(x=results_df['Modalidad'], y=results_df['DB_test'], 
                   name='DB Index', marker_color=self.color_palette[2]),
            row=1, col=2
        )
        
        # Optimal clusters
        fig.add_trace(
            go.Bar(x=results_df['Modalidad'], y=results_df['k_opt'], 
                   name='Optimal k', marker_color=self.color_palette[3]),
            row=2, col=1
        )
        
        # Covariance types pie chart
        cov_counts = results_df['cov_opt'].value_counts()
        fig.add_trace(
            go.Pie(labels=cov_counts.index, values=cov_counts.values, 
                   name="Covariance Types"),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title="Clustering Analysis Dashboard",
            height=800,
            width=1200,
            showlegend=True
        )
        
        # Update x-axes for better readability
        for row in [1, 2]:
            for col in [1, 2]:
                if row == 2 and col == 2:  # Skip pie chart
                    continue
                fig.update_xaxes(tickangle=45, row=row, col=col)
        
        return fig
    
    def save_figure(self, fig: go.Figure, filename: str, output_dir: Optional[str] = None) -> None:
        """
        Save figure in multiple formats
        
        Args:
            fig: Plotly figure to save
            filename: Base filename (without extension)
            output_dir: Output directory (uses default if None)
        """
        if output_dir is None:
            output_dir = CLUSTERING_FIGURES_DIR
        
        os.makedirs(output_dir, exist_ok=True)
        
        for file_format in self.save_formats:
            output_path = os.path.join(output_dir, f"{filename}.{file_format}")
            
            try:
                if file_format == 'html':
                    fig.write_html(output_path)
                elif file_format == 'png':
                    fig.write_image(output_path, width=self.figure_size[0], 
                                  height=self.figure_size[1], scale=2)
                elif file_format == 'pdf':
                    fig.write_image(output_path, width=self.figure_size[0], 
                                  height=self.figure_size[1])
                
                print(f"Saved figure: {output_path}")
                
            except Exception as e:
                print(f"Error saving {file_format} format: {e}")
    
    def create_all_visualizations(self, results_df: pd.DataFrame, save_plots: bool = True) -> Dict[str, go.Figure]:
        """
        Create all visualization plots
        
        Args:
            results_df: DataFrame with clustering results
            save_plots: Whether to save plots to disk
            
        Returns:
            Dictionary with all created figures
        """
        print("=== Creating All Visualizations ===")
        
        figures = {}
        
        # Main comparison plot (reproduce original)
        figures['metrics_comparison'] = self.create_metrics_comparison_plot(results_df)
        
        # Additional plots
        figures['detailed_table'] = self.create_detailed_metrics_table(results_df)
        figures['optimal_clusters'] = self.create_optimal_clusters_plot(results_df)
        figures['covariance_types'] = self.create_covariance_type_plot(results_df)
        figures['silhouette_heatmap'] = self.create_silhouette_heatmap(results_df)
        figures['dashboard'] = self.create_comprehensive_dashboard(results_df)
        
        # Save plots if requested
        if save_plots:
            for plot_name, figure in figures.items():
                self.save_figure(figure, plot_name)
        
        print("=== All Visualizations Created ===")
        
        return figures
    
    def display_interactive_plots(self, figures: Dict[str, go.Figure]) -> None:
        """
        Display interactive plots (for Jupyter notebooks)
        
        Args:
            figures: Dictionary with figures to display
        """
        for plot_name, figure in figures.items():
            print(f"\n=== {plot_name.replace('_', ' ').title()} ===")
            figure.show()


def create_clustering_report(results_df: pd.DataFrame, additional_info: Dict) -> str:
    """
    Create text report summarizing clustering results
    
    Args:
        results_df: DataFrame with clustering results
        additional_info: Additional information about clustering
        
    Returns:
        String with formatted report
    """
    report = []
    report.append("=" * 60)
    report.append("CLUSTERING ANALYSIS REPORT")
    report.append("=" * 60)
    report.append("")
    
    # Best performing modality
    best_silhouette_idx = results_df['Sil_test'].idxmax()
    best_modality = results_df.loc[best_silhouette_idx]
    
    report.append(f"BEST PERFORMING MODALITY: {best_modality['Modalidad']}")
    report.append(f"  - Optimal clusters: {best_modality['k_opt']}")
    report.append(f"  - Covariance type: {best_modality['cov_opt']}")
    report.append(f"  - Test silhouette score: {best_modality['Sil_test']:.4f}")
    report.append(f"  - Davies-Bouldin index: {best_modality['DB_test']:.4f}")
    report.append("")
    
    # Summary statistics
    report.append("SUMMARY STATISTICS:")
    report.append(f"  - Average test silhouette: {results_df['Sil_test'].mean():.4f}")
    report.append(f"  - Average Davies-Bouldin: {results_df['DB_test'].mean():.4f}")
    report.append(f"  - Most common cluster count: {results_df['k_opt'].mode().iloc[0]}")
    report.append(f"  - Most common covariance: {results_df['cov_opt'].mode().iloc[0]}")
    report.append("")
    
    # Detailed results
    report.append("DETAILED RESULTS BY MODALITY:")
    report.append("-" * 40)
    
    for _, row in results_df.iterrows():
        report.append(f"{row['Modalidad']}:")
        report.append(f"  k={row['k_opt']}, cov={row['cov_opt']}")
        report.append(f"  Sil(train)={row['Sil_train']:.4f}, Sil(test)={row['Sil_test']:.4f}")
        report.append(f"  DB(test)={row['DB_test']:.4f}")
        report.append("")
    
    return "\n".join(report)