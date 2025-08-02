#!/usr/bin/env python3
"""
Advanced Map Layout Builder
Provides a comprehensive GUI for customizing map element positions, sizes, and styles
with drag-and-drop functionality and real-time preview.

Author: Generated for Tree Counting Project
Date: 2025
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import numpy as np
from professional_map_generator import ProfessionalMapGenerator
from map_elements import (
    TitleElement, LegendElement, BelitungOverviewElement,
    LogoInfoElement, CompassElement, ScaleBarElement
)

class MapLayoutBuilder:
    """
    Advanced layout builder for map elements with drag-and-drop interface
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Map Layout Builder - Professional Surveyor Style")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Layout configuration matching professional_map_generator.py defaults
        self.default_layout = {
            "main_map": {
                "position": [0.05, 0.05, 0.60, 0.93],  # [left, bottom, width, height]
                "border": True,
                "border_color": "black",
                "border_width": 2
            },
            "title": {
                "position": [0.66, 0.88, 0.32, 0.10],
                "text": "PETA KEBUN 1 B\nPT. REBINMAS JAYA",
                "font_size": 14,
                "font_weight": "bold",
                "text_color": "black",
                "background_color": "white",
                "border": True
            },
            "legend": {
                "position": [0.66, 0.38, 0.32, 0.18],
                "title": "LEGENDA",
                "title_font_size": 12,
                "item_font_size": 10,
                "background_color": "white",
                "border": True
            },
            "belitung_overview": {
                "position": [0.66, 0.58, 0.32, 0.28],
                "title": "LOKASI DALAM BELITUNG",
                "title_font_size": 10,
                "background_color": "white",
                "border": True
            },
            "logo_info": {
                "position": [0.66, 0.02, 0.32, 0.14],
                "company_name": "PT. REBINMAS JAYA",
                "production_info": "Diproduksi untuk : PT. REBINMAS JAYA",
                "program_info": "Program: IT Rebinmas | Data: Surveyor RMJ",
                "generated_date": "Generated: July 2025",
                "font_size": 8,
                "background_color": "white",
                "border": True
            },
            "compass": {
                "position": "overlay",  # Overlay on main map
                "main_map_position": [0.85, 0.85],  # Relative to main map
                "size": 0.08,
                "visible": True
            },
            "scale_bar": {
                "position": "overlay",  # Overlay on main map
                "main_map_position": [0.05, 0.05],  # Relative to main map
                "visible": True,
                "units": "meters"
            }
        }
        
        # Current layout (copy of default)
        self.current_layout = self.default_layout.copy()
        
        # UI Variables
        self.selected_element = tk.StringVar(value="main_map")
        self.preview_canvas = None
        self.preview_figure = None
        self.element_rectangles = {}  # Store visual representations
        
        # File paths
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar(value="custom_layout_map.pdf")
        self.logo_file = tk.StringVar()
        
        # Map generator instance
        self.map_generator = None
        
        self.setup_ui()
        self.load_default_paths()
        self.refresh_preview()
        
        # Bind keyboard shortcuts
        self.root.bind('<Escape>', lambda e: self.cancel_element_creation())
        self.root.bind('<Delete>', lambda e: self.delete_selected_element())
        self.root.focus_set()  # Make sure root can receive key events
    
    def setup_ui(self):
        """
        Setup the user interface with three main panels
        """
        # Create main container with three panels
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Element list and properties
        self.left_panel = ttk.Frame(self.main_container, width=300)
        self.main_container.add(self.left_panel, weight=1)
        
        # Center panel - Layout preview
        self.center_panel = ttk.Frame(self.main_container, width=600)
        self.main_container.add(self.center_panel, weight=2)
        
        # Right panel - Style properties
        self.right_panel = ttk.Frame(self.main_container, width=300)
        self.main_container.add(self.right_panel, weight=1)
        
        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()
    
    def setup_left_panel(self):
        """
        Setup left panel with element list and basic controls
        """
        # File selection section
        file_frame = ttk.LabelFrame(self.left_panel, text="File Settings", padding=10)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_frame, text="Input File:").pack(anchor=tk.W)
        input_frame = ttk.Frame(file_frame)
        input_frame.pack(fill=tk.X, pady=2)
        ttk.Entry(input_frame, textvariable=self.input_file).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="Browse", command=self.browse_input_file).pack(side=tk.RIGHT)
        
        ttk.Label(file_frame, text="Logo File:").pack(anchor=tk.W, pady=(10,0))
        logo_frame = ttk.Frame(file_frame)
        logo_frame.pack(fill=tk.X, pady=2)
        ttk.Entry(logo_frame, textvariable=self.logo_file).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo_file).pack(side=tk.RIGHT)
        
        ttk.Label(file_frame, text="Output File:").pack(anchor=tk.W, pady=(10,0))
        output_frame = ttk.Frame(file_frame)
        output_frame.pack(fill=tk.X, pady=2)
        ttk.Entry(output_frame, textvariable=self.output_file).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_file).pack(side=tk.RIGHT)
        
        # Element selection section
        element_frame = ttk.LabelFrame(self.left_panel, text="Map Elements", padding=10)
        element_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Element listbox
        ttk.Label(element_frame, text="Select Element to Edit:").pack(anchor=tk.W)
        
        element_list = ttk.Combobox(element_frame, textvariable=self.selected_element, 
                                   values=list(self.current_layout.keys()), 
                                   state="readonly")
        element_list.pack(fill=tk.X, pady=5)
        element_list.bind('<<ComboboxSelected>>', self.on_element_selected)
        
        # Position controls
        pos_frame = ttk.LabelFrame(element_frame, text="Position & Size", padding=5)
        pos_frame.pack(fill=tk.X, pady=10)
        
        # Position entries
        self.pos_vars = {
            'left': tk.DoubleVar(),
            'bottom': tk.DoubleVar(),
            'width': tk.DoubleVar(),
            'height': tk.DoubleVar()
        }
        
        for i, (label, var) in enumerate(self.pos_vars.items()):
            row = ttk.Frame(pos_frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{label.title()}:", width=8).pack(side=tk.LEFT)
            entry = ttk.Entry(row, textvariable=var, width=10)
            entry.pack(side=tk.LEFT, padx=5)
            entry.bind('<Return>', self.update_element_position)
        
        # Quick action buttons
        action_frame = ttk.Frame(element_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Apply Position", 
                  command=self.update_element_position).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Reset to Default", 
                  command=self.reset_element_to_default).pack(side=tk.RIGHT, padx=2)
        
        # Element creation section
        creation_frame = ttk.LabelFrame(element_frame, text="Add New Elements", padding=5)
        creation_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(creation_frame, text="Click and drag on canvas to add:").pack(anchor=tk.W)
        
        creation_buttons = ttk.Frame(creation_frame)
        creation_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(creation_buttons, text="Add Compass", 
                  command=lambda: self.start_element_creation('compass')).pack(side=tk.LEFT, padx=2)
        ttk.Button(creation_buttons, text="Add Scale Bar", 
                  command=lambda: self.start_element_creation('scale_bar')).pack(side=tk.LEFT, padx=2)
        ttk.Button(creation_buttons, text="Add Text Box", 
                  command=lambda: self.start_element_creation('text_box')).pack(side=tk.LEFT, padx=2)
        
        # Cancel creation button
        cancel_frame = ttk.Frame(creation_frame)
        cancel_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(cancel_frame, text="Cancel Creation (ESC)", 
                  command=self.cancel_element_creation).pack(side=tk.RIGHT, padx=2)
        
        # Creation mode indicator
        self.creation_mode_label = ttk.Label(creation_frame, text="", foreground="red")
        self.creation_mode_label.pack(anchor=tk.W, pady=2)
        
        # Layout management
        layout_frame = ttk.LabelFrame(self.left_panel, text="Layout Management", padding=10)
        layout_frame.pack(fill=tk.X, padx=5, pady=5)
        
        layout_buttons = ttk.Frame(layout_frame)
        layout_buttons.pack(fill=tk.X)
        
        ttk.Button(layout_buttons, text="Save Layout", 
                  command=self.save_layout).pack(side=tk.LEFT, padx=2)
        ttk.Button(layout_buttons, text="Load Layout", 
                  command=self.load_layout).pack(side=tk.LEFT, padx=2)
        ttk.Button(layout_buttons, text="Reset All", 
                  command=self.reset_all_to_default).pack(side=tk.RIGHT, padx=2)
    
    def setup_center_panel(self):
        """
        Setup center panel with layout preview canvas
        """
        # Preview controls
        control_frame = ttk.Frame(self.center_panel)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Layout Preview", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="Refresh Preview", 
                  command=self.refresh_preview).pack(side=tk.RIGHT, padx=2)
        ttk.Button(control_frame, text="Generate Map", 
                  command=self.generate_final_map).pack(side=tk.RIGHT, padx=2)
        
        # Preview canvas
        canvas_frame = ttk.Frame(self.center_panel)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure for preview
        self.preview_figure = plt.Figure(figsize=(8, 6), dpi=100)
        self.preview_canvas = FigureCanvasTkAgg(self.preview_figure, canvas_frame)
        self.preview_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events for drag and drop and element creation
        self.preview_canvas.mpl_connect('button_press_event', self.on_canvas_click)
        self.preview_canvas.mpl_connect('motion_notify_event', self.on_canvas_drag)
        self.preview_canvas.mpl_connect('button_release_event', self.on_canvas_release)
        
        # Drag state
        self.drag_state = {
            'active': False,
            'element': None,
            'start_pos': None,
            'offset': None
        }
        
        # Element creation state
        self.creation_state = {
            'active': False,
            'element_type': None,
            'start_pos': None,
            'current_rect': None
        }
    
    def setup_right_panel(self):
        """
        Setup right panel with detailed style properties
        """
        # Style properties section
        style_frame = ttk.LabelFrame(self.right_panel, text="Style Properties", padding=10)
        style_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create scrollable frame for properties
        canvas = tk.Canvas(style_frame)
        scrollbar = ttk.Scrollbar(style_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Style variables (will be populated based on selected element)
        self.style_vars = {}
        
        self.update_style_panel()
    
    def on_element_selected(self, event=None):
        """
        Handle element selection change
        """
        element_name = self.selected_element.get()
        if element_name in self.current_layout:
            element_config = self.current_layout[element_name]
            
            # Update position variables
            if 'position' in element_config and isinstance(element_config['position'], list):
                pos = element_config['position']
                self.pos_vars['left'].set(pos[0])
                self.pos_vars['bottom'].set(pos[1])
                self.pos_vars['width'].set(pos[2])
                self.pos_vars['height'].set(pos[3])
            
            # Update style panel
            self.update_style_panel()
            
            # Highlight selected element in preview
            self.highlight_selected_element()
    
    def update_style_panel(self):
        """
        Update the style properties panel based on selected element
        """
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        element_name = self.selected_element.get()
        if element_name not in self.current_layout:
            return
        
        element_config = self.current_layout[element_name]
        
        # Create style controls based on element type
        row = 0
        
        # Common properties
        if 'background_color' in element_config:
            self.create_color_control("Background Color", 'background_color', element_config, row)
            row += 1
        
        if 'border' in element_config:
            self.create_boolean_control("Show Border", 'border', element_config, row)
            row += 1
        
        if 'border_color' in element_config:
            self.create_color_control("Border Color", 'border_color', element_config, row)
            row += 1
        
        if 'border_width' in element_config:
            self.create_number_control("Border Width", 'border_width', element_config, row)
            row += 1
        
        # Element-specific properties
        if element_name == 'title':
            self.create_text_control("Title Text", 'text', element_config, row)
            row += 1
            self.create_number_control("Font Size", 'font_size', element_config, row)
            row += 1
            self.create_color_control("Text Color", 'text_color', element_config, row)
            row += 1
        
        elif element_name == 'legend':
            self.create_text_control("Legend Title", 'title', element_config, row)
            row += 1
            self.create_number_control("Title Font Size", 'title_font_size', element_config, row)
            row += 1
            self.create_number_control("Item Font Size", 'item_font_size', element_config, row)
            row += 1
        
        elif element_name == 'logo_info':
            self.create_text_control("Company Name", 'company_name', element_config, row)
            row += 1
            self.create_text_control("Production Info", 'production_info', element_config, row)
            row += 1
            self.create_text_control("Program Info", 'program_info', element_config, row)
            row += 1
            self.create_number_control("Font Size", 'font_size', element_config, row)
            row += 1
        
        elif element_name == 'compass' or element_name.startswith('compass_'):
            self.create_boolean_control("Visible", 'visible', element_config, row)
            row += 1
            self.create_number_control("Size", 'size', element_config, row)
            row += 1
            if 'style' in element_config:
                self.create_text_control("Style", 'style', element_config, row)
                row += 1
        
        elif element_name == 'scale_bar' or element_name.startswith('scale_bar_'):
            self.create_boolean_control("Visible", 'visible', element_config, row)
            row += 1
            self.create_text_control("Units", 'units', element_config, row)
            row += 1
            if 'style' in element_config:
                self.create_text_control("Style", 'style', element_config, row)
                row += 1
        
        elif element_name.startswith('text_box'):
            self.create_text_control("Text Content", 'text', element_config, row)
            row += 1
            self.create_number_control("Font Size", 'font_size', element_config, row)
            row += 1
            self.create_text_control("Font Weight", 'font_weight', element_config, row)
            row += 1
            self.create_color_control("Text Color", 'text_color', element_config, row)
            row += 1
            if 'border_color' in element_config:
                self.create_color_control("Border Color", 'border_color', element_config, row)
                row += 1
            if 'border_width' in element_config:
                self.create_number_control("Border Width", 'border_width', element_config, row)
                row += 1
    
    def create_text_control(self, label, key, config, row):
        """
        Create a text input control
        """
        frame = ttk.Frame(self.scrollable_frame)
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        
        ttk.Label(frame, text=f"{label}:").pack(anchor=tk.W)
        
        var = tk.StringVar(value=config.get(key, ""))
        entry = ttk.Entry(frame, textvariable=var)
        entry.pack(fill=tk.X, pady=2)
        
        # Store variable for later access
        self.style_vars[key] = var
        
        # Bind change event
        var.trace('w', lambda *args: self.update_element_style(key, var.get()))
    
    def create_number_control(self, label, key, config, row):
        """
        Create a number input control
        """
        frame = ttk.Frame(self.scrollable_frame)
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        
        ttk.Label(frame, text=f"{label}:").pack(anchor=tk.W)
        
        var = tk.DoubleVar(value=config.get(key, 0))
        spinbox = ttk.Spinbox(frame, textvariable=var, from_=0, to=100, increment=0.1)
        spinbox.pack(fill=tk.X, pady=2)
        
        # Store variable for later access
        self.style_vars[key] = var
        
        # Bind change event
        var.trace('w', lambda *args: self.update_element_style(key, var.get()))
    
    def create_color_control(self, label, key, config, row):
        """
        Create a color picker control
        """
        frame = ttk.Frame(self.scrollable_frame)
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        
        ttk.Label(frame, text=f"{label}:").pack(anchor=tk.W)
        
        color_frame = ttk.Frame(frame)
        color_frame.pack(fill=tk.X, pady=2)
        
        var = tk.StringVar(value=config.get(key, "white"))
        entry = ttk.Entry(color_frame, textvariable=var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def choose_color():
            color = colorchooser.askcolor(color=var.get())[1]
            if color:
                var.set(color)
        
        ttk.Button(color_frame, text="Pick", command=choose_color).pack(side=tk.RIGHT)
        
        # Store variable for later access
        self.style_vars[key] = var
        
        # Bind change event
        var.trace('w', lambda *args: self.update_element_style(key, var.get()))
    
    def create_boolean_control(self, label, key, config, row):
        """
        Create a boolean checkbox control
        """
        frame = ttk.Frame(self.scrollable_frame)
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        
        var = tk.BooleanVar(value=config.get(key, True))
        checkbox = ttk.Checkbutton(frame, text=label, variable=var)
        checkbox.pack(anchor=tk.W)
        
        # Store variable for later access
        self.style_vars[key] = var
        
        # Bind change event
        var.trace('w', lambda *args: self.update_element_style(key, var.get()))
    
    def update_element_style(self, key, value):
        """
        Update element style property
        """
        element_name = self.selected_element.get()
        if element_name in self.current_layout:
            self.current_layout[element_name][key] = value
            self.refresh_preview()
    
    def update_element_position(self, event=None):
        """
        Update element position from input fields
        """
        element_name = self.selected_element.get()
        if element_name in self.current_layout:
            new_position = [
                self.pos_vars['left'].get(),
                self.pos_vars['bottom'].get(),
                self.pos_vars['width'].get(),
                self.pos_vars['height'].get()
            ]
            self.current_layout[element_name]['position'] = new_position
            self.refresh_preview()
    
    def reset_element_to_default(self):
        """
        Reset selected element to default configuration
        """
        element_name = self.selected_element.get()
        if element_name in self.default_layout:
            self.current_layout[element_name] = self.default_layout[element_name].copy()
            self.on_element_selected()  # Refresh UI
            self.refresh_preview()
    
    def reset_all_to_default(self):
        """
        Reset all elements to default configuration
        """
        if messagebox.askyesno("Reset Layout", "Reset all elements to default positions and styles?"):
            self.current_layout = {k: v.copy() for k, v in self.default_layout.items()}
            self.on_element_selected()  # Refresh UI
            self.refresh_preview()
    
    def refresh_preview(self):
        """
        Refresh the layout preview
        """
        self.preview_figure.clear()
        ax = self.preview_figure.add_subplot(111)
        
        # Set up the preview area to match A3 proportions
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        
        # Draw element rectangles
        self.element_rectangles.clear()
        
        for element_name, config in self.current_layout.items():
            if 'position' in config and isinstance(config['position'], list):
                pos = config['position']
                
                # Create rectangle
                rect = Rectangle((pos[0], pos[1]), pos[2], pos[3], 
                               fill=True, alpha=0.3, 
                               facecolor=self.get_element_color(element_name),
                               edgecolor='black', linewidth=1)
                ax.add_patch(rect)
                
                # Add label with better formatting for dynamic elements
                display_name = element_name.replace('_', ' ').title()
                if element_name.startswith('compass_'):
                    display_name = f"Compass {element_name.split('_')[1]}"
                elif element_name.startswith('scale_bar_'):
                    display_name = f"Scale Bar {element_name.split('_')[1]}"
                elif element_name.startswith('text_box_'):
                    display_name = f"Text Box {element_name.split('_')[1]}"
                
                ax.text(pos[0] + pos[2]/2, pos[1] + pos[3]/2, 
                       display_name,
                       ha='center', va='center', fontsize=8, fontweight='bold')
                
                # Store rectangle for interaction
                self.element_rectangles[element_name] = rect
        
        # Highlight selected element
        self.highlight_selected_element()
        
        ax.set_title("Map Layout Preview (Drag elements to reposition)", fontsize=10)
        ax.set_xlabel("Figure Width (0-1)")
        ax.set_ylabel("Figure Height (0-1)")
        
        self.preview_canvas.draw()
    
    def get_element_color(self, element_name):
        """
        Get color for element visualization
        """
        colors = {
            'main_map': 'lightblue',
            'title': 'lightgreen',
            'legend': 'lightyellow',
            'belitung_overview': 'lightcoral',
            'logo_info': 'lightgray',
            'compass': 'orange',
            'scale_bar': 'purple'
        }
        
        # Handle dynamic element names
        if element_name.startswith('compass'):
            return 'orange'
        elif element_name.startswith('scale_bar'):
            return 'purple'
        elif element_name.startswith('text_box'):
            return 'lightcyan'
        
        return colors.get(element_name, 'lightgray')
    
    def highlight_selected_element(self):
        """
        Highlight the currently selected element
        """
        selected = self.selected_element.get()
        
        for element_name, rect in self.element_rectangles.items():
            if element_name == selected:
                rect.set_edgecolor('red')
                rect.set_linewidth(3)
            else:
                rect.set_edgecolor('black')
                rect.set_linewidth(1)
        
        self.preview_canvas.draw()
    
    def on_canvas_click(self, event):
        """
        Handle canvas click for element selection, drag start, or element creation
        """
        if event.inaxes is None:
            return
        
        # Handle element creation mode
        if self.creation_state['active']:
            self.creation_state['start_pos'] = (event.xdata, event.ydata)
            return
        
        # Find clicked element
        clicked_element = None
        for element_name, rect in self.element_rectangles.items():
            if rect.contains(event)[0]:
                clicked_element = element_name
                break
        
        if clicked_element:
            # Select element
            self.selected_element.set(clicked_element)
            self.on_element_selected()
            
            # Start drag
            self.drag_state['active'] = True
            self.drag_state['element'] = clicked_element
            self.drag_state['start_pos'] = (event.xdata, event.ydata)
            
            # Calculate offset from element origin
            pos = self.current_layout[clicked_element]['position']
            self.drag_state['offset'] = (event.xdata - pos[0], event.ydata - pos[1])
    
    def on_canvas_drag(self, event):
        """
        Handle canvas drag for element repositioning or element creation
        """
        if event.inaxes is None:
            return
        
        # Handle element creation mode
        if self.creation_state['active'] and self.creation_state['start_pos']:
            self.update_creation_preview(event.xdata, event.ydata)
            return
        
        # Handle element dragging
        if not self.drag_state['active']:
            return
        
        element_name = self.drag_state['element']
        if element_name and element_name in self.current_layout:
            # Calculate new position
            offset = self.drag_state['offset']
            new_x = event.xdata - offset[0]
            new_y = event.ydata - offset[1]
            
            # Update position (keep size unchanged)
            pos = self.current_layout[element_name]['position']
            self.current_layout[element_name]['position'] = [new_x, new_y, pos[2], pos[3]]
            
            # Update position variables
            self.pos_vars['left'].set(new_x)
            self.pos_vars['bottom'].set(new_y)
            
            # Refresh preview
            self.refresh_preview()
    
    def on_canvas_release(self, event):
        """
        Handle canvas release to end drag or complete element creation
        """
        if event.inaxes is None:
            return
        
        # Handle element creation completion
        if self.creation_state['active'] and self.creation_state['start_pos']:
            self.complete_element_creation(event.xdata, event.ydata)
            return
        
        # Handle drag end
        self.drag_state['active'] = False
        self.drag_state['element'] = None
        self.drag_state['start_pos'] = None
        self.drag_state['offset'] = None
    
    def start_element_creation(self, element_type):
        """
        Start element creation mode
        
        Args:
            element_type (str): Type of element to create ('compass', 'scale_bar', 'text_box')
        """
        self.creation_state['active'] = True
        self.creation_state['element_type'] = element_type
        self.creation_state['start_pos'] = None
        self.creation_state['current_rect'] = None
        
        # Update UI to show creation mode
        self.creation_mode_label.config(text=f"Creation Mode: {element_type.replace('_', ' ').title()}\nClick and drag on canvas to place element")
        
        # Change cursor to crosshair (if supported)
        try:
            self.preview_canvas.get_tk_widget().config(cursor="crosshair")
        except:
            pass
    
    def update_creation_preview(self, current_x, current_y):
        """
        Update the preview rectangle during element creation
        
        Args:
            current_x (float): Current mouse X position
            current_y (float): Current mouse Y position
        """
        if not self.creation_state['start_pos']:
            return
        
        start_x, start_y = self.creation_state['start_pos']
        
        # Calculate rectangle bounds
        left = min(start_x, current_x)
        right = max(start_x, current_x)
        bottom = min(start_y, current_y)
        top = max(start_y, current_y)
        
        width = right - left
        height = top - bottom
        
        # Remove previous preview rectangle if exists
        if self.creation_state['current_rect']:
            self.creation_state['current_rect'].remove()
        
        # Add new preview rectangle
        ax = self.preview_figure.axes[0]
        rect = Rectangle((left, bottom), width, height, 
                        fill=False, edgecolor='red', linewidth=2, 
                        linestyle='--', alpha=0.7)
        ax.add_patch(rect)
        self.creation_state['current_rect'] = rect
        
        # Update canvas
        self.preview_canvas.draw()
    
    def complete_element_creation(self, end_x, end_y):
        """
        Complete element creation and add to layout
        
        Args:
            end_x (float): End mouse X position
            end_y (float): End mouse Y position
        """
        if not self.creation_state['start_pos']:
            return
        
        start_x, start_y = self.creation_state['start_pos']
        element_type = self.creation_state['element_type']
        
        # Calculate rectangle bounds
        left = min(start_x, end_x)
        right = max(start_x, end_x)
        bottom = min(start_y, end_y)
        top = max(start_y, end_y)
        
        width = right - left
        height = top - bottom
        
        # Minimum size check
        if width < 0.05 or height < 0.05:
            messagebox.showwarning("Element Too Small", "Element must be at least 5% of canvas size. Please draw a larger area.")
            self.cancel_element_creation()
            return
        
        # Generate unique element name
        base_name = element_type
        counter = 1
        element_name = base_name
        while element_name in self.current_layout:
            element_name = f"{base_name}_{counter}"
            counter += 1
        
        # Create element configuration based on type
        if element_type == 'compass':
            element_config = {
                "position": [left, bottom, width, height],
                "size": min(width, height),  # Use smaller dimension for compass size
                "visible": True,
                "style": "modern"
            }
        elif element_type == 'scale_bar':
            element_config = {
                "position": [left, bottom, width, height],
                "visible": True,
                "units": "meters",
                "style": "standard"
            }
        elif element_type == 'text_box':
            element_config = {
                "position": [left, bottom, width, height],
                "text": "New Text Box",
                "font_size": 12,
                "font_weight": "normal",
                "text_color": "black",
                "background_color": "white",
                "border": True,
                "border_color": "black",
                "border_width": 1
            }
        else:
            # Default configuration
            element_config = {
                "position": [left, bottom, width, height],
                "visible": True
            }
        
        # Add element to layout
        self.current_layout[element_name] = element_config
        
        # Update element list
        current_values = list(self.current_layout.keys())
        element_list_widget = None
        for widget in self.left_panel.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and "Map Elements" in widget.cget("text"):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Combobox):
                        element_list_widget = child
                        break
                break
        
        if element_list_widget:
            element_list_widget['values'] = current_values
        
        # Select the new element
        self.selected_element.set(element_name)
        self.on_element_selected()
        
        # Show success message
        messagebox.showinfo("Element Added", f"{element_type.replace('_', ' ').title()} '{element_name}' has been added to the layout.")
        
        # Cancel creation mode
        self.cancel_element_creation()
        
        # Refresh preview
        self.refresh_preview()
    
    def cancel_element_creation(self):
        """
        Cancel element creation mode
        """
        # Remove preview rectangle if exists
        if self.creation_state['current_rect']:
            self.creation_state['current_rect'].remove()
            self.preview_canvas.draw()
        
        # Reset creation state
        self.creation_state['active'] = False
        self.creation_state['element_type'] = None
        self.creation_state['start_pos'] = None
        self.creation_state['current_rect'] = None
        
        # Update UI
        self.creation_mode_label.config(text="")
        
        # Reset cursor
        try:
            self.preview_canvas.get_tk_widget().config(cursor="")
        except:
            pass
    
    def delete_selected_element(self):
        """
        Delete the currently selected element
        """
        element_name = self.selected_element.get()
        
        # Don't allow deletion of core elements
        core_elements = ['main_map', 'title', 'legend', 'belitung_overview', 'logo_info']
        if element_name in core_elements:
            messagebox.showwarning("Cannot Delete", f"Core element '{element_name}' cannot be deleted.")
            return
        
        if element_name in self.current_layout:
            # Confirm deletion
            if messagebox.askyesno("Delete Element", f"Are you sure you want to delete '{element_name}'?"):
                # Remove from layout
                del self.current_layout[element_name]
                
                # Update element list
                current_values = list(self.current_layout.keys())
                element_list_widget = None
                for widget in self.left_panel.winfo_children():
                    if isinstance(widget, ttk.LabelFrame) and "Map Elements" in widget.cget("text"):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Combobox):
                                element_list_widget = child
                                break
                        break
                
                if element_list_widget:
                    element_list_widget['values'] = current_values
                    # Select first available element
                    if current_values:
                        self.selected_element.set(current_values[0])
                        self.on_element_selected()
                
                # Refresh preview
                self.refresh_preview()
                
                messagebox.showinfo("Element Deleted", f"Element '{element_name}' has been deleted.")
    
    def generate_final_map(self):
        """
        Generate the final map with current layout settings
        """
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file first.")
            return
        
        try:
            # Create map generator with custom layout
            self.map_generator = ProfessionalMapGenerator(
                input_path=self.input_file.get(),
                logo_path=self.logo_file.get() if self.logo_file.get() else None
            )
            
            # Load data
            if self.input_file.get().lower().endswith('.tif'):
                self.map_generator.load_tiff_data()
            else:
                self.map_generator.load_data()
            
            self.map_generator.load_belitung_data()
            
            # Apply custom layout and generate map
            success = self.create_custom_layout_map()
            
            if success:
                messagebox.showinfo("Success", f"Map generated successfully: {self.output_file.get()}")
            else:
                messagebox.showerror("Error", "Failed to generate map.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating map: {str(e)}")
    
    def create_custom_layout_map(self):
        """
        Create map with custom layout configuration
        """
        try:
            # Create figure with A3 proportions
            fig = plt.figure(figsize=(16.54, 11.69))
            fig.patch.set_facecolor('white')
            
            # Add border if enabled
            border_rect = Rectangle((0.01, 0.01), 0.98, 0.98,
                                  fill=False, edgecolor='blue', linewidth=3,
                                  transform=fig.transFigure)
            fig.patches.append(border_rect)
            
            # Create main map
            main_config = self.current_layout['main_map']
            main_pos = main_config['position']
            ax_main = plt.axes(main_pos)
            
            # Add main map border if enabled
            if main_config.get('border', True):
                main_border = Rectangle((main_pos[0], main_pos[1]), main_pos[2], main_pos[3],
                                      fill=False, 
                                      edgecolor=main_config.get('border_color', 'black'), 
                                      linewidth=main_config.get('border_width', 2),
                                      transform=fig.transFigure)
                fig.patches.append(main_border)
            
            # Plot main map data
            self.map_generator._plot_main_map_degrees(ax_main)
            
            # Create and render other elements with custom positions
            self.create_custom_elements(fig)
            
            # Save map
            plt.savefig(self.output_file.get(), dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            
            plt.show()
            return True
            
        except Exception as e:
            print(f"Error creating custom layout map: {e}")
            return False
    
    def create_custom_elements(self, fig):
        """
        Create map elements with custom layout configuration
        """
        # Title element
        if 'title' in self.current_layout:
            title_config = self.current_layout['title']
            title_element = TitleElement(
                title_text=title_config.get('text', 'PETA KEBUN 1 B\nPT. REBINMAS JAYA'),
                position=title_config['position']
            )
            title_element.render(fig)
        
        # Legend element
        if 'legend' in self.current_layout:
            legend_config = self.current_layout['legend']
            legend_element = LegendElement(
                position=legend_config['position'],
                file_type=self.map_generator.file_type,
                colors=self.map_generator.colors,
                gdf=self.map_generator.gdf,
                tiff_legend=self.map_generator.tiff_legend
            )
            legend_element.render(fig)
        
        # Belitung overview element
        if 'belitung_overview' in self.current_layout:
            overview_config = self.current_layout['belitung_overview']
            overview_element = BelitungOverviewElement(
                position=overview_config['position'],
                belitung_gdf=self.map_generator.belitung_gdf,
                main_gdf=self.map_generator.gdf,
                colors=self.map_generator.colors,
                file_type=self.map_generator.file_type,
                tiff_bounds=getattr(self.map_generator, 'tiff_bounds_wgs84', None)
            )
            overview_element.render(fig)
        
        # Logo info element
        if 'logo_info' in self.current_layout:
            logo_config = self.current_layout['logo_info']
            logo_element = LogoInfoElement(
                position=logo_config['position'],
                logo_path=self.map_generator.logo_path,
                company_name=logo_config.get('company_name', 'PT. REBINMAS JAYA'),
                production_info=logo_config.get('production_info', 'Diproduksi untuk : PT. REBINMAS JAYA'),
                program_info=logo_config.get('program_info', 'Program: IT Rebinmas | Data: Surveyor RMJ'),
                generated_date=logo_config.get('generated_date', 'Generated: July 2025')
            )
            logo_element.render(fig)
    
    def save_layout(self):
        """
        Save current layout configuration to JSON file
        """
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Layout Configuration"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.current_layout, f, indent=2)
                messagebox.showinfo("Success", f"Layout saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save layout: {str(e)}")
    
    def load_layout(self):
        """
        Load layout configuration from JSON file
        """
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Layout Configuration"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.current_layout = json.load(f)
                self.on_element_selected()  # Refresh UI
                self.refresh_preview()
                messagebox.showinfo("Success", f"Layout loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load layout: {str(e)}")
    
    def load_default_paths(self):
        """
        Load default file paths
        """
        # Default shapefile
        default_shapefile = "../merge_all_sub_divisi_map/merged_estates_HCV0_20250721_092606.shp"
        if os.path.exists(default_shapefile):
            self.input_file.set(default_shapefile)
        
        # Default logo
        default_logo = "rebinmas_logo.jpg"
        if os.path.exists(default_logo):
            self.logo_file.set(default_logo)
    
    def browse_input_file(self):
        """
        Browse for input file (shapefile or TIFF)
        """
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Shapefile", "*.shp"),
                ("TIFF files", "*.tif;*.tiff"),
                ("All files", "*.*")
            ],
            title="Select Input File"
        )
        if filename:
            self.input_file.set(filename)
    
    def browse_logo_file(self):
        """
        Browse for logo file
        """
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp"),
                ("All files", "*.*")
            ],
            title="Select Logo File"
        )
        if filename:
            self.logo_file.set(filename)
    
    def browse_output_file(self):
        """
        Browse for output file
        """
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ],
            title="Save Map As"
        )
        if filename:
            self.output_file.set(filename)

def main():
    """
    Main function to run the layout builder
    """
    root = tk.Tk()
    app = MapLayoutBuilder(root)
    root.mainloop()

if __name__ == "__main__":
    main()