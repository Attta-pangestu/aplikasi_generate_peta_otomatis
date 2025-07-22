#!/usr/bin/env python3
"""
Enhanced Professional Map Generator GUI with Attribute-Based Feature Selection
User-friendly interface for generating professional surveyor-style maps
with dynamic attribute scanning and filtering capabilities.

Author: IT Rebinmas - PT. REBINMAS JAYA
Date: 2025
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from pathlib import Path
import threading
import geopandas as gpd
import pandas as pd
from professional_map_generator_optimized import FixedOptimizedMapGenerator
from collections import Counter

class EnhancedMapGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Professional Map Generator - IT Rebinmas")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        
        # Variables
        self.shapefile_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.map_title = tk.StringVar(value="Peta Areal Tanam DME\nPT Rebinmas Jaya")
        self.logo_path = tk.StringVar()
        self.dpi_var = tk.IntVar(value=300)
        self.context_map_type = tk.StringVar(value="belitung")
        self.enable_georeferencing = tk.BooleanVar(value=True)
        
        # NEW: Attribute-based selection variables
        self.gdf = None  # Store loaded geodataframe
        self.available_attributes = []  # List of attribute columns
        self.selected_attribute = tk.StringVar()  # Selected attribute field
        self.attribute_values = {}  # Dict to store attribute values and their selection status
        self.attribute_vars = {}  # Dict to store checkbox variables for attribute values
        
        # NEW: Additional attribute and filter variables
        self.current_gdf = None
        self.attribute_columns = []
        self.selected_filters = []
        
        # Legacy subdivision variables (for backward compatibility)
        self.subdivision_vars = {}
        self.available_subdivisions = []
        
        # Set default paths
        default_shapefile = "../merge_all_sub_divisi_map/merged_estates_HCV0_20250721_092606.shp"
        if os.path.exists(default_shapefile):
            self.shapefile_path.set(default_shapefile)
        
        # Force use the specific logo path
        forced_logo_path = r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\rebinmas_logo.jpg"
        self.logo_path.set(forced_logo_path)
        
        self.output_path.set("Professional_Map.pdf")
        
        self.setup_ui()
        
    def setup_ui(self):
        """
        Setup the enhanced user interface with attribute-based selection
        """
        # Main frame with scrollbar
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🗺️ Enhanced Professional Map Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        subtitle_label = ttk.Label(main_frame, text="Generate professional maps with dynamic attribute-based feature selection", 
                                  font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 5))
        
        # Credits
        credits_label = ttk.Label(main_frame, text="Developed by: IT Rebinmas - PT. REBINMAS JAYA", 
                                 font=('Arial', 9, 'italic'), foreground='gray')
        credits_label.grid(row=2, column=0, columnspan=3, pady=(0, 15))
        
        # Input file selection
        ttk.Label(main_frame, text="Shapefile Input:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        shapefile_frame = ttk.Frame(main_frame)
        shapefile_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        shapefile_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(shapefile_frame, textvariable=self.shapefile_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(shapefile_frame, text="Browse", command=self.browse_shapefile).grid(row=0, column=1)
        ttk.Button(shapefile_frame, text="🔍 Scan Attributes", command=self.scan_shapefile_attributes, 
                  style='Accent.TButton').grid(row=0, column=2, padx=(5, 0))
        
        # ENHANCED: Attribute Analysis Section
        self.attribute_frame = ttk.LabelFrame(main_frame, text="🔍 Attribute-Based Feature Selection", padding="10")
        self.attribute_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        self.attribute_frame.columnconfigure(1, weight=1)
        
        # Attribute selection
        ttk.Label(self.attribute_frame, text="Select Attribute Field:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.attribute_combo = ttk.Combobox(self.attribute_frame, textvariable=self.selected_attribute, 
                                           state="readonly", width=30)
        self.attribute_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        self.attribute_combo.bind('<<ComboboxSelected>>', self.on_attribute_selected)
        
        ttk.Button(self.attribute_frame, text="📊 Analyze Values", 
                  command=self.analyze_attribute_values).grid(row=0, column=2, padx=(5, 0))
        
        # Attribute values selection frame
        self.values_frame = ttk.LabelFrame(self.attribute_frame, text="Select Values to Include in Map", padding="5")
        self.values_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Values selection area with scrollbar
        self.values_canvas = tk.Canvas(self.values_frame, height=150)
        values_scrollbar = ttk.Scrollbar(self.values_frame, orient="vertical", command=self.values_canvas.yview)
        self.values_scrollable_frame = ttk.Frame(self.values_canvas)
        
        self.values_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.values_canvas.configure(scrollregion=self.values_canvas.bbox("all"))
        )
        
        self.values_canvas.create_window((0, 0), window=self.values_scrollable_frame, anchor="nw")
        self.values_canvas.configure(yscrollcommand=values_scrollbar.set)
        
        self.values_canvas.pack(side="left", fill="both", expand=True)
        values_scrollbar.pack(side="right", fill="y")
        
        # Values selection buttons
        values_buttons_frame = ttk.Frame(self.attribute_frame)
        values_buttons_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        ttk.Button(values_buttons_frame, text="Select All", command=self.select_all_values).grid(row=0, column=0, padx=5)
        ttk.Button(values_buttons_frame, text="Deselect All", command=self.deselect_all_values).grid(row=0, column=1, padx=5)
        ttk.Button(values_buttons_frame, text="🎨 Preview Selection", command=self.preview_selection).grid(row=0, column=2, padx=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output PDF:").grid(row=5, column=0, sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1)
        
        # Map title input
        ttk.Label(main_frame, text="Map Title:").grid(row=6, column=0, sticky=tk.W, pady=5)
        
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        title_frame.columnconfigure(0, weight=1)
        
        title_entry = tk.Text(title_frame, height=2, width=50)
        title_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        title_entry.insert("1.0", self.map_title.get())
        title_entry.bind('<KeyRelease>', lambda e: self.map_title.set(title_entry.get("1.0", "end-1c")))
        
        # Logo path input
        ttk.Label(main_frame, text="Logo Path:").grid(row=7, column=0, sticky=tk.W, pady=5)
        
        logo_frame = ttk.Frame(main_frame)
        logo_frame.grid(row=7, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        logo_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(logo_frame, textvariable=self.logo_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo).grid(row=0, column=1)
        
        # Context map type selection
        ttk.Label(main_frame, text="Context Map Type:").grid(row=8, column=0, sticky=tk.W, pady=5)
        
        context_frame = ttk.Frame(main_frame)
        context_frame.grid(row=8, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(context_frame, text="Belitung Island", variable=self.context_map_type, 
                       value="belitung").grid(row=0, column=0, padx=(0, 15))
        ttk.Radiobutton(context_frame, text="Study Area Only", variable=self.context_map_type, 
                       value="self").grid(row=0, column=1)
        
        # Georeferencing options
        ttk.Label(main_frame, text="Georeferencing:").grid(row=9, column=0, sticky=tk.W, pady=5)
        geo_frame = ttk.Frame(main_frame)
        geo_frame.grid(row=9, column=1, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(geo_frame, text="Enable for Avenza Maps (preserves original CRS)", 
                       variable=self.enable_georeferencing).grid(row=0, column=0, sticky=tk.W)
        
        # DPI selection
        ttk.Label(main_frame, text="Resolution (DPI):").grid(row=10, column=0, sticky=tk.W, pady=5)
        
        dpi_frame = ttk.Frame(main_frame)
        dpi_frame.grid(row=10, column=1, sticky=tk.W, pady=5)
        
        dpi_options = [150, 300, 600, 1200]
        for i, dpi in enumerate(dpi_options):
            ttk.Radiobutton(dpi_frame, text=f"{dpi} DPI", variable=self.dpi_var, 
                           value=dpi).grid(row=0, column=i, padx=5)
        
        # Generate buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=11, column=0, columnspan=3, pady=20)
        
        # Quick Default Generate button
        quick_generate_btn = ttk.Button(buttons_frame, text="⚡ Quick Generate (SUB_DIVISI defaults)", 
                                       command=self.quick_generate_default, style='Accent.TButton')
        quick_generate_btn.grid(row=0, column=0, padx=10)
        
        # Enhanced Generate button
        generate_btn = ttk.Button(buttons_frame, text="🗺️ Generate Professional Map", 
                                 command=self.generate_map, style='Accent.TButton')
        generate_btn.grid(row=0, column=1, padx=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status text
        self.status_text = scrolledtext.ScrolledText(main_frame, height=10, width=80)
        self.status_text.grid(row=13, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Configure row weight for status text
        main_frame.rowconfigure(13, weight=1)
        
        # Initial status
        self.log_message("🗺️ Enhanced Map Generator Ready - IT Rebinmas")
        self.log_message("📋 Step 1: Select shapefile → Step 2: Scan attributes → Step 3: Select features → Step 4: Generate map")
        self.log_message(f"Default shapefile: {self.shapefile_path.get()}")
        
    def browse_shapefile(self):
        """Browse for shapefile input"""
        filename = filedialog.askopenfilename(
            title="Select Shapefile",
            filetypes=[("Shapefiles", "*.shp"), ("All files", "*.*")]
        )
        if filename:
            self.shapefile_path.set(filename)
            self.log_message(f"📁 Selected shapefile: {filename}")
            
            # Load and analyze shapefile for attribute detection
            try:
                self.current_gdf = gpd.read_file(filename)
                self.scan_shapefile_attributes()
                self.log_message(f"✅ Shapefile loaded: {len(self.current_gdf)} features found")
            except Exception as e:
                self.log_message(f"❌ Error loading shapefile: {str(e)}")
                messagebox.showerror("Error", f"Error loading shapefile: {str(e)}")
                self.current_gdf = None
            
            # Reset attribute selection when new file is selected
            self.reset_attribute_selection()
    
    def scan_shapefile_attributes(self):
        """Scan shapefile and populate available attributes"""
        shapefile_path = self.shapefile_path.get()
        if not shapefile_path or not os.path.exists(shapefile_path):
            messagebox.showerror("Error", "Please select a valid shapefile first.")
            return
        
        try:
            self.log_message("🔍 Scanning shapefile attributes...")
            self.gdf = gpd.read_file(shapefile_path)
            
            # Get all column names except geometry
            self.available_attributes = [col for col in self.gdf.columns if col != 'geometry']
            
            # Populate attribute combobox
            self.attribute_combo['values'] = self.available_attributes
            
            self.log_message(f"✅ Found {len(self.available_attributes)} attribute fields:")
            for attr in self.available_attributes:
                unique_count = self.gdf[attr].nunique()
                self.log_message(f"   • {attr}: {unique_count} unique values")
            
            # Auto-select SUB_DIVISI if available
            if 'SUB_DIVISI' in self.available_attributes:
                self.selected_attribute.set('SUB_DIVISI')
                self.log_message("🎯 Auto-selected 'SUB_DIVISI' field")
                self.analyze_attribute_values()
            
        except Exception as e:
            error_msg = f"Error scanning shapefile: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def on_attribute_selected(self, event=None):
        """Handle attribute selection change - ENHANCED with better scanning"""
        selected_attr = self.selected_attribute.get()
        if not selected_attr or self.current_gdf is None:
            return
        
        try:
            self.log_message(f"🔍 Scanning values for attribute: '{selected_attr}'...")
            
            # Get unique values for the selected attribute with counts
            attr_series = self.current_gdf[selected_attr].dropna()
            value_counts = attr_series.value_counts().sort_index()
            
            # Clear existing checkboxes
            self.clear_filter_frame()
            self.attribute_vars.clear()
            
            # Store attribute values for later use
            self.attribute_values = list(value_counts.index)
            
            # Create checkboxes for each unique value with feature counts
            for i, (value, count) in enumerate(value_counts.items()):
                var = tk.BooleanVar(value=True)  # Default to selected
                self.attribute_vars[str(value)] = var
                
                # Create more informative checkbox text
                percentage = (count / len(self.current_gdf)) * 100
                checkbox_text = f"{value} ({count} features, {percentage:.1f}%)"
                
                cb = ttk.Checkbutton(
                    self.values_scrollable_frame,
                    text=checkbox_text,
                    variable=var
                )
                cb.grid(row=i, column=0, sticky='w', padx=5, pady=2)
            
            # Update canvas scroll region
            self.values_scrollable_frame.update_idletasks()
            self.values_canvas.configure(scrollregion=self.values_canvas.bbox("all"))
            
            # Enhanced logging
            total_features = len(self.current_gdf)
            unique_count = len(value_counts)
            self.log_message(f"✅ Attribute '{selected_attr}' scanned:")
            self.log_message(f"   📊 {unique_count} unique values found")
            self.log_message(f"   📈 Total features: {total_features}")
            self.log_message(f"   🎯 Ready for filter selection")
            
        except Exception as e:
            self.log_message(f"❌ Error processing attribute '{selected_attr}': {str(e)}")
            messagebox.showerror("Error", f"Error processing attribute: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def analyze_attribute_values(self):
        """Analyze and display unique values for selected attribute"""
        if self.gdf is None:
            messagebox.showerror("Error", "Please scan shapefile attributes first.")
            return
        
        selected_attr = self.selected_attribute.get()
        if not selected_attr:
            messagebox.showerror("Error", "Please select an attribute field first.")
            return
        
        try:
            self.log_message(f"📊 Analyzing values for '{selected_attr}'...")
            
            # Clear existing checkboxes
            for widget in self.values_scrollable_frame.winfo_children():
                widget.destroy()
            
            # Get unique values and their counts
            value_counts = self.gdf[selected_attr].value_counts()
            
            # Reset attribute values storage
            self.attribute_values = {}
            self.attribute_vars = {}
            
            # Create checkboxes for each unique value
            row = 0
            col = 0
            for value, count in value_counts.items():
                if pd.notna(value):  # Skip NaN values
                    # Create checkbox variable (default to selected for common values)
                    is_default = any(keyword in str(value).upper() for keyword in ['KANDIS', 'CENDONG', 'RAYA', 'DIVISI'])
                    var = tk.BooleanVar(value=is_default)
                    self.attribute_vars[value] = var
                    
                    # Create checkbox with value and count
                    checkbox_text = f"{value} ({count} features)"
                    checkbox = ttk.Checkbutton(self.values_scrollable_frame, 
                                             text=checkbox_text, variable=var)
                    checkbox.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
                    
                    col += 1
                    if col >= 2:  # 2 columns
                        col = 0
                        row += 1
                    
                    self.attribute_values[value] = count
            
            self.log_message(f"✅ Found {len(self.attribute_values)} unique values in '{selected_attr}'")
            self.log_message("💡 Default selection applied for common area names")
            
        except Exception as e:
            error_msg = f"Error analyzing attribute values: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def browse_output(self):
        """Browse for output PDF file"""
        filename = filedialog.asksaveasfilename(
            title="Save Map As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            self.log_message(f"📁 Output file set: {filename}")
    
    def browse_logo(self):
        """Browse for logo file"""
        filename = filedialog.askopenfilename(
            title="Select Logo File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.logo_path.set(filename)
            self.log_message(f"🎨 Logo file set: {filename}")
    
    def reset_attribute_selection(self):
        """Reset attribute selection when new shapefile is loaded"""
        self.gdf = None
        self.available_attributes = []
        self.attribute_values = {}
        self.attribute_vars = {}
        self.selected_attribute.set("")
        self.attribute_combo['values'] = []
        
        # Clear checkboxes
        for widget in self.values_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.log_message("🔄 Attribute selection reset")
    
    def clear_filter_frame(self):
        """Clear the filter frame widgets"""
        for widget in self.values_scrollable_frame.winfo_children():
            widget.destroy()
    
    def create_attribute_widgets(self):
        """Create attribute selection widgets"""
        # This method can be used to recreate widgets if needed
        pass
    
    def select_all_values(self):
        """Select all attribute values"""
        for var in self.attribute_vars.values():
            var.set(True)
        self.log_message("✅ All values selected")
    
    def deselect_all_values(self):
        """Deselect all attribute values"""
        for var in self.attribute_vars.values():
            var.set(False)
    
    def preview_selection(self):
        """Preview the currently selected values for the attribute"""
        if self.gdf is None:
            messagebox.showerror("Error", "Please scan shapefile attributes first.")
            return
        
        selected_attr = self.selected_attribute.get()
        if not selected_attr:
            messagebox.showerror("Error", "Please select an attribute field first.")
            return
        
        try:
            self.log_message(f"👁️ Previewing selection for '{selected_attr}'...")
            
            # Get selected values and their counts
            selected_values = {v: self.attribute_values[v] for v in self.attribute_vars if self.attribute_vars[v].get()}
            
            if not selected_values:
                messagebox.showinfo("Info", "No values selected for preview.")
                return
            
            preview_text = f"Preview of Selected Values for '{selected_attr}':\n"
            for value, count in selected_values.items():
                preview_text += f" • {value} ({count} features)\n"
            
            messagebox.showinfo("Selection Preview", preview_text)
            self.log_message(f"✅ Previewed {len(selected_values)} selected values.")
            
        except Exception as e:
            error_msg = f"Error previewing selection: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def quick_generate_default(self):
        """
        Quick generate with default subdivisions (Kandis, Cendong, Hari Raya)
        """
        # Validate shapefile first
        if not self.shapefile_path.get() or not os.path.exists(self.shapefile_path.get()):
            messagebox.showerror("Error", "Please select a valid shapefile first.")
            return
        
        self.log_message("⚡ Quick Generate: Loading subdivisions and setting defaults...")
        
        # Load subdivisions if not already loaded
        if not self.available_subdivisions:
            self.load_subdivisions()
        
        # If subdivisions still not loaded, try to load them
        if not self.available_subdivisions:
            messagebox.showerror("Error", "Could not load subdivisions from shapefile.")
            return
        
        # Set default subdivisions
        default_subdivisions = ['SUB DIVISI AIR KANDIS', 'SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR RAYA']
        
        # Deselect all first
        self.deselect_all_subdivisions()
        
        # Select only the default ones that exist
        selected_count = 0
        for subdivision in default_subdivisions:
            if subdivision in self.subdivision_vars:
                self.subdivision_vars[subdivision].set(True)
                selected_count += 1
                self.log_message(f"🎨 Selected default area: {subdivision}")
        
        if selected_count == 0:
            # Fallback: try partial matches
            for subdivision in self.available_subdivisions:
                if any(default in subdivision.upper() for default in ['KANDIS', 'CENDONG', 'RAYA']):
                    self.subdivision_vars[subdivision].set(True)
                    selected_count += 1
                    self.log_message(f"🎨 Selected area (partial match): {subdivision}")
        
        if selected_count == 0:
            messagebox.showerror("Error", "No default areas found. Please select manually.")
            return
        
        self.log_message(f"⚡ Quick Generate: {selected_count} areas selected with auto-colors, starting generation...")
        
        # Start generation immediately
        self.generate_map()
    
    def generate_map(self):
        """
        Generate the optimized professional map using attribute-based selection - ENHANCED with filter support
        """
        # Validate inputs
        if not self.shapefile_path.get() or not os.path.exists(self.shapefile_path.get()):
            messagebox.showerror("Error", "Please select a valid shapefile.")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify an output file path.")
            return
        
        # Check if we have scanned attributes and selected values
        if self.gdf is None:
            messagebox.showerror("Error", "Please scan shapefile attributes first.")
            return
        
        selected_attr = self.selected_attribute.get()
        if not selected_attr:
            messagebox.showerror("Error", "Please select an attribute field.")
            return
        
        selected_values = self.get_selected_values()
        if not selected_values:
            messagebox.showerror("Error", "Please select at least one value from the attribute.")
            return
        
        # ENHANCED: Log filter information with IT Rebinmas branding
        self.log_message(f"🎯 Filter applied on '{selected_attr}' by IT Rebinmas:")
        self.log_message(f"   📋 Selected {len(selected_values)} out of {len(self.attribute_vars)} values")
        if len(selected_values) <= 5:
            self.log_message(f"   📝 Values: {', '.join(map(str, selected_values))}")
        else:
            self.log_message(f"   📝 Values: {', '.join(map(str, selected_values[:3]))}... and {len(selected_values)-3} more")
        
        self.log_message("🚀 Starting professional map generation by IT Rebinmas...")
        
        # Start generation in a separate thread
        self.progress.start()
        thread = threading.Thread(target=self._generate_map_thread, 
                                 args=(selected_attr, selected_values))
        thread.daemon = True
        thread.start()
    
    def _generate_map_thread(self, selected_attr, selected_values):
        """
        Generate map in a separate thread using attribute-based filtering - ENHANCED with better filtering and IT Rebinmas branding
        """
        try:
            self.log_message("🚀 Starting enhanced map generation by IT Rebinmas...")
            
            # Load shapefile with CRS preservation
            gdf = gpd.read_file(self.shapefile_path.get())
            original_crs = gdf.crs
            self.log_message(f"📁 Loaded shapefile: {len(gdf)} features")
            self.log_message(f"📍 Original CRS: {original_crs}")
            
            # ENHANCED: Apply attribute filter if specified
            if selected_attr and selected_values:
                original_count = len(gdf)
                
                # Convert selected values to appropriate types
                try:
                    # Try to match the data type of the column
                    column_dtype = gdf[selected_attr].dtype
                    if column_dtype in ['int64', 'int32', 'float64', 'float32']:
                        # Convert to numeric if possible
                        converted_values = []
                        for val in selected_values:
                            try:
                                if 'int' in str(column_dtype):
                                    converted_values.append(int(float(val)))
                                else:
                                    converted_values.append(float(val))
                            except:
                                converted_values.append(val)
                        selected_values = converted_values
                except Exception as e:
                    self.log_message(f"⚠️ Type conversion warning: {e}")
                
                # Apply filter
                gdf = gdf[gdf[selected_attr].isin(selected_values)]
                filtered_count = len(gdf)
                
                self.log_message(f"🎯 Filter applied by IT Rebinmas:")
                self.log_message(f"   📊 Original features: {original_count}")
                self.log_message(f"   ✅ Filtered features: {filtered_count}")
                self.log_message(f"   📈 Retention rate: {(filtered_count/original_count)*100:.1f}%")
                
                if filtered_count == 0:
                    self.log_message("❌ No features match the selected criteria")
                    self.root.after(0, lambda: messagebox.showerror("Error", "No features match the selected criteria"))
                    return
            else:
                self.log_message("📊 No filter applied - using all features")
            
            # FIXED: Create map generator with proper attribute-based filtering
            map_gen = FixedOptimizedMapGenerator(
                self.shapefile_path.get(), 
                selected_subdivisions=None,  # Will be overridden by attribute filtering
                map_title=self.map_title.get(),
                logo_path=self.logo_path.get() if self.logo_path.get() else None,
                context_map_type=self.context_map_type.get(),
                enable_georeferencing=self.enable_georeferencing.get()
            )
            
            # FIXED: Properly set attribute filtering parameters using the new method
            map_gen.set_attribute_filter(selected_attr, selected_values)
            
            self.log_message(f"🎯 Set filter parameters using set_attribute_filter method:")
            self.log_message(f"   📋 Attribute: {selected_attr}")
            self.log_message(f"   📝 Values: {selected_values}")
            self.log_message(f"   📊 Value count: {len(selected_values)}")
            
            # Load data with attribute filtering
            self.log_message("🗺️ Loading shapefile data with enhanced filtering...")
            if not map_gen.load_data_with_attribute_filter():
                self.log_message("❌ Failed to load shapefile data")
                return
            
            # Load Belitung data
            self.log_message("🌍 Loading Belitung overview data...")
            map_gen.load_belitung_data()
            
            # Generate map
            self.log_message("🎨 Generating professional map layout...")
            success = map_gen.create_professional_map(
                output_path=self.output_path.get(),
                dpi=self.dpi_var.get()
            )
            
            if success:
                self.log_message(f"✅ Professional map generated successfully by IT Rebinmas!")
                self.log_message(f"📄 Output: {self.output_path.get()}")
                self.log_message(f"📱 Enhanced Avenza Maps compatibility included")
                self.log_message(f"🎯 CRS preserved: {original_crs}")
                self.log_message("\n🎨 FEATURES APPLIED BY IT REBINMAS:")
                self.log_message("- ✅ Enhanced attribute-based feature filtering")
                self.log_message("- ✅ Automatic distinct colors for each value")
                self.log_message("- ✅ Original CRS preservation for Avenza Maps")
                self.log_message("- ✅ Clean context map without red box")
                self.log_message("- ✅ Logo positioned above company name")
                self.log_message("- ✅ Accurate scale bar for distance reference")
                self.log_message("- ✅ Maximum zoom for study area")
                self.log_message("- ✅ Professional coordinate grid")
                
                # Show enhanced success message
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success - IT Rebinmas", 
                    f"Professional map generated successfully!\n\n"
                    f"📄 Saved to: {self.output_path.get()}\n"
                    f"📱 Avenza Maps compatible\n"
                    f"🎯 Features: {len(gdf) if 'gdf' in locals() else 'N/A'}\n"
                    f"📍 CRS: {original_crs}\n\n"
                    f"Created by: IT Rebinmas"))
            else:
                self.log_message("❌ Failed to generate map")
                self.root.after(0, lambda: messagebox.showerror(
                    "Error - IT Rebinmas", "Failed to generate map. Check the log for details.\n\nPlease contact IT Rebinmas for support."))
                
        except Exception as e:
            error_msg = f"Error generating map: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            import traceback
            self.log_message(traceback.format_exc())
            self.root.after(0, lambda: messagebox.showerror("Error - IT Rebinmas", f"{error_msg}\n\nPlease contact IT Rebinmas for support."))
        
        finally:
            self.root.after(0, self.progress.stop)
    
    def log_message(self, message):
        """
        Add a message to the status log
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)
        self.root.update_idletasks()

    def get_selected_values(self):
        """Get list of selected attribute values"""
        return [value for value, var in self.attribute_vars.items() if var.get()]
    
    def load_subdivisions(self):
        """Legacy method for backward compatibility"""
        if self.gdf is not None and 'SUB_DIVISI' in self.gdf.columns:
            self.available_subdivisions = list(self.gdf['SUB_DIVISI'].unique())
            self.subdivision_vars = {}
            for subdivision in self.available_subdivisions:
                self.subdivision_vars[subdivision] = tk.BooleanVar()
    
    def deselect_all_subdivisions(self):
        """Legacy method for backward compatibility"""
        for var in self.subdivision_vars.values():
            var.set(False)

def main():
    """
    Main function to run the optimized GUI
    """
    root = tk.Tk()
    app = EnhancedMapGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()