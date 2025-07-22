#!/usr/bin/env python3
"""
Professional Map Generator GUI
User-friendly interface for generating professional surveyor-style maps

Author: Generated for Tree Counting Project
Date: 2025
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from pathlib import Path
import threading
import geopandas as gpd
from professional_map_generator import ProfessionalMapGenerator

class MapGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Map Generator - Palm Oil Plantation")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.shapefile_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.map_title = tk.StringVar(value="PETA KEBUN 1 B\nPT. REBINMAS JAYA")
        self.logo_path = tk.StringVar()
        self.dpi_var = tk.IntVar(value=300)
        self.subdivision_vars = {}  # Dictionary to store subdivision checkbox variables
        self.available_subdivisions = []  # List of available subdivisions
        
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
        
        self.output_path.set("Peta_Profesional_Sub_Divisi.pdf")
        
        self.setup_ui()
        
    def setup_ui(self):
        """
        Setup the user interface
        """
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Professional Map Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Generate professional surveyor-style maps with degree coordinates and Belitung overview", 
                                  font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 15))
        
        # Input file selection
        ttk.Label(main_frame, text="Shapefile Input:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        shapefile_frame = ttk.Frame(main_frame)
        shapefile_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        shapefile_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(shapefile_frame, textvariable=self.shapefile_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(shapefile_frame, text="Browse", command=self.browse_shapefile).grid(row=0, column=1)
        
        # Output file selection
        ttk.Label(main_frame, text="Output PDF:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1)
        
        # Map title input
        ttk.Label(main_frame, text="Map Title:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        title_frame.columnconfigure(0, weight=1)
        
        title_entry = tk.Text(title_frame, height=2, width=50)
        title_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        title_entry.insert("1.0", self.map_title.get())
        title_entry.bind('<KeyRelease>', lambda e: self.map_title.set(title_entry.get("1.0", "end-1c")))
        
        # Logo path input
        ttk.Label(main_frame, text="Logo Path:").grid(row=5, column=0, sticky=tk.W, pady=5)
        
        logo_frame = ttk.Frame(main_frame)
        logo_frame.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        logo_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(logo_frame, textvariable=self.logo_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo).grid(row=0, column=1)
        
        # Subdivision selection
        self.subdivision_frame = ttk.LabelFrame(main_frame, text="Select Sub-Divisions to Display", padding="10")
        self.subdivision_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Load subdivisions button
        load_subdivisions_btn = ttk.Button(self.subdivision_frame, text="Load Available Sub-Divisions", 
                                          command=self.load_subdivisions)
        load_subdivisions_btn.grid(row=0, column=0, columnspan=3, pady=5)
        
        # Info label
        info_label = ttk.Label(self.subdivision_frame, 
                              text="Default selection: SUB DIVISI AIR CENDONG, SUB DIVISI AIR KANDIS, SUB DIVISI AIR RAYA", 
                              font=('Arial', 9, 'italic'))
        info_label.grid(row=1, column=0, columnspan=3, pady=2)
        
        # Subdivision checkboxes will be added dynamically
        self.subdivision_checkboxes_frame = ttk.Frame(self.subdivision_frame)
        self.subdivision_checkboxes_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Select/Deselect all buttons
        buttons_frame = ttk.Frame(self.subdivision_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=5)
        
        ttk.Button(buttons_frame, text="Select All", command=self.select_all_subdivisions).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="Deselect All", command=self.deselect_all_subdivisions).grid(row=0, column=1, padx=5)
        ttk.Button(buttons_frame, text="Select Default", command=self.select_default_subdivisions).grid(row=0, column=2, padx=5)
        
        # DPI selection
        ttk.Label(main_frame, text="Resolution (DPI):").grid(row=7, column=0, sticky=tk.W, pady=5)
        
        dpi_frame = ttk.Frame(main_frame)
        dpi_frame.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        dpi_options = [150, 300, 600, 1200]
        for i, dpi in enumerate(dpi_options):
            ttk.Radiobutton(dpi_frame, text=f"{dpi} DPI", variable=self.dpi_var, 
                           value=dpi).grid(row=0, column=i, padx=5)
        
        # Map features info
        features_frame = ttk.LabelFrame(main_frame, text="Professional Map Features", padding="10")
        features_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        features_text = [
            "✓ Professional layout matching surveyor standards",
            "✓ Coordinate display in degrees (WGS84) - BOLD formatting",
            "✓ Plus markers at axis intersections (more prominent)",
            "✓ Belitung island overview with study area location",
            "✓ WADMKK categorization (Belitung & Belitung Timur)",
            "✓ Compass image from kompas.webp asset",
            "✓ Color classification by sub-division",
            "✓ Block labels (BLOK codes) on each area",
            "✓ Professional legend with proper colors",
            "✓ Scale bar 1:77.000 with black-white segments",
            "✓ Company logo from specified path",
            "✓ Blue border frame for professional appearance"
        ]
        
        for i, feature in enumerate(features_text):
            ttk.Label(features_frame, text=feature).grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2)
        
        # Generate button
        generate_btn = ttk.Button(main_frame, text="Generate Professional Map", 
                                 command=self.generate_map, style='Accent.TButton')
        generate_btn.grid(row=9, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status text
        self.status_text = scrolledtext.ScrolledText(main_frame, height=8, width=80)
        self.status_text.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Configure row weight for status text
        main_frame.rowconfigure(11, weight=1)
        
        # Initial status
        self.log_message("Ready to generate professional map...")
        self.log_message(f"Default shapefile: {self.shapefile_path.get()}")
        self.log_message(f"Default logo: {self.logo_path.get()}")
        self.log_message("Features: BOLD coordinates, Plus at axis intersections, Belitung overview")
        
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
    
    def load_subdivisions(self):
        """
        Load available subdivisions from the shapefile
        """
        if not self.shapefile_path.get():
            messagebox.showerror("Error", "Please select a shapefile first")
            return
        
        if not os.path.exists(self.shapefile_path.get()):
            messagebox.showerror("Error", "Shapefile does not exist")
            return
        
        try:
            # Load shapefile to get subdivisions
            self.log_message("Loading subdivisions from shapefile...")
            gdf = gpd.read_file(self.shapefile_path.get())
            
            # Get unique subdivisions
            subdivisions = sorted(gdf['SUB_DIVISI'].dropna().unique())
            self.available_subdivisions = subdivisions
            
            # Clear existing checkboxes
            for widget in self.subdivision_checkboxes_frame.winfo_children():
                widget.destroy()
            
            # Clear existing variables
            self.subdivision_vars.clear()
            
            # Default subdivisions based on the image
            default_subdivisions = ['SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR KANDIS', 'SUB DIVISI AIR RAYA']
            
            # Create checkboxes for each subdivision
            for i, subdivision in enumerate(subdivisions):
                # Set default based on image
                default_value = subdivision in default_subdivisions
                var = tk.BooleanVar(value=default_value)
                self.subdivision_vars[subdivision] = var
                
                checkbox = ttk.Checkbutton(
                    self.subdivision_checkboxes_frame,
                    text=subdivision,
                    variable=var
                )
                
                # Arrange in 2 columns
                row = i // 2
                col = i % 2
                checkbox.grid(row=row, column=col, sticky=tk.W, padx=15, pady=3)
            
            self.log_message(f"Loaded {len(subdivisions)} subdivisions: {', '.join(subdivisions)}")
            self.log_message(f"Default selected: {', '.join(default_subdivisions)}")
            
        except Exception as e:
            error_msg = f"Error loading subdivisions: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def select_all_subdivisions(self):
        """
        Select all subdivision checkboxes
        """
        for var in self.subdivision_vars.values():
            var.set(True)
        self.log_message("Selected all subdivisions")
    
    def deselect_all_subdivisions(self):
        """
        Deselect all subdivision checkboxes
        """
        for var in self.subdivision_vars.values():
            var.set(False)
        self.log_message("Deselected all subdivisions")
    
    def select_default_subdivisions(self):
        """
        Select default subdivisions based on the image
        """
        default_subdivisions = ['SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR KANDIS', 'SUB DIVISI AIR RAYA']
        
        # First deselect all
        for var in self.subdivision_vars.values():
            var.set(False)
        
        # Then select default ones
        for subdivision, var in self.subdivision_vars.items():
            if subdivision in default_subdivisions:
                var.set(True)
        
        self.log_message(f"Selected default subdivisions: {', '.join(default_subdivisions)}")
    
    def get_selected_subdivisions(self):
        """
        Get list of selected subdivisions
        """
        selected = []
        for subdivision, var in self.subdivision_vars.items():
            if var.get():
                selected.append(subdivision)
        return selected
    
    def log_message(self, message):
        """
        Add message to status log
        """
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def generate_map(self):
        """
        Generate the professional map
        """
        # Validate inputs
        if not self.shapefile_path.get():
            messagebox.showerror("Error", "Please select a shapefile")
            return
        
        if not os.path.exists(self.shapefile_path.get()):
            messagebox.showerror("Error", "Shapefile does not exist")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify output file")
            return
        
        # Check if subdivisions are selected
        selected_subdivisions = self.get_selected_subdivisions()
        if not selected_subdivisions:
            messagebox.showerror("Error", "Please select at least one subdivision to display")
            return
        
        # Start generation in separate thread
        thread = threading.Thread(target=self._generate_map_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_map_thread(self):
        """
        Generate map in separate thread to prevent GUI freezing
        """
        try:
            # Start progress bar
            self.progress.start()
            
            self.log_message("\n" + "="*60)
            self.log_message("Starting professional map generation...")
            self.log_message("="*60)
            
            # Get selected subdivisions
            selected_subdivisions = self.get_selected_subdivisions()
            self.log_message(f"Selected subdivisions: {', '.join(selected_subdivisions)}")
            
            # Create map generator with selected subdivisions
            self.log_message("Initializing professional map generator...")
            map_gen = ProfessionalMapGenerator(
                self.shapefile_path.get(), 
                selected_subdivisions=selected_subdivisions,
                map_title=self.map_title.get(),
                logo_path=self.logo_path.get() if self.logo_path.get() else None
            )
            
            # Load data
            self.log_message("Loading shapefile data...")
            if not map_gen.load_data():
                self.log_message("ERROR: Failed to load shapefile data")
                messagebox.showerror("Error", "Failed to load shapefile data")
                return
            
            self.log_message(f"Successfully loaded {len(map_gen.gdf)} features (filtered)")
            
            # Get unique sub-divisions in filtered data
            sub_divs = map_gen.gdf['SUB_DIVISI'].dropna().unique()
            self.log_message(f"Displaying sub-divisions: {', '.join(sub_divs)}")
            
            # Generate map
            self.log_message("Generating professional map...")
            self.log_message("Features: Degree coordinates, Plus grid, Belitung overview")
            self.log_message("This may take a few minutes depending on data complexity...")
            
            success = map_gen.create_professional_map(
                output_path=self.output_path.get(),
                dpi=self.dpi_var.get()
            )
            
            if success:
                self.log_message("\n" + "="*60)
                self.log_message("PROFESSIONAL MAP GENERATION COMPLETED SUCCESSFULLY!")
                self.log_message("="*60)
                self.log_message(f"Output file: {self.output_path.get()}")
                self.log_message(f"Resolution: {self.dpi_var.get()} DPI")
                self.log_message(f"Selected subdivisions: {', '.join(selected_subdivisions)}")
                self.log_message("\nProfessional map features included:")
                self.log_message("✓ Layout matching surveyor standards")
                self.log_message("✓ Coordinates in degrees (BOLD/TEBAL)")
                self.log_message("✓ Plus markers at axis intersections")
                self.log_message("✓ Belitung overview with study area marker")
                self.log_message("✓ WADMKK categorization")
                self.log_message("✓ Compass image and company logo")
                self.log_message("✓ Color classification by sub-division")
                self.log_message("✓ Block labels (BLOK codes)")
                self.log_message("✓ Professional legend")
                self.log_message("✓ Scale bar and north arrow")
                self.log_message("✓ Blue border frame")
                
                # Show success message
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Professional map generated successfully!\n\nOutput: {self.output_path.get()}\n\nKey Features:\n- BOLD degree coordinates\n- Plus markers at axis intersections\n- Belitung overview with study area\n- Compass & logo assets\n- Professional layout"
                ))
                
                # Ask if user wants to open the file
                self.root.after(0, self._ask_open_file)
                
            else:
                self.log_message("ERROR: Map generation failed")
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", "Map generation failed. Check the log for details."
                ))
        
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        finally:
            # Stop progress bar
            self.progress.stop()
    
    def _ask_open_file(self):
        """
        Ask user if they want to open the generated file
        """
        if messagebox.askyesno("Open File", "Would you like to open the generated map?"):
            try:
                os.startfile(self.output_path.get())
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

def main():
    """
    Main function to run the GUI
    """
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    app = MapGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()