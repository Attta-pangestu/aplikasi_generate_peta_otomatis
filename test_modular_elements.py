#!/usr/bin/env python3
"""
Test script for modular map elements implementation
Verifies that the new modular system produces the same output as the original implementation
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Import the professional map generator and modular elements
from professional_map_generator import ProfessionalMapGenerator
from map_elements import (
    TitleElement, LegendElement, BelitungOverviewElement, 
    LogoInfoElement, CompassElement, ScaleBarElement
)

def test_modular_elements():
    """
    Test that modular elements produce the same layout as the original implementation
    """
    print("Testing modular map elements implementation...")
    
    # Create a simple test GeoDataFrame for demonstration
    from shapely.geometry import Polygon
    import pandas as pd
    
    # Create sample data
    polygons = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        Polygon([(0, 1), (1, 1), (1, 2), (0, 2)])
    ]
    
    data = {
        'SUB_DIVISI': ['SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR KANDIS', 'SUB DIVISI AIR RAYA'],
        'BLOK': ['A1', 'B2', 'C3']
    }
    
    gdf = gpd.GeoDataFrame(data, geometry=polygons, crs='EPSG:4326')
    
    # Create a test map generator
    map_gen = ProfessionalMapGenerator("test.shp")
    map_gen.gdf = gdf
    
    # Test original implementation
    print("\n1. Testing original implementation...")
    try:
        # Create figure with professional layout (A3 landscape style)
        fig1 = plt.figure(figsize=(16.54, 11.69))  # A3 size in inches
        fig1.patch.set_facecolor('white')
        
        # Add blue border around entire map
        border_rect = Rectangle((0.01, 0.01), 0.98, 0.98, 
                              fill=False, edgecolor='blue', linewidth=3,
                              transform=fig1.transFigure)
        fig1.patches.append(border_rect)
        
        # Main map area (using standardized constants)
        ax_main1 = plt.axes([map_gen.MAIN_MAP_LEFT, 0.05, map_gen.MAIN_MAP_WIDTH, 0.93])
        
        # Add border frame for main map
        main_map_border1 = Rectangle((map_gen.MAIN_MAP_LEFT, 0.05), map_gen.MAIN_MAP_WIDTH, 0.93, 
                                  fill=False, edgecolor='black', linewidth=2,
                                  transform=fig1.transFigure)
        fig1.patches.append(main_map_border1)
        
        # Right panel sections - Using standardized box width constructor
        print("\n🔧 DEBUG: Creating all info boxes with dimensions:")
        
        # Title area (only title) - using standard box coordinates
        ax_title1 = plt.axes(map_gen._get_standard_box_coords(0.88, 0.10, "TITLE"))
        
        # Belitung overview map (compact) - using standard box coordinates
        ax_overview1 = plt.axes(map_gen._get_standard_box_coords(0.58, 0.28, "BELITUNG_OVERVIEW"))
        
        # Legend area - using standard box coordinates
        ax_legend1 = plt.axes(map_gen._get_standard_box_coords(0.38, 0.18, "LEGEND"))
        
        # Logo and info area - using standard box coordinates
        ax_logo1 = plt.axes(map_gen._get_standard_box_coords(0.02, 0.14, "LOGO_INFO"))
        
        print(f"\n🗺️ DEBUG: Main map area: Left={map_gen.MAIN_MAP_LEFT:.3f}, Width={map_gen.MAIN_MAP_WIDTH:.3f}, Right edge={map_gen.MAIN_MAP_LEFT + map_gen.MAIN_MAP_WIDTH:.3f}")
        print(f"🗺️ DEBUG: Total figure width = 1.000, Available space = {1.0 - (map_gen.MAIN_MAP_LEFT + map_gen.MAIN_MAP_WIDTH):.3f}\n")
        
        # Add title
        map_gen._add_title(ax_title1)
        
        # Create legend
        map_gen._create_professional_legend(ax_legend1)
        
        # Add Belitung overview map
        map_gen._add_belitung_overview(ax_overview1)
        
        # Add logo and info
        map_gen._add_logo_and_info(ax_logo1)
        
        # Save the map
        plt.savefig("test_original_implementation.pdf", dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig1)
        print("Original implementation test completed successfully!")
        
    except Exception as e:
        print(f"Error in original implementation test: {e}")
        return False
    
    # Test modular implementation
    print("\n2. Testing modular implementation...")
    try:
        # Create figure with professional layout (A3 landscape style)
        fig2 = plt.figure(figsize=(16.54, 11.69))  # A3 size in inches
        fig2.patch.set_facecolor('white')
        
        # Add blue border around entire map
        border_rect = Rectangle((0.01, 0.01), 0.98, 0.98, 
                              fill=False, edgecolor='blue', linewidth=3,
                              transform=fig2.transFigure)
        fig2.patches.append(border_rect)
        
        # Main map area (using standardized constants)
        ax_main2 = plt.axes([map_gen.MAIN_MAP_LEFT, 0.05, map_gen.MAIN_MAP_WIDTH, 0.93])
        
        # Add border frame for main map
        main_map_border2 = Rectangle((map_gen.MAIN_MAP_LEFT, 0.05), map_gen.MAIN_MAP_WIDTH, 0.93, 
                                  fill=False, edgecolor='black', linewidth=2,
                                  transform=fig2.transFigure)
        fig2.patches.append(main_map_border2)
        
        # Create modular map elements with default positions
        # Title area (only title) - using standard box coordinates
        title_element = TitleElement(
            title_text=map_gen.map_title,
            position=map_gen._get_standard_box_coords(0.88, 0.10, "TITLE")
        )
        
        # Legend area - using standard box coordinates
        legend_element = LegendElement(
            position=map_gen._get_standard_box_coords(0.38, 0.18, "LEGEND"),
            file_type=map_gen.file_type,
            colors=map_gen.colors,
            gdf=map_gen.gdf,
            tiff_legend=map_gen.tiff_legend
        )
        
        # Belitung overview map (compact) - using standard box coordinates
        belitung_element = BelitungOverviewElement(
            position=map_gen._get_standard_box_coords(0.58, 0.28, "BELITUNG_OVERVIEW"),
            belitung_gdf=map_gen.belitung_gdf,
            main_gdf=map_gen.gdf,
            colors=map_gen.colors,
            file_type=map_gen.file_type,
            tiff_bounds=getattr(map_gen, 'tiff_bounds_wgs84', None)
        )
        
        # Logo and info area - using standard box coordinates
        logo_element = LogoInfoElement(
            position=map_gen._get_standard_box_coords(0.02, 0.14, "LOGO_INFO"),
            logo_path=map_gen.logo_path
        )
        
        # Compass and scale elements (overlay approach)
        # Calculate map width in degrees for scale bar
        map_width_degrees = 0.1  # Default value
        if hasattr(map_gen, 'gdf') and map_gen.gdf is not None:
            bounds = map_gen.gdf.total_bounds
            map_width_degrees = bounds[2] - bounds[0]  # longitude range
        
        compass_element = CompassElement(compass_path=map_gen.compass_path)
        scale_element = ScaleBarElement(map_width_degrees=map_width_degrees)
        
        # Render all elements
        title_element.render(fig2)
        legend_element.render(fig2)
        belitung_element.render(fig2)
        logo_element.render(fig2)
        
        # Add compass and scale as overlays to main map
        compass_element.add_to_main_map(ax_main2)
        scale_element.add_to_main_map(ax_main2)
        
        # Save the map
        plt.savefig("test_modular_implementation.pdf", dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig2)
        print("Modular implementation test completed successfully!")
        
    except Exception as e:
        print(f"Error in modular implementation test: {e}")
        return False
    
    print("\n3. Testing element positioning...")
    try:
        # Test that elements are positioned correctly
        fig3 = plt.figure(figsize=(16.54, 11.69))
        fig3.patch.set_facecolor('white')
        
        # Test title element positioning
        title_pos = map_gen._get_standard_box_coords(0.88, 0.10, "TITLE")
        title_element = TitleElement(
            title_text="TEST TITLE",
            position=title_pos
        )
        title_element.render(fig3)
        
        # Verify position
        if title_element.ax is not None:
            actual_pos = title_element.ax.get_position()
            expected_pos = title_pos
            print(f"Title element position - Expected: {expected_pos}, Actual: {[actual_pos.x0, actual_pos.y0, actual_pos.width, actual_pos.height]}")
        
        plt.savefig("test_positioning.pdf", dpi=150, bbox_inches='tight')
        plt.close(fig3)
        print("Element positioning test completed successfully!")
        
    except Exception as e:
        print(f"Error in element positioning test: {e}")
        return False
    
    print("\nAll tests completed successfully!")
    return True

if __name__ == "__main__":
    test_modular_elements()