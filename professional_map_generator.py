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
import rasterio
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
import warnings
warnings.filterwarnings('ignore')

class ProfessionalMapGenerator:
    # Standardized box layout constants for consistent horizontal width (WIDENED FOR BETTER VISIBILITY)
    BOX_WIDTH = 0.32  # Standard width for all info boxes (increased from 0.26)
    BOX_LEFT_POSITION = 0.66  # Standard left position for all info boxes (adjusted for wider boxes)
    MAIN_MAP_WIDTH = 0.60  # Main map area width (slightly reduced to accommodate wider boxes)
    MAIN_MAP_LEFT = 0.05   # Main map left position
    
    def __init__(self, input_path, selected_subdivisions=None, map_title=None, logo_path=None, file_type="shapefile", tiff_legend=None, custom_colors=None):
        """
        Initialize the map generator with input file path
        
        Args:
            input_path (str): Path to the input file (shapefile or TIFF)
            selected_subdivisions (list): List of subdivisions to display (None = all, for shapefile only)
            map_title (str): Custom title for the map (default: "PETA KEBUN 1 B\nPT. REBINMAS JAYA")
            logo_path (str): Path to company logo image
            file_type (str): Type of input file ("shapefile" or "tiff")
            tiff_legend (list): List of legend entries for TIFF maps [{"color": "#FF0000", "description": "Label"}]
            custom_colors (dict): Custom colors for subdivisions (None = use defaults)
        """
        self.input_path = input_path
        self.shapefile_path = input_path if file_type == "shapefile" else None  # Backward compatibility
        self.file_type = file_type
        self.gdf = None
        self.tiff_data = None
        self.tiff_legend = tiff_legend or []
        self.selected_subdivisions = selected_subdivisions
        self.map_title = map_title or "PETA KEBUN 1 B\nPT. REBINMAS JAYA"
        
        # Updated logo path
        self.logo_path = logo_path or r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\rebinmas_logo.jpg"
        
        # Compass image path
        self.compass_path = r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\kompas.webp"
        
        # Default colors matching the image legend
        default_colors = {
            'SUB DIVISI AIR RAYA': '#FFB6C1',       # Light Pink (DIVISI GUNUNG PANJANG)
            'SUB DIVISI AIR CENDONG': '#98FB98',    # Pale Green (DIVISI GUNUNG RUM) 
            'SUB DIVISI AIR KANDIS': '#F4A460',     # Sandy Brown (DIVISI PADANG TEMBALUN)
            'IUP TIMAH': '#FF8C00',                 # Dark Orange
            'INCLAVE': '#9370DB'                    # Medium Purple
        }
        
        # Use custom colors if provided, otherwise use defaults
        if custom_colors:
            self.colors = {**default_colors, **custom_colors}  # Merge with custom colors taking precedence
        else:
            self.colors = default_colors
        
        # Belitung overview shapefile path
        self.belitung_shapefile_path = r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\batas_desa_belitung.shp"
        self.belitung_gdf = None
    
    def _get_standard_box_coords(self, bottom_position, height, box_name="Unknown"):
        """
        Generate standardized box coordinates with consistent horizontal width
        
        Args:
            bottom_position (float): Bottom Y coordinate of the box
            height (float): Height of the box
            box_name (str): Name of the box for debugging
            
        Returns:
            list: [left, bottom, width, height] coordinates for plt.axes()
        """
        coords = [self.BOX_LEFT_POSITION, bottom_position, self.BOX_WIDTH, height]
        print(f"📦 DEBUG BOX [{box_name}]: Left={self.BOX_LEFT_POSITION:.3f}, Bottom={bottom_position:.3f}, Width={self.BOX_WIDTH:.3f}, Height={height:.3f}")
        print(f"📦 DEBUG BOX [{box_name}]: Right edge = {self.BOX_LEFT_POSITION + self.BOX_WIDTH:.3f}")
        return coords
        
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
    
    def load_tiff_data(self):
        """
        Load and prepare TIFF raster data
        """
        try:
            print("Loading TIFF data...")
            
            # Open TIFF file
            with rasterio.open(self.input_path) as src:
                # Read the raster data
                self.tiff_data = src.read()
                self.tiff_transform = src.transform
                self.tiff_crs = src.crs
                self.tiff_bounds = src.bounds
                
                print(f"TIFF shape: {self.tiff_data.shape}")
                print(f"TIFF CRS: {self.tiff_crs}")
                print(f"TIFF bounds: {self.tiff_bounds}")
                
                # Convert bounds to WGS84 if needed
                if self.tiff_crs != 'EPSG:4326':
                    from rasterio.warp import transform_bounds
                    self.tiff_bounds_wgs84 = transform_bounds(self.tiff_crs, 'EPSG:4326', *self.tiff_bounds)
                    print(f"TIFF bounds (WGS84): {self.tiff_bounds_wgs84}")
                else:
                    self.tiff_bounds_wgs84 = self.tiff_bounds
                
                # Store extent for plotting
                self.tiff_extent = [self.tiff_bounds_wgs84[0], self.tiff_bounds_wgs84[2], 
                                   self.tiff_bounds_wgs84[1], self.tiff_bounds_wgs84[3]]
                
            return True
            
        except Exception as e:
            print(f"Error loading TIFF data: {e}")
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
        # Check data based on file type
        if self.file_type == "shapefile":
            if self.gdf is None:
                print("No shapefile data loaded. Please run load_data() first.")
                return False
            if len(self.gdf) == 0:
                print("No features to display after filtering.")
                return False
        elif self.file_type == "tiff":
            if self.tiff_data is None:
                print("No TIFF data loaded. Please run load_tiff_data() first.")
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
            
            # Main map area (using standardized constants)
            ax_main = plt.axes([self.MAIN_MAP_LEFT, 0.05, self.MAIN_MAP_WIDTH, 0.93])
            
            # Add border frame for main map
            main_map_border = Rectangle((self.MAIN_MAP_LEFT, 0.05), self.MAIN_MAP_WIDTH, 0.93, 
                                      fill=False, edgecolor='black', linewidth=2,
                                      transform=fig.transFigure)
            fig.patches.append(main_map_border)
            
            # Right panel sections - Using standardized box width constructor
            print("\n🔧 DEBUG: Creating all info boxes with dimensions:")
            
            # Title area (only title) - using standard box coordinates
            ax_title = plt.axes(self._get_standard_box_coords(0.88, 0.10, "TITLE"))
            
            # Belitung overview map (compact) - using standard box coordinates
            ax_overview = plt.axes(self._get_standard_box_coords(0.58, 0.28, "BELITUNG_OVERVIEW"))
            
            # Legend area - using standard box coordinates
            ax_legend = plt.axes(self._get_standard_box_coords(0.38, 0.18, "LEGEND"))
            
            # North arrow and scale - DISABLED (moved to main map overlay)
            # ax_north_scale = plt.axes(self._get_standard_box_coords(0.18, 0.14, "COMPASS_SCALE"))
            
            # Logo and info area - using standard box coordinates
            ax_logo = plt.axes(self._get_standard_box_coords(0.02, 0.14, "LOGO_INFO"))
            
            print(f"\n🗺️ DEBUG: Main map area: Left={self.MAIN_MAP_LEFT:.3f}, Width={self.MAIN_MAP_WIDTH:.3f}, Right edge={self.MAIN_MAP_LEFT + self.MAIN_MAP_WIDTH:.3f}")
            print(f"🗺️ DEBUG: Total figure width = 1.000, Available space = {1.0 - (self.MAIN_MAP_LEFT + self.MAIN_MAP_WIDTH):.3f}\n")
            
            # Plot main map with degree coordinates
            self._plot_main_map_degrees(ax_main)
            
            # Add title
            self._add_title(ax_title)
            
            # Add north arrow and scale - DISABLED (moved to main map overlay)
            # self._add_north_arrow_and_scale(ax_north_scale)
            
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
        if self.file_type == "shapefile":
            # Plot shapefile data
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
            
        elif self.file_type == "tiff":
            # Plot TIFF data
            print("Plotting TIFF raster data...")
            
            # Display the TIFF image
            with rasterio.open(self.input_path) as src:
                # Read and display the raster
                raster_data = src.read()
                
                # Handle different band configurations
                if raster_data.shape[0] == 1:
                    # Single band - display as grayscale
                    im = ax.imshow(raster_data[0], extent=self.tiff_extent, 
                                  cmap='viridis', alpha=0.8)
                elif raster_data.shape[0] >= 3:
                    # Multi-band - display as RGB
                    rgb_data = np.transpose(raster_data[:3], (1, 2, 0))
                    # Normalize to 0-1 range if needed
                    if rgb_data.max() > 1:
                        rgb_data = rgb_data / rgb_data.max()
                    im = ax.imshow(rgb_data, extent=self.tiff_extent, alpha=0.8)
                else:
                    # Fallback for other configurations
                    im = ax.imshow(raster_data[0], extent=self.tiff_extent, 
                                  cmap='viridis', alpha=0.8)
            
            # Set extent based on TIFF bounds
            bounds = self.tiff_bounds_wgs84
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
        
        # Add compass and scale bar overlay to main map
        self._add_compass_scale_overlay(ax)
    
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
        Add map title only in professional style with underline and nested box
        """
        ax.axis('off')
        
        # DEBUG: Print title box dimensions for comparison
        print(f"🔍 TITLE BOX DEBUG: Axis position = {ax.get_position()}")
        
        # White background
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        # Inner nested box for title
        inner_box = Rectangle((0.05, 0.2), 0.9, 0.6, facecolor='white', 
                             edgecolor='black', linewidth=1, transform=ax.transAxes)
        ax.add_patch(inner_box)
        
        # Title text centered in the box
        ax.text(0.5, 0.6, self.map_title, ha='center', va='center',
               fontsize=12, fontweight='bold', transform=ax.transAxes)
        
        # Add underline below title
        ax.plot([0.1, 0.9], [0.45, 0.45], 'k-', linewidth=1, transform=ax.transAxes)
    
    def _add_compass_scale_overlay(self, ax):
        """
        Add compass and scale bar as overlay on main map (improved design)
        """
        # Add scale bar in bottom left corner
        self._add_scale_bar_overlay(ax)
        
        # Add compass in top right corner using image
        self._add_compass_image_overlay(ax)
    
    def _add_scale_bar_overlay(self, ax):
        """
        Add improved scale bar overlay to main map with CRS info
        """
        # Get current axis limits to calculate scale
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Calculate appropriate scale based on map width
        map_width_degrees = xlim[1] - xlim[0]
        # At latitude ~-2.6°, 1 degree longitude ≈ 111 km
        map_width_km = map_width_degrees * 111
        
        # Determine appropriate scale bar length (make it longer as requested)
        if map_width_km > 20:
            scale_km = 8  # 8 km scale bar (longer)
        elif map_width_km > 10:
            scale_km = 4  # 4 km scale bar (longer)
        elif map_width_km > 5:
            scale_km = 2  # 2 km scale bar (longer)
        else:
            scale_km = 1  # 1 km scale bar
        
        # Convert scale to degrees
        scale_degrees = scale_km / 111  # Approximate conversion
        
        # Position scale bar in bottom left corner with margin
        margin_x = (xlim[1] - xlim[0]) * 0.05
        margin_y = (ylim[1] - ylim[0]) * 0.05
        scale_x = xlim[0] + margin_x
        scale_y = ylim[0] + margin_y
        
        # Create semi-transparent background for scale bar (larger for better spacing)
        scale_bg_width = scale_degrees * 1.3
        scale_bg_height = (ylim[1] - ylim[0]) * 0.12  # Taller for CRS info
        
        from matplotlib.patches import Rectangle
        scale_bg = Rectangle((scale_x - scale_degrees * 0.1, scale_y - scale_bg_height * 0.2), 
                           scale_bg_width, scale_bg_height,
                           facecolor='white', alpha=0.95, edgecolor='black', 
                           linewidth=1.5, zorder=100)
        ax.add_patch(scale_bg)
        
        # Create 5 segments alternating black and white (more segments for longer bar)
        segment_width = scale_degrees / 5
        segment_height = (ylim[1] - ylim[0]) * 0.018
        
        for i in range(5):
            x_pos = scale_x + (i * segment_width)
            # Alternating colors
            if i % 2 == 0:
                color = 'black'
            else:
                color = 'white'
            
            segment = Rectangle((x_pos, scale_y), segment_width, segment_height,
                              facecolor=color, edgecolor='black', linewidth=0.8, zorder=101)
            ax.add_patch(segment)
        
        # Add scale labels with better spacing
        fifth_km = scale_km / 5
        label_positions = [scale_x + (i * segment_width) for i in range(6)]
        
        for i, x_pos in enumerate(label_positions):
            km_value = fifth_km * i
            if km_value == 0:
                label = '0'
            elif km_value < 1:
                label = f'{int(km_value * 1000)}m'
            else:
                label = f'{km_value:.1f}km' if km_value != int(km_value) else f'{int(km_value)}km'
            
            ax.text(x_pos, scale_y - segment_height * 1.2, label, 
                   ha='center', va='top', fontsize=9, fontweight='bold',
                   color='black', zorder=102)
        
        # Add "Scale" title
        ax.text(scale_x + scale_degrees/2, scale_y + segment_height * 2.0, 'SCALE', 
               ha='center', va='bottom', fontsize=11, fontweight='bold',
               color='black', zorder=102)
        
        # Add CRS and coordinate system information
        ax.text(scale_x + scale_degrees/2, scale_y - segment_height * 3.0, 
               'CRS: WGS84 (EPSG:4326)\nCoordinates: Decimal Degrees', 
               ha='center', va='top', fontsize=8, fontweight='normal',
               color='black', zorder=102)
    
    def _add_compass_image_overlay(self, ax):
        """
        Add compass overlay using compass image to main map
        """
        # Get current axis limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Position compass in top right corner with margin
        margin_x = (xlim[1] - xlim[0]) * 0.05
        margin_y = (ylim[1] - ylim[0]) * 0.05
        compass_x = xlim[1] - margin_x
        compass_y = ylim[1] - margin_y
        
        # Compass size (larger for better visibility)
        compass_size = min((xlim[1] - xlim[0]) * 0.12, (ylim[1] - ylim[0]) * 0.12)
        
        # Create semi-transparent background for compass
        from matplotlib.patches import Circle
        compass_bg = Circle((compass_x, compass_y), compass_size * 0.6, 
                          facecolor='white', alpha=0.95, edgecolor='black', 
                          linewidth=1.5, zorder=100)
        ax.add_patch(compass_bg)
        
        # Try to load and display compass image
        try:
            import matplotlib.image as mpimg
            import os
            
            # Enhanced debug compass file path
            compass_full_path = os.path.abspath(self.compass_path)
            print(f"🔍 OVERLAY COMPASS DEBUG: Compass path: {self.compass_path}")
            print(f"🔍 OVERLAY COMPASS DEBUG: Absolute compass path: {compass_full_path}")
            print(f"🔍 OVERLAY COMPASS DEBUG: Compass file exists: {os.path.exists(compass_full_path)}")
            
            if os.path.exists(compass_full_path):
                print("📁 Loading compass image for overlay...")
                compass_img = mpimg.imread(compass_full_path)
                print(f"🖼️ Compass overlay image shape: {compass_img.shape}")
                
                # Calculate compass image extent in data coordinates
                left = compass_x - compass_size * 0.5
                right = compass_x + compass_size * 0.5
                bottom = compass_y - compass_size * 0.5
                top = compass_y + compass_size * 0.5
                
                # Display compass image
                ax.imshow(compass_img, extent=[left, right, bottom, top],
                         alpha=1.0, zorder=101)
                print("✅ COMPASS IMAGE OVERLAY LOADED!")
                
                # Add "N" label below compass
                ax.text(compass_x, compass_y - compass_size * 0.7, 'UTARA', 
                       ha='center', va='center', fontsize=10, fontweight='bold',
                       color='darkred', zorder=102,
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
                
            else:
                print("❌ Compass file not found, using simple arrow fallback")
                # Fallback: simple north arrow
                arrow_length = compass_size * 0.4
                ax.annotate('', xy=(compass_x, compass_y + arrow_length), 
                           xytext=(compass_x, compass_y),
                           arrowprops=dict(arrowstyle='->', lw=4, color='red'), zorder=101)
                
                # Add north label
                ax.text(compass_x, compass_y + arrow_length * 1.3, 'N', 
                       ha='center', va='center', fontsize=14, fontweight='bold',
                       color='red', zorder=102)
                
        except Exception as e:
            print(f"❌ ERROR loading compass overlay: {e}")
            # Emergency fallback: simple north arrow
            arrow_length = compass_size * 0.4
            ax.annotate('', xy=(compass_x, compass_y + arrow_length), 
                       xytext=(compass_x, compass_y),
                       arrowprops=dict(arrowstyle='->', lw=4, color='red'), zorder=101)
            
            ax.text(compass_x, compass_y + arrow_length * 1.3, 'N', 
                   ha='center', va='center', fontsize=14, fontweight='bold',
                   color='red', zorder=102)
    
    def _add_north_arrow_and_scale(self, ax):
        """
        Add north arrow with compass image and scale information with improved horizontal layout
        """
        ax.axis('off')
        
        # DEBUG: Print actual axis bounds and position
        print(f"🔍 COMPASS BOX DEBUG: Axis position = {ax.get_position()}")
        print(f"🔍 COMPASS BOX DEBUG: Axis bounds = {ax.get_xlim()}, {ax.get_ylim()}")
        
        # White background - FORCE FULL BOX VISIBILITY
        outer_box = Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=2, transform=ax.transAxes)
        ax.add_patch(outer_box)
        print(f"🔍 COMPASS BOX DEBUG: Added outer box with full dimensions (0,0,1,1)")
        
        # Create attractive separate containers with better spacing and design
        # FIXED: Make containers larger and closer together to match legend box visual density (90% total coverage)

        # COMPASS CONTAINER (Left side - with padding)
        compass_container = Rectangle((0.05, 0.05), 0.42, 0.90,
                                    facecolor='#f8f9fa', edgecolor='#2c3e50',
                                    linewidth=2, alpha=0.95, transform=ax.transAxes)
        ax.add_patch(compass_container)

        # Add compass container shadow for depth
        compass_shadow = Rectangle((0.055, 0.045), 0.42, 0.90,
                                 facecolor='#bdc3c7', edgecolor='none',
                                 alpha=0.3, transform=ax.transAxes, zorder=1)
        ax.add_patch(compass_shadow)

        # SCALE CONTAINER (Right side - with padding and longer scale area)
        scale_container = Rectangle((0.53, 0.05), 0.42, 0.90,
                                  facecolor='#f8f9fa', edgecolor='#2c3e50',
                                  linewidth=2, alpha=0.95, transform=ax.transAxes)
        ax.add_patch(scale_container)

        # Add scale container shadow for depth
        scale_shadow = Rectangle((0.535, 0.045), 0.42, 0.90,
                               facecolor='#bdc3c7', edgecolor='none',
                               alpha=0.3, transform=ax.transAxes, zorder=1)
        ax.add_patch(scale_shadow)
        
        # Add attractive container headers with background
        # Compass header (updated for new container width with padding)
        compass_header = Rectangle((0.05, 0.88), 0.42, 0.07,
                                 facecolor='#3498db', edgecolor='#2c3e50',
                                 linewidth=1, alpha=0.9, transform=ax.transAxes, zorder=5)
        ax.add_patch(compass_header)
        ax.text(0.26, 0.915, 'KOMPAS', ha='center', va='center',
               fontsize=12, fontweight='bold', color='white', transform=ax.transAxes, zorder=6)

        # Scale header (updated for new container position and width with padding)
        scale_header = Rectangle((0.53, 0.88), 0.42, 0.07,
                               facecolor='#e74c3c', edgecolor='#2c3e50',
                               linewidth=1, alpha=0.9, transform=ax.transAxes, zorder=5)
        ax.add_patch(scale_header)
        ax.text(0.74, 0.915, 'SKALA', ha='center', va='center',
               fontsize=12, fontweight='bold', color='white', transform=ax.transAxes, zorder=6)
        
        # Load and display compass image using FULL BOX SPACE (no margins)
        try:
            import matplotlib.image as mpimg
            import os
            
            # Enhanced debug compass file path
            compass_full_path = os.path.abspath(self.compass_path)
            print(f"🔍 DEBUG: Compass path: {self.compass_path}")
            print(f"🔍 DEBUG: Absolute compass path: {compass_full_path}")
            print(f"🔍 DEBUG: Compass file exists: {os.path.exists(compass_full_path)}")
            print(f"🔍 DEBUG: Current working directory: {os.getcwd()}")
            
            if os.path.exists(compass_full_path):
                print("📁 Loading compass image...")
                compass_img = mpimg.imread(compass_full_path)
                print(f"🖼️ Compass image shape: {compass_img.shape}")
                print(f"🖼️ Compass image dtype: {compass_img.dtype}")
                
                # Display compass image WITHIN IMPROVED COMPASS CONTAINER (updated for new container width)
                ax.imshow(compass_img, extent=[0.08, 0.44, 0.45, 0.82],
                         transform=ax.transAxes, aspect='equal', alpha=1.0, zorder=10)
                print("✅ COMPASS IMAGE LOADED - WITHIN IMPROVED CONTAINER!")

                # Add compass direction labels with better styling (updated for new container)
                ax.text(0.26, 0.35, '↑', ha='center', va='center', fontsize=20,
                       fontweight='bold', color='#c0392b', transform=ax.transAxes, zorder=11)
                ax.text(0.26, 0.25, 'UTARA', ha='center', va='center', fontsize=11,
                       fontweight='bold', color='#2c3e50', transform=ax.transAxes, zorder=11)

                # Add decorative border around compass area (updated for new container)
                compass_border = Rectangle((0.07, 0.20), 0.38, 0.65,
                                         facecolor='none', edgecolor='#34495e',
                                         linewidth=1, linestyle='--', alpha=0.5,
                                         transform=ax.transAxes, zorder=9)
                ax.add_patch(compass_border)
                
            else:
                print("❌ Compass file not found, no fallback will be displayed")
                # No fallback compass - just leave empty space
                
        except Exception as e:
            print(f"❌ ERROR loading compass: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            
            # No emergency fallback - leave empty space
            pass
        
        # Scale section positioned WITHIN IMPROVED SCALE CONTAINER (updated for new container position)
        # Scale ratio with better styling
        ax.text(0.74, 0.80, '1:31.300', ha='center', va='center',
               fontsize=16, fontweight='bold', color='#2c3e50', transform=ax.transAxes, zorder=11)

        # Add decorative underline below scale ratio (updated for new container position)
        ax.plot([0.58, 0.90], [0.75, 0.75], color='#e74c3c', linewidth=2, transform=ax.transAxes, zorder=10)
        
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
        
        # Scale bar title positioned WITHIN IMPROVED SCALE CONTAINER (updated for new container position)
        ax.text(0.74, 0.65, 'SKALA JARAK', ha='center', va='center',
               fontsize=13, fontweight='bold', color='#2c3e50', transform=ax.transAxes, zorder=11)

        # Scale bar visual with 4 segments - LONGER DESIGN (updated for new container and longer scale)
        scale_width = 0.38  # LONGER scale bar as requested (increased from 0.36)
        scale_height = 0.06  # Appropriate height for better spacing
        scale_x = 0.555  # Centered within new scale container position
        scale_y = 0.45  # Better vertical positioning
        
        # Add background for scale bar area
        scale_bg = Rectangle((scale_x - 0.02, scale_y - 0.02), scale_width + 0.04, scale_height + 0.04, 
                           facecolor='#ecf0f1', edgecolor='#bdc3c7', 
                           linewidth=1, alpha=0.8, transform=ax.transAxes, zorder=8)
        ax.add_patch(scale_bg)
        
        # Create 4 segments alternating black and white
        segment_width = scale_width / 4
        
        for i in range(4):
            x_pos = scale_x + (i * segment_width)
            # Improved alternating colors with better contrast
            if i % 2 == 0:
                color = '#2c3e50'  # Dark blue-gray
                edgecolor = '#34495e'
            else:
                color = '#ecf0f1'  # Light gray
                edgecolor = '#34495e'
            
            ax.add_patch(Rectangle((x_pos, scale_y), segment_width, scale_height, 
                                  facecolor=color, edgecolor=edgecolor, linewidth=1,
                                  transform=ax.transAxes, zorder=9))
        
        # Scale labels based on calculated scale (5 labels for 4 segments)
        label_positions = [scale_x + (i * segment_width) for i in range(5)]
        
        if scale_km >= 1:
            # For km scale
            quarter_km = scale_km / 4
            labels = []
            for i in range(5):
                km_value = quarter_km * i
                if km_value == 0:
                    labels.append('0')
                elif km_value < 1:
                    labels.append(f'{int(km_value * 1000)} m')
                else:
                    labels.append(f'{km_value:.1f} km' if km_value != int(km_value) else f'{int(km_value)} km')
        else:
            # For meter scale
            quarter_m = (scale_km * 1000) / 4
            labels = [f'{int(quarter_m * i)} m' if i > 0 else '0' for i in range(5)]
        
        # Add scale labels with improved styling
        for i, (x_pos, label) in enumerate(zip(label_positions, labels)):
            ax.text(x_pos, scale_y - 0.08, label, ha='center', va='center', 
                   fontsize=9, fontweight='bold', color='#2c3e50', 
                   transform=ax.transAxes, zorder=11)
        
        # Add decorative frame around entire scale container content (updated for larger container)
        scale_content_frame = Rectangle((0.53, 0.25), 0.40, 0.45,
                                      facecolor='none', edgecolor='#95a5a6',
                                      linewidth=1, linestyle=':', alpha=0.6,
                                      transform=ax.transAxes, zorder=7)
        ax.add_patch(scale_content_frame)
    

    def _create_professional_legend(self, ax):
        """
        Create professional legend based on file type (shapefile or TIFF) with nested boxes
        """
        ax.axis('off')
        
        # White background
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        # Inner nested box for legend content
        inner_box = Rectangle((0.05, 0.05), 0.9, 0.9, facecolor='white', 
                             edgecolor='black', linewidth=1, transform=ax.transAxes)
        ax.add_patch(inner_box)
        
        # Legend title with underline
        ax.text(0.5, 0.9, 'LEGENDA', ha='center', va='center', 
               fontsize=10, fontweight='bold', transform=ax.transAxes)
        
        # Add underline below legend title
        ax.plot([0.1, 0.9], [0.85, 0.85], 'k-', linewidth=1, transform=ax.transAxes)
        
        if self.file_type == "shapefile":
            # Shapefile legend - subdivisions
            displayed_subdivisions = self.gdf['SUB_DIVISI'].dropna().unique()
            
            # Create legend items based on actual data (adjusted for nested box)
            y_start = 0.75
            for i, sub_div in enumerate(displayed_subdivisions):
                if pd.isna(sub_div):
                    continue
                    
                y_pos = y_start - (i * 0.12)
                color = self.colors.get(sub_div, '#808080')  # Get actual color used
                
                # Color patch (adjusted position for nested box)
                rect = Rectangle((0.1, y_pos - 0.03), 0.12, 0.06, 
                               facecolor=color, alpha=0.8, 
                               edgecolor='black', linewidth=0.5,
                               transform=ax.transAxes)
                ax.add_patch(rect)
                
                # Label - use actual subdivision name (adjusted position)
                label = sub_div if len(sub_div) <= 20 else sub_div[:17] + '...'
                ax.text(0.25, y_pos, label, ha='left', va='center',
                       fontsize=7, transform=ax.transAxes)
            
            # Add symbols legend (adjusted positioning)
            y_pos_symbols = y_start - (len(displayed_subdivisions) * 0.12) - 0.05
            
            # Add separator line
            ax.plot([0.1, 0.9], [y_pos_symbols + 0.02, y_pos_symbols + 0.02], 'k-', linewidth=0.5, transform=ax.transAxes)
            
            ax.text(0.5, y_pos_symbols - 0.02, 'SIMBOL', ha='center', va='center',
                   fontsize=8, fontweight='bold', transform=ax.transAxes)
            
            y_pos_symbols -= 0.08
            ax.text(0.1, y_pos_symbols, '━━━', ha='left', va='center',
                   fontsize=10, color='black', transform=ax.transAxes)
            ax.text(0.3, y_pos_symbols, 'Batas Area', ha='left', va='center',
                   fontsize=7, transform=ax.transAxes)
            
            y_pos_symbols -= 0.08
            ax.text(0.1, y_pos_symbols, 'A1', ha='center', va='center',
                   fontsize=7, fontweight='bold', transform=ax.transAxes,
                   bbox=dict(boxstyle='square,pad=0.2', facecolor='white', edgecolor='black', linewidth=0.5))
            ax.text(0.3, y_pos_symbols, 'Kode Blok', ha='left', va='center',
                   fontsize=7, transform=ax.transAxes)
                   
        elif self.file_type == "tiff":
            # TIFF legend - custom legend entries (adjusted for nested box)
            if self.tiff_legend and len(self.tiff_legend) > 0:
                y_start = 0.75
                for i, legend_entry in enumerate(self.tiff_legend):
                    y_pos = y_start - (i * 0.12)
                    color = legend_entry.get('color', '#808080')
                    description = legend_entry.get('description', 'Unknown')
                    
                    # Color patch (adjusted position for nested box)
                    rect = Rectangle((0.1, y_pos - 0.03), 0.12, 0.06, 
                                   facecolor=color, alpha=0.8, 
                                   edgecolor='black', linewidth=0.5,
                                   transform=ax.transAxes)
                    ax.add_patch(rect)
                    
                    # Label - use description (adjusted position)
                    label = description if len(description) <= 20 else description[:17] + '...'
                    ax.text(0.25, y_pos, label, ha='left', va='center',
                           fontsize=7, transform=ax.transAxes)
            else:
                # No legend data provided (adjusted for nested box)
                ax.text(0.5, 0.4, 'No legend data\nprovided for TIFF', 
                       ha='center', va='center', fontsize=9, 
                       transform=ax.transAxes)
            
    def _add_belitung_overview(self, ax):
        """
        Add Belitung island overview map from shapefile with study area overlay
        """
        ax.axis('off')
        
        # White background with border
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        # Inner nested box for overview content
        inner_box = Rectangle((0.05, 0.05), 0.9, 0.9, facecolor='white', 
                             edgecolor='black', linewidth=1, transform=ax.transAxes)
        ax.add_patch(inner_box)
        
        # Remove title - no 'PETA KONTEKS' text needed
        # Title and underline removed as requested
        
        print("=== BELITUNG OVERVIEW MAP ===")
        
        try:
            # Load Belitung data
            belitung_loaded = self.load_belitung_data()
            print(f"Belitung loading result: {belitung_loaded}")
            
            if belitung_loaded and self.belitung_gdf is not None and len(self.belitung_gdf) > 0:
                print(f"Creating overview map with {len(self.belitung_gdf)} features")
                
                # Create overview map (moved up to avoid overlaps)
                overview_rect = [0.15, 0.2, 0.7, 0.65]  # [left, bottom, width, height] - moved up
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
                    print("Adding SHAPEFILE study area overlay...")
                    
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
                
                # Add TIFF area overlay for TIFF files
                elif self.file_type == "tiff" and hasattr(self, 'tiff_bounds_wgs84') and self.tiff_bounds_wgs84 is not None:
                    print("Adding TIFF area overlay...")
                    
                    # Get TIFF bounds in WGS84 (these were calculated during TIFF loading)
                    bounds = self.tiff_bounds_wgs84  # [minx, miny, maxx, maxy]
                    center_x = (bounds[0] + bounds[2]) / 2
                    center_y = (bounds[1] + bounds[3]) / 2
                    width = bounds[2] - bounds[0]
                    height = bounds[3] - bounds[1]
                    
                    print(f"TIFF area bounds (WGS84): {bounds}")
                    print(f"TIFF area center: {center_x:.5f}, {center_y:.5f}")
                    
                    # Verify coordinates are reasonable for Indonesia
                    if bounds[0] < 95 or bounds[2] > 141 or bounds[1] < -11 or bounds[3] > 6:
                        print("WARNING: TIFF area coordinates seem outside Indonesia!")
                        print(f"Longitude range: {bounds[0]:.6f} to {bounds[2]:.6f}")
                        print(f"Latitude range: {bounds[1]:.6f} to {bounds[3]:.6f}")
                    
                    # Add TIFF area rectangle with red color to match shapefile areas
                    from matplotlib.patches import Rectangle as MPLRectangle
                    tiff_rect = MPLRectangle(
                        (bounds[0], bounds[1]), width, height,
                        fill=True, facecolor='red', edgecolor='darkred', 
                        linewidth=3, linestyle='-', alpha=0.3, zorder=18
                    )
                    overview_ax.add_patch(tiff_rect)
                    
                    # Add center marker for TIFF (red square)
                    overview_ax.plot(center_x, center_y, 's', color='red', markersize=8, 
                                   markeredgecolor='darkred', markeredgewidth=2, zorder=20)
                    
                    # TIFF AREA text label removed as requested
                    
                    print(f"Added TIFF area overlay at: {center_x:.5f}, {center_y:.5f}")
                    
                # Remove context map title as requested
                # No 'PETA KONTEKS' title needed
                
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
        Add company logo and information with nested box structure
        """
        ax.axis('off')
        
        # White background
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        # Inner nested box for logo content
        inner_box = Rectangle((0.05, 0.05), 0.9, 0.9, facecolor='white', 
                             edgecolor='black', linewidth=1, transform=ax.transAxes)
        ax.add_patch(inner_box)

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
                    # Logo positioned in upper part of enlarged box
                    ax.imshow(logo, extent=[0.1, 0.9, 0.55, 0.9], transform=ax.transAxes, aspect='auto')
                    logo_loaded = True
                    print(f"✅ LOGO REBINMAS LOADED - MAXIMUM VISIBILITY!")
                else:
                    print("Logo file not found, using fallback")
            except Exception as e:
                print(f"Warning: Could not load logo from {self.logo_path}: {e}")
        
        # Fallback logo design if image not loaded (adjusted for enlarged box)
        if not logo_loaded:
            # Create professional logo placeholder in upper part
            ax.text(0.5, 0.75, "REBINMAS", ha='center', va='center',
                   fontsize=14, fontweight='bold', color='#1E90FF', 
                   transform=ax.transAxes)
            ax.text(0.5, 0.65, "JAYA", ha='center', va='center',
                   fontsize=12, fontweight='bold', color='#FF6B35', 
                   transform=ax.transAxes)
            # Add decorative border in upper part
            logo_rect = Rectangle((0.25, 0.55), 0.5, 0.25, fill=False, 
                                edgecolor='#1E90FF', linewidth=2, 
                                transform=ax.transAxes)
            ax.add_patch(logo_rect)
        
        # Company name with underline
        ax.text(0.5, 0.45, "PT. REBINMAS JAYA", ha='center', va='center',
               fontsize=10, fontweight='bold', color='#1E90FF', transform=ax.transAxes)
        
        # Add underline below company name
        ax.plot([0.1, 0.9], [0.4, 0.4], 'k-', linewidth=1, transform=ax.transAxes)
        
        # Add production information with proper spacing
        ax.text(0.5, 0.32, 'Diproduksi untuk : PT. REBINMAS JAYA', ha='center', va='center',
               fontsize=8, transform=ax.transAxes)
        ax.text(0.5, 0.25, 'Program: IT Rebinmas | Data: Surveyor RMJ', ha='center', va='center',
               fontsize=8, transform=ax.transAxes)
        ax.text(0.5, 0.18, 'Generated: July 2025', ha='center', va='center',
               fontsize=8, transform=ax.transAxes)

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