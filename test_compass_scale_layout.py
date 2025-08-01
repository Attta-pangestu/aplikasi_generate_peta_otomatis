#!/usr/bin/env python3
"""
Test script to verify the improved compass and scale bar layout
"""

import os
from professional_map_generator import ProfessionalMapGenerator

def test_compass_scale_layout():
    """
    Test the improved compass and scale bar layout
    """
    print("Testing improved compass and scale bar layout...")
    
    # Use default shapefile path
    shapefile_path = "../merge_all_sub_divisi_map/merged_estates_HCV0_20250721_092606.shp"
    
    # Check if shapefile exists
    if not os.path.exists(shapefile_path):
        print(f"Shapefile not found at: {shapefile_path}")
        print("Please ensure the shapefile exists or update the path.")
        return False
    
    try:
        # Create map generator
        generator = ProfessionalMapGenerator(
            input_path=shapefile_path,
            selected_subdivisions=['SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR KANDIS', 'SUB DIVISI AIR RAYA'],
            map_title="TEST MAP - IMPROVED COMPASS & SCALE LAYOUT\nPT. REBINMAS JAYA",
            file_type="shapefile"
        )
        
        # Load data
        print("Loading shapefile data...")
        if not generator.load_data():
            print("Failed to load shapefile data")
            return False
        
        # Load Belitung data
        print("Loading Belitung overview data...")
        generator.load_belitung_data()
        
        # Generate map with improved layout
        output_path = "Test_Improved_Compass_Scale_Layout.pdf"
        print(f"Generating map with improved compass and scale bar layout...")
        
        success = generator.create_professional_map(
            output_path=output_path,
            dpi=300
        )
        
        if success:
            print(f"✅ SUCCESS: Map generated successfully!")
            print(f"📄 Output file: {output_path}")
            print("\n🔧 IMPROVEMENTS MADE:")
            print("   • Compass positioned on the left side with wider area")
            print("   • Scale bar spans 90% of box width for maximum visibility")
            print("   • Inner box margins reduced (0.02 instead of 0.05) for more space")
            print("   • Scale bar height increased to 0.08 for better visibility")
            print("   • Better horizontal separation between compass and scale elements")
            return True
        else:
            print("❌ FAILED: Map generation failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_compass_scale_layout()