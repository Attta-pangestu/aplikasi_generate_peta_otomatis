#!/usr/bin/env python3
"""
Professional Surveyor-Style Map Generator
Creates a professional map from shapefile data showing sub-divisions with different colors,
block labels, legend, scale, and location context within Belitung Island.

Author: Generated for Tree Counting Project
Date: 2025
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from shapely.geometry import Point
import contextily as ctx
from matplotlib_scalebar.scalebar import ScaleBar
import warnings
warnings.filterwarnings('ignore')

class ProfessionalMapGenerator:
    def __init__(self, shapefile_path, selected_subdivisions=None, map_title=None, logo_path=None):
        """
        Initialize the map generator with shapefile path
        
        Args:
            shapefile_path (str): Path to the shapefile
            selected_subdivisions (list): List of subdivisions to display (None = all)
            map_title (str): Custom title for the map (default: "PETA KEBUN 1 B\nPT. REBINMAS JAYA")
            logo_path (str): Path to company logo image
        """
        self.shapefile_path = shapefile_path
        self.gdf = None
        self.selected_subdivisions = selected_subdivisions
        self.map_title = map_title or "PETA KEBUN 1 B\nPT. REBINMAS JAYA"
        
        # Updated logo path
        self.logo_path = logo_path or r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\rebinmas_logo.jpg"
        
        # Compass image path
        self.compass_path = r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\kompas.webp"
        
        # Colors matching the image legend
        self.colors = {
            'SUB DIVISI AIR RAYA': '#FFB6C1',       # Light Pink (DIVISI GUNUNG PANJANG)
            'SUB DIVISI AIR CENDONG': '#98FB98',    # Pale Green (DIVISI GUNUNG RUM) 
            'SUB DIVISI AIR KANDIS': '#F4A460',     # Sandy Brown (DIVISI PADANG TEMBALUN)
            'IUP TIMAH': '#FF8C00',                 # Dark Orange
            'INCLAVE': '#9370DB'                    # Medium Purple
        }
        
        # Belitung overview shapefile path
        self.belitung_shapefile_path = r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\batas_desa_belitung.shp"
        self.belitung_gdf = None
        
    def load_data(self):
        """
        Load and prepare the shapefile data
        """
        try:
            print("Loading shapefile data...")
            self.gdf = gpd.read_file(self.shapefile_path)
            
            # Keep in WGS84 (degrees) for coordinate display
            if self.gdf.crs is None:
                self.gdf.set_crs('EPSG:4326', inplace=True)
            elif self.gdf.crs != 'EPSG:4326':
                self.gdf = self.gdf.to_crs('EPSG:4326')  # Convert to WGS84
            
            # Filter data based on selected subdivisions
            if self.selected_subdivisions:
                print(f"Filtering for subdivisions: {self.selected_subdivisions}")
                self.gdf = self.gdf[self.gdf['SUB_DIVISI'].isin(self.selected_subdivisions)]
                print(f"Filtered to {len(self.gdf)} features")
            
            print(f"Loaded {len(self.gdf)} features")
            print(f"Sub-divisions found: {self.gdf['SUB_DIVISI'].unique()}")
            print(f"Main data CRS: {self.gdf.crs}")
            print(f"Main data bounds: {self.gdf.total_bounds}")
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def load_belitung_data(self):
        """
        Load Belitung overview data
        """
        try:
            import os
            print(f"Loading Belitung shapefile from: {self.belitung_shapefile_path}")
            print(f"File exists: {os.path.exists(self.belitung_shapefile_path)}")
            
            if os.path.exists(self.belitung_shapefile_path):
                self.belitung_gdf = gpd.read_file(self.belitung_shapefile_path)
                
                # Check if coordinates are in degrees or meters to detect true CRS
                initial_bounds = self.belitung_gdf.total_bounds
                print(f"Initial Belitung bounds: {initial_bounds}")
                
                # If coordinates are very large (>1000), it's likely a projected CRS (UTM)
                # Belitung is around 107-108°E, 2-3°S, so correct values should be around 107, -2
                if abs(initial_bounds[0]) > 1000 or abs(initial_bounds[1]) > 1000:
                    print("Detected projected coordinates (likely UTM). Converting to geographic...")
                    # Belitung is in UTM Zone 48S
                    self.belitung_gdf = self.belitung_gdf.set_crs('EPSG:32748')  # UTM 48S
                    print(f"Set Belitung CRS to UTM 48S (EPSG:32748)")
                    self.belitung_gdf = self.belitung_gdf.to_crs('EPSG:4326')
                    print(f"Converted to WGS84 (EPSG:4326)")
                else:
                    # Coordinates are already in degrees
                    if self.belitung_gdf.crs is None:
                        print("Setting Belitung CRS to EPSG:4326 (already in degrees)")
                        self.belitung_gdf = self.belitung_gdf.set_crs('EPSG:4326')
                    elif self.belitung_gdf.crs != 'EPSG:4326':
                        print(f"Reprojecting Belitung data from {self.belitung_gdf.crs} to EPSG:4326")
                        self.belitung_gdf = self.belitung_gdf.to_crs('EPSG:4326')
                
                print(f"Loaded Belitung shapefile with {len(self.belitung_gdf)} features")
                print(f"Available columns: {list(self.belitung_gdf.columns)}")
                print(f"Belitung shapefile CRS: {self.belitung_gdf.crs}")
                print(f"Belitung bounds: {self.belitung_gdf.total_bounds}")
                
                if 'WADMKK' in self.belitung_gdf.columns:
                    print(f"WADMKK values: {self.belitung_gdf['WADMKK'].unique()}")
                
                return True
            else:
                print(f"Warning: Belitung shapefile not found at {self.belitung_shapefile_path}")
                self.belitung_gdf = None
                return False
        except Exception as e:
            print(f"Warning: Could not load Belitung shapefile: {e}")
            self.belitung_gdf = None
            return False
    
    def create_professional_map(self, output_path="professional_map.pdf", dpi=300):
        """
        Create a professional surveyor-style map with layout matching the image
        
        Args:
            output_path (str): Output file path
            dpi (int): Resolution for output
        """
        if self.gdf is None:
            print("No data loaded. Please run load_data() first.")
            return False
            
        if len(self.gdf) == 0:
            print("No features to display after filtering.")
            return False
            
        try:
            # Create figure with professional layout (A3 landscape style)
            fig = plt.figure(figsize=(16.54, 11.69))  # A3 size in inches
            fig.patch.set_facecolor('white')
            
            # Add blue border around entire map
            border_rect = Rectangle((0.01, 0.01), 0.98, 0.98, 
                                  fill=False, edgecolor='blue', linewidth=3,
                                  transform=fig.transFigure)
            fig.patches.append(border_rect)
            
            # Main map area (expanded to be level with title box)
            ax_main = plt.axes([0.05, 0.05, 0.65, 0.93])  # [left, bottom, width, height] - increased height
            
            # Add border frame for main map to match title box level
            main_map_border = Rectangle((0.05, 0.05), 0.65, 0.93, 
                                      fill=False, edgecolor='black', linewidth=2,
                                      transform=fig.transFigure)
            fig.patches.append(main_map_border)
            
            # Right panel sections - Reorganized with larger context map
            # Title area
            ax_title = plt.axes([0.72, 0.88, 0.26, 0.10])
            
            # Belitung overview map (ENLARGED - main focus)
            ax_overview = plt.axes([0.72, 0.50, 0.26, 0.36])  # Much larger context map
            
            # Legend area  
            ax_legend = plt.axes([0.72, 0.28, 0.26, 0.20])
            
            # North arrow and scale
            ax_north_scale = plt.axes([0.72, 0.14, 0.26, 0.12])
            
            # Logo and info area (moved to bottom)
            ax_logo = plt.axes([0.72, 0.02, 0.26, 0.10])
            
            # Plot main map with degree coordinates
            self._plot_main_map_degrees(ax_main)
            
            # Add title
            self._add_title(ax_title)
            
            # Add north arrow and scale
            self._add_north_arrow_and_scale(ax_north_scale)
            
            # Create legend
            self._create_professional_legend(ax_legend)
            
            # Add Belitung overview map
            self._add_belitung_overview(ax_overview)
            
            # Add logo and info
            self._add_logo_and_info(ax_logo)
            
            # Save the map
            plt.savefig(output_path, dpi=dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            
            print(f"Professional map saved to: {output_path}")
            plt.show()
            
            return True
            
        except Exception as e:
            print(f"Error creating map: {e}")
            return False
    
    def _plot_main_map_degrees(self, ax):
        """
        Plot the main map with degree coordinates and improved plus markers
        """
        # Plot each sub-division with different colors
        for sub_div in self.gdf['SUB_DIVISI'].unique():
            if pd.isna(sub_div):
                continue
                
            subset = self.gdf[self.gdf['SUB_DIVISI'] == sub_div]
            color = self.colors.get(sub_div, '#808080')  # Default gray
            
            subset.plot(ax=ax, color=color, alpha=0.8, edgecolor='black', 
                       linewidth=0.8, label=sub_div)
        
        # Add block labels (BLOK codes)
        for idx, row in self.gdf.iterrows():
            if pd.notna(row['BLOK']):
                # Get centroid for label placement
                centroid = row.geometry.centroid
                
                # Add block label with white background
                ax.annotate(row['BLOK'], 
                           xy=(centroid.x, centroid.y),
                           ha='center', va='center',
                           fontsize=7, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', 
                                   facecolor='white', alpha=0.9, edgecolor='black'))
        
        # Set extent and format coordinates
        bounds = self.gdf.total_bounds
        margin_x = (bounds[2] - bounds[0]) * 0.05
        margin_y = (bounds[3] - bounds[1]) * 0.05
        
        ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
        ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
        
        # Format coordinate labels to show degrees with more precision
        from matplotlib.ticker import FuncFormatter
        
        def degree_formatter_x(x, pos):
            return f"{x:.5f}"
        
        def degree_formatter_y(y, pos):
            return f"{y:.4f}"
        
        ax.xaxis.set_major_formatter(FuncFormatter(degree_formatter_x))
        ax.yaxis.set_major_formatter(FuncFormatter(degree_formatter_y))
        
        # Add coordinate labels with bold formatting
        ax.set_xlabel('')
        ax.set_ylabel('')
        
        # Make coordinate labels bold and larger
        ax.tick_params(axis='both', which='major', labelsize=9, pad=3, width=1.5)
        for label in ax.get_xticklabels():
            label.set_fontweight('bold')
        for label in ax.get_yticklabels():
            label.set_fontweight('bold')
        
        # Add improved plus markers at axis intersections
        self._add_axis_plus_markers(ax)
        
        # Style the axes with thicker border
        for spine in ax.spines.values():
            spine.set_linewidth(2)
            spine.set_color('black')
    
    def _add_axis_plus_markers(self, ax):
        """
        Add plus markers at axis intersections (more prominent)
        """
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Get the actual tick positions
        x_ticks = ax.get_xticks()
        y_ticks = ax.get_yticks()
        
        # Filter ticks to be within the plot area
        x_ticks = x_ticks[(x_ticks >= xlim[0]) & (x_ticks <= xlim[1])]
        y_ticks = y_ticks[(y_ticks >= ylim[0]) & (y_ticks <= ylim[1])]
        
        # Calculate plus size based on axis range
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        plus_size_x = x_range * 0.004  # Size in x direction
        plus_size_y = y_range * 0.004  # Size in y direction
        
        # Draw plus markers at each axis intersection
        for x in x_ticks:
            for y in y_ticks:
                # Horizontal line of plus
                ax.plot([x - plus_size_x, x + plus_size_x], [y, y], 'k-', 
                       linewidth=1.5, alpha=0.8, solid_capstyle='round')
                # Vertical line of plus
                ax.plot([x, x], [y - plus_size_y, y + plus_size_y], 'k-', 
                       linewidth=1.5, alpha=0.8, solid_capstyle='round')
    
    def _add_title(self, ax):
        """
        Add map title in professional style
        """
        ax.axis('off')
        
        # White background
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        # Title text
        ax.text(0.5, 0.5, self.map_title, ha='center', va='center',
               fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    def _add_north_arrow_and_scale(self, ax):
        """
        Add north arrow with compass image and scale information
        """
        ax.axis('off')
        
        # White background
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        # Add compass image if available
        try:
            import matplotlib.image as mpimg
            import os
            print(f"Loading compass from: {self.compass_path}")
            print(f"Compass file exists: {os.path.exists(self.compass_path)}")
            
            if os.path.exists(self.compass_path):
                compass_img = mpimg.imread(self.compass_path)
                # MAXIMUM VISIBILITY compass - larger and more prominent
                ax.imshow(compass_img, extent=[0.05, 0.75, 0.4, 0.98], transform=ax.transAxes, aspect='auto')
                print("✅ COMPASS IMAGE LOADED - MAXIMUM VISIBILITY!")
            else:
                raise FileNotFoundError("Compass file not found")
        except Exception as e:
            print(f"Warning: Could not load compass image: {e}")
            print("Using professional compass design fallback...")
            
            # Professional compass design
            # Outer circle
            circle_outer = plt.Circle((0.25, 0.7), 0.12, fill=False, edgecolor='black', 
                                    linewidth=2, transform=ax.transAxes)
            ax.add_patch(circle_outer)
            
            # Inner circle
            circle_inner = plt.Circle((0.25, 0.7), 0.08, fill=False, edgecolor='gray', 
                                    linewidth=1, transform=ax.transAxes)
            ax.add_patch(circle_inner)
            
            # North arrow (main)
            ax.annotate('', xy=(0.25, 0.82), xytext=(0.25, 0.58),
                       arrowprops=dict(arrowstyle='->', lw=3, color='red'),
                       transform=ax.transAxes)
            
            # Cardinal directions
            ax.text(0.25, 0.86, 'U', ha='center', va='center', fontsize=14, 
                   fontweight='bold', color='red', transform=ax.transAxes)
            ax.text(0.37, 0.7, 'T', ha='center', va='center', fontsize=10, 
                   fontweight='bold', transform=ax.transAxes)
            ax.text(0.25, 0.54, 'S', ha='center', va='center', fontsize=10, 
                   fontweight='bold', transform=ax.transAxes)
            ax.text(0.13, 0.7, 'B', ha='center', va='center', fontsize=10, 
                   fontweight='bold', transform=ax.transAxes)
            
            # Decorative lines for professional look
            for angle in [45, 135, 225, 315]:
                x_end = 0.25 + 0.1 * np.cos(np.radians(angle))
                y_end = 0.7 + 0.1 * np.sin(np.radians(angle))
                ax.plot([0.25, x_end], [0.7, y_end], 'k-', linewidth=1, 
                       alpha=0.7, transform=ax.transAxes)
        
        # Visual indicator for compass visibility  
        ax.text(0.4, 0.25, '🧭 COMPASS HERE', ha='center', va='center', fontsize=8, 
               fontweight='bold', color='green', alpha=0.7, transform=ax.transAxes)
        
        # Scale information
        ax.text(0.7, 0.7, 'Skala\n1:77.000', ha='center', va='center',
               fontsize=11, fontweight='bold', transform=ax.transAxes)
        
        # Calculate scale bar based on actual map extent
        if hasattr(self, 'gdf') and self.gdf is not None:
            bounds = self.gdf.total_bounds
            map_width_degrees = bounds[2] - bounds[0]  # longitude range
            
            # Convert degrees to approximate kilometers (at this latitude)
            # At latitude ~-2.6°, 1 degree longitude ≈ 111 km
            map_width_km = map_width_degrees * 111
            
            # Determine appropriate scale bar length (round number)
            if map_width_km > 20:
                scale_km = 5  # 5 km scale bar
            elif map_width_km > 10:
                scale_km = 2  # 2 km scale bar  
            elif map_width_km > 5:
                scale_km = 1  # 1 km scale bar
            else:
                scale_km = 0.5  # 500 m scale bar
            
            scale_meters = scale_km * 1000
        else:
            # Fallback values
            scale_km = 2
            scale_meters = 2000
        
        # Scale bar visual
        scale_width = 0.3
        scale_height = 0.05
        scale_x = 0.55
        scale_y = 0.25
        
        # Black section
        ax.add_patch(Rectangle((scale_x, scale_y), scale_width/2, scale_height, 
                              facecolor='black', transform=ax.transAxes))
        # White section
        ax.add_patch(Rectangle((scale_x + scale_width/2, scale_y), scale_width/2, scale_height, 
                              facecolor='white', edgecolor='black', transform=ax.transAxes))
        
        # Scale labels based on calculated scale
        ax.text(scale_x, scale_y - 0.08, '0', ha='center', va='center', fontsize=8, transform=ax.transAxes)
        
        if scale_km >= 1:
            mid_label = f'{scale_km/2:.0f} km' if scale_km/2 >= 1 else f'{int(scale_km*500)} m'
            end_label = f'{scale_km:.0f} km'
        else:
            mid_label = f'{int(scale_km*500)} m'
            end_label = f'{int(scale_km*1000)} m'
            
        ax.text(scale_x + scale_width/2, scale_y - 0.08, mid_label, ha='center', va='center', fontsize=8, transform=ax.transAxes)
        ax.text(scale_x + scale_width, scale_y - 0.08, end_label, ha='center', va='center', fontsize=8, transform=ax.transAxes)
    
    def _create_professional_legend(self, ax):
        """
        Create professional legend based on actual displayed subdivisions
        """
        ax.axis('off')
        
        # White background
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        # Legend title
        ax.text(0.5, 0.95, 'Legenda :', ha='center', va='top', 
               fontsize=11, fontweight='bold', transform=ax.transAxes)
        
        # Get actual subdivisions being displayed
        displayed_subdivisions = self.gdf['SUB_DIVISI'].dropna().unique()
        
        # Create legend items based on actual data
        y_start = 0.85
        for i, sub_div in enumerate(displayed_subdivisions):
            if pd.isna(sub_div):
                continue
                
            y_pos = y_start - (i * 0.12)
            color = self.colors.get(sub_div, '#808080')  # Get actual color used
            
            # Color patch
            rect = Rectangle((0.05, y_pos - 0.03), 0.12, 0.06, 
                           facecolor=color, alpha=0.8, 
                           edgecolor='black', linewidth=0.5,
                           transform=ax.transAxes)
            ax.add_patch(rect)
            
            # Label - use actual subdivision name
            label = sub_div if len(sub_div) <= 25 else sub_div[:22] + '...'
            ax.text(0.2, y_pos, label, ha='left', va='center',
                   fontsize=7, transform=ax.transAxes)
        
        # Add symbols legend
        y_pos_symbols = y_start - (len(displayed_subdivisions) * 0.12) - 0.05
        ax.text(0.5, y_pos_symbols, 'SIMBOL', ha='center', va='center',
               fontsize=9, fontweight='bold', transform=ax.transAxes)
        
        y_pos_symbols -= 0.08
        ax.text(0.05, y_pos_symbols, '━━━', ha='left', va='center',
               fontsize=10, color='black', transform=ax.transAxes)
        ax.text(0.25, y_pos_symbols, 'Batas Blok', ha='left', va='center',
               fontsize=7, transform=ax.transAxes)
        
        y_pos_symbols -= 0.08
        ax.text(0.05, y_pos_symbols, 'P XX/XX', ha='left', va='center',
               fontsize=7, fontweight='bold', transform=ax.transAxes,
               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        ax.text(0.25, y_pos_symbols, 'Kode Blok', ha='left', va='center',
               fontsize=7, transform=ax.transAxes)
            
    def _add_belitung_overview(self, ax):
        """
        Add Belitung island overview map from shapefile with study area overlay
        """
        ax.axis('off')
        
        # White background with border
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        # Title
        ax.text(0.5, 0.95, 'Dibuat Oleh : Surveyor / Surveyor R.M.J', ha='center', va='top',
               fontsize=8, transform=ax.transAxes)
        
        print("=== BELITUNG OVERVIEW MAP ===")
        
        try:
            # Load Belitung data
            belitung_loaded = self.load_belitung_data()
            print(f"Belitung loading result: {belitung_loaded}")
            
            if belitung_loaded and self.belitung_gdf is not None and len(self.belitung_gdf) > 0:
                print(f"Creating overview map with {len(self.belitung_gdf)} features")
                
                # Create overview map
                overview_rect = [0.1, 0.15, 0.8, 0.75]  # [left, bottom, width, height]
                overview_ax = ax.inset_axes(overview_rect)
                
                # Plot Belitung with WADMKK categorization if available
                if 'WADMKK' in self.belitung_gdf.columns:
                    unique_values = self.belitung_gdf['WADMKK'].dropna().unique()
                    print(f"WADMKK values: {unique_values}")
                    
                    for value in unique_values:
                        subset = self.belitung_gdf[self.belitung_gdf['WADMKK'] == value]
                        if 'BELITUNG TIMUR' in str(value).upper():
                            color = '#ADD8E6'  # Light Blue
                            label = 'Belitung Timur'
                        elif 'BELITUNG' in str(value).upper():
                            color = '#90EE90'  # Light Green
                            label = 'Belitung'
                        else:
                            color = '#D3D3D3'  # Gray
                            label = str(value)
                        
                        subset.plot(ax=overview_ax, color=color, alpha=0.7, 
                                   edgecolor='black', linewidth=0.8, label=label, aspect=None)
                        print(f"Plotted {label} with {len(subset)} features")
                else:
                    # Plot without categorization
                    self.belitung_gdf.plot(ax=overview_ax, color='#90EE90', alpha=0.7, 
                                          edgecolor='black', linewidth=0.8, label='Belitung', aspect=None)
                    print("Plotted Belitung without WADMKK categorization")
                
                # Add study area overlay with better visibility
                if hasattr(self, 'gdf') and self.gdf is not None and len(self.gdf) > 0:
                    print("Adding study area overlay...")
                    
                    # CRITICAL: Ensure both datasets have exactly the same CRS
                    print(f"Main data CRS: {self.gdf.crs}")
                    print(f"Belitung data CRS: {self.belitung_gdf.crs}")
                    
                    # Create a copy of main data in the same CRS as Belitung for overlay
                    study_gdf = self.gdf.copy()
                    if study_gdf.crs != self.belitung_gdf.crs:
                        print(f"Converting study area from {study_gdf.crs} to {self.belitung_gdf.crs}")
                        study_gdf = study_gdf.to_crs(self.belitung_gdf.crs)
                    
                    # Get study area bounds for rectangle overlay
                    bounds = study_gdf.total_bounds
                    center_x = (bounds[0] + bounds[2]) / 2
                    center_y = (bounds[1] + bounds[3]) / 2
                    width = bounds[2] - bounds[0]
                    height = bounds[3] - bounds[1]
                    
                    print(f"Study area CRS after conversion: {study_gdf.crs}")
                    print(f"Study area bounds after CRS alignment: {bounds}")
                    
                    # Verify coordinates are reasonable for Indonesia
                    if bounds[0] < 95 or bounds[2] > 141 or bounds[1] < -11 or bounds[3] > 6:
                        print("WARNING: Study area coordinates seem outside Indonesia!")
                        print(f"Longitude range: {bounds[0]:.6f} to {bounds[2]:.6f}")
                        print(f"Latitude range: {bounds[1]:.6f} to {bounds[3]:.6f}")
                    
                    # Add actual study area polygons with same colors as main map
                    study_gdf.plot(ax=overview_ax, 
                                 column='SUB_DIVISI', 
                                 categorical=True,
                                 legend=False,
                                 color=[self.colors.get(div, '#87CEEB') for div in study_gdf['SUB_DIVISI']], 
                                 alpha=0.8, 
                                 edgecolor='darkred', 
                                 linewidth=2, 
                                 zorder=15)
                    
                    # Add red rectangle boundary for visibility
                    from matplotlib.patches import Rectangle as MPLRectangle
                    study_rect = MPLRectangle(
                        (bounds[0], bounds[1]), width, height,
                        fill=False, edgecolor='red', linewidth=3, 
                        linestyle='-', alpha=0.9, zorder=18
                    )
                    overview_ax.add_patch(study_rect)
                    
                    # Add center marker
                    overview_ax.plot(center_x, center_y, 's', color='red', markersize=8, 
                                   markeredgecolor='darkred', markeredgewidth=2, zorder=20)
                    
                    print(f"Added study area polygons at: {center_x:.5f}, {center_y:.5f}")
                    print(f"Study area bounds: {bounds}")
                
                # Add context map title
                overview_ax.text(0.5, 1.05, 'PETA KONTEKS', ha='center', va='bottom',
                               fontsize=10, fontweight='bold', transform=overview_ax.transAxes)
                
                # Set map extent
                belitung_bounds = self.belitung_gdf.total_bounds
                margin = max((belitung_bounds[2] - belitung_bounds[0]), 
                           (belitung_bounds[3] - belitung_bounds[1])) * 0.1
                
                overview_ax.set_xlim(belitung_bounds[0] - margin, belitung_bounds[2] + margin)
                overview_ax.set_ylim(belitung_bounds[1] - margin, belitung_bounds[3] + margin)
                
                # Clean up axes
                overview_ax.set_xticks([])
                overview_ax.set_yticks([])
                
                # Style border
                for spine in overview_ax.spines.values():
                    spine.set_linewidth(1.5)
                    spine.set_color('black')
                
                # Add title
                overview_ax.set_title('Lokasi dalam Pulau Belitung', 
                                    fontsize=8, fontweight='bold', pad=5)
                
                # Add legend if there are handles
                handles, labels = overview_ax.get_legend_handles_labels()
                if handles:
                    legend = overview_ax.legend(handles, labels, loc='upper right', 
                                              fontsize=5, frameon=True)
                    legend.get_frame().set_facecolor('white')
                    legend.get_frame().set_alpha(0.9)
                
                print("Belitung overview map created successfully!")
                
            else:
                print("Using fallback representation...")
                # Simple fallback representation
                ax.text(0.5, 0.6, 'Peta Belitung\n(Simplified)', ha='center', va='center',
                       fontsize=9, fontweight='bold', transform=ax.transAxes)
                
                # Simple island shape
                from matplotlib.patches import Ellipse
                island = Ellipse((0.5, 0.45), 0.6, 0.3, facecolor='lightgreen', 
                               edgecolor='darkgreen', alpha=0.7, transform=ax.transAxes)
                ax.add_patch(island)
                
                # Study area marker
                study_marker = Rectangle((0.45, 0.4), 0.1, 0.1, facecolor='red', 
                                       alpha=0.8, transform=ax.transAxes)
                ax.add_patch(study_marker)
                
                ax.text(0.5, 0.2, 'Area Kajian', ha='center', va='center',
                       fontsize=8, transform=ax.transAxes,
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white'))
            
        except Exception as e:
            print(f"Error in Belitung overview: {e}")
            import traceback
            traceback.print_exc()
            
            # Final fallback
            ax.text(0.5, 0.5, 'Peta Konteks\nBelitung\n(Error)', ha='center', va='center',
                   fontsize=10, transform=ax.transAxes,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.5))
    
    def _add_logo_and_info(self, ax):
        """
        Add company logo and information
        """
        ax.axis('off')
        
        # White background
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        # Visual indicator for logo visibility
        ax.text(0.5, 0.1, '📍 LOGO REBINMAS HERE', ha='center', va='center', fontsize=8, 
               fontweight='bold', color='red', alpha=0.7, transform=ax.transAxes)

        # Company logo with better error handling
        logo_loaded = False
        if self.logo_path:
            try:
                import matplotlib.image as mpimg
                import os
                print(f"Loading logo from: {self.logo_path}")
                print(f"Logo file exists: {os.path.exists(self.logo_path)}")
                
                if os.path.exists(self.logo_path):
                    logo = mpimg.imread(self.logo_path)
                    # MAXIMUM VISIBILITY logo - larger and more prominent
                    ax.imshow(logo, extent=[0.05, 0.95, 0.2, 0.9], transform=ax.transAxes, aspect='auto')
                    logo_loaded = True
                    print(f"✅ LOGO REBINMAS LOADED - MAXIMUM VISIBILITY!")
                else:
                    print("Logo file not found, using fallback")
            except Exception as e:
                print(f"Warning: Could not load logo from {self.logo_path}: {e}")
        
        # Fallback logo design if image not loaded
        if not logo_loaded:
            # Create professional logo placeholder
            ax.text(0.5, 0.65, "REBINMAS", ha='center', va='center',
                   fontsize=16, fontweight='bold', color='#1E90FF', 
                   transform=ax.transAxes)
            ax.text(0.5, 0.55, "JAYA", ha='center', va='center',
                   fontsize=14, fontweight='bold', color='#FF6B35', 
                   transform=ax.transAxes)
            # Add decorative border
            logo_rect = Rectangle((0.2, 0.45), 0.6, 0.3, fill=False, 
                                edgecolor='#1E90FF', linewidth=2, 
                                transform=ax.transAxes)
            ax.add_patch(logo_rect)
        
        # Company name at bottom
        ax.text(0.5, 0.15, "PT. REBINMAS JAYA", ha='center', va='center',
               fontsize=12, fontweight='bold', color='#1E90FF', transform=ax.transAxes)

def main():
    """
    Main function to generate the professional map
    """
    # Path to the shapefile
    shapefile_path = "../merge_all_sub_divisi_map/merged_estates_HCV0_20250721_092606.shp"
    
    # Default subdivisions based on the image
    selected_subdivisions = ['SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR KANDIS', 'SUB DIVISI AIR RAYA']
    
    # Custom title and logo
    custom_title = "PETA KEBUN 1 B\nPT. REBINMAS JAYA"
    
    # Create map generator
    map_gen = ProfessionalMapGenerator(shapefile_path, selected_subdivisions, custom_title)
    
    # Load data
    if not map_gen.load_data():
        print("Failed to load data. Exiting.")
        return
    
    # Generate professional map
    output_path = "Test_Peta_Profesional_Sub_Divisi_FIXED.pdf"
    if map_gen.create_professional_map(output_path):
        print(f"\nPeta profesional berhasil dibuat: {output_path}")
        print("\nFitur yang disertakan:")
        print("- Layout profesional sesuai gambar")
        print("- Koordinat dalam derajat (bold/tebal)")
        print("- Grid dengan tanda plus di perpotongan axis")
        print("- Peta overview Pulau Belitung dengan lokasi kajian")
        print("- Kategorisasi berdasarkan WADMKK")
        print("- Kompas image dan logo perusahaan")
        print("- Auto-zoom ke area yang dipilih")
        print("- Klasifikasi warna berdasarkan sub divisi")
        print("- Label blok pada setiap area")
        print("- Legenda profesional")
        print("- Skala peta dan panah utara")
        if selected_subdivisions:
            print(f"- Default menampilkan: {', '.join(selected_subdivisions)}")
    else:
        print("Gagal membuat peta.")

if __name__ == "__main__":
    import pandas as pd
    main()