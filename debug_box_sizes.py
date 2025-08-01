#!/usr/bin/env python3
"""
Debug script to check box sizes and positions
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from professional_map_generator import ProfessionalMapGenerator

def debug_box_positions():
    """
    Create a simple figure to debug box positions and sizes
    """
    print("🔍 DEBUGGING BOX POSITIONS AND SIZES...")
    
    # Create figure
    fig = plt.figure(figsize=(16.54, 11.69))
    fig.patch.set_facecolor('white')
    
    # Create a generator instance to access the constants
    generator = ProfessionalMapGenerator(
        input_path="dummy.shp",  # Dummy path
        file_type="shapefile"
    )
    
    print(f"\n📏 BOX LAYOUT CONSTANTS:")
    print(f"   BOX_WIDTH = {generator.BOX_WIDTH}")
    print(f"   BOX_LEFT_POSITION = {generator.BOX_LEFT_POSITION}")
    print(f"   MAIN_MAP_WIDTH = {generator.MAIN_MAP_WIDTH}")
    print(f"   MAIN_MAP_LEFT = {generator.MAIN_MAP_LEFT}")
    
    # Create all boxes using the same method as the main generator
    print(f"\n🔧 CREATING ALL BOXES:")
    
    # Title box
    title_coords = generator._get_standard_box_coords(0.88, 0.10, "TITLE")
    ax_title = plt.axes(title_coords)
    ax_title.add_patch(Rectangle((0, 0), 1, 1, facecolor='lightblue', edgecolor='black', linewidth=2))
    ax_title.text(0.5, 0.5, 'TITLE BOX', ha='center', va='center', fontweight='bold')
    ax_title.axis('off')
    
    # Belitung overview box
    overview_coords = generator._get_standard_box_coords(0.58, 0.28, "BELITUNG_OVERVIEW")
    ax_overview = plt.axes(overview_coords)
    ax_overview.add_patch(Rectangle((0, 0), 1, 1, facecolor='lightgreen', edgecolor='black', linewidth=2))
    ax_overview.text(0.5, 0.5, 'BELITUNG\nOVERVIEW', ha='center', va='center', fontweight='bold')
    ax_overview.axis('off')
    
    # Legend box
    legend_coords = generator._get_standard_box_coords(0.38, 0.18, "LEGEND")
    ax_legend = plt.axes(legend_coords)
    ax_legend.add_patch(Rectangle((0, 0), 1, 1, facecolor='lightyellow', edgecolor='black', linewidth=2))
    ax_legend.text(0.5, 0.5, 'LEGEND BOX', ha='center', va='center', fontweight='bold')
    ax_legend.axis('off')
    
    # Compass & Scale box
    compass_coords = generator._get_standard_box_coords(0.18, 0.18, "COMPASS_SCALE")
    ax_compass = plt.axes(compass_coords)
    ax_compass.add_patch(Rectangle((0, 0), 1, 1, facecolor='lightcoral', edgecolor='black', linewidth=2))
    ax_compass.text(0.5, 0.5, 'COMPASS &\nSCALE BOX', ha='center', va='center', fontweight='bold')
    ax_compass.axis('off')
    
    # Logo box
    logo_coords = generator._get_standard_box_coords(0.02, 0.14, "LOGO_INFO")
    ax_logo = plt.axes(logo_coords)
    ax_logo.add_patch(Rectangle((0, 0), 1, 1, facecolor='lightpink', edgecolor='black', linewidth=2))
    ax_logo.text(0.5, 0.5, 'LOGO BOX', ha='center', va='center', fontweight='bold')
    ax_logo.axis('off')
    
    # Main map area for reference
    ax_main = plt.axes([generator.MAIN_MAP_LEFT, 0.05, generator.MAIN_MAP_WIDTH, 0.93])
    ax_main.add_patch(Rectangle((0, 0), 1, 1, facecolor='lightgray', edgecolor='black', linewidth=2))
    ax_main.text(0.5, 0.5, 'MAIN MAP AREA', ha='center', va='center', fontweight='bold', fontsize=16)
    ax_main.axis('off')
    
    # Add blue border around entire figure
    border_rect = Rectangle((0.01, 0.01), 0.98, 0.98, 
                          fill=False, edgecolor='blue', linewidth=3,
                          transform=fig.transFigure)
    fig.patches.append(border_rect)
    
    # Save debug image
    plt.savefig("Debug_Box_Sizes.pdf", dpi=300, bbox_inches='tight')
    print(f"\n✅ Debug image saved as: Debug_Box_Sizes.pdf")
    print(f"\n📊 ANALYSIS:")
    print(f"   All boxes should have identical width: {generator.BOX_WIDTH}")
    print(f"   All boxes should start at same left position: {generator.BOX_LEFT_POSITION}")
    print(f"   If compass box appears different, the issue is in content rendering, not box size.")
    
    plt.show()
    return True

if __name__ == "__main__":
    debug_box_positions()