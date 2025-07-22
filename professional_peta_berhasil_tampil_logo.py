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
    def __init__(self, shapefile_path, selected_subdivisions=None, map_title=None, logo_path=None, compass_path=None, belitung_shapefile_path=None):
        """
        Initialize the map generator with shapefile path
        
        Args:
            shapefile_path (str): Path to the shapefile
            selected_subdivisions (list): List of subdivisions to display (None = all)
            map_title (str): Custom title for the map (default: "Peta Areal Tanam DME\nPT Rebinmas Jaya")
            logo_path (str): Path to company logo image
            compass_path (str): Path to compass/north arrow image
            belitung_shapefile_path (str): Path to Belitung island shapefile for context map
        """
        self.shapefile_path = shapefile_path
        self.gdf = None
        self.belitung_gdf = None
        self.selected_subdivisions = selected_subdivisions
        self.map_title = map_title or "Peta Areal Tanam DME\nPT Rebinmas Jaya"
        self.logo_path = logo_path
        self.compass_path = compass_path
        self.belitung_shapefile_path = belitung_shapefile_path or r"D:\Gawean Rebinmas\Tree Counting Project\Information System Web Tree Counted\Assets\batas_desa_belitung\batas_desa_belitung.shp"
        self.colors = {
            'SUB DIVISI AIR RAYA': '#FFB6C1',      # Light Pink
            'SUB DIVISI AIR CENDONG': '#98FB98',   # Pale Green
            'SUB DIVISI AIR KANDIS': '#F4A460',    # Sandy Brown
            'IUP TIMAH': '#FF8C00',                # Dark Orange
            'INCLAVE': '#9370DB'                   # Medium Purple
        }
        
    def load_data(self):
        """
        Load and prepare the shapefile data
        """
        try:
            print("Loading shapefile data...")
            self.gdf = gpd.read_file(self.shapefile_path)
            
            # Ensure we have the correct CRS (WGS84 UTM Zone 48S for Belitung)
            if self.gdf.crs is None:
                self.gdf.set_crs('EPSG:4326', inplace=True)
            
            # Convert to UTM for better measurement
            self.gdf = self.gdf.to_crs('EPSG:32748')  # UTM Zone 48S
            
            # Filter data based on selected subdivisions
            if self.selected_subdivisions:
                print(f"Filtering for subdivisions: {self.selected_subdivisions}")
                self.gdf = self.gdf[self.gdf['SUB_DIVISI'].isin(self.selected_subdivisions)]
                print(f"Filtered to {len(self.gdf)} features")
            
            print(f"Loaded {len(self.gdf)} features")
            print(f"Sub-divisions found: {self.gdf['SUB_DIVISI'].unique()}")
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
     
    def load_belitung_data(self):
        """
        Load Belitung overview data for context map
        """
        try:
            import os
            if os.path.exists(self.belitung_shapefile_path):
                self.belitung_gdf = gpd.read_file(self.belitung_shapefile_path)
                # Convert to same CRS as main data
                if self.belitung_gdf.crs != 'EPSG:32748':
                    self.belitung_gdf = self.belitung_gdf.to_crs('EPSG:32748')
                print(f"Loaded Belitung data with {len(self.belitung_gdf)} features")
                return True
            else:
                print(f"Belitung shapefile not found at: {self.belitung_shapefile_path}")
                return False
        except Exception as e:
            print(f"Warning: Could not load Belitung shapefile: {e}")
            return False
    
    def create_professional_map(self, output_path="professional_map.pdf", dpi=300):
        """
        Create a professional surveyor-style map
        
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
            # Create figure with professional layout
            fig = plt.figure(figsize=(16, 12))
            
            # Main map area (takes most of the space)
            ax_main = plt.subplot2grid((5, 4), (1, 0), colspan=3, rowspan=3)
            
            # Title and logo area (top)
            ax_title = plt.subplot2grid((5, 4), (0, 0), colspan=4)
            
            # Legend area (right side)
            ax_legend = plt.subplot2grid((5, 4), (1, 3), rowspan=1)
            
            # Context map area (right middle)
            ax_context = plt.subplot2grid((5, 4), (2, 3), rowspan=1)
            
            # Info area (bottom right)
            ax_info = plt.subplot2grid((5, 4), (3, 3), rowspan=1)
            
            # Bottom info area
            ax_bottom = plt.subplot2grid((5, 4), (4, 0), colspan=4)
            
            # Plot main map with auto-zoom
            self._plot_main_map_with_zoom(ax_main)
            
            # Add title and logo
            self._add_title_and_logo(ax_title)
            
            # Create legend (only for selected subdivisions)
            self._create_filtered_legend(ax_legend)
            
            # Add context map
            self._add_context_map(ax_context)
            
            # Add technical information
            self._add_technical_info(ax_info)
            
            # Add bottom information
            self._add_bottom_info(ax_bottom)
            
            # Adjust layout
            plt.tight_layout(pad=1.0)
            
            # Save the map
            plt.savefig(output_path, dpi=dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            
            print(f"Professional map saved to: {output_path}")
            plt.show()
            
            return True
            
        except Exception as e:
            print(f"Error creating map: {e}")
            return False
    
    def _plot_main_map_with_zoom(self, ax):
        """
        Plot the main map with auto-zoom to selected areas
        """
        # Plot each sub-division with different colors
        for sub_div in self.gdf['SUB_DIVISI'].unique():
            if pd.isna(sub_div):
                continue
                
            subset = self.gdf[self.gdf['SUB_DIVISI'] == sub_div]
            color = self.colors.get(sub_div, '#808080')  # Default gray
            
            subset.plot(ax=ax, color=color, alpha=0.7, edgecolor='black', 
                       linewidth=0.5, label=sub_div)
        
        # Add block labels
        for idx, row in self.gdf.iterrows():
            if pd.notna(row['BLOK']):
                # Get centroid for label placement
                centroid = row.geometry.centroid
                
                # Add block label
                ax.annotate(row['BLOK'], 
                           xy=(centroid.x, centroid.y),
                           ha='center', va='center',
                           fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', 
                                   facecolor='white', alpha=0.8))
        
        # Auto-zoom to the extent of filtered data
        bounds = self.gdf.total_bounds
        margin = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) * 0.05  # 5% margin
        ax.set_xlim(bounds[0] - margin, bounds[2] + margin)
        ax.set_ylim(bounds[1] - margin, bounds[3] + margin)
        
        # Add improved scale bar
        from matplotlib_scalebar.scalebar import ScaleBar
        scalebar = ScaleBar(1, units="m", location="lower left", 
                           length_fraction=0.2, width_fraction=0.01,
                           box_alpha=0.8, color='black', box_color='white',
                           font_properties={'size': 10, 'weight': 'bold'})
        ax.add_artist(scalebar)
        
        # Add north arrow
        self._add_north_arrow(ax)
        
        # Remove axis labels for cleaner look
        ax.set_xlabel('Easting (m)', fontsize=10)
        ax.set_ylabel('Northing (m)', fontsize=10)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
    # Location context removed as requested
    
    def _create_filtered_legend(self, ax):
        """
        Create professional legend for filtered subdivisions only
        """
        ax.axis('off')
        
        # Legend title
        ax.text(0.5, 0.95, 'LEGENDA', ha='center', va='top', 
               fontsize=12, fontweight='bold', transform=ax.transAxes)
        
        # Sub-division legend (only for displayed subdivisions)
        y_pos = 0.85
        displayed_subdivisions = self.gdf['SUB_DIVISI'].unique()
        
        for sub_div in displayed_subdivisions:
            if pd.isna(sub_div):
                continue
                
            color = self.colors.get(sub_div, '#808080')
            
            # Color patch
            rect = Rectangle((0.05, y_pos-0.03), 0.15, 0.06, 
                           facecolor=color, alpha=0.7, 
                           edgecolor='black', linewidth=0.5,
                           transform=ax.transAxes)
            ax.add_patch(rect)
            
            # Label (truncate if too long)
            label = sub_div if len(sub_div) <= 20 else sub_div[:17] + '...'
            ax.text(0.25, y_pos, label, ha='left', va='center',
                   fontsize=8, transform=ax.transAxes)
            
            y_pos -= 0.12
        
        # Add symbols legend
        y_pos -= 0.05
        ax.text(0.5, y_pos, 'SIMBOL', ha='center', va='center',
               fontsize=10, fontweight='bold', transform=ax.transAxes)
        
        y_pos -= 0.08
        ax.text(0.05, y_pos, '━━━', ha='left', va='center',
               fontsize=12, color='black', transform=ax.transAxes)
        ax.text(0.25, y_pos, 'Batas Blok', ha='left', va='center',
               fontsize=8, transform=ax.transAxes)
        
        y_pos -= 0.08
        ax.text(0.05, y_pos, 'P XX/XX', ha='left', va='center',
               fontsize=8, fontweight='bold', transform=ax.transAxes,
               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        ax.text(0.25, y_pos, 'Kode Blok', ha='left', va='center',
               fontsize=8, transform=ax.transAxes)
    
    def _add_north_arrow(self, ax):
        """
        Add north arrow to the map
        """
        # Get map bounds
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Position north arrow in top right
        x_pos = xlim[1] - (xlim[1] - xlim[0]) * 0.1
        y_pos = ylim[1] - (ylim[1] - ylim[0]) * 0.1
        
        # Draw north arrow
        arrow_length = (ylim[1] - ylim[0]) * 0.05
        
        ax.annotate('', xy=(x_pos, y_pos), 
                   xytext=(x_pos, y_pos - arrow_length),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
        
        ax.text(x_pos, y_pos + arrow_length * 0.3, 'U', 
               ha='center', va='center', fontsize=12, fontweight='bold')
    
    def _add_title_and_logo(self, ax):
         """
         Add title, company logo, and compass
         """
         ax.axis('off')
         
         # Add logo if provided
         if self.logo_path:
             try:
                 import matplotlib.image as mpimg
                 logo = mpimg.imread(self.logo_path)
                 # Position logo on the left side
                 ax.imshow(logo, extent=[0.02, 0.18, 0.2, 0.8], transform=ax.transAxes, aspect='auto')
                 print(f"Logo loaded successfully from: {self.logo_path}")
             except Exception as e:
                 print(f"Warning: Could not load logo from {self.logo_path}: {e}")
         
         # Main title in the center
         ax.text(0.5, 0.5, self.map_title, ha='center', va='center',
                fontsize=18, fontweight='bold', transform=ax.transAxes)
         
         # Add compass if provided
         if self.compass_path:
             try:
                 import matplotlib.image as mpimg
                 compass = mpimg.imread(self.compass_path)
                 # Position compass on the right side
                 ax.imshow(compass, extent=[0.75, 0.85, 0.3, 0.7], transform=ax.transAxes, aspect='auto')
                 print(f"Compass loaded successfully from: {self.compass_path}")
             except Exception as e:
                 print(f"Warning: Could not load compass from {self.compass_path}: {e}")
         
         # Scale information below compass
         ax.text(0.8, 0.2, "Skala\n1:77.000", ha='center', va='center',
                fontsize=12, fontweight='bold', transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black'))
    
    def _add_technical_info(self, ax):
        """
        Add technical information and signature area
        """
        ax.axis('off')
        
        # Technical information
        info_text = [
            "Dibuat Oleh : Surveyor / Surveyor R.M.J",
            f"Tanggal: {pd.Timestamp.now().strftime('%d %B %Y')}",
            "Sistem Koordinat: UTM Zone 48S",
            "Datum: WGS 1984"
        ]
        
        y_start = 0.9
        for i, info in enumerate(info_text):
            ax.text(0.05, y_start - i*0.2, info, ha='left', va='center',
                   fontsize=8, transform=ax.transAxes)
        
        # Company logo at bottom
        ax.text(0.5, 0.1, "PT. REBINMAS JAYA", ha='center', va='center',
               fontsize=10, fontweight='bold', color='red', transform=ax.transAxes)
     
    def _add_context_map(self, ax):
        """
        Add Belitung context map showing study area location
        """
        ax.axis('off')
        
        # Title for context map
        ax.text(0.5, 0.95, 'Peta Konteks\nPulau Belitung', ha='center', va='top',
               fontsize=10, fontweight='bold', transform=ax.transAxes)
        
        try:
            # Load Belitung data if not already loaded
            if self.belitung_gdf is None:
                self.load_belitung_data()
            
            if self.belitung_gdf is not None:
                # Plot Belitung islands
                self.belitung_gdf.plot(ax=ax, color='lightblue', alpha=0.7, 
                                      edgecolor='black', linewidth=0.5)
                
                # Add study area location marker
                if hasattr(self, 'gdf') and len(self.gdf) > 0:
                    project_bounds = self.gdf.total_bounds
                    project_center_x = (project_bounds[0] + project_bounds[2]) / 2
                    project_center_y = (project_bounds[1] + project_bounds[3]) / 2
                    
                    # Add marker for project location
                    ax.plot(project_center_x, project_center_y, 'ro', 
                           markersize=8, markeredgecolor='darkred', markeredgewidth=1)
                    
                    # Add text label
                    ax.text(project_center_x, project_center_y - 5000, 'Area Kajian', 
                           ha='center', va='top', fontsize=6, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
                
                # Set extent with margins
                belitung_bounds = self.belitung_gdf.total_bounds
                margin = max((belitung_bounds[2] - belitung_bounds[0]), 
                           (belitung_bounds[3] - belitung_bounds[1])) * 0.1
                
                ax.set_xlim(belitung_bounds[0] - margin, belitung_bounds[2] + margin)
                ax.set_ylim(belitung_bounds[1] - margin, belitung_bounds[3] + margin)
                
                # Remove ticks
                ax.set_xticks([])
                ax.set_yticks([])
                
                # Add border
                for spine in ax.spines.values():
                    spine.set_linewidth(1)
                    spine.set_color('black')
                
            else:
                # Fallback if Belitung data not available
                ax.text(0.5, 0.5, 'Peta Konteks\nTidak Tersedia', ha='center', va='center',
                       fontsize=8, transform=ax.transAxes,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.5))
                
        except Exception as e:
            print(f"Error creating context map: {e}")
            ax.text(0.5, 0.5, 'Peta Konteks\nTidak Tersedia', ha='center', va='center',
                   fontsize=8, transform=ax.transAxes,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.5))
    
    def _add_bottom_info(self, ax):
        """
        Add bottom information panel with coordinate system and scale details
        """
        ax.axis('off')
        
        # Add coordinate system information
        coord_info = "Sistem Koordinat: UTM Zone 48S (EPSG:32748) | Datum: WGS 1984 | Proyeksi: Transverse Mercator"
        ax.text(0.02, 0.7, coord_info, ha='left', va='center',
               fontsize=9, transform=ax.transAxes)
        
        # Add scale and accuracy information
        scale_info = "Skala Peta: 1:77.000 | Akurasi: ±5 meter | Sumber Data: Survey GPS RTK"
        ax.text(0.02, 0.3, scale_info, ha='left', va='center',
               fontsize=9, transform=ax.transAxes)
        
        # Add border
        border_rect = Rectangle((0.01, 0.1), 0.98, 0.8, 
                              fill=False, edgecolor='black', linewidth=1,
                              transform=ax.transAxes)
        ax.add_patch(border_rect)

def main():
    # Example usage
    import os
    
    # Path to shapefile
    shapefile_path = "../merge_all_sub_divisi_map/merged_estates_HCV0_20250721_092606.shp"
    
    # Example: Select specific subdivisions (None = all subdivisions)
    # selected_subdivisions = ['SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR KANDIS']
    selected_subdivisions = None  # Show all by default
    
    # Custom title and logo
    custom_title = "PETA KEBUN 1 B\nPT. REBINMAS JAYA"
    logo_path = r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\rebinmas_logo.jpg"
    compass_path = r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\kompas.webp"
    belitung_shapefile_path = r"D:\Gawean Rebinmas\Tree Counting Project\Information System Web Tree Counted\Assets\batas_desa_belitung\batas_desa_belitung.shp"
    
    # Create map generator
    map_gen = ProfessionalMapGenerator(shapefile_path, selected_subdivisions, custom_title, logo_path, compass_path, belitung_shapefile_path)
    
    # Load data
    if not map_gen.load_data():
        print("Failed to load data. Exiting.")
        return
    
    # Generate professional map
    output_path = "Peta_Profesional_Sub_Divisi.pdf"
    if map_gen.create_professional_map(output_path):
        print(f"\nPeta profesional berhasil dibuat: {output_path}")
        print("\nFitur yang disertakan:")
        print("- Auto-zoom ke area yang dipilih")
        print("- Klasifikasi warna berdasarkan sub divisi")
        print("- Label blok pada setiap area")
        print("- Legenda untuk area yang ditampilkan saja")
        print("- Skala peta")
        print("- Panah utara")
        print("- Informasi teknis pemetaan")
        if selected_subdivisions:
            print(f"- Menampilkan hanya: {', '.join(selected_subdivisions)}")
    else:
        print("Gagal membuat peta.")

if __name__ == "__main__":
    import pandas as pd
    main()