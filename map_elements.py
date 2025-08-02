#!/usr/bin/env python3
"""
Modular Map Elements for Professional Surveyor-Style Map Generator
Provides reusable, positionable components for map layouts.

Author: Generated for Tree Counting Project
Date: 2025
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np


class MapElement:
    """
    Base class for all map elements
    """
    def __init__(self, name, position=None, size=None):
        """
        Initialize a map element
        
        Args:
            name (str): Name of the element
            position (list): [left, bottom, width, height] in figure coordinates (0-1)
            size (tuple): (width, height) in figure coordinates
        """
        self.name = name
        self.position = position or [0, 0, 1, 1]  # Default to full figure
        self.size = size
        self.ax = None  # Will be set when added to figure
    
    def create_axes(self, fig):
        """
        Create axes for this element on the given figure
        
        Args:
            fig: matplotlib figure object
            
        Returns:
            matplotlib axes object
        """
        self.ax = fig.add_axes(self.position)
        return self.ax
    
    def render(self, fig, data=None):
        """
        Render the element on the figure
        
        Args:
            fig: matplotlib figure object
            data: Optional data needed for rendering
        """
        if self.ax is None:
            self.ax = self.create_axes(fig)
        self._render_content(data)
    
    def _render_content(self, data=None):
        """
        Render the specific content of this element
        Should be overridden by subclasses
        
        Args:
            data: Optional data needed for rendering
        """
        pass
    
    def set_position(self, position):
        """
        Set the position of this element
        
        Args:
            position (list): [left, bottom, width, height] in figure coordinates (0-1)
        """
        self.position = position
        if self.ax is not None:
            self.ax.set_position(position)


class TitleElement(MapElement):
    """
    Map title element with nested box design
    """
    def __init__(self, title_text, position=None):
        """
        Initialize title element
        
        Args:
            title_text (str): Text to display as title
            position (list): [left, bottom, width, height] in figure coordinates
        """
        super().__init__("Title", position)
        self.title_text = title_text
    
    def _render_content(self, data=None):
        """
        Render the title content with nested box design
        """
        if self.ax is None:
            return
            
        self.ax.axis('off')
        
        # White background
        self.ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                                  linewidth=1, transform=self.ax.transAxes))
        
        # Inner nested box for title
        inner_box = Rectangle((0.05, 0.2), 0.9, 0.6, facecolor='white', 
                             edgecolor='black', linewidth=1, transform=self.ax.transAxes)
        self.ax.add_patch(inner_box)
        
        # Title text centered in the box
        self.ax.text(0.5, 0.6, self.title_text, ha='center', va='center',
               fontsize=12, fontweight='bold', transform=self.ax.transAxes)
        
        # Add underline below title
        self.ax.plot([0.1, 0.9], [0.45, 0.45], 'k-', linewidth=1, transform=self.ax.transAxes)


class LegendElement(MapElement):
    """
    Map legend element with nested box design
    """
    def __init__(self, position=None, file_type="shapefile", colors=None, gdf=None, tiff_legend=None):
        """
        Initialize legend element
        
        Args:
            position (list): [left, bottom, width, height] in figure coordinates
            file_type (str): Type of map data ("shapefile" or "tiff")
            colors (dict): Color mapping for subdivisions
            gdf: GeoDataFrame for shapefile legends
            tiff_legend (list): Legend entries for TIFF maps
        """
        super().__init__("Legend", position)
        self.file_type = file_type
        self.colors = colors or {}
        self.gdf = gdf
        self.tiff_legend = tiff_legend or []
    
    def _render_content(self, data=None):
        """
        Render the legend content with nested box design
        """
        if self.ax is None:
            return
            
        self.ax.axis('off')
        
        # White background
        self.ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                                  linewidth=1, transform=self.ax.transAxes))
        
        # Inner nested box for legend content
        inner_box = Rectangle((0.05, 0.05), 0.9, 0.9, facecolor='white', 
                             edgecolor='black', linewidth=1, transform=self.ax.transAxes)
        self.ax.add_patch(inner_box)
        
        # Legend title with underline
        self.ax.text(0.5, 0.9, 'LEGENDA', ha='center', va='center', 
               fontsize=10, fontweight='bold', transform=self.ax.transAxes)
        
        # Add underline below legend title
        self.ax.plot([0.1, 0.9], [0.85, 0.85], 'k-', linewidth=1, transform=self.ax.transAxes)
        
        if self.file_type == "shapefile" and self.gdf is not None:
            # Shapefile legend - subdivisions
            displayed_subdivisions = self.gdf['SUB_DIVISI'].dropna().unique()
            
            # Create legend items based on actual data (adjusted for nested box)
            y_start = 0.75
            for i, sub_div in enumerate(displayed_subdivisions):
                if len(sub_div) == 0 or str(sub_div).lower() == 'nan':
                    continue
                    
                y_pos = y_start - (i * 0.12)
                color = self.colors.get(sub_div, '#808080')  # Get actual color used
                
                # Color patch (adjusted position for nested box)
                rect = Rectangle((0.1, y_pos - 0.03), 0.12, 0.06, 
                               facecolor=color, alpha=0.8, 
                               edgecolor='black', linewidth=0.5,
                               transform=self.ax.transAxes)
                self.ax.add_patch(rect)
                
                # Label - use actual subdivision name (adjusted position)
                label = sub_div if len(str(sub_div)) <= 20 else str(sub_div)[:17] + '...'
                self.ax.text(0.25, y_pos, label, ha='left', va='center',
                       fontsize=7, transform=self.ax.transAxes)
            
            # Add symbols legend (adjusted positioning)
            y_pos_symbols = y_start - (len(displayed_subdivisions) * 0.12) - 0.05
            
            # Add separator line
            self.ax.plot([0.1, 0.9], [y_pos_symbols + 0.02, y_pos_symbols + 0.02], 'k-', linewidth=0.5, transform=self.ax.transAxes)
            
            self.ax.text(0.5, y_pos_symbols - 0.02, 'SIMBOL', ha='center', va='center',
                   fontsize=8, fontweight='bold', transform=self.ax.transAxes)
            
            y_pos_symbols -= 0.08
            self.ax.text(0.1, y_pos_symbols, '━━━', ha='left', va='center',
                   fontsize=10, color='black', transform=self.ax.transAxes)
            self.ax.text(0.3, y_pos_symbols, 'Batas Area', ha='left', va='center',
                   fontsize=7, transform=self.ax.transAxes)
            
            y_pos_symbols -= 0.08
            self.ax.text(0.1, y_pos_symbols, 'A1', ha='center', va='center',
                   fontsize=7, fontweight='bold', transform=self.ax.transAxes,
                   bbox=dict(boxstyle='square,pad=0.2', facecolor='white', edgecolor='black', linewidth=0.5))
            self.ax.text(0.3, y_pos_symbols, 'Kode Blok', ha='left', va='center',
                   fontsize=7, transform=self.ax.transAxes)
                    
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
                                   transform=self.ax.transAxes)
                    self.ax.add_patch(rect)
                    
                    # Label - use description (adjusted position)
                    label = description if len(description) <= 20 else description[:17] + '...'
                    self.ax.text(0.25, y_pos, label, ha='left', va='center',
                           fontsize=7, transform=self.ax.transAxes)
            else:
                # No legend data provided (adjusted for nested box)
                self.ax.text(0.5, 0.4, 'No legend data\nprovided for TIFF', 
                       ha='center', va='center', fontsize=9, 
                       transform=self.ax.transAxes)


class BelitungOverviewElement(MapElement):
    """
    Belitung overview map element with nested box design
    """
    def __init__(self, position=None, belitung_gdf=None, main_gdf=None, colors=None, file_type="shapefile", tiff_bounds=None):
        """
        Initialize Belitung overview element
        
        Args:
            position (list): [left, bottom, width, height] in figure coordinates
            belitung_gdf: GeoDataFrame with Belitung island data
            main_gdf: GeoDataFrame with main map data
            colors (dict): Color mapping for subdivisions
            file_type (str): Type of map data ("shapefile" or "tiff")
            tiff_bounds: Bounds for TIFF data
        """
        super().__init__("Belitung Overview", position)
        self.belitung_gdf = belitung_gdf
        self.main_gdf = main_gdf
        self.colors = colors or {}
        self.file_type = file_type
        self.tiff_bounds = tiff_bounds
    
    def _render_content(self, data=None):
        """
        Render the Belitung overview content with nested box design
        """
        if self.ax is None:
            return
            
        self.ax.axis('off')
        
        # White background with border
        self.ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                                  linewidth=1, transform=self.ax.transAxes))
        
        # Inner nested box for overview content
        inner_box = Rectangle((0.05, 0.05), 0.9, 0.9, facecolor='white', 
                             edgecolor='black', linewidth=1, transform=self.ax.transAxes)
        self.ax.add_patch(inner_box)
        
        try:
            if self.belitung_gdf is not None and len(self.belitung_gdf) > 0:
                # Create overview map (moved up to avoid overlaps)
                overview_rect = [0.15, 0.2, 0.7, 0.65]  # [left, bottom, width, height] - moved up
                overview_ax = self.ax.inset_axes(overview_rect)
                
                # Plot Belitung with WADMKK categorization if available
                if 'WADMKK' in self.belitung_gdf.columns:
                    unique_values = self.belitung_gdf['WADMKK'].dropna().unique()
                    
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
                else:
                    # Plot without categorization
                    self.belitung_gdf.plot(ax=overview_ax, color='#90EE90', alpha=0.7, 
                                          edgecolor='black', linewidth=0.8, label='Belitung', aspect=None)
                
                # Add study area overlay with better visibility
                if self.main_gdf is not None and len(self.main_gdf) > 0:
                    # Add actual study area polygons with same colors as main map
                    self.main_gdf.plot(ax=overview_ax, 
                                     column='SUB_DIVISI', 
                                     categorical=True,
                                     legend=False,
                                     color=[self.colors.get(div, '#87CEEB') for div in self.main_gdf['SUB_DIVISI']], 
                                     alpha=0.8, 
                                     edgecolor='darkred', 
                                     linewidth=2, 
                                     zorder=15)
                    
                    # Get study area bounds for rectangle overlay
                    bounds = self.main_gdf.total_bounds
                    center_x = (bounds[0] + bounds[2]) / 2
                    center_y = (bounds[1] + bounds[3]) / 2
                    width = bounds[2] - bounds[0]
                    height = bounds[3] - bounds[1]
                    
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
                
                # Add TIFF area overlay for TIFF files
                elif self.file_type == "tiff" and self.tiff_bounds is not None:
                    # Get TIFF bounds in WGS84
                    bounds = self.tiff_bounds  # [minx, miny, maxx, maxy]
                    center_x = (bounds[0] + bounds[2]) / 2
                    center_y = (bounds[1] + bounds[3]) / 2
                    width = bounds[2] - bounds[0]
                    height = bounds[3] - bounds[1]
                    
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
            else:
                # Try to load Belitung data if not already loaded
                print("Belitung data not available, attempting to load...")
                try:
                    import geopandas as gpd
                    import os
                    
                    # Default Belitung shapefile path
                    belitung_path = r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\batas_desa_belitung.shp"
                    
                    if os.path.exists(belitung_path):
                        print(f"Loading Belitung shapefile from: {belitung_path}")
                        belitung_gdf = gpd.read_file(belitung_path)
                        
                        # Set/convert CRS to WGS84
                        if belitung_gdf.crs is None:
                            belitung_gdf = belitung_gdf.set_crs('EPSG:4326')
                        elif belitung_gdf.crs != 'EPSG:4326':
                            # Check if coordinates suggest UTM (large values)
                            bounds = belitung_gdf.total_bounds
                            if abs(bounds[0]) > 1000 or abs(bounds[1]) > 1000:
                                belitung_gdf = belitung_gdf.set_crs('EPSG:32748')  # UTM 48S
                            belitung_gdf = belitung_gdf.to_crs('EPSG:4326')
                        
                        # Update the instance data
                        self.belitung_gdf = belitung_gdf
                        print(f"Successfully loaded Belitung data with {len(belitung_gdf)} features")
                        
                        # Recursively call render to use the real data
                        self._render_content(data)
                        return
                    else:
                        print(f"Belitung shapefile not found at: {belitung_path}")
                        
                except Exception as load_error:
                    print(f"Failed to load Belitung data: {load_error}")
                
                # Only show error message if we really can't load the data
                self.ax.text(0.5, 0.5, 'Peta Belitung\n(Data tidak tersedia)\nPeriksa file batas_desa_belitung.shp', 
                           ha='center', va='center', fontsize=9, fontweight='bold', 
                           transform=self.ax.transAxes,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))
        except Exception as e:
            # Final fallback
            self.ax.text(0.5, 0.5, 'Peta Konteks\nBelitung\n(Error)', ha='center', va='center',
                   fontsize=10, transform=self.ax.transAxes,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.5))


class LogoInfoElement(MapElement):
    """
    Logo and information element with nested box design
    """
    def __init__(self, position=None, logo_path=None, company_name="PT. REBINMAS JAYA", 
                 production_info="Diproduksi untuk : PT. REBINMAS JAYA",
                 program_info="Program: IT Rebinmas | Data: Surveyor RMJ",
                 generated_date="Generated: July 2025"):
        """
        Initialize logo and information element
        
        Args:
            position (list): [left, bottom, width, height] in figure coordinates
            logo_path (str): Path to company logo image
            company_name (str): Company name to display
            production_info (str): Production information
            program_info (str): Program information
            generated_date (str): Generation date
        """
        super().__init__("Logo and Info", position)
        self.logo_path = logo_path
        self.company_name = company_name
        self.production_info = production_info
        self.program_info = program_info
        self.generated_date = generated_date
    
    def _render_content(self, data=None):
        """
        Render the logo and information content with nested box design
        """
        if self.ax is None:
            return
            
        self.ax.axis('off')
        
        # White background
        self.ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                                  linewidth=1, transform=self.ax.transAxes))
        
        # Inner nested box for logo content
        inner_box = Rectangle((0.05, 0.05), 0.9, 0.9, facecolor='white', 
                             edgecolor='black', linewidth=1, transform=self.ax.transAxes)
        self.ax.add_patch(inner_box)

        # Company logo with better error handling
        logo_loaded = False
        if self.logo_path:
            try:
                import matplotlib.image as mpimg
                import os
                if os.path.exists(self.logo_path):
                    logo = mpimg.imread(self.logo_path)
                    # Logo positioned in upper part of enlarged box
                    self.ax.imshow(logo, extent=[0.1, 0.9, 0.55, 0.9], transform=self.ax.transAxes, aspect='auto')
                    logo_loaded = True
            except Exception as e:
                pass
        
        # Fallback logo design if image not loaded (adjusted for enlarged box)
        if not logo_loaded:
            # Create professional logo placeholder in upper part
            self.ax.text(0.5, 0.75, "REBINMAS", ha='center', va='center',
                   fontsize=14, fontweight='bold', color='#1E90FF', 
                   transform=self.ax.transAxes)
            self.ax.text(0.5, 0.65, "JAYA", ha='center', va='center',
                   fontsize=12, fontweight='bold', color='#FF6B35', 
                   transform=self.ax.transAxes)
            # Add decorative border in upper part
            logo_rect = Rectangle((0.25, 0.55), 0.5, 0.25, fill=False, 
                                edgecolor='#1E90FF', linewidth=2, 
                                transform=self.ax.transAxes)
            self.ax.add_patch(logo_rect)
        
        # Company name with underline
        self.ax.text(0.5, 0.45, self.company_name, ha='center', va='center',
               fontsize=10, fontweight='bold', color='#1E90FF', transform=self.ax.transAxes)
        
        # Add underline below company name
        self.ax.plot([0.1, 0.9], [0.4, 0.4], 'k-', linewidth=1, transform=self.ax.transAxes)
        
        # Add production information with proper spacing
        self.ax.text(0.5, 0.32, self.production_info, ha='center', va='center',
               fontsize=8, transform=self.ax.transAxes)
        self.ax.text(0.5, 0.25, self.program_info, ha='center', va='center',
               fontsize=8, transform=self.ax.transAxes)
        self.ax.text(0.5, 0.18, self.generated_date, ha='center', va='center',
               fontsize=8, transform=self.ax.transAxes)


class CompassElement(MapElement):
    """
    Compass element for map orientation
    """
    def __init__(self, position=None, compass_path=None):
        """
        Initialize compass element
        
        Args:
            position (list): [left, bottom, width, height] in figure coordinates
            compass_path (str): Path to compass image
        """
        super().__init__("Compass", position)
        self.compass_path = compass_path
    
    def add_to_main_map(self, main_ax):
        """
        Add compass directly to main map axes (overlay approach)
        
        Args:
            main_ax: Main map axes to add compass to
        """
        # REMOVED: This compass was too close to the scale bar
        # The compass at position (0.85, 0.30) has been removed to avoid duplication
        # Only one compass will remain in the system
        print("Compass element skipped - removed duplicate compass near scale bar")
        return
        # This compass implementation has been removed to avoid duplication
        # The remaining compass will be positioned elsewhere in the system


class ScaleBarElement(MapElement):
    """
    Scale bar element for map scale
    """
    def __init__(self, position=None, map_width_degrees=None):
        """
        Initialize scale bar element
        
        Args:
            position (list): [left, bottom, width, height] in figure coordinates
            map_width_degrees (float): Width of map in degrees
        """
        super().__init__("Scale Bar", position)
        self.map_width_degrees = map_width_degrees or 0.1  # Default value
    
    def add_to_main_map(self, main_ax):
        """
        Add scale bar directly to main map axes (overlay approach)
        
        Args:
            main_ax: Main map axes to add scale bar to
        """
        # Add scale bar outside bottom left of coordinate frame
        fig = main_ax.get_figure()
        
        # Calculate appropriate scale based on map width
        map_width_km = self.map_width_degrees * 111
        
        # Determine appropriate scale bar length
        if map_width_km > 20:
            scale_km = 8  # 8 km scale bar
        elif map_width_km > 10:
            scale_km = 4  # 4 km scale bar
        elif map_width_km > 5:
            scale_km = 2  # 2 km scale bar
        else:
            scale_km = 1  # 1 km scale bar
        
        # Position scale bar outside the coordinate frame using figure coordinates
        # Bottom left outside the main map frame
        scale_x_fig = 0.66  # Align with legend box
        scale_y_fig = 0.30  # Below the legend area
        
        # Create scale bar width in figure coordinates (proportional to map)
        scale_width_fig = 0.15  # 15% of figure width
        scale_height_fig = 0.02  # 2% of figure height
        
        # Create background rectangle using figure coordinates
        from matplotlib.patches import Rectangle
        scale_bg = Rectangle((scale_x_fig - 0.01, scale_y_fig - 0.005),
                           scale_width_fig + 0.02, scale_height_fig + 0.03,
                           facecolor='white', alpha=0.95, edgecolor='black',
                           linewidth=1.5, transform=fig.transFigure, zorder=200)
        fig.patches.append(scale_bg)
        
        # Create 5 segments alternating black and white
        segment_width_fig = scale_width_fig / 5
        
        for i in range(5):
            x_pos = scale_x_fig + (i * segment_width_fig)
            # Alternating colors
            if i % 2 == 0:
                color = 'black'
            else:
                color = 'white'
            
            segment = Rectangle((x_pos, scale_y_fig + 0.01), segment_width_fig, scale_height_fig,
                          facecolor=color, edgecolor='black', linewidth=0.8,
                          transform=fig.transFigure, zorder=201)
            fig.patches.append(segment)
        
        # Add scale labels only at start and end (remove duplicate numbers)
        fifth_km = scale_km / 5
        
        # Only show labels at 0 and maximum scale
        for i in [0, 5]:  # Only first and last positions
            x_pos = scale_x_fig + (i * segment_width_fig)
            km_value = fifth_km * i
            if km_value == 0:
                label = '0'
            elif km_value < 1:
                label = f'{int(km_value * 1000)}m'
            else:
                label = f'{km_value:.1f}km' if km_value != int(km_value) else f'{int(km_value)}km'
            
            # Moved labels down for better visibility
            fig.text(x_pos, scale_y_fig - 0.005, label,
                   ha='center', va='top', fontsize=10, fontweight='bold',
                   color='black', transform=fig.transFigure, zorder=202)
        
        # Add "Scale" title (moved up slightly for better spacing)
        fig.text(scale_x_fig + scale_width_fig/2, scale_y_fig + scale_height_fig + 0.025, 'SKALA',
               ha='center', va='bottom', fontsize=12, fontweight='bold',
               color='black', transform=fig.transFigure, zorder=202)
        
        # Add simplified coordinate system information below the scale bar (single line)
        fig.text(scale_x_fig + scale_width_fig/2, scale_y_fig - 0.04,
               'WGS84 (EPSG:4326) - Derajat Desimal',
               ha='center', va='top', fontsize=8, fontweight='normal',
               color='black', transform=fig.transFigure, zorder=202)
        
        # Calculate and add scale ratio (1:X format) below coordinate information
        # At latitude ~-2.6°, 1 degree longitude ≈ 111 km
        scale_ratio = int((scale_km * 1000) / (scale_width_fig * 0.21))  # Approximate conversion
        fig.text(scale_x_fig + scale_width_fig/2, scale_y_fig - 0.06, 
               f'1:{scale_ratio:,}',
               ha='center', va='top', fontsize=10, fontweight='bold',
               color='#2c3e50', transform=fig.transFigure, zorder=202)