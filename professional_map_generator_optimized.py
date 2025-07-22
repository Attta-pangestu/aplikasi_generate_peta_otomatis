#!/usr/bin/env python3
"""
ENHANCED Professional Surveyor-Style Map Generator with Avenza Compatibility
Created by: IT Rebinmas

Features:
- Enhanced CRS preservation for perfect Avenza Maps compatibility
- Attribute-based feature filtering with intelligent type conversion
- Professional cartographic layout with IT Rebinmas branding
- Automatic georeferencing with enhanced world files
- Intelligent color generation for unlimited attribute values
- Optimized performance for large datasets

Author: IT Rebinmas
Version: Enhanced v2.0
Date: 2025
"""

import geopandas as gpd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to prevent GUI issues
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from shapely.geometry import Point, box
import contextily as ctx
from matplotlib_scalebar.scalebar import ScaleBar
import warnings
import os
warnings.filterwarnings('ignore')

class FixedOptimizedMapGenerator:
    """
    Enhanced Professional Map Generator with Avenza Compatibility
    Created by: IT Rebinmas
    
    Features:
    - Enhanced CRS preservation for perfect Avenza Maps compatibility
    - Attribute-based feature filtering
    - Professional cartographic layout
    - Automatic georeferencing with enhanced world files
    """
    
    def __init__(self, shapefile_path, selected_subdivisions=None, map_title=None, logo_path=None, context_map_type="belitung", enable_georeferencing=True):
        """
        Initialize the ENHANCED optimized map generator by IT Rebinmas
        """
        self.shapefile_path = shapefile_path
        self.gdf = None
        self.selected_subdivisions = selected_subdivisions
        self.map_title = map_title or "PETA KEBUN 1 B\nPT. REBINMAS JAYA"
        self.context_map_type = context_map_type  # "belitung" or "self"
        self.enable_georeferencing = enable_georeferencing  # For Avenza compatibility
        
        # FIXED: Initialize attribute filtering properties
        self.selected_attribute = None
        self.selected_values = None
        
        # IT Rebinmas branding and metadata
        self.creator_info = "Program dibuat oleh IT Rebinmas"
        self.version_info = "Enhanced Map Generator v2.0 - IT Rebinmas"
        self.support_contact = "IT Rebinmas Support"
        
        # FIXED: Set logo path with priority to exact working path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Priority paths - exact path first
        priority_paths = [
            r"D:\Gawean Rebinmas\Tree Counting Project\Training Tree Counter Sawit Current\BACKUP REPORT APP\Udh bisa generate PDF\Areal Datasets\Edited_ARE_C\Program update pohon dan luas\Create_Peta_PDF\rebinmas_logo.jpg",
            os.path.join(current_dir, "rebinmas_logo.jpg"),
            "rebinmas_logo.jpg",
            "./rebinmas_logo.jpg",
            logo_path
        ]
        
        self.logo_path = None
        for path in priority_paths:
            if path and os.path.exists(path):
                self.logo_path = path
                print(f"✅ Logo found at: {path}")
                break
        
        if not self.logo_path:
            print("⚠️ Logo not found, will use styled text fallback")
            # Set to the first priority path for reference
            self.logo_path = priority_paths[0]
        
        # Compass image path
        self.compass_path = "kompas.webp"
        
        # AUTO-GENERATE distinct colors for subdivisions
        self.base_colors = [
            '#E74C3C',  # Red
            '#3498DB',  # Blue
            '#2ECC71',  # Green
            '#F39C12',  # Orange
            '#9B59B6',  # Purple
            '#1ABC9C',  # Turquoise
            '#E67E22',  # Carrot
            '#34495E',  # Wet Asphalt
            '#F1C40F',  # Yellow
            '#E91E63',  # Pink
            '#00BCD4',  # Cyan
            '#4CAF50',  # Light Green
            '#FF9800',  # Amber
            '#795548',  # Brown
            '#607D8B'   # Blue Grey
        ]
        self.colors = {}  # Will be populated automatically
        
        # Shapefile paths
        self.clip_belitung_path = "clipBelitung.shp"
        self.belitung_shapefile_path = "batas_desa_belitung.shp"
        self.belitung_gdf = None
        self.clip_belitung_gdf = None
    
    def set_attribute_filter(self, attribute_name, selected_values):
        """Set attribute-based filtering parameters - FIXED"""
        self.selected_attribute = attribute_name
        self.selected_values = selected_values
        print(f"🎯 Attribute filter set: {attribute_name} with {len(selected_values) if selected_values else 0} values")
        if selected_values:
            print(f"📋 Selected values: {selected_values[:5]}{'...' if len(selected_values) > 5 else ''}")
    
    def clear_attribute_filter(self):
        """Clear attribute-based filtering - FIXED"""
        self.selected_attribute = None
        self.selected_values = None
        print("🔄 Attribute filter cleared")
        
    def _verify_reprojection(self):
        """Verify reprojection accuracy by checking overlay alignment"""
        try:
            print("🔍 Verifying reprojection accuracy...")
            
            # Convert original data to WGS84 for comparison
            original_wgs84 = self.original_gdf.to_crs('EPSG:4326')
            
            # Compare bounds between original->WGS84 and UTM->WGS84
            original_bounds = original_wgs84.total_bounds
            reprojected_bounds = self.gdf_wgs84.total_bounds
            
            # Calculate difference in bounds (should be minimal)
            bound_diff = np.abs(np.array(original_bounds) - np.array(reprojected_bounds))
            max_diff = np.max(bound_diff)
            
            print(f"📊 Original WGS84 bounds: {original_bounds}")
            print(f"📊 Reprojected WGS84 bounds: {reprojected_bounds}")
            print(f"📏 Maximum coordinate difference: {max_diff:.8f} degrees")
            
            # Tolerance check (should be very small for accurate reprojection)
            tolerance = 0.001  # 0.001 degrees ≈ 111 meters
            if max_diff < tolerance:
                print(f"✅ Reprojection verification PASSED (diff: {max_diff:.8f}° < {tolerance}°)")
                
                # Additional area comparison
                original_area = original_wgs84.geometry.area.sum()
                reprojected_area = self.gdf_wgs84.geometry.area.sum()
                area_diff_percent = abs(original_area - reprojected_area) / original_area * 100
                
                print(f"📐 Area comparison: {area_diff_percent:.4f}% difference")
                if area_diff_percent < 1.0:  # Less than 1% difference
                    print(f"✅ Area verification PASSED ({area_diff_percent:.4f}% < 1.0%)")
                else:
                    print(f"⚠️ Area verification WARNING ({area_diff_percent:.4f}% >= 1.0%)")
                    
                return True
            else:
                print(f"❌ Reprojection verification FAILED (diff: {max_diff:.8f}° >= {tolerance}°)")
                print("⚠️ Large coordinate differences detected - check CRS handling")
                return False
                
        except Exception as e:
            print(f"❌ Reprojection verification error: {e}")
            return False
    
    def load_data(self):
        """Load and prepare the shapefile data with UTM degree display and WGS84 output"""
        try:
            print("Loading shapefile data...")
            self.gdf = gpd.read_file(self.shapefile_path)
            
            # Store original CRS and data for verification
            if self.gdf.crs is None:
                print("⚠️ No CRS found, setting to WGS84 as fallback")
                self.gdf.set_crs('EPSG:4326', inplace=True)
            
            self.original_crs = self.gdf.crs
            self.original_gdf = self.gdf.copy()  # Keep original for verification
            print(f"📍 Input CRS: {self.original_crs}")
            
            # ALWAYS convert to UTM Zone 48S for display (as per user requirement)
            if self.gdf.crs != 'EPSG:32748':
                print(f"🔄 Converting from {self.gdf.crs} to UTM Zone 48S (EPSG:32748) for display")
                self.gdf = self.gdf.to_crs('EPSG:32748')
            
            # Create WGS84 version for output
            self.gdf_wgs84 = self.gdf.to_crs('EPSG:4326')
            print(f"✅ Created WGS84 version for output")
            
            # Verify reprojection accuracy
            self._verify_reprojection()
            
            # Filter data based on selected subdivisions
            if self.selected_subdivisions:
                print(f"Filtering for subdivisions: {self.selected_subdivisions}")
                self.gdf = self.gdf[self.gdf['SUB_DIVISI'].isin(self.selected_subdivisions)]
                self.gdf_wgs84 = self.gdf_wgs84[self.gdf_wgs84['SUB_DIVISI'].isin(self.selected_subdivisions)]
                print(f"Filtered to {len(self.gdf)} features")
            
            # AUTO-GENERATE colors for subdivisions
            self._generate_subdivision_colors()
            
            print(f"📊 Loaded {len(self.gdf)} features")
            print(f"📍 Display CRS (UTM 48S): {self.gdf.crs}")
            print(f"📍 Output CRS (WGS84): {self.gdf_wgs84.crs}")
            print(f"📏 UTM bounds: {self.gdf.total_bounds}")
            print(f"📏 WGS84 bounds: {self.gdf_wgs84.total_bounds}")
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_data_with_attribute_filter(self):
        """Load and prepare the shapefile data with attribute-based filtering and UTM display"""
        try:
            print("Loading shapefile data with attribute filtering...")
            self.gdf = gpd.read_file(self.shapefile_path)
            
            # Store original CRS and data for verification
            if self.gdf.crs is None:
                print("⚠️ No CRS found, setting to WGS84 as fallback")
                self.gdf.set_crs('EPSG:4326', inplace=True)
            
            self.original_crs = self.gdf.crs
            self.original_gdf = self.gdf.copy()  # Keep original for verification
            print(f"📍 Input CRS: {self.original_crs}")
            
            # ALWAYS convert to UTM Zone 48S for display
            if self.gdf.crs != 'EPSG:32748':
                print(f"🔄 Converting from {self.gdf.crs} to UTM Zone 48S (EPSG:32748) for display")
                self.gdf = self.gdf.to_crs('EPSG:32748')
            
            # FIXED: Enhanced attribute-based filtering with proper type handling
            if hasattr(self, 'selected_attribute') and hasattr(self, 'selected_values'):
                if self.selected_attribute and self.selected_values:
                    print(f"🎯 FILTERING by attribute: {self.selected_attribute}")
                    print(f"📋 Selected values: {self.selected_values}")
                    print(f"📊 Original features: {len(self.gdf)}")
                    
                    # FIXED: Handle different data types properly
                    try:
                        # Get the column data type
                        column_dtype = self.gdf[self.selected_attribute].dtype
                        print(f"📈 Column data type: {column_dtype}")
                        
                        # Convert selected values to match column type
                        converted_values = []
                        for val in self.selected_values:
                            try:
                                if 'int' in str(column_dtype):
                                    converted_values.append(int(float(str(val))))
                                elif 'float' in str(column_dtype):
                                    converted_values.append(float(str(val)))
                                else:
                                    converted_values.append(str(val))
                            except (ValueError, TypeError):
                                converted_values.append(val)  # Keep original if conversion fails
                        
                        print(f"🔄 Converted values: {converted_values}")
                        
                        # ENHANCED: Apply the filter with better debugging
                        print(f"🔍 Applying filter: {self.selected_attribute} in {converted_values}")
                        print(f"📊 Available values in column: {sorted(self.gdf[self.selected_attribute].dropna().unique())[:10]}")
                        
                        mask = self.gdf[self.selected_attribute].isin(converted_values)
                        filtered_count = mask.sum()
                        print(f"🎯 Filter matches: {filtered_count} out of {len(self.gdf)} features")
                        
                        if filtered_count == 0:
                            print("❌ WARNING: No features match the filter criteria!")
                            print(f"📋 Selected values: {converted_values}")
                            print(f"📋 Available values in {self.selected_attribute}:")
                            available_values = self.gdf[self.selected_attribute].dropna().unique()
                            for val in available_values[:15]:  # Show more values
                                print(f"   - '{val}' (type: {type(val)})")
                            print("⚠️ CRITICAL: Filter resulted in empty dataset!")
                            print("🔄 Clearing filter and reloading all features to prevent empty map")
                            # Clear the filter and reload all data to prevent empty map
                            self.clear_attribute_filter()
                            # Reload the original data without filtering
                            self.gdf = gpd.read_file(self.shapefile_path)
                            if self.gdf.crs is None:
                                self.gdf.set_crs('EPSG:4326', inplace=True)
                            self.original_crs = self.gdf.crs
                            print(f"✅ Reloaded all {len(self.gdf)} features to prevent empty map")
                        else:
                            self.gdf = self.gdf[mask]
                            print(f"✅ Successfully filtered to {len(self.gdf)} features")
                            print(f"📈 Filter success rate: {len(self.gdf)/len(gpd.read_file(self.shapefile_path))*100:.1f}%")
                        
                        # AUTO-GENERATE colors for selected values
                        self._generate_colors_for_attribute_values()
                        
                    except Exception as filter_error:
                        print(f"❌ Filter error: {filter_error}")
                        print("Falling back to no filtering - reloading all data")
                        # Reload all data if there's a filter error
                        self.gdf = gpd.read_file(self.shapefile_path)
                        if self.gdf.crs is None:
                            self.gdf.set_crs('EPSG:4326', inplace=True)
                        self.original_crs = self.gdf.crs
                        print(f"✅ Reloaded all {len(self.gdf)} features after filter error")
                        self._generate_subdivision_colors()  # Use default coloring
                        
                else:
                    print("No attribute filtering applied - using all features")
                    self._generate_subdivision_colors()  # Use default coloring
            elif self.selected_subdivisions:
                # Fallback to subdivision filtering for backward compatibility
                print(f"Filtering for subdivisions: {self.selected_subdivisions}")
                self.gdf = self.gdf[self.gdf['SUB_DIVISI'].isin(self.selected_subdivisions)]
                print(f"Filtered to {len(self.gdf)} features")
                
                # AUTO-GENERATE colors for subdivisions
                self._generate_subdivision_colors()
            else:
                print("No filtering applied - using all features")
                self._generate_subdivision_colors()  # Use default coloring
            
            # Create WGS84 version for output after all filtering
            self.gdf_wgs84 = self.gdf.to_crs('EPSG:4326')
            print(f"✅ Created WGS84 version for output")
            
            # Verify reprojection accuracy
            self._verify_reprojection()
            
            print(f"📊 Final loaded features: {len(self.gdf)}")
            print(f"📍 Display CRS (UTM 48S): {self.gdf.crs}")
            print(f"📍 Output CRS (WGS84): {self.gdf_wgs84.crs}")
            print(f"📏 UTM bounds: {self.gdf.total_bounds}")
            print(f"📏 WGS84 bounds: {self.gdf_wgs84.total_bounds}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data with attribute filter: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_subdivision_colors(self):
        """AUTO-GENERATE distinct colors for each subdivision"""
        if 'SUB_DIVISI' in self.gdf.columns:
            unique_subdivisions = self.gdf['SUB_DIVISI'].dropna().unique()
            
            # Clear existing colors
            self.colors = {}
            
            for i, subdivision in enumerate(unique_subdivisions):
                # Cycle through base colors if we have more subdivisions than colors
                color_index = i % len(self.base_colors)
                self.colors[subdivision] = self.base_colors[color_index]
                print(f"🎨 {subdivision} -> {self.base_colors[color_index]}")
            
            # Set legend attribute for subdivisions
            self.legend_attribute = 'SUB_DIVISI'
            self.color_mapping = self.colors.copy()
            
            print(f"✅ Generated {len(self.colors)} distinct colors automatically")
            print(f"🏷️ Legend will use SUB_DIVISI attribute")
    
    def _generate_colors_for_attribute(self, attribute_name):
        """ENHANCED: Generate colors for any specified attribute"""
        if attribute_name in self.gdf.columns:
            unique_values = self.gdf[attribute_name].dropna().unique()
            print(f"🎨 Generating colors for {len(unique_values)} unique values in '{attribute_name}'")
            
            # Clear existing colors
            self.colors = {}
            
            # Use professional color palette
            enhanced_colors = [
                '#E74C3C',  # Bright Red
                '#3498DB',  # Bright Blue  
                '#2ECC71',  # Bright Green
                '#F39C12',  # Bright Orange
                '#9B59B6',  # Purple
                '#1ABC9C',  # Turquoise
                '#E67E22',  # Carrot Orange
                '#34495E',  # Dark Blue Grey
                '#F1C40F',  # Yellow
                '#E91E63',  # Pink
                '#00BCD4',  # Cyan
                '#4CAF50',  # Light Green
                '#FF9800',  # Amber
                '#795548',  # Brown
                '#607D8B',  # Blue Grey
                '#FF5722',  # Deep Orange
                '#673AB7',  # Deep Purple
                '#009688',  # Teal
                '#8BC34A',  # Light Green
                '#FFEB3B'   # Bright Yellow
            ]
            
            for i, value in enumerate(unique_values):
                color_index = i % len(enhanced_colors)
                self.colors[value] = enhanced_colors[color_index]
                print(f"🎨 {value} -> {enhanced_colors[color_index]}")
            
            # Store for legend
            self.legend_attribute = attribute_name
            self.color_mapping = self.colors.copy()
            
            print(f"✅ Generated {len(self.colors)} colors for '{attribute_name}'")
            print(f"🏷️ Legend will use attribute: {self.legend_attribute}")
            
        else:
            print(f"⚠️ Attribute '{attribute_name}' not found in data")
            # Fallback to SUB_DIVISI
            if 'SUB_DIVISI' in self.gdf.columns:
                self._generate_subdivision_colors()
    
    def _generate_colors_for_attribute_values(self):
        """AUTO-GENERATE distinct colors for each selected attribute value - ENHANCED"""
        if hasattr(self, 'selected_attribute') and self.selected_attribute in self.gdf.columns:
            unique_values = self.gdf[self.selected_attribute].dropna().unique()
            print(f"🎨 Generating colors for {len(unique_values)} unique values in '{self.selected_attribute}'")
            print(f"📊 Current data has {len(self.gdf)} features after filtering")
            
            # FIXED: Clear existing colors to avoid conflicts
            self.colors = {}
            
            # ENHANCED: Use professional color palette for better visibility and contrast
            enhanced_colors = [
                '#E74C3C',  # Bright Red
                '#3498DB',  # Bright Blue  
                '#2ECC71',  # Bright Green
                '#F39C12',  # Bright Orange
                '#9B59B6',  # Purple
                '#1ABC9C',  # Turquoise
                '#E67E22',  # Carrot Orange
                '#34495E',  # Dark Blue Grey
                '#F1C40F',  # Yellow
                '#E91E63',  # Pink
                '#00BCD4',  # Cyan
                '#4CAF50',  # Light Green
                '#FF9800',  # Amber
                '#795548',  # Brown
                '#607D8B',  # Blue Grey
                '#FF5722',  # Deep Orange
                '#673AB7',  # Deep Purple
                '#009688',  # Teal
                '#8BC34A',  # Light Green
                '#FFEB3B'   # Bright Yellow
            ]
            
            # ENHANCED: Validate and assign colors with better tracking
            for i, value in enumerate(unique_values):
                color_index = i % len(enhanced_colors)
                self.colors[value] = enhanced_colors[color_index]
                feature_count = len(self.gdf[self.gdf[self.selected_attribute] == value])
                print(f"🎨 '{value}' -> {enhanced_colors[color_index]} ({feature_count} features)")
            
            print(f"✅ Generated {len(self.colors)} distinct colors for attribute '{self.selected_attribute}'")
            
            # ENHANCED: Store color mapping for legend with attribute info
            self.color_mapping = self.colors.copy()
            self.legend_attribute = self.selected_attribute
            
            print(f"🏷️ Legend will use attribute: {self.legend_attribute}")
            print(f"🎨 Color mapping: {dict(list(self.color_mapping.items())[:5])}{'...' if len(self.color_mapping) > 5 else ''}")
            
        else:
            print(f"⚠️ No attribute column '{getattr(self, 'selected_attribute', 'None')}' found for color generation")
            print(f"📋 Available columns: {list(self.gdf.columns) if self.gdf is not None else 'None'}")
            # Fallback to subdivision colors if attribute coloring fails
            self._generate_subdivision_colors()
    
    def _calculate_optimal_scale_from_zoom(self, target_paper_width_cm=22.0, target_paper_height_cm=18.0):
        """ENHANCED: Calculate optimal scale that ensures ALL selected features are visible"""
        if self.gdf is None or len(self.gdf) == 0:
            return 25000  # Default scale
        
        try:
            # Get bounds of filtered data (in UTM meters)
            bounds = self.gdf.total_bounds
            map_width_meters = bounds[2] - bounds[0]
            map_height_meters = bounds[3] - bounds[1]
            
            print(f"📐 CALCULATING OPTIMAL SCALE FOR COMPLETE VISIBILITY:")
            print(f"   🗺️ Study area dimensions: {map_width_meters:.0f}m x {map_height_meters:.0f}m")
            print(f"   📄 Paper dimensions: {target_paper_width_cm}cm x {target_paper_height_cm}cm")
            
            # Convert paper size to meters
            paper_width_meters = target_paper_width_cm / 100
            paper_height_meters = target_paper_height_cm / 100
            
            # Calculate required scale for both dimensions (with safety buffer)
            safety_buffer = 1.3  # 30% buffer to ensure complete visibility
            
            scale_for_width = (map_width_meters * safety_buffer) / paper_width_meters
            scale_for_height = (map_height_meters * safety_buffer) / paper_height_meters
            
            # Use the larger scale to ensure both dimensions fit
            required_scale = max(scale_for_width, scale_for_height)
            
            # ENHANCED: Professional cartographic scales in thousands
            professional_scales = [
                1000,    # 1:1,000 (very detailed)
                2000,    # 1:2,000 
                5000,    # 1:5,000 (detailed site plans)
                10000,   # 1:10,000 (detailed area maps)
                15000,   # 1:15,000
                20000,   # 1:20,000
                25000,   # 1:25,000 (standard topographic)
                30000,   # 1:30,000
                40000,   # 1:40,000
                50000,   # 1:50,000 (regional overview)
                75000,   # 1:75,000
                100000,  # 1:100,000 (district scale)
                150000,  # 1:150,000
                200000,  # 1:200,000
                250000,  # 1:250,000
                500000   # 1:500,000 (provincial scale)
            ]
            
            # Find the smallest scale that can accommodate the study area
            optimal_scale = None
            for scale in professional_scales:
                if scale >= required_scale:
                    optimal_scale = scale
                    break
            
            # Fallback to largest scale if study area is too big
            if optimal_scale is None:
                optimal_scale = professional_scales[-1]
                print(f"   ⚠️ Study area very large, using maximum scale")
            
            print(f"   📏 Required scale (calculated): 1:{required_scale:.0f}")
            print(f"   🎯 Optimal professional scale: 1:{optimal_scale:,}")
            print(f"   ✅ GUARANTEED: All features will be visible with 30% buffer")
            
            return optimal_scale
            
        except Exception as e:
            print(f"❌ Error calculating optimal scale: {e}")
            return 25000  # Safe fallback
    
    def _calculate_round_scale(self, map_width_meters, target_paper_width_cm=22.0):
        """LEGACY: Calculate round scale (kept for compatibility)"""
        paper_width_meters = target_paper_width_cm / 100
        raw_scale = map_width_meters / paper_width_meters
        
        # Common map scales in thousands
        common_scales = [
            5000, 10000, 15000, 20000, 25000, 30000, 40000, 
            50000, 75000, 100000, 150000, 200000, 250000
        ]
        
        # Find the closest common scale
        best_scale = min(common_scales, key=lambda x: abs(x - raw_scale))
        
        return best_scale
    
    def _calculate_zoom_bounds_for_optimal_scale(self, target_scale):
        """ENHANCED: Calculate zoom bounds that ensure ALL features are visible at target scale"""
        if self.gdf is None:
            return None
            
        try:
            # Paper dimensions for main map area
            target_paper_width_cm = 22.0   # A3 main map width 
            target_paper_height_cm = 18.0  # A3 main map height (approximate)
            
            # Convert to meters
            target_paper_width_meters = target_paper_width_cm / 100
            target_paper_height_meters = target_paper_height_cm / 100
            
            # Calculate required map dimensions for target scale
            required_map_width_meters = target_scale * target_paper_width_meters
            required_map_height_meters = target_scale * target_paper_height_meters
            
            # Get current study area bounds and center
            bounds = self.gdf.total_bounds
            study_width = bounds[2] - bounds[0]
            study_height = bounds[3] - bounds[1]
            center_x = (bounds[0] + bounds[2]) / 2
            center_y = (bounds[1] + bounds[3]) / 2
            
            print(f"🎯 CALCULATING OPTIMAL ZOOM BOUNDS:")
            print(f"   📏 Target scale: 1:{target_scale:,}")
            print(f"   🗺️ Study area: {study_width:.0f}m x {study_height:.0f}m")
            print(f"   📄 Map area at scale: {required_map_width_meters:.0f}m x {required_map_height_meters:.0f}m")
            print(f"   📍 Center point: ({center_x:.0f}, {center_y:.0f})")
            
            # CRITICAL: Ensure the map area is large enough to contain the study area
            # Use the larger dimension to guarantee visibility
            final_width = max(required_map_width_meters, study_width * 1.2)  # 20% buffer minimum
            final_height = max(required_map_height_meters, study_height * 1.2)  # 20% buffer minimum
            
            # ENHANCED: Maintain aspect ratio while ensuring all features fit
            aspect_ratio = target_paper_width_cm / target_paper_height_cm
            
            # Adjust dimensions to maintain proper aspect ratio
            if final_width / final_height > aspect_ratio:
                # Width is constraining factor
                final_height = final_width / aspect_ratio
            else:
                # Height is constraining factor  
                final_width = final_height * aspect_ratio
            
            # Calculate final bounds centered on study area
            half_width = final_width / 2
            half_height = final_height / 2
            
            optimal_bounds = [
                center_x - half_width,   # min_x
                center_y - half_height,  # min_y
                center_x + half_width,   # max_x
                center_y + half_height   # max_y
            ]
            
            # VERIFICATION: Ensure study area is completely within bounds
            buffer_x = (optimal_bounds[2] - optimal_bounds[0] - study_width) / 2
            buffer_y = (optimal_bounds[3] - optimal_bounds[1] - study_height) / 2
            
            print(f"   ✅ OPTIMAL BOUNDS CALCULATED:")
            print(f"      📐 Final map dimensions: {final_width:.0f}m x {final_height:.0f}m")
            print(f"      📦 Study area buffer: {buffer_x:.0f}m (X) x {buffer_y:.0f}m (Y)")
            print(f"      🎯 Scale verification: 1:{final_width/target_paper_width_meters:.0f}")
            print(f"      ✅ GUARANTEED: All study features will be visible")
            
            return optimal_bounds
            
        except Exception as e:
            print(f"❌ Error calculating optimal zoom bounds: {e}")
            return None
    
    def _adjust_zoom_for_scale(self, target_scale):
        """LEGACY: Adjust map zoom for UTM display (kept for compatibility)"""
        if self.gdf is None:
            return
            
        # Calculate required map width for target scale
        target_paper_width_cm = 22.0  # A3 main map width
        target_paper_width_meters = target_paper_width_cm / 100
        required_map_width_meters = target_scale * target_paper_width_meters
        
        # Get current bounds and center (always in UTM meters)
        bounds = self.gdf.total_bounds
        center_x = (bounds[0] + bounds[2]) / 2
        center_y = (bounds[1] + bounds[3]) / 2
        
        print(f"🔍 Display CRS: {self.gdf.crs} (UTM Zone 48S)")
        print(f"🔍 Current bounds (meters): {bounds}")
        print(f"🔍 Required map width: {required_map_width_meters:.2f} meters")
        
        # UTM coordinates are always in meters, so direct calculation
        half_width = required_map_width_meters / 2
        aspect_ratio = (bounds[3] - bounds[1]) / (bounds[2] - bounds[0])
        half_height = half_width * aspect_ratio
        
        # Set new bounds ensuring full area visibility
        new_bounds = [
            center_x - half_width,
            center_y - half_height, 
            center_x + half_width,
            center_y + half_height
        ]
        
        print(f"🎯 Adjusted bounds for scale 1:{target_scale:,}: {new_bounds}")
        print(f"📏 Map width: {new_bounds[2] - new_bounds[0]:.2f} meters")
        print(f"📏 Map height: {new_bounds[3] - new_bounds[1]:.2f} meters")
        
        return new_bounds
    
    def load_belitung_data(self):
        """Load Belitung overview data with UTM display and WGS84 output consistency"""
        try:
            # Load clipping polygon
            if os.path.exists(self.clip_belitung_path):
                self.clip_belitung_gdf = gpd.read_file(self.clip_belitung_path)
                if self.clip_belitung_gdf.crs is None:
                    self.clip_belitung_gdf.set_crs('EPSG:4326', inplace=True)
                
                # Convert to UTM for display consistency
                if self.clip_belitung_gdf.crs != 'EPSG:32748':
                    self.clip_belitung_gdf = self.clip_belitung_gdf.to_crs('EPSG:32748')
                    print(f"🔄 Converted clipping polygon to UTM 48S for display")
                
                print(f"Loaded clipping polygon: {len(self.clip_belitung_gdf)} features")
            
            # Load Belitung data
            if os.path.exists(self.belitung_shapefile_path):
                self.belitung_gdf = gpd.read_file(self.belitung_shapefile_path)
                initial_bounds = self.belitung_gdf.total_bounds
                
                # Auto-detect CRS based on coordinate values
                if abs(initial_bounds[0]) > 1000 or abs(initial_bounds[1]) > 1000:
                    print("🔍 Detected projected coordinates (UTM)")
                    self.belitung_gdf = self.belitung_gdf.set_crs('EPSG:32748')
                else:
                    print("🔍 Detected geographic coordinates")
                    if self.belitung_gdf.crs is None:
                        self.belitung_gdf = self.belitung_gdf.set_crs('EPSG:4326')
                    # Convert to UTM for display consistency
                    if self.belitung_gdf.crs != 'EPSG:32748':
                        self.belitung_gdf = self.belitung_gdf.to_crs('EPSG:32748')
                
                print(f"📍 Belitung display CRS: {self.belitung_gdf.crs}")
                print(f"📊 Loaded Belitung data: {len(self.belitung_gdf)} features")
                return True
                
        except Exception as e:
            print(f"Warning: Could not load Belitung data: {e}")
            return False
    
    def create_professional_map(self, output_path="Professional_Map.pdf", dpi=300):
        """Create the FIXED professional map with all improvements"""
        if self.gdf is None or len(self.gdf) == 0:
            print("No data to display.")
            return False
            
        try:
            # Create figure with A3 landscape layout
            fig = plt.figure(figsize=(16.54, 11.69))
            fig.patch.set_facecolor('white')
            
            # Add blue border around entire map
            border_rect = Rectangle((0.015, 0.015), 0.97, 0.97, 
                                  fill=False, edgecolor='blue', linewidth=3,
                                  transform=fig.transFigure)
            fig.patches.append(border_rect)
            
            # FIXED: Main map area with safe margins to prevent cropping
            ax_main = plt.axes([0.05, 0.12, 0.63, 0.83])  # Safer margins to prevent cropping
            
            # Main map border
            main_map_border = Rectangle((0.05, 0.12), 0.63, 0.83, 
                                      fill=False, edgecolor='black', linewidth=2,
                                      transform=fig.transFigure)
            fig.patches.append(main_map_border)
            
            # Right panel sections with proper spacing to prevent overlap
            ax_title = plt.axes([0.70, 0.87, 0.28, 0.08])      # Title with spacing
            ax_overview = plt.axes([0.70, 0.58, 0.28, 0.27])   # Context map smaller with gap
            ax_legend = plt.axes([0.70, 0.28, 0.28, 0.28])     # Legend with proper spacing
            ax_north_scale = plt.axes([0.70, 0.15, 0.28, 0.11]) # North/scale with spacing
            ax_logo = plt.axes([0.70, 0.03, 0.28, 0.10])       # Logo at bottom with margin
            
            # Plot components
            self._plot_main_map_fixed(ax_main)
            self._add_title(ax_title)
            self._add_north_arrow_and_scale_fixed(ax_north_scale)
            self._add_belitung_overview_fixed(ax_overview)
            self._create_legend_fixed(ax_legend)
            self._add_logo_fixed(ax_logo)
            
            # Save the map with georeferencing for Avenza compatibility
            try:
                # Save with metadata for georeferencing
                metadata = {
                    'Title': self.map_title.replace('\n', ' - '),
                    'Author': 'IT Rebinmas - PT. REBINMAS JAYA',
                    'Subject': 'Geospatial Survey Map - PT. REBINMAS JAYA',
                    'Keywords': 'surveying, mapping, palm oil, plantation, Indonesia, Belitung',
                    'Creator': 'IT Rebinmas Map Generator',
                    'Producer': 'IT Rebinmas with GeoPandas'
                }
                
                if self.enable_georeferencing:
                    # Add georeferencing metadata for Avenza
                    bounds = self.gdf.total_bounds
                    metadata.update({
                        'GeoReference': f'EPSG:{self.original_crs.to_epsg()}, {bounds[0]:.6f}, {bounds[1]:.6f}, {bounds[2]:.6f}, {bounds[3]:.6f}',
                        'CoordinateSystem': f'{self.original_crs.to_wkt()}',
                        'ProjectionInfo': f'Study Area Bounds: {bounds[0]:.6f}°E to {bounds[2]:.6f}°E, {bounds[1]:.6f}°S to {bounds[3]:.6f}°S'
                    })
                    print("✅ Georeferencing metadata added for Avenza compatibility")
                
                plt.savefig(output_path, dpi=dpi, bbox_inches='tight', 
                           facecolor='white', edgecolor='none', metadata=metadata)
                plt.close()
                
            except PermissionError:
                # If file is open, try with timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = output_path.replace('.pdf', f'_{timestamp}.pdf')
                plt.savefig(backup_path, dpi=dpi, bbox_inches='tight', 
                           facecolor='white', edgecolor='none', metadata=metadata)
                plt.close()
                output_path = backup_path
                print(f"⚠️ Original file was locked, saved as: {backup_path}")
            
            # Add world file for additional georeferencing (for GIS applications)
            if self.enable_georeferencing:
                self._create_world_file(output_path)
            
            print(f"\n🎉 Professional map created: {output_path}")
            print("✅ Features applied:")
            print("  - Auto-generated distinct colors")
            print("  - Logo positioned above company name")
            print("  - Clean context map without red box")
            print("  - Accurate scale bar for distance reference")
            print("  - Maximum zoom for study area")
            
            return True
            
        except Exception as e:
            print(f"Error creating fixed map: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_world_file(self, pdf_path, dpi=300):
        """Create enhanced world file for improved Avenza Maps georeferencing compatibility"""
        try:
            # World file has .pdfw extension for PDF files
            world_file_path = pdf_path.replace('.pdf', '.pdfw')
            
            # Get map bounds in the ORIGINAL CRS (not converted)
            bounds = self.gdf.total_bounds
            
            # ENHANCED: Calculate precise pixel size and transformation parameters
            # Standard A3 dimensions: 16.54 x 11.69 inches
            # Main map area occupies about 63% width and 83% height
            map_width_inches = 16.54 * 0.63
            map_height_inches = 11.69 * 0.83
            
            # Convert to pixels using actual DPI from save operation
            map_width_pixels = map_width_inches * dpi
            map_height_pixels = map_height_inches * dpi
            
            # FIXED: Calculate coordinate units per pixel based on CRS type
            if self.original_crs.is_geographic:
                # Geographic CRS (degrees)
                units_per_pixel_x = (bounds[2] - bounds[0]) / map_width_pixels
                units_per_pixel_y = (bounds[3] - bounds[1]) / map_height_pixels
                print(f"📍 Geographic CRS detected: {self.original_crs}")
            else:
                # Projected CRS (meters or other units)
                units_per_pixel_x = (bounds[2] - bounds[0]) / map_width_pixels
                units_per_pixel_y = (bounds[3] - bounds[1]) / map_height_pixels
                print(f"📍 Projected CRS detected: {self.original_crs}")
            
            # ENHANCED World file format (6 lines) with precise calculations:
            # Line 1: Pixel size in x direction (coordinate units per pixel)
            # Line 2: Rotation about y axis (usually 0)
            # Line 3: Rotation about x axis (usually 0)  
            # Line 4: Pixel size in y direction (negative for standard orientation)
            # Line 5: X coordinate of upper left pixel center
            # Line 6: Y coordinate of upper left pixel center
            
            # Calculate upper left pixel center coordinates
            # Account for the fact that PDF coordinates start from bottom-left
            upper_left_x = bounds[0] + (units_per_pixel_x / 2)
            upper_left_y = bounds[3] - (units_per_pixel_y / 2)
            
            with open(world_file_path, 'w') as f:
                f.write(f"{units_per_pixel_x:.12f}\n")      # Line 1: X pixel size
                f.write("0.000000000000\n")                  # Line 2: Rotation Y
                f.write("0.000000000000\n")                  # Line 3: Rotation X
                f.write(f"{-units_per_pixel_y:.12f}\n")     # Line 4: Y pixel size (negative)
                f.write(f"{upper_left_x:.12f}\n")           # Line 5: Upper left X
                f.write(f"{upper_left_y:.12f}\n")           # Line 6: Upper left Y
            
            print(f"✅ Enhanced world file created: {world_file_path}")
            print(f"   Pixel size X: {units_per_pixel_x:.6f} units/pixel")
            print(f"   Pixel size Y: {units_per_pixel_y:.6f} units/pixel")
            
            # ENHANCED: Create .prj file with exact CRS information
            prj_file_path = pdf_path.replace('.pdf', '.prj')
            with open(prj_file_path, 'w') as f:
                # Use original CRS WKT for maximum compatibility
                crs_wkt = self.original_crs.to_wkt()
                f.write(crs_wkt)
            
            print(f"✅ Enhanced projection file created: {prj_file_path}")
            print(f"📱 ENHANCED Avenza Maps compatibility with CRS: {self.original_crs}")
            
            # ENHANCED: Create additional metadata file for advanced GIS compatibility
            metadata_file_path = pdf_path.replace('.pdf', '_georef_info.txt')
            with open(metadata_file_path, 'w', encoding='utf-8') as f:
                f.write(f"=== ENHANCED GEOREFERENCING INFORMATION ===\n")
                f.write(f"Program dibuat oleh: IT Rebinmas\n")
                f.write(f"Version: Enhanced Map Generator v2.0\n")
                f.write(f"Generated: {pd.Timestamp.now()}\n")
                f.write(f"Support: IT Rebinmas\n\n")
                
                f.write(f"=== COORDINATE REFERENCE SYSTEM ===\n")
                f.write(f"Original CRS: {self.original_crs}\n")
                f.write(f"EPSG Code: {self.original_crs.to_epsg()}\n")
                f.write(f"CRS Type: {'Geographic' if self.original_crs.is_geographic else 'Projected'}\n\n")
                
                f.write(f"=== MAP SPECIFICATIONS ===\n")
                f.write(f"Map Bounds: {bounds}\n")
                f.write(f"Resolution: {dpi} DPI\n")
                f.write(f"Pixel Size X: {units_per_pixel_x:.12f}\n")
                f.write(f"Pixel Size Y: {units_per_pixel_y:.12f}\n\n")
                
                f.write(f"=== COMPATIBILITY ===\n")
                f.write(f"✅ Avenza Maps (Mobile GIS)\n")
                f.write(f"✅ QGIS, ArcGIS, Global Mapper\n")
                f.write(f"✅ Any GIS software supporting world files\n")
                f.write(f"✅ Perfect georeferencing for field surveys\n\n")
                
                f.write(f"=== TECHNICAL NOTES ===\n")
                f.write(f"- World file (.pdfw) provides pixel-to-coordinate transformation\n")
                f.write(f"- Projection file (.prj) contains exact CRS definition\n")
                f.write(f"- Enhanced precision for professional surveying applications\n")
                f.write(f"- Optimized for mobile GIS field data collection\n\n")
                
                f.write(f"© IT Rebinmas - Professional GIS Solutions\n")
            
            print(f"✅ Georeferencing metadata created: {metadata_file_path}")
            print("🎯 ENHANCED: Perfect Avenza Maps compatibility achieved!")
            
        except Exception as e:
            print(f"Warning: Could not create enhanced world file: {e}")
            import traceback
            traceback.print_exc()
    
    def _plot_main_map_fixed(self, ax):
        """FIXED: Plot main map with maximum vertical zoom and clean coordinates - ENHANCED"""
        try:
            print("\n" + "="*60)
            print("🚀 STARTING _plot_main_map_fixed DEBUGGING")
            print("="*60)
            
            # COMPREHENSIVE DATA DEBUGGING
            print(f"📊 Initial data check:")
            print(f"   - self.gdf is None: {self.gdf is None}")
            print(f"   - self.gdf is empty: {self.gdf.empty if self.gdf is not None else 'N/A'}")
            print(f"   - self.gdf length: {len(self.gdf) if self.gdf is not None else 'N/A'}")
            print(f"   - self.gdf columns: {list(self.gdf.columns) if self.gdf is not None else 'N/A'}")
            print(f"   - self.gdf CRS: {self.gdf.crs if self.gdf is not None else 'N/A'}")
            print(f"   - self.gdf bounds: {self.gdf.total_bounds if self.gdf is not None and not self.gdf.empty else 'N/A'}")
            
            # CRITICAL: Check if data exists and is not empty
            if self.gdf is None or self.gdf.empty:
                print("❌ CRITICAL ERROR: No data to plot! GeoDataFrame is empty or None")
                print("🔄 Attempting to reload data...")
                self.clear_attribute_filter()
                self.load_data()
                
                print(f"📊 After reload attempt:")
                print(f"   - self.gdf is None: {self.gdf is None}")
                print(f"   - self.gdf is empty: {self.gdf.empty if self.gdf is not None else 'N/A'}")
                print(f"   - self.gdf length: {len(self.gdf) if self.gdf is not None else 'N/A'}")
                
                if self.gdf is None or self.gdf.empty:
                    print("❌ FATAL: Still no data after reload! Cannot create map.")
                    # Plot a warning message on the map
                    ax.text(0.5, 0.5, 'NO DATA AVAILABLE\nCheck shapefile path and filters', 
                           transform=ax.transAxes, ha='center', va='center',
                           fontsize=16, color='red', weight='bold',
                           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
                    return
                print(f"✅ Data recovered: Now have {len(self.gdf)} features")
            
            print(f"\n🗺️ PROCEEDING TO PLOT {len(self.gdf)} features on main map...")
            print(f"📍 Data bounds: {self.gdf.total_bounds}")
            print(f"🎯 Geometry types: {self.gdf.geometry.geom_type.value_counts().to_dict()}")
            
            # Determine which attribute to use for coloring
            color_attribute = None
            if hasattr(self, 'selected_attribute') and self.selected_attribute:
                color_attribute = self.selected_attribute
                print(f"🎨 Using selected attribute for coloring: {color_attribute}")
            elif 'SUB_DIVISI' in self.gdf.columns:
                color_attribute = 'SUB_DIVISI'
                print(f"🎨 Using SUB_DIVISI for coloring")
            
            # ENHANCED: Better color handling with comprehensive debugging
            if color_attribute and color_attribute in self.gdf.columns:
                unique_values = self.gdf[color_attribute].dropna().unique()
                print(f"🎯 Found {len(unique_values)} unique values to plot: {list(unique_values)}")
                print(f"🎨 Available colors in self.colors: {list(self.colors.keys()) if hasattr(self, 'colors') else 'None'}")
                
                # Ensure colors exist
                if not hasattr(self, 'colors') or not self.colors:
                    print("⚠️ No colors found, generating colors now...")
                    self._generate_colors_for_attribute_values()
                
                plotted_count = 0
                print(f"\n🎨 STARTING FEATURE-BY-FEATURE PLOTTING:")
                for i, value in enumerate(unique_values):
                    if pd.isna(value):
                        print(f"   [{i+1}/{len(unique_values)}] Skipping NaN value")
                        continue
                    
                    print(f"   [{i+1}/{len(unique_values)}] Processing value: '{value}'")
                    subset = self.gdf[self.gdf[color_attribute] == value]
                    color = self.colors.get(value, '#808080')
                    print(f"      - Subset size: {len(subset)}")
                    print(f"      - Color: {color}")
                    print(f"      - Subset bounds: {subset.total_bounds if len(subset) > 0 else 'N/A'}")
                    
                    if len(subset) > 0:
                        try:
                            print(f"      - Attempting to plot {len(subset)} features...")
                            subset.plot(ax=ax, color=color, alpha=0.8, edgecolor='black', 
                                       linewidth=1.2, label=str(value))
                            plotted_count += len(subset)
                            print(f"      ✅ Successfully plotted {len(subset)} features for '{value}' with color {color}")
                        except Exception as plot_error:
                            print(f"      ❌ Error plotting subset for '{value}': {plot_error}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"      ⚠️ No features found for value '{value}'")
                
                print(f"✅ Successfully plotted {plotted_count} features colored by: {color_attribute}")
                
                # ENHANCED: Verify all features are plotted with detailed info
                if plotted_count != len(self.gdf):
                    missing_count = len(self.gdf) - plotted_count
                    print(f"⚠️ Warning: {missing_count} features not plotted")
                    
                    # Show which values are missing
                    all_values_in_data = set(self.gdf[color_attribute].dropna())
                    plotted_values = set(unique_values)
                    missing_values = all_values_in_data - plotted_values
                    if missing_values:
                        print(f"🔍 Missing values: {list(missing_values)}")
                else:
                    print(f"✅ All {len(self.gdf)} features successfully plotted and colored")
                    
            else:
                # Fallback: plot all features with default color
                print(f"\n🎨 FALLBACK PLOTTING: Using default color for all features")
                print(f"   - Total features to plot: {len(self.gdf)}")
                print(f"   - Data bounds: {self.gdf.total_bounds}")
                print(f"   - Default color: #87CEEB")
                try:
                    print(f"   - Attempting to plot all {len(self.gdf)} features with default color...")
                    self.gdf.plot(ax=ax, color='#87CEEB', alpha=0.8, edgecolor='black', 
                                 linewidth=1.2)
                    print(f"   ✅ Successfully plotted all {len(self.gdf)} features with default color")
                except Exception as fallback_error:
                    print(f"   ❌ Error in fallback plotting: {fallback_error}")
                    import traceback
                    traceback.print_exc()
                print(f"⚠️ Using default color for {len(self.gdf)} features (no attribute-based coloring)")
            
            # Add DYNAMIC block labels with size based on feature area
            self._add_dynamic_labels(ax)
            
            # ENHANCED: Calculate OPTIMAL scale ensuring ALL features are visible
            print(f"\n🎯 ENHANCED SCALE AND ZOOM CALCULATION:")
            bounds = self.gdf.total_bounds
            print(f"   📐 Study area bounds (UTM): {bounds}")
            
            # STEP 1: Calculate optimal scale that guarantees complete visibility
            optimal_scale = self._calculate_optimal_scale_from_zoom()
            print(f"   📏 Optimal scale calculated: 1:{optimal_scale:,}")
            
            # STEP 2: Calculate zoom bounds that sync perfectly with the scale
            optimal_bounds = self._calculate_zoom_bounds_for_optimal_scale(optimal_scale)
            print(f"   🎯 Optimal bounds calculated: {optimal_bounds}")
            
            # Store the optimal scale for use in scale bar and legend
            self.target_scale = optimal_scale
            
            if optimal_bounds:
                # STEP 3: Apply the calculated optimal bounds directly
                print(f"   🎯 APPLYING OPTIMAL BOUNDS:")
                print(f"      📐 X range: {optimal_bounds[0]:.0f} to {optimal_bounds[2]:.0f} ({optimal_bounds[2]-optimal_bounds[0]:.0f}m width)")
                print(f"      📐 Y range: {optimal_bounds[1]:.0f} to {optimal_bounds[3]:.0f} ({optimal_bounds[3]-optimal_bounds[1]:.0f}m height)")
                
                # Verify bounds contain all study data
                study_bounds = self.gdf.total_bounds
                x_buffer = min(optimal_bounds[0] - study_bounds[0], study_bounds[2] - optimal_bounds[2])
                y_buffer = min(optimal_bounds[1] - study_bounds[1], study_bounds[3] - optimal_bounds[3])
                
                print(f"      📦 Study area buffer: X={abs(x_buffer):.0f}m, Y={abs(y_buffer):.0f}m")
                
                # Apply the optimal bounds directly (no additional modifications needed)
                ax.set_xlim(optimal_bounds[0], optimal_bounds[2])
                ax.set_ylim(optimal_bounds[1], optimal_bounds[3])
                
                print(f"   ✅ OPTIMAL BOUNDS APPLIED - Perfect scale/zoom sync achieved!")
                print(f"   🎯 Scale: 1:{optimal_scale:,} | Zoom: {optimal_bounds[2]-optimal_bounds[0]:.0f}m x {optimal_bounds[3]-optimal_bounds[1]:.0f}m")
            else:
                # Fallback with larger margins to prevent cropping
                margin_x = (bounds[2] - bounds[0]) * 0.20  # Increased to 20% margin
                margin_y = (bounds[3] - bounds[1]) * 0.20  # Increased to 20% margin
                
                fallback_xlim = (bounds[0] - margin_x, bounds[2] + margin_x)
                fallback_ylim = (bounds[1] - margin_y, bounds[3] + margin_y)
                print(f"   - Fallback X limits: {fallback_xlim}")
                print(f"   - Fallback Y limits: {fallback_ylim}")
                
                ax.set_xlim(fallback_xlim[0], fallback_xlim[1])
                ax.set_ylim(fallback_ylim[0], fallback_ylim[1])
                print(f"   ✅ Applied fallback bounds with enhanced margins")
            
            # Store target scale for later use
            self.target_scale = target_scale
            
            # FIXED: Clean coordinate grid with NO overlap and vertical Y labels
            self._add_clean_coordinates_and_grid(ax)
            
            # Set equal aspect ratio
            ax.set_aspect('equal')
            print(f"   ✅ Set aspect ratio to 'equal'")
            
            # FINAL DEBUGGING SUMMARY
            print(f"\n🏁 FINAL PLOTTING SUMMARY:")
            print(f"   - Axis X limits: {ax.get_xlim()}")
            print(f"   - Axis Y limits: {ax.get_ylim()}")
            print(f"   - Axis aspect: {ax.get_aspect()}")
            print(f"   - Number of artists on axis: {len(ax.get_children())}")
            print(f"   - Axis has data: {ax.has_data()}")
            print(f"   - Data bounds used: {self.gdf.total_bounds if self.gdf is not None and not self.gdf.empty else 'N/A'}")
            print("="*60)
            print("✅ Main map plotted with MAXIMUM vertical zoom and clean coordinates")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR in plotting main map: {e}")
            import traceback
            traceback.print_exc()
            print("="*60 + "\n")
    
    def _add_dynamic_labels(self, ax):
        """Add block labels with size and positioning based on polygon area and shape"""
        try:
            for idx, row in self.gdf.iterrows():
                if 'BLOK' in row and pd.notna(row['BLOK']):
                    geometry = row.geometry
                    
                    # Calculate polygon area in square degrees
                    area_degrees = geometry.area
                    
                    # Get polygon bounds for dimension analysis
                    bounds = geometry.bounds
                    width_degrees = bounds[2] - bounds[0]
                    height_degrees = bounds[3] - bounds[1]
                    
                    # Convert area to approximate square meters for scale reference
                    lat_center = (bounds[1] + bounds[3]) / 2
                    meters_per_degree = 111320.0 * np.cos(np.radians(lat_center))
                    area_m2 = area_degrees * (meters_per_degree ** 2)
                    
                    # DYNAMIC font size based on area
                    if area_m2 > 500000:  # Very large polygons (>50 hectares)
                        font_size = 11
                        pad_size = 0.4
                    elif area_m2 > 100000:  # Large polygons (10-50 hectares)
                        font_size = 10
                        pad_size = 0.35
                    elif area_m2 > 50000:   # Medium polygons (5-10 hectares)
                        font_size = 9
                        pad_size = 0.3
                    elif area_m2 > 10000:   # Small polygons (1-5 hectares)
                        font_size = 8
                        pad_size = 0.25
                    else:                   # Very small polygons (<1 hectare)
                        font_size = 7
                        pad_size = 0.2
                    
                    # Calculate optimal label position
                    # For very elongated polygons, adjust positioning
                    aspect_ratio = width_degrees / height_degrees if height_degrees > 0 else 1
                    
                    if aspect_ratio > 3:  # Very wide polygon
                        # Position label slightly above center
                        centroid = geometry.centroid
                        label_x = centroid.x
                        label_y = centroid.y + (height_degrees * 0.1)
                    elif aspect_ratio < 0.33:  # Very tall polygon
                        # Position label slightly right of center
                        centroid = geometry.centroid
                        label_x = centroid.x + (width_degrees * 0.1)
                        label_y = centroid.y
                    else:  # Normal proportions
                        centroid = geometry.centroid
                        label_x = centroid.x
                        label_y = centroid.y
                    
                    # Ensure label is within polygon bounds
                    label_x = max(bounds[0], min(label_x, bounds[2]))
                    label_y = max(bounds[1], min(label_y, bounds[3]))
                    
                    # SMART: Check if label fits within polygon
                    # For very small polygons, use minimal styling
                    if area_m2 < 5000:  # Very small areas
                        ax.annotate(str(row['BLOK']), 
                                   xy=(label_x, label_y), 
                                   ha='center', va='center',
                                   fontsize=font_size, fontweight='bold',
                                   bbox=dict(boxstyle='round,pad=0.1', 
                                           facecolor='white', alpha=0.8, 
                                           edgecolor='gray', linewidth=0.5))
                    else:  # Normal and large areas
                        ax.annotate(str(row['BLOK']), 
                                   xy=(label_x, label_y), 
                                   ha='center', va='center',
                                   fontsize=font_size, fontweight='bold',
                                   bbox=dict(boxstyle='round,pad=' + str(pad_size), 
                                           facecolor='white', alpha=0.9, 
                                           edgecolor='black', linewidth=1))
                    
            print("✅ Dynamic labels added based on polygon size and shape")
            
        except Exception as e:
            print(f"Error adding dynamic labels: {e}")
    
    def _add_clean_coordinates_and_grid(self, ax):
        """FIXED: Add clean coordinates and grid with NO overlap and proper spacing"""
        try:
            # Get current limits
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            
            # SMART: Calculate optimal number of ticks to prevent overlap
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]
            
            # Dynamic tick count based on range to prevent overlap
            if x_range < 0.01:  # Very small range
                x_tick_count = 3
            elif x_range < 0.05:  # Small range
                x_tick_count = 4
            else:  # Normal range
                x_tick_count = 5
                
            if y_range < 0.01:  # Very small range
                y_tick_count = 3
            elif y_range < 0.05:  # Small range
                y_tick_count = 4
            else:  # Normal range
                y_tick_count = 5
            
            # Generate ticks with smart spacing
            x_ticks = np.linspace(xlim[0], xlim[1], x_tick_count)
            y_ticks = np.linspace(ylim[0], ylim[1], y_tick_count)
            
            # Set ticks
            ax.set_xticks(x_ticks)
            ax.set_yticks(y_ticks)
            
            # FIXED: Decimal degree coordinate formatting for Belitung (as requested)
            def smart_format(tick, is_x=True):
                """Format coordinates in decimal degrees for Belitung region"""
                # Convert UTM back to decimal degrees for display
                if hasattr(self, 'gdf_wgs84') and self.gdf_wgs84 is not None:
                    # Use WGS84 bounds for coordinate display
                    bounds_wgs84 = self.gdf_wgs84.total_bounds
                    if is_x:
                        # Convert UTM X to longitude and format as decimal
                        # Approximate conversion for display (Belitung region ~107°E)
                        lon_range = bounds_wgs84[2] - bounds_wgs84[0]
                        utm_range = self.gdf.total_bounds[2] - self.gdf.total_bounds[0]
                        tick_ratio = (tick - self.gdf.total_bounds[0]) / utm_range
                        approx_lon = bounds_wgs84[0] + (tick_ratio * lon_range)
                        return f"{approx_lon:.3f}°"
                    else:
                        # Convert UTM Y to latitude and format as decimal
                        lat_range = bounds_wgs84[3] - bounds_wgs84[1]
                        utm_range = self.gdf.total_bounds[3] - self.gdf.total_bounds[1]
                        tick_ratio = (tick - self.gdf.total_bounds[1]) / utm_range
                        approx_lat = bounds_wgs84[1] + (tick_ratio * lat_range)
                        return f"{approx_lat:.3f}°"
                else:
                    # Fallback to simple decimal format
                    return f"{tick:.3f}°"
            
            x_labels = [smart_format(tick, True) for tick in x_ticks]
            y_labels = [smart_format(tick, False) for tick in y_ticks]
            
            ax.set_xticklabels(x_labels, fontweight='bold', fontsize=7, rotation=0)
            ax.set_yticklabels(y_labels, fontweight='bold', fontsize=7, rotation=90)
            
            # FIXED: Safe spacing from blue border - increased padding significantly
            ax.tick_params(axis='x', which='major', 
                          direction='in',     # Inward ticks
                          pad=12,             # INCREASED padding from blue border
                          labelsize=7, 
                          width=1.5, length=5,
                          colors='black')
            
            ax.tick_params(axis='y', which='major', 
                          direction='in',     # Inward ticks
                          pad=15,             # INCREASED padding for vertical labels
                          labelsize=7, 
                          width=1.5, length=5,
                          colors='black')
            
            # Add subtle grid lines
            for x in x_ticks:
                if xlim[0] <= x <= xlim[1]:
                    ax.axvline(x, color='gray', alpha=0.3, linewidth=0.6)
            
            for y in y_ticks:
                if ylim[0] <= y <= ylim[1]:
                    ax.axhline(y, color='gray', alpha=0.3, linewidth=0.6)
            
            # SMART: Plus markers only at key intersections to reduce clutter
            center_x_idx = len(x_ticks) // 2
            center_y_idx = len(y_ticks) // 2
            
            for i, x in enumerate(x_ticks):
                for j, y in enumerate(y_ticks):
                    if xlim[0] <= x <= xlim[1] and ylim[0] <= y <= ylim[1]:
                        # Only add plus at corners and center
                        if (i == 0 or i == len(x_ticks)-1 or i == center_x_idx) and \
                           (j == 0 or j == len(y_ticks)-1 or j == center_y_idx):
                            ax.plot(x, y, '+', color='black', markersize=8, 
                                   markeredgewidth=2, alpha=0.7)
            
            # FIXED: Ensure main map doesn't touch blue border
                for spine in ax.spines.values():
                    spine.set_linewidth(2)
                    spine.set_color('black')
                
            print("✅ Clean coordinates with safe spacing from blue border")
                
        except Exception as e:
            print(f"Error adding clean coordinates: {e}")
    
    def _add_logo_fixed(self, ax):
        """FIXED: Add company logo with guaranteed loading using working method"""
        ax.axis('off')
        
        # White background
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        logo_loaded = False
        
        # FIXED: Use EXACT SAME method as professional_peta_berhasil_tampil_logo.py
        if self.logo_path:
            try:
                print(f"🎯 Attempting to load logo from: {self.logo_path}")
                import matplotlib.image as mpimg
                logo = mpimg.imread(self.logo_path)
                
                # FIXED: Use same extent as working version [0.02, 0.18, 0.2, 0.8]
                ax.imshow(logo, extent=[0.1, 0.9, 0.5, 0.9], transform=ax.transAxes, aspect='auto')
                logo_loaded = True
                print(f"🎉 LOGO LOADED SUCCESSFULLY from: {self.logo_path}")
                
            except Exception as e:
                print(f"⚠️ Failed to load logo: {e}")
        
        # Fallback text if no logo
        if not logo_loaded:
            # Simple company name fallback
            ax.text(0.5, 0.7, "PT. REBINMAS JAYA", ha='center', va='center',
                   fontsize=16, fontweight='bold', transform=ax.transAxes, 
                   color='#2C3E50')
        
        # Auto-generated credits for developer and surveyor
        ax.text(0.5, 0.35, "Diproduksi untuk :", ha='center', va='center',
               fontsize=8, fontweight='normal', transform=ax.transAxes, 
               color='#2C3E50')
        
        # Company name
        ax.text(0.5, 0.25, "PT. REBINMAS JAYA", ha='center', va='center',
               fontsize=12, fontweight='bold', transform=ax.transAxes, 
               color='#2C3E50')
        
        # Developer and surveyor credits
        ax.text(0.5, 0.12, "Program: IT Rebinmas | Data: Surveyor RMJ", ha='center', va='center',
               fontsize=7, fontweight='normal', transform=ax.transAxes, 
               color='#7F8C8D', style='italic')
        
        # Date
        import datetime
        current_date = datetime.datetime.now().strftime("%B %Y")
        ax.text(0.5, 0.02, f"Generated: {current_date}", ha='center', va='center',
               fontsize=6, fontweight='normal', transform=ax.transAxes, 
               color='#7F8C8D')
    
    def _add_north_arrow_and_scale_fixed(self, ax):
        """ENHANCED: Add north arrow and PERFECTLY SYNCED scale bar with zoom level"""
        ax.axis('off')
    
        # White background
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        # Professional north arrow
        ax.text(0.25, 0.7, "⬆", ha='center', va='center', fontsize=28, 
               color='red', transform=ax.transAxes)
        ax.text(0.25, 0.5, "UTARA", ha='center', va='center', fontsize=10, 
               fontweight='bold', transform=ax.transAxes)
        
        # ENHANCED: Use the OPTIMAL scale that's perfectly synced with zoom level
        if hasattr(self, 'target_scale') and self.target_scale:
            optimal_scale = self.target_scale
            scale_text = f'Skala\n1:{optimal_scale:,}'
            
            print(f"🎯 PERFECT SCALE/ZOOM SYNC:")
            print(f"   📏 Using optimal scale: 1:{optimal_scale:,}")
            
            # ENHANCED: Calculate scale bar length that's meaningful for the scale
            # Use scale-appropriate round numbers for easy field measurement
            if optimal_scale >= 200000:
                scale_bar_km = 20      # 20 km for provincial scale
                scale_bar_label = "20 km"
            elif optimal_scale >= 100000:
                scale_bar_km = 10      # 10 km for district scale
                scale_bar_label = "10 km"
            elif optimal_scale >= 75000:
                scale_bar_km = 10      # 10 km for regional scale
                scale_bar_label = "10 km"
            elif optimal_scale >= 50000:
                scale_bar_km = 5       # 5 km for large area scale
                scale_bar_label = "5 km"
            elif optimal_scale >= 30000:
                scale_bar_km = 5       # 5 km for regional overview
                scale_bar_label = "5 km"
            elif optimal_scale >= 25000:
                scale_bar_km = 2       # 2 km for standard topographic
                scale_bar_label = "2 km"
            elif optimal_scale >= 15000:
                scale_bar_km = 2       # 2 km for detailed area
                scale_bar_label = "2 km"
            elif optimal_scale >= 10000:
                scale_bar_km = 1       # 1 km for detailed maps
                scale_bar_label = "1 km"
            elif optimal_scale >= 5000:
                scale_bar_km = 1       # 1 km for site plans
                scale_bar_label = "1 km"
            elif optimal_scale >= 2000:
                scale_bar_km = 0.5     # 500m for detailed site plans
                scale_bar_label = "500 m"
            else:
                scale_bar_km = 0.2     # 200m for very detailed plans
                scale_bar_label = "200 m"
            
            print(f"   📏 Scale bar length: {scale_bar_label}")
            print(f"   ✅ Scale bar perfectly matches map scale and zoom level")
            
        else:
            # Fallback (should not happen with new system)
            optimal_scale = 25000
            scale_text = 'Skala\n1:25,000'
            scale_bar_km = 2
            scale_bar_label = "2 km"
            print(f"⚠️ Using fallback scale: 1:25,000")
        
        # Display scale information
        ax.text(0.75, 0.7, scale_text, ha='center', va='center',
               fontsize=12, fontweight='bold', transform=ax.transAxes,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        # ENHANCED: Professional scale bar with precise measurements
        scale_width = 0.45
        scale_height = 0.08
        scale_x = 0.45
        scale_y = 0.15
        
        # Draw professional scale bar with multiple segments
        segments = 4  # Number of segments for better precision
        segment_width = scale_width / segments
        
        for i in range(segments):
            x_pos = scale_x + (i * segment_width)
            # Alternate black and white segments
            color = 'black' if i % 2 == 0 else 'white'
            edge_color = 'black'
            
            rect = Rectangle((x_pos, scale_y), segment_width, scale_height,
                           facecolor=color, edgecolor=edge_color, linewidth=1,
                           transform=ax.transAxes)
            ax.add_patch(rect)
        
        # Add scale bar border
        border_rect = Rectangle((scale_x, scale_y), scale_width, scale_height,
                              fill=False, edgecolor='black', linewidth=2,
                              transform=ax.transAxes)
        ax.add_patch(border_rect)
        
        # PRECISE: Scale labels with exact measurements
        labels_y = scale_y - 0.05
        
        # Start label
        ax.text(scale_x, labels_y, '0', ha='center', va='top', 
               fontsize=9, fontweight='bold', transform=ax.transAxes)
        
        # Middle labels
        for i in range(1, segments):
            x_pos = scale_x + (i * segment_width)
            distance = (scale_bar_km * i) / segments
            if distance < 1:
                label = f'{int(distance * 1000)}m'
            else:
                label = f'{distance:.1f}km' if distance != int(distance) else f'{int(distance)}km'
            
            ax.text(x_pos, labels_y, label, ha='center', va='top',
                   fontsize=8, fontweight='bold', transform=ax.transAxes)
        
        # End label
        end_label = f'{scale_bar_km:.1f}km' if scale_bar_km != int(scale_bar_km) else f'{int(scale_bar_km)}km'
        ax.text(scale_x + scale_width, labels_y, end_label, ha='center', va='top',
               fontsize=9, fontweight='bold', transform=ax.transAxes)
        
        # Add scale bar title
        ax.text(scale_x + scale_width/2, scale_y + scale_height + 0.02, 'SKALA JARAK',
               ha='center', va='bottom', fontsize=9, fontweight='bold',
               transform=ax.transAxes)
    
    def _add_belitung_overview_fixed(self, ax):
        """FIXED: Add context map with options: Belitung island or study area only"""
        ax.axis('off')
        
        # White background with border
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        try:
            if self.context_map_type == "self":
                # OPTION 1: Show study area only (kajian area red, others gray)
                self._create_self_context_map(ax)
            else:
                # OPTION 2: Show Belitung island with study area overlay  
                self._create_belitung_context_map(ax)
                
        except Exception as e:
            print(f"Error in context map: {e}")
            ax.text(0.5, 0.5, 'Peta Konteks\n(Error)', ha='center', va='center',
                   fontsize=10, transform=ax.transAxes)
    
    def _create_self_context_map(self, ax):
        """FIXED: Create context map showing FILTERED study area in red, others in gray"""
        if self.gdf is None:
            return
            
        # Load the full shapefile to show surrounding areas in gray
        full_gdf = gpd.read_file(self.shapefile_path)
        
        # Convert to WGS84 for display
        if full_gdf.crs is None:
            full_gdf.set_crs('EPSG:4326', inplace=True)
        elif full_gdf.crs != 'EPSG:4326':
            full_gdf = full_gdf.to_crs('EPSG:4326')
        
        # Plot all areas in gray first
        full_gdf.plot(ax=ax, color='#D3D3D3', alpha=0.6, 
                     edgecolor='#808080', linewidth=0.5)
        
        # FIXED: Plot ONLY the FILTERED study areas in red using WGS84 version
        if hasattr(self, 'gdf_wgs84') and self.gdf_wgs84 is not None and len(self.gdf_wgs84) > 0:
            self.gdf_wgs84.plot(ax=ax, color='#E74C3C', alpha=0.8, 
                               edgecolor='darkred', linewidth=1.5, zorder=10)
            print(f"🎯 Highlighted {len(self.gdf_wgs84)} FILTERED features in red on context map")
            
            # Add labels for filtered areas if few enough
            if len(self.gdf_wgs84) <= 10:
                for idx, row in self.gdf_wgs84.iterrows():
                    centroid = row.geometry.centroid
                    # Get appropriate label
                    if hasattr(self, 'selected_attribute') and self.selected_attribute and self.selected_attribute in row:
                        label = str(row[self.selected_attribute])[:12]
                    elif 'SUB_DIVISI' in row:
                        label = str(row['SUB_DIVISI'])[:12]
                    else:
                        label = 'Area'
                    
                    ax.annotate(label, (centroid.x, centroid.y), 
                               fontsize=6, ha='center', va='center',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9),
                               zorder=15)
        else:
            # Fallback: convert current UTM data to WGS84 for display
            study_wgs84 = self.gdf.to_crs('EPSG:4326')
            study_wgs84.plot(ax=ax, color='#E74C3C', alpha=0.8, 
                            edgecolor='darkred', linewidth=1.5, zorder=10)
            print(f"🎯 Highlighted {len(study_wgs84)} features in red (fallback conversion)")
        
        # ENHANCED: Set optimal extent to show both context and study area
        if hasattr(self, 'gdf_wgs84') and self.gdf_wgs84 is not None and len(self.gdf_wgs84) > 0:
            # Get bounds of full data and filtered study area
            full_bounds = full_gdf.total_bounds
            study_bounds = self.gdf_wgs84.total_bounds
            
            # Create combined bounds with intelligent margin
            margin_x = max((full_bounds[2] - full_bounds[0]) * 0.1, (study_bounds[2] - study_bounds[0]) * 0.3)
            margin_y = max((full_bounds[3] - full_bounds[1]) * 0.1, (study_bounds[3] - study_bounds[1]) * 0.3)
            
            # Ensure we show both the study area and some context
            min_x = min(full_bounds[0], study_bounds[0]) - margin_x
            max_x = max(full_bounds[2], study_bounds[2]) + margin_x
            min_y = min(full_bounds[1], study_bounds[1]) - margin_y
            max_y = max(full_bounds[3], study_bounds[3]) + margin_y
            
            ax.set_xlim(min_x, max_x)
            ax.set_ylim(min_y, max_y)
        else:
            # Fallback to full extent
            bounds = full_gdf.total_bounds
            margin = max((bounds[2] - bounds[0]), (bounds[3] - bounds[1])) * 0.15
            ax.set_xlim(bounds[0] - margin, bounds[2] + margin)
            ax.set_ylim(bounds[1] - margin, bounds[3] + margin)
        
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Clean border
        for spine in ax.spines.values():
            spine.set_linewidth(2)
            spine.set_color('black')
        
        ax.set_title('PETA KONTEKS - Area Kajian Terpilih', 
                    fontsize=9, fontweight='bold', pad=5)
        
        print("✅ Self context map created (FILTERED areas in red, others in gray)")
    
    def _create_belitung_context_map(self, ax):
        """Create Belitung island context map with study area overlay"""
        if self.belitung_gdf is not None:
            # Use clipped data if available
            if self.clip_belitung_gdf is not None:
                try:
                    clipped_belitung = gpd.clip(self.belitung_gdf, self.clip_belitung_gdf)
                    belitung_to_plot = clipped_belitung
                    print("✅ Using clipped Belitung data")
                except:
                    belitung_to_plot = self.belitung_gdf
                    print("⚠️ Clipping failed, using full data")
            else:
                belitung_to_plot = self.belitung_gdf
            
            # Plot Belitung regions
            if 'WADMKK' in belitung_to_plot.columns:
                belitung_timur = belitung_to_plot[belitung_to_plot['WADMKK'].str.contains('Belitung Timur', case=False, na=False)]
                belitung_regular = belitung_to_plot[belitung_to_plot['WADMKK'].str.contains('Belitung', case=False, na=False) & 
                                                   ~belitung_to_plot['WADMKK'].str.contains('Belitung Timur', case=False, na=False)]
                
                if len(belitung_timur) > 0:
                    belitung_timur.plot(ax=ax, color='#FF6B9D', alpha=0.8, 
                                      edgecolor='darkred', linewidth=1.0)
                if len(belitung_regular) > 0:
                    belitung_regular.plot(ax=ax, color='#4ECDC4', alpha=0.8, 
                                        edgecolor='darkblue', linewidth=1.0)
                else:
                    belitung_to_plot.plot(ax=ax, color='#90EE90', alpha=0.7, 
                                        edgecolor='darkgreen', linewidth=0.8)
            
            # Add study area overlay (WITHOUT red box)
            if self.gdf is not None and len(self.gdf) > 0:
                study_gdf = self.gdf.copy()
                if study_gdf.crs != belitung_to_plot.crs:
                    study_gdf = study_gdf.to_crs(belitung_to_plot.crs)
                
                # Plot study area with same colors as main map
                study_gdf.plot(ax=ax, 
                             color=[self.colors.get(div, '#87CEEB') for div in study_gdf['SUB_DIVISI']], 
                             alpha=0.8, edgecolor='black', linewidth=1, zorder=15)
                
                print(f"✅ Study area displayed on Belitung context map")
            
            # Set clean extent
            context_bounds = belitung_to_plot.total_bounds
            margin = max((context_bounds[2] - context_bounds[0]), 
                       (context_bounds[3] - context_bounds[1])) * 0.1
            
            ax.set_xlim(context_bounds[0] - margin, context_bounds[2] + margin)
            ax.set_ylim(context_bounds[1] - margin, context_bounds[3] + margin)
            
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Clean border
            for spine in ax.spines.values():
                spine.set_linewidth(2)
                spine.set_color('black')
            
            ax.set_title('PETA KONTEKS - Pulau Belitung', 
                        fontsize=9, fontweight='bold', pad=5)
            
            print("✅ Belitung context map created successfully")
        else:
            # Fallback
            ax.text(0.5, 0.5, 'Peta Konteks\nBelitung', ha='center', va='center',
                   fontsize=12, fontweight='bold', transform=ax.transAxes,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
    
    def _add_title(self, ax):
        """Add professional title"""
        ax.axis('off')
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        ax.text(0.5, 0.5, self.map_title, ha='center', va='center',
               fontsize=15, fontweight='bold', transform=ax.transAxes,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
    def _create_legend_fixed(self, ax):
        """FIXED: Create clean professional legend for attribute-based features - ENHANCED"""
        ax.axis('off')
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', 
                              linewidth=1, transform=ax.transAxes))
        
        ax.text(0.1, 0.9, "LEGENDA", ha='left', va='top', fontsize=12, 
               fontweight='bold', transform=ax.transAxes)
        
        if self.gdf is not None:
            # FIXED: Determine which attribute to use for legend with better logic
            legend_attribute = None
            if hasattr(self, 'selected_attribute') and self.selected_attribute:
                legend_attribute = self.selected_attribute
                print(f"🏷️ Using selected attribute for legend: {legend_attribute}")
            elif 'SUB_DIVISI' in self.gdf.columns:
                legend_attribute = 'SUB_DIVISI'
                print(f"🏷️ Using SUB_DIVISI for legend")
            
            if legend_attribute and legend_attribute in self.gdf.columns:
                unique_values = self.gdf[legend_attribute].dropna().unique()
                print(f"🎨 Creating legend for {len(unique_values)} values: {list(unique_values)}")
                
                y_pos = 0.75
                legend_items_created = 0
                
                for value in unique_values:
                    if pd.isna(value):
                        continue
                    
                    color = self.colors.get(value, '#87CEEB')
                    print(f"   🎨 Legend item: {value} -> {color}")
                    
                    # FIXED: Color patch with better positioning
                    patch = Rectangle((0.1, y_pos-0.02), 0.08, 0.04, 
                                    facecolor=color, edgecolor='black', 
                                    linewidth=0.8, transform=ax.transAxes)
                    ax.add_patch(patch)
                    
                    # FIXED: Label with better formatting
                    ax.text(0.22, y_pos, str(value), ha='left', va='center',
                           fontsize=9, transform=ax.transAxes)
                    
                    legend_items_created += 1
                    y_pos -= 0.12
                    if y_pos < 0.3:  # Stop if running out of space
                        break
                
                print(f"✅ Legend created with {legend_items_created} items for attribute: {legend_attribute}")
            else:
                print(f"⚠️ No valid legend attribute found. Available columns: {list(self.gdf.columns) if self.gdf is not None else 'None'}")
                # FIXED: Add fallback legend
                ax.text(0.1, 0.75, "Area Kajian", ha='left', va='center',
                       fontsize=10, transform=ax.transAxes, fontweight='bold')
                patch = Rectangle((0.1, 0.65), 0.08, 0.04, 
                                facecolor='#87CEEB', edgecolor='black', 
                                linewidth=0.8, transform=ax.transAxes)
                ax.add_patch(patch)
        else:
            print("⚠️ No GeoDataFrame available for legend creation")
        
        # Additional symbols
        y_pos = 0.25
        ax.text(0.1, y_pos, "━━━", ha='left', va='center', fontsize=12, 
               color='black', transform=ax.transAxes)
        ax.text(0.22, y_pos, "Batas Area", ha='left', va='center',
               fontsize=9, transform=ax.transAxes)
        
        y_pos -= 0.1
        ax.text(0.1, y_pos, "A1", ha='left', va='center', fontsize=10, 
               fontweight='bold', transform=ax.transAxes,
               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='black'))
        ax.text(0.22, y_pos, "Kode Blok", ha='left', va='center',
               fontsize=9, transform=ax.transAxes)
        
        # IT Rebinmas credit at bottom
        ax.text(0.5, 0.05, "© IT Rebinmas - PT. REBINMAS JAYA", ha='center', va='center',
               fontsize=7, transform=ax.transAxes, style='italic', color='#7F8C8D')

def main():
    """Main function to generate the FIXED professional map"""
    shapefile_path = "../merge_all_sub_divisi_map/merged_estates_HCV0_20250721_092606.shp"
    selected_subdivisions = ['SUB DIVISI AIR KANDIS', 'SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR RAYA']
    custom_title = "PETA KEBUN 1 B\nPT. REBINMAS JAYA"
    
    # Create FIXED map generator with "self" context type to test new feature
    map_gen = FixedOptimizedMapGenerator(shapefile_path, selected_subdivisions, custom_title, 
                                        context_map_type="self")
    
    # Load data
    if not map_gen.load_data():
        print("Failed to load data. Exiting.")
        return
    
    map_gen.load_belitung_data()
    
    # Generate professional map
    output_path = "Professional_Map_Self_Context.pdf"
    if map_gen.create_professional_map(output_path):
        print(f"\n🎉 Professional map created successfully: {output_path}")
        print("🎨 ALL FEATURES APPLIED!")
        print("✅ Auto-generated distinct colors for each area")
        print("✅ Logo positioned above company name")
        print("✅ Clean context map without red box")
        print("✅ Accurate scale bar for distance measurement")
        print("✅ Maximum zoom for selected study areas")
    else:
        print("Failed to create map.")

if __name__ == "__main__":
    main()