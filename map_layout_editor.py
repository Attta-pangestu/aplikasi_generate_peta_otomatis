#!/usr/bin/env python3
"""
Enhanced Map Layout Editor
Advanced visual editor for arranging map components with drag-and-drop functionality,
real-time preview, and comprehensive styling options.

Author: Generated for Tree Counting Project
Date: 2025
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, colorchooser
import os
import sys
from pathlib import Path
import threading
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import numpy as np
from professional_map_generator import ProfessionalMapGenerator
from map_elements import (
    TitleElement, LegendElement, BelitungOverviewElement,
    LogoInfoElement, CompassElement, ScaleBarElement
)

class MapLayoutEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Map Layout Editor - Professional Surveyor Style")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Variables
        self.file_type = tk.StringVar(value="shapefile")  # "shapefile" or "tiff"
        self.shapefile_path = tk.StringVar()
        self.tiff_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.map_title = tk.StringVar(value="PETA KEBUN 1 B\nPT. REBINMAS JAYA")
        self.logo_path = tk.StringVar()
        self.dpi_var = tk.IntVar(value=300)
        self.subdivision_vars = {}  # Dictionary to store subdivision checkbox variables
        self.available_subdivisions = []  # List of available subdivisions
        
        # TIFF legend variables
        self.tiff_legend_entries = []  # List of legend entries for TIFF
        self.tiff_legend_frame = None
        
        # Layout editor variables
        self.elements = {}  # Store layout elements
        self.selected_element = None
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.scale_factor = tk.DoubleVar(value=1.0)
        
        # Layout configuration matching professional_map_generator.py
        self.layout_config = {
            "main_map": {"x": 50, "y": 50, "width": 600, "height": 700},
            "title_box": {"x": 670, "y": 700, "width": 200, "height": 80},
            "legend_box": {"x": 670, "y": 420, "width": 200, "height": 150},
            "overview_box": {"x": 670, "y": 250, "width": 200, "height": 150},
            "logo_box": {"x": 670, "y": 50, "width": 200, "height": 100}
        }
        
        # Set default paths
        default_shapefile = "../merge_all_sub_divisi_map/merged_estates_HCV0_20250721_092606.shp"
        if os.path.exists(default_shapefile):
            self.shapefile_path.set(default_shapefile)
        
        # Updated default logo path
        default_logo = r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\rebinmas_logo.jpg"
        if os.path.exists(default_logo):
            self.logo_path.set(default_logo)
        else:
            # Fallback to local logo if full path doesn't exist
            fallback_logo = "rebinmas_logo.jpg"
            if os.path.exists(fallback_logo):
                self.logo_path.set(fallback_logo)
        
        self.output_path.set("Peta_Profesional_Sub_Divisi_Edited.pdf")
        
        self.setup_ui()
        
    def setup_ui(self):
        """
        Setup the user interface with layout editor
        """
        # Create main panes
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for controls
        self.left_frame = ttk.Frame(self.main_paned, width=300)
        self.main_paned.add(self.left_frame, weight=1)
        
        # Right panel for canvas
        self.right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_frame, weight=3)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.left_frame.columnconfigure(0, weight=1)
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(1, weight=1)
        
        # Setup left panel
        self.setup_left_panel()
        
        # Setup right panel (canvas)
        self.setup_canvas_panel()
        
        # Initial status
        self.log_message("Map Layout Editor ready...")
        self.log_message("Drag elements on the canvas to reposition them")
        self.log_message("Use the controls on the left to adjust element properties")
        
    def setup_left_panel(self):
        """
        Setup the left control panel
        """
        # Notebook for different control sections
        self.control_notebook = ttk.Notebook(self.left_frame)
        self.control_notebook.pack(fill=tk.BOTH, expand=True)
        
        # File settings tab
        self.file_tab = ttk.Frame(self.control_notebook)
        self.control_notebook.add(self.file_tab, text="File Settings")
        self.setup_file_tab()
        
        # Layout elements tab
        self.layout_tab = ttk.Frame(self.control_notebook)
        self.control_notebook.add(self.layout_tab, text="Layout Elements")
        self.setup_layout_tab()
        
        # Element properties tab
        self.properties_tab = ttk.Frame(self.control_notebook)
        self.control_notebook.add(self.properties_tab, text="Properties")
        self.setup_properties_tab()
        
        # Preview/Export tab
        self.preview_tab = ttk.Frame(self.control_notebook)
        self.control_notebook.add(self.preview_tab, text="Preview/Export")
        self.setup_preview_tab()
        
    def setup_file_tab(self):
        """
        Setup the file settings tab
        """
        # File type selection
        file_type_frame = ttk.LabelFrame(self.file_tab, text="Input File Type", padding="10")
        file_type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(file_type_frame, text="Shapefile (Polygon)", variable=self.file_type, 
                       value="shapefile", command=self.on_file_type_change).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(file_type_frame, text="TIFF (Raster Image)", variable=self.file_type, 
                       value="tiff", command=self.on_file_type_change).pack(anchor=tk.W, pady=2)
        
        # Shapefile input
        self.shapefile_label = ttk.Label(self.file_tab, text="Shapefile Input:")
        self.shapefile_label.pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        self.shapefile_frame = ttk.Frame(self.file_tab)
        self.shapefile_frame.pack(fill=tk.X, padx=5, pady=2)
        self.shapefile_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(self.shapefile_frame, textvariable=self.shapefile_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(self.shapefile_frame, text="Browse", command=self.browse_shapefile).pack(side=tk.RIGHT, padx=(2, 0))
        
        # TIFF input
        self.tiff_label = ttk.Label(self.file_tab, text="TIFF Input:")
        self.tiff_label.pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        self.tiff_frame = ttk.Frame(self.file_tab)
        self.tiff_frame.pack(fill=tk.X, padx=5, pady=2)
        self.tiff_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(self.tiff_frame, textvariable=self.tiff_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(self.tiff_frame, text="Browse", command=self.browse_tiff).pack(side=tk.RIGHT, padx=(2, 0))
        
        # Output file selection
        ttk.Label(self.file_tab, text="Output PDF:").pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        output_frame = ttk.Frame(self.file_tab)
        output_frame.pack(fill=tk.X, padx=5, pady=2)
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse", command=self.browse_output).pack(side=tk.RIGHT, padx=(2, 0))
        
        # Map title input
        ttk.Label(self.file_tab, text="Map Title:").pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        title_frame = ttk.Frame(self.file_tab)
        title_frame.pack(fill=tk.X, padx=5, pady=2)
        title_frame.columnconfigure(0, weight=1)
        
        title_entry = tk.Text(title_frame, height=2)
        title_entry.pack(fill=tk.X, expand=True)
        title_entry.insert("1.0", self.map_title.get())
        title_entry.bind('<KeyRelease>', lambda e: self.map_title.set(title_entry.get("1.0", "end-1c")))
        
        # Logo path input
        ttk.Label(self.file_tab, text="Logo Path:").pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        logo_frame = ttk.Frame(self.file_tab)
        logo_frame.pack(fill=tk.X, padx=5, pady=2)
        logo_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(logo_frame, textvariable=self.logo_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo).pack(side=tk.RIGHT, padx=(2, 0))
        
        # DPI selection
        ttk.Label(self.file_tab, text="Resolution (DPI):").pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        dpi_frame = ttk.Frame(self.file_tab)
        dpi_frame.pack(fill=tk.X, padx=5, pady=2)
        
        dpi_options = [150, 300, 600, 1200]
        for i, dpi in enumerate(dpi_options):
            ttk.Radiobutton(dpi_frame, text=f"{dpi} DPI", variable=self.dpi_var, 
                           value=dpi).pack(side=tk.LEFT, padx=5)
        
        # Initialize UI state
        self.on_file_type_change()
        
    def setup_layout_tab(self):
        """
        Setup the layout elements tab
        """
        # Elements list
        elements_frame = ttk.LabelFrame(self.layout_tab, text="Map Elements", padding="10")
        elements_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Listbox for elements
        self.elements_listbox = tk.Listbox(elements_frame)
        self.elements_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.elements_listbox.bind('<<ListboxSelect>>', self.on_element_select)
        
        # Buttons to add/remove elements
        btn_frame = ttk.Frame(elements_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Add Element", command=self.add_element).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Remove Element", command=self.remove_element).pack(side=tk.LEFT)
        
        # Load default elements
# Note: Default elements loading is deferred until properties panel is accessed
        # to ensure all UI variables are properly initialized
        # self.load_default_elements()  # Deferred until properties panel is accessed
        
    def setup_properties_tab(self):
        """
        Setup the element properties tab
        """
        # Properties frame
        self.properties_frame = ttk.LabelFrame(self.properties_tab, text="Element Properties", padding="10")
        self.properties_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Position controls
        pos_frame = ttk.Frame(self.properties_frame)
        pos_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(pos_frame, text="Position:").pack(anchor=tk.W)
        
        pos_controls = ttk.Frame(pos_frame)
        pos_controls.pack(fill=tk.X, pady=2)
        
        ttk.Label(pos_controls, text="X:").pack(side=tk.LEFT)
        self.pos_x_var = tk.DoubleVar()
        ttk.Entry(pos_controls, textvariable=self.pos_x_var, width=10).pack(side=tk.LEFT, padx=(2, 10))
        
        ttk.Label(pos_controls, text="Y:").pack(side=tk.LEFT)
        self.pos_y_var = tk.DoubleVar()
        ttk.Entry(pos_controls, textvariable=self.pos_y_var, width=10).pack(side=tk.LEFT, padx=(2, 10))
        
        ttk.Button(pos_controls, text="Apply", command=self.apply_position).pack(side=tk.LEFT)
        
        # Size controls
        size_frame = ttk.Frame(self.properties_frame)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="Size:").pack(anchor=tk.W)
        
        size_controls = ttk.Frame(size_frame)
        size_controls.pack(fill=tk.X, pady=2)
        
        ttk.Label(size_controls, text="Width:").pack(side=tk.LEFT)
        self.width_var = tk.DoubleVar()
        ttk.Entry(size_controls, textvariable=self.width_var, width=10).pack(side=tk.LEFT, padx=(2, 10))
        
        ttk.Label(size_controls, text="Height:").pack(side=tk.LEFT)
        self.height_var = tk.DoubleVar()
        ttk.Entry(size_controls, textvariable=self.height_var, width=10).pack(side=tk.LEFT, padx=(2, 10))
        
        ttk.Button(size_controls, text="Apply", command=self.apply_size).pack(side=tk.LEFT)
        
        # Scale controls
        scale_frame = ttk.Frame(self.properties_frame)
        scale_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(scale_frame, text="Scale:").pack(anchor=tk.W)
        
        scale_controls = ttk.Frame(scale_frame)
        scale_controls.pack(fill=tk.X, pady=2)
        
        ttk.Scale(scale_controls, from_=0.1, to=3.0, variable=self.scale_factor, 
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(scale_controls, text="Apply Scale", command=self.apply_scale).pack(side=tk.LEFT, padx=(5, 0))
        
        # Reset button
        ttk.Button(self.properties_frame, text="Reset to Default", 
                  command=self.reset_properties).pack(pady=(10, 0))
        
    def setup_preview_tab(self):
        """
        Setup the preview/export tab
        """
        # Preview controls
        preview_frame = ttk.LabelFrame(self.preview_tab, text="Preview Controls", padding="10")
        preview_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(preview_frame, text="Refresh Preview", 
                  command=self.refresh_preview).pack(fill=tk.X, pady=2)
        
        ttk.Button(preview_frame, text="Export Map", 
                  command=self.export_map).pack(fill=tk.X, pady=2)
        
# Save/Load layout buttons
        ttk.Button(preview_frame, text="Save Layout", 
                  command=self.save_layout).pack(fill=tk.X, pady=2)
        ttk.Button(preview_frame, text="Load Layout", 
                  command=self.load_layout).pack(fill=tk.X, pady=2)
        # Status text
        ttk.Label(self.preview_tab, text="Status:").pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        self.status_text = scrolledtext.ScrolledText(self.preview_tab, height=10)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_canvas_panel(self):
        """
        Setup the canvas panel for visual editing
        """
        # Canvas frame
        canvas_frame = ttk.Frame(self.right_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        # Canvas with scrollbars
        self.canvas_container = ttk.Frame(canvas_frame)
        self.canvas_container.grid(row=0, column=0, sticky="nsew")
        self.canvas_container.columnconfigure(0, weight=1)
        self.canvas_container.rowconfigure(0, weight=1)
        
        # Create canvas
        self.canvas = tk.Canvas(self.canvas_container, bg="white", scrollregion=(0, 0, 2000, 1500))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(self.canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-plus>", self.scale_up)
        self.root.bind("<Control-minus>", self.scale_down)
        self.root.bind("<Control-0>", self.reset_scale)
        
        # Toolbar
        toolbar = ttk.Frame(self.right_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(toolbar, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Reset View", command=self.reset_view).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Grid", command=self.toggle_grid).pack(side=tk.LEFT, padx=(0, 5))
        
        # Draw initial grid
        self.draw_grid()
        
    def draw_grid(self):
        """
        Draw grid on the canvas
        """
        # Clear existing grid
        self.canvas.delete("grid")
        
        # Draw grid lines
        for i in range(0, 2000, 50):
            # Vertical lines
            self.canvas.create_line(i, 0, i, 1500, fill="#e0e0e0", tags="grid")
            # Horizontal lines
            self.canvas.create_line(0, i, 2000, i, fill="#e0e0e0", tags="grid")
            
        # Draw axes
        self.canvas.create_line(0, 750, 2000, 750, fill="#000000", width=2, tags="grid")  # X-axis
        self.canvas.create_line(1000, 0, 1000, 1500, fill="#000000", width=2, tags="grid")  # Y-axis
        
    def toggle_grid(self):
        """
        Toggle grid visibility
        """
        if "grid" in self.canvas.gettags("all"):
            self.canvas.itemconfig("grid", state="hidden")
        else:
            self.canvas.itemconfig("grid", state="normal")
            
    def zoom_in(self):
        """
        Zoom in on the canvas
        """
        self.canvas.scale("all", 1000, 750, 1.2, 1.2)
        
    def zoom_out(self):
        """
        Zoom out on the canvas
        """
        self.canvas.scale("all", 1000, 750, 1/1.2, 1/1.2)
        
    def reset_view(self):
        """
        Reset canvas view
        """
        self.canvas.scale("all", 1000, 750, 1, 1)
        # Reset view by scrolling to top-left corner
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        
    def load_default_elements(self):
        """
        Load default map elements with proper layout configuration
        """
        # Map elements with their configuration
        element_configs = {
            "Main Map Area": self.layout_config["main_map"],
            "Title Box": self.layout_config["title_box"],
            "Legend Box": self.layout_config["legend_box"],
            "Belitung Overview": self.layout_config["overview_box"],
            "Logo and Info": self.layout_config["logo_box"]
        }
        
        # Clear existing elements
        self.elements.clear()
        self.elements_listbox.delete(0, tk.END)
        
        # Load elements with proper configuration
        for name, config in element_configs.items():
            self.elements[name] = {
                "x": config["x"],
                "y": config["y"],
                "width": config["width"],
                "height": config["height"],
                "visible": True
            }
            self.elements_listbox.insert(tk.END, name)
            
        # Select first element
        if self.elements_listbox.size() > 0:
            self.elements_listbox.selection_set(0)
            self.selected_element = self.elements_listbox.get(0)
            self.update_properties_panel()
        
        # Refresh preview to show elements
        self.refresh_preview()
        
    def on_element_select(self, event):
        """
        Handle element selection from listbox
        """
        selection = self.elements_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_element = self.elements_listbox.get(index)
            self.update_properties_panel()
            
    def update_properties_panel(self):
        """
        Update properties panel with selected element values
        """
        if self.selected_element and self.selected_element in self.elements:
            element = self.elements[self.selected_element]
            self.pos_x_var.set(element["x"])
            self.pos_y_var.set(element["y"])
            self.width_var.set(element["width"])
            self.height_var.set(element["height"])
            
    def apply_position(self):
        """
        Apply position changes to selected element
        """
        if self.selected_element:
            self.elements[self.selected_element]["x"] = self.pos_x_var.get()
            self.elements[self.selected_element]["y"] = self.pos_y_var.get()
            self.refresh_preview()
            
    def apply_size(self):
        """
        Apply size changes to selected element
        """
        if self.selected_element:
            self.elements[self.selected_element]["width"] = self.width_var.get()
            self.elements[self.selected_element]["height"] = self.height_var.get()
            self.refresh_preview()
            
    def apply_scale(self):
        """
        Apply scale factor to selected element
        """
        if self.selected_element:
            scale = self.scale_factor.get()
            # Store original dimensions
            original_width = self.elements[self.selected_element]["width"]
            original_height = self.elements[self.selected_element]["height"]
            
            # Apply scaling
            self.elements[self.selected_element]["width"] *= scale
            self.elements[self.selected_element]["height"] *= scale
            
            # Update UI
            self.width_var.set(self.elements[self.selected_element]["width"])
            self.height_var.set(self.elements[self.selected_element]["height"])
            
            # Refresh preview
            self.refresh_preview()
            
            # Reset scale factor to 1.0 for next scaling operation
            self.scale_factor.set(1.0)
            
    def scale_element_proportionally(self, element_name, scale_factor):
        """
        Scale an element proportionally while maintaining aspect ratio
        """
        if element_name in self.elements:
            element = self.elements[element_name]
            # Calculate aspect ratio
            aspect_ratio = element["width"] / element["height"]
            
            # Apply scaling while maintaining aspect ratio
            element["width"] *= scale_factor
            element["height"] = element["width"] / aspect_ratio
            
            # Update UI if this is the selected element
            if element_name == self.selected_element:
                self.width_var.set(element["width"])
                self.height_var.set(element["height"])
                
            return True
        return False
            
    def reset_properties(self):
        """
        Reset properties to default values
        """
        if self.selected_element:
            self.elements[self.selected_element]["x"] = 100
            self.elements[self.selected_element]["y"] = 100
            self.elements[self.selected_element]["width"] = 200
            self.elements[self.selected_element]["height"] = 150
            self.update_properties_panel()
            self.refresh_preview()
            
    def add_element(self):
        """
        Add a new element
        """
        element_name = f"New Element {len(self.elements) + 1}"
        self.elements[element_name] = {
            "x": 100,
            "y": 100,
            "width": 200,
            "height": 150,
            "visible": True
        }
        self.elements_listbox.insert(tk.END, element_name)
        
    def remove_element(self):
        """
        Remove selected element
        """
        selection = self.elements_listbox.curselection()
        if selection:
            index = selection[0]
            element_name = self.elements_listbox.get(index)
            del self.elements[element_name]
            self.elements_listbox.delete(index)
            
    def on_canvas_click(self, event):
        """
        Handle canvas click event
        """
        # Find clicked item
        item = self.canvas.find_closest(event.x, event.y)
        if item:
            self.drag_data["item"] = item[0]
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            # Select element in listbox
            tags = self.canvas.gettags(item[0])
            for tag in tags:
                if tag in self.elements:
                    idx = self.elements_listbox.get(0, tk.END).index(tag)
                    self.elements_listbox.selection_clear(0, tk.END)
                    self.elements_listbox.selection_set(idx)
                    self.selected_element = tag
                    self.update_properties_panel()
                    break
                    
    def on_canvas_drag(self, event):
        """
        Handle canvas drag event
        """
        if self.drag_data["item"]:
            # Calculate the delta
            delta_x = event.x - self.drag_data["x"]
            delta_y = event.y - self.drag_data["y"]
            
            # Move the item
            self.canvas.move(self.drag_data["item"], delta_x, delta_y)
            
            # Update drag data
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            # Update element position
            if self.selected_element:
                self.elements[self.selected_element]["x"] += delta_x
                self.elements[self.selected_element]["y"] += delta_y
                self.pos_x_var.set(self.elements[self.selected_element]["x"])
                self.pos_y_var.set(self.elements[self.selected_element]["y"])
                
    def on_canvas_release(self, event):
        """
        Handle canvas release event
        """
        self.drag_data["item"] = None
        
    def refresh_preview(self):
        """
        Refresh the preview canvas with current layout
        """
        # Clear canvas
        self.canvas.delete("element")
        
        # Draw elements with appropriate styling
        for name, element in self.elements.items():
            if element["visible"]:
                x, y, w, h = element["x"], element["y"], element["width"], element["height"]
                
                # Draw different elements with appropriate styling
                if name == "Main Map Area":
                    # Main map with grid pattern
                    self.canvas.create_rectangle(x, y, x+w, y+h, fill="#f0f8ff", outline="#1E90FF", width=2, tags=("element", name))
                    # Draw grid lines
                    for i in range(0, int(w), 20):
                        self.canvas.create_line(x+i, y, x+i, y+h, fill="#d0e0ff", tags=("element", name))
                    for i in range(0, int(h), 20):
                        self.canvas.create_line(x, y+i, x+w, y+i, fill="#d0e0ff", tags=("element", name))
                    # Draw label
                    self.canvas.create_text(x+w/2, y+20, text="Main Map", font=("Arial", 10, "bold"), fill="#1E90FF", tags=("element", name))
                elif name == "Title Box":
                    # Title box with underline
                    self.canvas.create_rectangle(x, y, x+w, y+h, fill="#fffacd", outline="#ffd700", width=2, tags=("element", name))
                    self.canvas.create_line(x+10, y+30, x+w-10, y+30, fill="#000000", tags=("element", name))
                    self.canvas.create_text(x+w/2, y+15, text="Title Box", font=("Arial", 10, "bold"), fill="#000000", tags=("element", name))
                elif name == "Legend Box":
                    # Legend box with color patches
                    self.canvas.create_rectangle(x, y, x+w, y+h, fill="#e0ffff", outline="#20b2aa", width=2, tags=("element", name))
                    # Draw sample legend items
                    for i in range(3):
                        y_pos = y + 30 + i*30
                        self.canvas.create_rectangle(x+10, y_pos-8, x+25, y_pos+7, fill=["#98FB98", "#F4A460", "#FFB6C1"][i], outline="#000000", tags=("element", name))
                        self.canvas.create_text(x+35, y_pos, text=f"Legend Item {i+1}", anchor="w", font=("Arial", 8), tags=("element", name))
                    self.canvas.create_text(x+w/2, y+15, text="Legend", font=("Arial", 10, "bold"), fill="#000000", tags=("element", name))
                elif name == "Belitung Overview":
                    # Overview map with island shape
                    self.canvas.create_rectangle(x, y, x+w, y+h, fill="#f5f5dc", outline="#daa520", width=2, tags=("element", name))
                    # Draw simple island shape
                    self.canvas.create_oval(x+50, y+30, x+w-50, y+h-30, fill="#90ee90", outline="#006400", tags=("element", name))
                    self.canvas.create_text(x+w/2, y+15, text="Overview Map", font=("Arial", 10, "bold"), fill="#000000", tags=("element", name))
                elif name == "Logo and Info":
                    # Logo box with company info
                    self.canvas.create_rectangle(x, y, x+w, y+h, fill="#ffe4e1", outline="#ff6347", width=2, tags=("element", name))
                    # Draw logo placeholder
                    self.canvas.create_rectangle(x+20, y+20, x+80, y+60, fill="#1e90ff", outline="#4169e1", tags=("element", name))
                    self.canvas.create_text(x+50, y+40, text="Logo", fill="#ffffff", font=("Arial", 8), tags=("element", name))
                    self.canvas.create_text(x+w/2, y+70, text="Company Info", font=("Arial", 8), fill="#000000", tags=("element", name))
                    self.canvas.create_text(x+w/2, y+15, text="Logo & Info", font=("Arial", 10, "bold"), fill="#000000", tags=("element", name))
                else:
                    # Default element styling
                    self.canvas.create_rectangle(x, y, x+w, y+h, fill="#ADD8E6", outline="#1E90FF", width=2, tags=("element", name))
                    self.canvas.create_text(x+w/2, y+h/2, text=name, fill="#000000", font=("Arial", 8), tags=("element", name))
                
    def export_map(self):
        """
        Export the final map with current layout
        """
        try:
            # Create map generator with current settings
            file_type = self.file_type.get()
            
            if file_type == "shapefile":
                if not self.shapefile_path.get():
                    messagebox.showerror("Error", "Please select a shapefile")
                    return
                    
                # Get selected subdivisions
                selected_subdivisions = self.get_selected_subdivisions()
                if not selected_subdivisions:
                    messagebox.showerror("Error", "Please select at least one subdivision to display")
                    return
                    
                map_gen = ProfessionalMapGenerator(
                    self.shapefile_path.get(),
                    selected_subdivisions=selected_subdivisions,
                    map_title=self.map_title.get(),
                    logo_path=self.logo_path.get() if self.logo_path.get() else None
                )
                
                # Load data
                if not map_gen.load_data():
                    messagebox.showerror("Error", "Failed to load shapefile data")
                    return
                    
            elif file_type == "tiff":
                if not self.tiff_path.get():
                    messagebox.showerror("Error", "Please select a TIFF file")
                    return
                    
                # Get legend data
                legend_data = self.get_tiff_legend_data()
                if not legend_data:
                    messagebox.showerror("Error", "Please add at least one legend entry for TIFF map")
                    return
                    
                map_gen = ProfessionalMapGenerator(
                    self.tiff_path.get(),
                    file_type="tiff",
                    tiff_legend=legend_data,
                    map_title=self.map_title.get(),
                    logo_path=self.logo_path.get() if self.logo_path.get() else None
                )
                
                # Load TIFF data
                if not map_gen.load_tiff_data():
                    messagebox.showerror("Error", "Failed to load TIFF data")
                    return
            
            # Generate map with custom layout
            output_path = self.output_path.get() or "Peta_Profesional_Sub_Divisi_Edited.pdf"
            
            # Update map generator with custom layout configuration
            if hasattr(map_gen, 'BOX_WIDTH'):
                # Update layout constants based on our configuration
                map_gen.BOX_WIDTH = 0.32
                map_gen.BOX_LEFT_POSITION = 0.66
                map_gen.MAIN_MAP_WIDTH = 0.60
                map_gen.MAIN_MAP_LEFT = 0.05
                
            success = map_gen.create_professional_map(
                output_path=output_path,
                dpi=self.dpi_var.get()
            )
            
            if success:
                messagebox.showinfo("Success", f"Map exported successfully to:\n{output_path}")
                self.log_message(f"Map exported to: {output_path}")
            else:
                messagebox.showerror("Error", "Failed to export map")
                self.log_message("ERROR: Failed to export map")
                
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def get_selected_subdivisions(self):
        """
        Get list of selected subdivisions (placeholder)
        """
        # In a real implementation, this would get actual selections
        return ['SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR KANDIS', 'SUB DIVISI AIR RAYA']
        
    def get_tiff_legend_data(self):
        """
        Get TIFF legend data (placeholder)
        """
        # In a real implementation, this would get actual legend data
        return [
            {"color": "#228B22", "description": "Palm Oil Plantation"},
            {"color": "#8B4513", "description": "Bare Soil"},
            {"color": "#4169E1", "description": "Water Bodies"},
            {"color": "#32CD32", "description": "Natural Forest"}
        ]
        
    def log_message(self, message):
        """
        Add message to status log
        """
        if hasattr(self, 'status_text') and self.status_text:
            self.status_text.insert(tk.END, f"{message}\n")
            self.status_text.see(tk.END)
            self.root.update_idletasks()
            
    def browse_shapefile(self):
        """
        Browse for shapefile input
        """
        filename = filedialog.askopenfilename(
            title="Select Shapefile",
            filetypes=[("Shapefiles", "*.shp"), ("All files", "*.*")]
        )
        if filename:
            self.shapefile_path.set(filename)
            self.log_message(f"Selected shapefile: {filename}")
            
    def browse_tiff(self):
        """
        Browse for TIFF file
        """
        filename = filedialog.askopenfilename(
            title="Select TIFF File",
            filetypes=[("TIFF files", "*.tif *.tiff"), ("All files", "*.*")]
        )
        if filename:
            self.tiff_path.set(filename)
            self.log_message(f"Selected TIFF: {filename}")
            
    def browse_output(self):
        """
        Browse for output file
        """
        filename = filedialog.asksaveasfilename(
            title="Save Map As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            self.log_message(f"Output file: {filename}")
            
    def browse_logo(self):
        """
        Browse for logo file
        """
        filename = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.logo_path.set(filename)
            self.log_message(f"Selected logo: {filename}")
            
    def on_file_type_change(self):
        """
        Handle file type selection change
        """
        file_type = self.file_type.get()
        
        if file_type == "shapefile":
            # Show shapefile elements
            self.shapefile_label.pack()
            self.shapefile_frame.pack()
            
            # Hide TIFF elements
            self.tiff_label.pack_forget()
            self.tiff_frame.pack_forget()
            
            self.log_message("Switched to Shapefile mode - polygon-based mapping")
            
        elif file_type == "tiff":
            # Hide shapefile elements
            self.shapefile_label.pack_forget()
            self.shapefile_frame.pack_forget()
            
            # Show TIFF elements
            self.tiff_label.pack()
            self.tiff_frame.pack()
            
            self.log_message("Switched to TIFF mode - raster image mapping with custom legend")

    def scale_up(self, event=None):
        """
        Scale selected element up by 10%
        """
        if self.selected_element:
            self.scale_element_proportionally(self.selected_element, 1.1)
            self.refresh_preview()

    def scale_down(self, event=None):
        """
        Scale selected element down by 10%
        """
        if self.selected_element:
            self.scale_element_proportionally(self.selected_element, 0.9)
            self.refresh_preview()

    def reset_scale(self, event=None):
        """
        Reset scale of selected element to default
        """
        if self.selected_element:
            # Reset to default dimensions from layout_config
            element_name = self.selected_element
            element_key = None
            
            # Map element names to layout config keys
            name_mapping = {
                "Main Map Area": "main_map",
                "Title Box": "title_box",
                "Legend Box": "legend_box",
                "Belitung Overview": "overview_box",
                "Logo and Info": "logo_box"
            }
            
            if element_name in name_mapping:
                element_key = name_mapping[element_name]
                
            if element_key and element_key in self.layout_config:
                config = self.layout_config[element_key]
                self.elements[element_name]["width"] = config["width"]
                self.elements[element_name]["height"] = config["height"]
                
                # Update UI
                self.width_var.set(config["width"])
                self.height_var.set(config["height"])
                self.refresh_preview()
                
    def save_layout(self):
        """
        Save current layout configuration to a file
        """
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Layout",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                layout_data = {
                    "elements": self.elements,
                    "layout_config": self.layout_config,
                    "file_type": self.file_type.get(),
                    "shapefile_path": self.shapefile_path.get(),
                    "tiff_path": self.tiff_path.get(),
                    "output_path": self.output_path.get(),
                    "map_title": self.map_title.get(),
                    "logo_path": self.logo_path.get(),
                    "dpi": self.dpi_var.get()
                }
                
                with open(filename, 'w') as f:
                    json.dump(layout_data, f, indent=2)
                    
                self.log_message(f"Layout saved to: {filename}")
                messagebox.showinfo("Success", f"Layout saved successfully to:\n{filename}")
        except Exception as e:
            error_msg = f"ERROR: Failed to save layout: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def load_layout(self):
        """
        Load layout configuration from a file
        """
        try:
            filename = filedialog.askopenfilename(
                title="Load Layout",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'r') as f:
                    layout_data = json.load(f)
                    
                # Restore layout data
                if "elements" in layout_data:
                    self.elements = layout_data["elements"]
                    
                if "layout_config" in layout_data:
                    self.layout_config = layout_data["layout_config"]
                    
                # Restore UI variables
                if "file_type" in layout_data:
                    self.file_type.set(layout_data["file_type"])
                    
                if "shapefile_path" in layout_data:
                    self.shapefile_path.set(layout_data["shapefile_path"])
                    
                if "tiff_path" in layout_data:
                    self.tiff_path.set(layout_data["tiff_path"])
                    
                if "output_path" in layout_data:
                    self.output_path.set(layout_data["output_path"])
                    
                if "map_title" in layout_data:
                    self.map_title.set(layout_data["map_title"])
                    
                if "logo_path" in layout_data:
                    self.logo_path.set(layout_data["logo_path"])
                    
                if "dpi" in layout_data:
                    self.dpi_var.set(layout_data["dpi"])
                    
                # Update UI
                self.on_file_type_change()
                # self.load_default_elements()  # Deferred until properties panel is accessed
                self.refresh_preview()
                    
                self.log_message(f"Layout loaded from: {filename}")
                messagebox.showinfo("Success", f"Layout loaded successfully from:\n{filename}")
        except Exception as e:
            error_msg = f"ERROR: Failed to load layout: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
            
def main():
    """
    Main function to run the layout editor
    """
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    app = MapLayoutEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()