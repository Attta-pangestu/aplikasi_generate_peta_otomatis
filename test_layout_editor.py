#!/usr/bin/env python3
"""
Test script for the Map Layout Editor
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from map_layout_editor import MapLayoutEditor
import tkinter as tk
from tkinter import ttk

def main():
    """Test the map layout editor"""
    root = tk.Tk()
    app = MapLayoutEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()