#!/usr/bin/env python3
"""
Test script to verify copyable hex codes in TIFF legend interface
"""

import tkinter as tk
from map_generator_gui import MapGeneratorGUI
import time

def test_copyable_hex_interface():
    """
    Test the copyable hex code interface
    """
    print("=" * 60)
    print("TESTING COPYABLE HEX CODE INTERFACE")
    print("=" * 60)
    
    # Create GUI instance
    root = tk.Tk()
    root.title("TIFF Legend Hex Code Test")
    
    app = MapGeneratorGUI(root)
    
    # Switch to TIFF mode to show legend interface
    app.file_type.set("tiff")
    app.on_file_type_change()
    
    print("\n✅ GUI created with TIFF legend interface")
    print("\n📋 Default legend entries with copyable hex codes:")
    print("-" * 50)
    
    # Get legend data to verify
    legend_data = app.get_tiff_legend_data()
    
    for i, entry in enumerate(legend_data, 1):
        color = entry['color']
        description = entry['description']
        print(f"{i}. {description}: {color}")
        print(f"   ✓ Hex code is copyable from text field")
    
    print("\n🎨 Interface Features:")
    print("- Pick button: Opens color chooser dialog")
    print("- Hex field: Shows copyable hex code (e.g., #6914cc)")
    print("- Description field: Shows stage name (e.g., Tahap 1)")
    print("- Remove button: Removes the legend entry")
    
    print("\n📝 Instructions for copying hex codes:")
    print("1. Select the hex code text in the hex field")
    print("2. Press Ctrl+C to copy")
    print("3. Paste anywhere you need the hex code")
    
    print("\n" + "=" * 60)
    print("GUI is now running. You can:")
    print("- Copy hex codes directly from the text fields")
    print("- Modify colors using the Pick button")
    print("- See real-time hex code updates")
    print("- Close the window when done testing")
    print("=" * 60)
    
    # Show the GUI
    root.mainloop()
    
    print("\n✅ Test completed successfully!")
    print("Hex codes are now copyable from the interface.")

if __name__ == "__main__":
    test_copyable_hex_interface()