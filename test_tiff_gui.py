#!/usr/bin/env python3
"""
Test script to verify TIFF GUI functionality
"""

import tkinter as tk
from map_generator_gui import MapGeneratorGUI

def test_gui():
    """
    Test the updated GUI with TIFF support
    """
    root = tk.Tk()
    app = MapGeneratorGUI(root)
    
    print("GUI initialized successfully!")
    print(f"File type options: {app.file_type.get()}")
    print(f"Default TIFF legend entries: {len(app.tiff_legend_entries)}")
    
    # Test switching to TIFF mode
    app.file_type.set("tiff")
    app.on_file_type_change()
    print("Switched to TIFF mode successfully!")
    
    # Test legend data retrieval
    legend_data = app.get_tiff_legend_data()
    print(f"Legend data entries: {len(legend_data)}")
    for i, entry in enumerate(legend_data, 1):
        print(f"  {i}. {entry['color']} - {entry['description']}")
    
    print("\nTIFF GUI functionality test completed successfully!")
    root.destroy()

if __name__ == "__main__":
    test_gui()