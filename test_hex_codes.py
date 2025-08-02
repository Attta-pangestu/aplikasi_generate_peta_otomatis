#!/usr/bin/env python3
"""
Test script to display the exact hex codes for TIFF legend colors
so user can copy them easily
"""

import tkinter as tk
from map_generator_gui import MapGeneratorGUI

def display_hex_codes():
    """
    Display the current hex codes for easy copying
    """
    print("=" * 60)
    print("CURRENT TIFF LEGEND HEX CODES")
    print("=" * 60)
    
    # Create GUI instance to get default legend
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    app = MapGeneratorGUI(root)
    
    # Get legend data
    legend_data = app.get_tiff_legend_data()
    
    print("\nHex codes you can copy:")
    print("-" * 30)
    
    for i, entry in enumerate(legend_data[:4]):  # Only show first 4 entries
        color = entry['color']
        description = entry['description']
        print(f"{description}: {color}")
        print(f"  Copy this: {color}")
        print()
    
    print("\nFor easy copying:")
    print("-" * 20)
    for entry in legend_data[:4]:
        print(entry['color'])
    
    root.destroy()
    
    print("\n" + "=" * 60)
    print("You can now copy these hex codes exactly as shown")
    print("=" * 60)

if __name__ == "__main__":
    display_hex_codes()