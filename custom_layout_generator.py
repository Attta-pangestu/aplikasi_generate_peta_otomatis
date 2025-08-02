#!/usr/bin/env python3
"""
Custom Layout Map Generator
Extends ProfessionalMapGenerator to support custom layout configurations
from the Layout Builder system.

Author: Generated for Tree Counting Project
Date: 2025
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import json
import os
from professional_map_generator import ProfessionalMapGenerator
from map_elements import (
    TitleElement, LegendElement, BelitungOverviewElement,
    LogoInfoElement, CompassElement, ScaleBarElement
)

class CustomLayoutMapGenerator(ProfessionalMapGenerator):
    """
    Enhanced map generator that supports custom layout configurations
    """
    
    def __init__(self, input_path, layout_config=None, **kwargs):
        """
        Initialize with custom layout configuration
        
        Args:
            input_path (str): Path to input file
            layout_config (dict): Custom layout configuration
            **kwargs: Other arguments passed to parent class
        """
        super().__init__(input_path, **kwargs)
        
        # Default layout configuration matching professional_map_generator.py
        self.default_layout = {
            "main_map": {
                "position": [0.05, 0.05, 0.60, 0.93],
                "border": True,
                "border_color": "black",
                "border_width": 2
            },
            "title": {
                "position": [0.66, 0.88, 0.32, 0.10],
                "text": self.map_title,
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
                "position": "overlay",
                "main_map_position": [0.85, 0.85],
                "size": 0.08,
                "visible": True
            },
            "scale_bar": {
                "position": "overlay",
                "main_map_position": [0.05, 0.05],
                "visible": True,
                "units": "meters"
            }
        }
        
        # Use custom layout if provided, otherwise use default
        self.layout_config = layout_config if layout_config else self.default_layout
    
    def load_layout_from_file(self, layout_file):
        """
        Load layout configuration from JSON file
        
        Args:
            layout_file (str): Path to layout JSON file
        """
        try:
            with open(layout_file, 'r') as f:
                self.layout_config = json.load(f)
            print(f"Layout configuration loaded from: {layout_file}")
            return True
        except Exception as e:
            print(f"Error loading layout configuration: {e}")
            return False
    
    def save_layout_to_file(self, layout_file):
        """
        Save current layout configuration to JSON file
        
        Args:
            layout_file (str): Path to save layout JSON file
        """
        try:
            with open(layout_file, 'w') as f:
                json.dump(self.layout_config, f, indent=2)
            print(f"Layout configuration saved to: {layout_file}")
            return True
        except Exception as e:
            print(f"Error saving layout configuration: {e}")
            return False
    
    def create_custom_layout_map(self, output_path="custom_layout_map.pdf", dpi=300):
        """
        Create a professional map with custom layout configuration
        
        Args:
            output_path (str): Output file path
            dpi (int): Resolution for output
        """
        # Check data based on file type
        if self.file_type == "shapefile":
            if self.gdf is None:
                print("No shapefile data loaded. Please run load_data() first.")
                return False
            if len(self.gdf) == 0:
                print("No features to display after filtering.")
                return False
        elif self.file_type == "tiff":
            if self.tiff_data is None:
                print("No TIFF data loaded. Please run load_tiff_data() first.")
                return False
        
        try:
            # Create figure with professional layout (A3 landscape style)
            fig = plt.figure(figsize=(16.54, 11.69))  # A3 size in inches
            fig.patch.set_facecolor('white')
            
            # Add blue border around entire map
            border_rect = Rectangle((0.01, 0.01), 0.98, 0.98,
                                  fill=False, edgecolor='blue', linewidth=3,
                                  transform=fig.transFigure)
            fig.patches.append(border_rect)
            
            # Create main map with custom configuration
            main_config = self.layout_config.get('main_map', self.default_layout['main_map'])
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
            self._plot_main_map_degrees(ax_main)
            
            # Create and render elements with custom configurations
            self._create_custom_elements(fig, ax_main)
            
            # Save the map
            plt.savefig(output_path, dpi=dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            
            print(f"Custom layout map saved to: {output_path}")
            plt.show()
            
            return True
            
        except Exception as e:
            print(f"Error creating custom layout map: {e}")
            return False
    
    def _create_custom_elements(self, fig, ax_main):
        """
        Create map elements with custom layout configuration
        
        Args:
            fig: matplotlib figure object
            ax_main: main map axes object
        """
        # Title element
        if 'title' in self.layout_config:
            title_config = self.layout_config['title']
            title_element = CustomTitleElement(
                title_text=title_config.get('text', self.map_title),
                position=title_config['position'],
                font_size=title_config.get('font_size', 14),
                font_weight=title_config.get('font_weight', 'bold'),
                text_color=title_config.get('text_color', 'black'),
                background_color=title_config.get('background_color', 'white'),
                border=title_config.get('border', True)
            )
            title_element.render(fig)
        
        # Legend element
        if 'legend' in self.layout_config:
            legend_config = self.layout_config['legend']
            legend_element = CustomLegendElement(
                position=legend_config['position'],
                file_type=self.file_type,
                colors=self.colors,
                gdf=self.gdf,
                tiff_legend=self.tiff_legend,
                title=legend_config.get('title', 'LEGENDA'),
                title_font_size=legend_config.get('title_font_size', 12),
                item_font_size=legend_config.get('item_font_size', 10),
                background_color=legend_config.get('background_color', 'white'),
                border=legend_config.get('border', True)
            )
            legend_element.render(fig)
        
        # Belitung overview element
        if 'belitung_overview' in self.layout_config:
            overview_config = self.layout_config['belitung_overview']
            overview_element = CustomBelitungOverviewElement(
                position=overview_config['position'],
                belitung_gdf=self.belitung_gdf,
                main_gdf=self.gdf,
                colors=self.colors,
                file_type=self.file_type,
                tiff_bounds=getattr(self, 'tiff_bounds_wgs84', None),
                title=overview_config.get('title', 'LOKASI DALAM BELITUNG'),
                title_font_size=overview_config.get('title_font_size', 10),
                background_color=overview_config.get('background_color', 'white'),
                border=overview_config.get('border', True)
            )
            overview_element.render(fig)
        
        # Logo info element
        if 'logo_info' in self.layout_config:
            logo_config = self.layout_config['logo_info']
            logo_element = CustomLogoInfoElement(
                position=logo_config['position'],
                logo_path=self.logo_path,
                company_name=logo_config.get('company_name', 'PT. REBINMAS JAYA'),
                production_info=logo_config.get('production_info', 'Diproduksi untuk : PT. REBINMAS JAYA'),
                program_info=logo_config.get('program_info', 'Program: IT Rebinmas | Data: Surveyor RMJ'),
                generated_date=logo_config.get('generated_date', 'Generated: July 2025'),
                font_size=logo_config.get('font_size', 8),
                background_color=logo_config.get('background_color', 'white'),
                border=logo_config.get('border', True)
            )
            logo_element.render(fig)
        
        # Compass element (overlay)
        if 'compass' in self.layout_config:
            compass_config = self.layout_config['compass']
            if compass_config.get('visible', True):
                compass_element = CompassElement(compass_path=self.compass_path)
                compass_element.add_to_main_map(ax_main)
        
        # Scale bar element removed (kilometer ranges no longer used)
        # if 'scale_bar' in self.layout_config:
        #     scale_config = self.layout_config['scale_bar']
        #     if scale_config.get('visible', True):
        #         # Scale bar with km ranges removed per user request
        #         pass
    
    def update_element_config(self, element_name, config_updates):
        """
        Update configuration for a specific element
        
        Args:
            element_name (str): Name of the element to update
            config_updates (dict): Dictionary of configuration updates
        """
        if element_name in self.layout_config:
            self.layout_config[element_name].update(config_updates)
        else:
            self.layout_config[element_name] = config_updates
    
    def get_element_config(self, element_name):
        """
        Get configuration for a specific element
        
        Args:
            element_name (str): Name of the element
            
        Returns:
            dict: Element configuration
        """
        return self.layout_config.get(element_name, {})
    
    def reset_to_default_layout(self):
        """
        Reset layout configuration to default
        """
        self.layout_config = self.default_layout.copy()
        print("Layout configuration reset to default")


# Custom element classes with enhanced styling support

class CustomTitleElement(TitleElement):
    """
    Enhanced title element with custom styling
    """
    
    def __init__(self, title_text, position=None, font_size=14, font_weight='bold', 
                 text_color='black', background_color='white', border=True):
        super().__init__(title_text, position)
        self.font_size = font_size
        self.font_weight = font_weight
        self.text_color = text_color
        self.background_color = background_color
        self.border = border
    
    def _render_content(self, data=None):
        """
        Render the title content with custom styling
        """
        if self.ax is None:
            return
        
        # Set background color
        self.ax.set_facecolor(self.background_color)
        
        # Add border if enabled
        if self.border:
            for spine in self.ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(2)
                spine.set_color('black')
        else:
            for spine in self.ax.spines.values():
                spine.set_visible(False)
        
        # Add title text
        self.ax.text(0.5, 0.5, self.title_text, 
                    ha='center', va='center',
                    fontsize=self.font_size, fontweight=self.font_weight,
                    color=self.text_color, transform=self.ax.transAxes)
        
        # Remove ticks
        self.ax.set_xticks([])
        self.ax.set_yticks([])


class CustomLegendElement(LegendElement):
    """
    Enhanced legend element with custom styling
    """
    
    def __init__(self, position=None, file_type="shapefile", colors=None, gdf=None, 
                 tiff_legend=None, title="LEGENDA", title_font_size=12, 
                 item_font_size=10, background_color='white', border=True):
        super().__init__(position, file_type, colors, gdf, tiff_legend)
        self.title = title
        self.title_font_size = title_font_size
        self.item_font_size = item_font_size
        self.background_color = background_color
        self.border = border
    
    def _render_content(self, data=None):
        """
        Render the legend content with custom styling
        """
        if self.ax is None:
            return
        
        # Set background color
        self.ax.set_facecolor(self.background_color)
        
        # Add border if enabled
        if self.border:
            for spine in self.ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(1.5)
                spine.set_color('black')
        else:
            for spine in self.ax.spines.values():
                spine.set_visible(False)
        
        # Call parent render method but with custom styling
        super()._render_content(data)


class CustomBelitungOverviewElement(BelitungOverviewElement):
    """
    Enhanced Belitung overview element with custom styling
    """
    
    def __init__(self, position=None, belitung_gdf=None, main_gdf=None, colors=None, 
                 file_type="shapefile", tiff_bounds=None, title="LOKASI DALAM BELITUNG",
                 title_font_size=10, background_color='white', border=True):
        super().__init__(position, belitung_gdf, main_gdf, colors, file_type, tiff_bounds)
        self.title = title
        self.title_font_size = title_font_size
        self.background_color = background_color
        self.border = border
    
    def _render_content(self, data=None):
        """
        Render the overview content with custom styling
        """
        if self.ax is None:
            return
        
        # Set background color
        self.ax.set_facecolor(self.background_color)
        
        # Add border if enabled
        if self.border:
            for spine in self.ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(1.5)
                spine.set_color('black')
        else:
            for spine in self.ax.spines.values():
                spine.set_visible(False)
        
        # Call parent render method
        super()._render_content(data)


class CustomLogoInfoElement(LogoInfoElement):
    """
    Enhanced logo info element with custom styling
    """
    
    def __init__(self, position=None, logo_path=None, company_name="PT. REBINMAS JAYA", 
                 production_info="Diproduksi untuk : PT. REBINMAS JAYA",
                 program_info="Program: IT Rebinmas | Data: Surveyor RMJ",
                 generated_date="Generated: July 2025", font_size=8,
                 background_color='white', border=True):
        super().__init__(position, logo_path, company_name, production_info, 
                        program_info, generated_date)
        self.font_size = font_size
        self.background_color = background_color
        self.border = border
    
    def _render_content(self, data=None):
        """
        Render the logo info content with custom styling
        """
        if self.ax is None:
            return
        
        # Set background color
        self.ax.set_facecolor(self.background_color)
        
        # Add border if enabled
        if self.border:
            for spine in self.ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(1.5)
                spine.set_color('black')
        else:
            for spine in self.ax.spines.values():
                spine.set_visible(False)
        
        # Call parent render method
        super()._render_content(data)


def main():
    """
    Example usage of CustomLayoutMapGenerator
    """
    # Example shapefile path
    shapefile_path = "../merge_all_sub_divisi_map/merged_estates_HCV0_20250721_092606.shp"
    
    if not os.path.exists(shapefile_path):
        print(f"Shapefile not found: {shapefile_path}")
        print("Please update the path to your shapefile.")
        return
    
    # Create custom layout generator
    generator = CustomLayoutMapGenerator(
        input_path=shapefile_path,
        map_title="CUSTOM LAYOUT MAP\nPT. REBINMAS JAYA"
    )
    
    # Load data
    if generator.load_data():
        generator.load_belitung_data()
        
        # Create map with default layout
        print("Creating map with default layout...")
        generator.create_custom_layout_map("default_custom_layout.pdf")
        
        # Example: Modify layout configuration
        print("\nModifying layout configuration...")
        
        # Move title to different position
        generator.update_element_config('title', {
            'position': [0.66, 0.75, 0.32, 0.15],  # Larger and lower
            'font_size': 16,
            'text_color': 'darkblue'
        })
        
        # Modify legend position and style
        generator.update_element_config('legend', {
            'position': [0.66, 0.45, 0.32, 0.25],  # Larger legend
            'background_color': 'lightgray',
            'title_font_size': 14
        })
        
        # Create map with modified layout
        generator.create_custom_layout_map("modified_custom_layout.pdf")
        
        # Save layout configuration
        generator.save_layout_to_file("custom_layout_config.json")
        print("\nLayout configuration saved to custom_layout_config.json")
        
    else:
        print("Failed to load data")


if __name__ == "__main__":
    main()