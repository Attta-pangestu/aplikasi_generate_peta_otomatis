#!/usr/bin/env python3
"""
Test script to visually compare all boxes including the updated compass and scale bar box
to verify that the compass box now appears as wide as other boxes with proper visual elements.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np

def create_box_comparison():
    """Create a visual comparison of all boxes to verify compass box width utilization"""
    
    # Create figure with same dimensions as the actual map
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    
    # Box parameters (same as in ProfessionalMapGenerator)
    BOX_WIDTH = 0.32
    BOX_LEFT_POSITION = 0.66
    
    # Define all boxes with their positions and labels
    boxes = [
        {'bottom': 0.85, 'height': 0.12, 'label': 'Title Box', 'color': 'lightblue'},
        {'bottom': 0.70, 'height': 0.12, 'label': 'Compass & Scale Box', 'color': 'lightgreen'},
        {'bottom': 0.45, 'height': 0.22, 'label': 'Legend Box', 'color': 'lightyellow'},
        {'bottom': 0.20, 'height': 0.22, 'label': 'Belitung Overview Box', 'color': 'lightcoral'},
        {'bottom': 0.02, 'height': 0.15, 'label': 'Logo & Info Box', 'color': 'lightgray'}
    ]
    
    # Draw all boxes
    for i, box in enumerate(boxes):
        # Draw box outline
        rect = Rectangle((BOX_LEFT_POSITION, box['bottom']), BOX_WIDTH, box['height'], 
                        facecolor=box['color'], edgecolor='black', linewidth=2, alpha=0.7)
        ax.add_patch(rect)
        
        # Add box label
        ax.text(BOX_LEFT_POSITION + BOX_WIDTH/2, box['bottom'] + box['height']/2, 
               box['label'], ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Add dimensions text
        ax.text(BOX_LEFT_POSITION + BOX_WIDTH + 0.01, box['bottom'] + box['height']/2, 
               f'W: {BOX_WIDTH:.2f}\nH: {box["height"]:.2f}', 
               ha='left', va='center', fontsize=8)
    
    # Special handling for compass box to show visual elements
    compass_box = boxes[1]  # Compass & Scale Box
    compass_bottom = compass_box['bottom']
    compass_height = compass_box['height']
    
    # Simulate the visual elements added to compass box
    # Background pattern
    bg_rect = Rectangle((BOX_LEFT_POSITION + 0.01*BOX_WIDTH, compass_bottom + 0.01*compass_height), 
                       0.98*BOX_WIDTH, 0.98*compass_height, 
                       facecolor='#f8f8f8', edgecolor='none', alpha=0.5)
    ax.add_patch(bg_rect)
    
    # Corner markers
    corner_size = 0.03
    corners = [
        # Top-left
        [(BOX_LEFT_POSITION + 0.02*BOX_WIDTH, BOX_LEFT_POSITION + (0.02+corner_size)*BOX_WIDTH), 
         (compass_bottom + 0.98*compass_height, compass_bottom + 0.98*compass_height)],
        [(BOX_LEFT_POSITION + 0.02*BOX_WIDTH, BOX_LEFT_POSITION + 0.02*BOX_WIDTH), 
         (compass_bottom + 0.98*compass_height, compass_bottom + (0.98-corner_size)*compass_height)],
        # Top-right
        [(BOX_LEFT_POSITION + (0.98-corner_size)*BOX_WIDTH, BOX_LEFT_POSITION + 0.98*BOX_WIDTH), 
         (compass_bottom + 0.98*compass_height, compass_bottom + 0.98*compass_height)],
        [(BOX_LEFT_POSITION + 0.98*BOX_WIDTH, BOX_LEFT_POSITION + 0.98*BOX_WIDTH), 
         (compass_bottom + 0.98*compass_height, compass_bottom + (0.98-corner_size)*compass_height)],
        # Bottom-left
        [(BOX_LEFT_POSITION + 0.02*BOX_WIDTH, BOX_LEFT_POSITION + (0.02+corner_size)*BOX_WIDTH), 
         (compass_bottom + 0.02*compass_height, compass_bottom + 0.02*compass_height)],
        [(BOX_LEFT_POSITION + 0.02*BOX_WIDTH, BOX_LEFT_POSITION + 0.02*BOX_WIDTH), 
         (compass_bottom + 0.02*compass_height, compass_bottom + (0.02+corner_size)*compass_height)],
        # Bottom-right
        [(BOX_LEFT_POSITION + (0.98-corner_size)*BOX_WIDTH, BOX_LEFT_POSITION + 0.98*BOX_WIDTH), 
         (compass_bottom + 0.02*compass_height, compass_bottom + 0.02*compass_height)],
        [(BOX_LEFT_POSITION + 0.98*BOX_WIDTH, BOX_LEFT_POSITION + 0.98*BOX_WIDTH), 
         (compass_bottom + 0.02*compass_height, compass_bottom + (0.02+corner_size)*compass_height)]
    ]
    
    for corner in corners:
        ax.plot(corner[0], corner[1], 'k-', linewidth=2)
    
    # Separator line
    ax.plot([BOX_LEFT_POSITION + 0.02*BOX_WIDTH, BOX_LEFT_POSITION + 0.98*BOX_WIDTH], 
           [compass_bottom + 0.50*compass_height, compass_bottom + 0.50*compass_height], 
           'k-', linewidth=1, alpha=0.3)
    
    # Scale bar representation
    scale_width = 0.94 * BOX_WIDTH
    scale_height = 0.12 * compass_height
    scale_x = BOX_LEFT_POSITION + 0.03*BOX_WIDTH
    scale_y = compass_bottom + 0.20*compass_height
    
    # Draw scale bar segments
    segment_width = scale_width / 4
    for i in range(4):
        x_pos = scale_x + (i * segment_width)
        color = 'black' if i % 2 == 0 else 'white'
        edgecolor = 'black'
        
        scale_rect = Rectangle((x_pos, scale_y), segment_width, scale_height, 
                              facecolor=color, edgecolor=edgecolor, linewidth=0.5)
        ax.add_patch(scale_rect)
    
    # Add compass representation (circle)
    compass_center_x = BOX_LEFT_POSITION + 0.25*BOX_WIDTH
    compass_center_y = compass_bottom + 0.70*compass_height
    compass_radius = 0.08*BOX_WIDTH
    
    compass_circle = plt.Circle((compass_center_x, compass_center_y), compass_radius, 
                               facecolor='white', edgecolor='black', linewidth=1)
    ax.add_patch(compass_circle)
    
    # Add title and grid
    ax.set_title('Box Width Comparison - All Boxes Should Appear Same Width\n' + 
                'Compass Box Now Has Visual Elements Spanning Full Width', 
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X Position (0-1 scale)', fontsize=12)
    ax.set_ylabel('Y Position (0-1 scale)', fontsize=12)
    
    # Add measurement lines
    for box in boxes:
        # Left edge line
        ax.axvline(x=BOX_LEFT_POSITION, color='red', linestyle='--', alpha=0.5)
        # Right edge line
        ax.axvline(x=BOX_LEFT_POSITION + BOX_WIDTH, color='red', linestyle='--', alpha=0.5)
    
    # Add width annotation
    ax.annotate('', xy=(BOX_LEFT_POSITION, 0.05), xytext=(BOX_LEFT_POSITION + BOX_WIDTH, 0.05),
               arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(BOX_LEFT_POSITION + BOX_WIDTH/2, 0.03, f'Box Width: {BOX_WIDTH}', 
           ha='center', va='center', fontsize=12, fontweight='bold', color='red')
    
    plt.tight_layout()
    plt.savefig('Box_Width_Comparison_With_Visual_Elements.pdf', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Box comparison visualization created: Box_Width_Comparison_With_Visual_Elements.pdf")
    print("📊 All boxes have identical width (0.32) and left position (0.66)")
    print("🎯 Compass box now includes visual elements that span the full width:")
    print("   • Background pattern covering 98% of box area")
    print("   • Corner markers at all four corners")
    print("   • Horizontal separator line spanning 96% of width")
    print("   • Scale bar spanning 94% of box width")
    print("   • These elements should make the box appear as wide as others")

if __name__ == "__main__":
    create_box_comparison()