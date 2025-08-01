#!/usr/bin/env python3
"""
Test script to verify the compass/scale box size fix
"""

import os
import sys
from professional_map_generator import ProfessionalMapGenerator

def test_compass_fix():
    """
    Test the compass/scale box size fix
    """
    print("🧪 Testing compass/scale box size fix...")
    
    # Check if default shapefile exists
    default_shapefile = "../merge_all_sub_divisi_map/merged_estates_HCV0_20250721_092606.shp"
    
    if not os.path.exists(default_shapefile):
        print(f"❌ Default shapefile not found: {default_shapefile}")
        print("Please ensure the shapefile exists or update the path")
        return False
    
    print(f"✅ Found shapefile: {default_shapefile}")
    
    # Create map generator with default subdivisions
    selected_subdivisions = ['SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR KANDIS', 'SUB DIVISI AIR RAYA']
    
    print(f"📋 Selected subdivisions: {', '.join(selected_subdivisions)}")
    
    map_gen = ProfessionalMapGenerator(
        default_shapefile, 
        selected_subdivisions=selected_subdivisions,
        map_title="TEST MAP - COMPASS FIX\nPT. REBINMAS JAYA"
    )
    
    # Load data
    print("📊 Loading shapefile data...")
    if not map_gen.load_data():
        print("❌ Failed to load shapefile data")
        return False
    
    print(f"✅ Loaded {len(map_gen.gdf)} features")
    
    # Generate test map
    output_path = "test_compass_fix_map.pdf"
    print(f"🗺️ Generating test map: {output_path}")
    
    success = map_gen.create_professional_map(
        output_path=output_path,
        dpi=150  # Lower DPI for faster testing
    )
    
    if success:
        print("✅ TEST MAP GENERATED SUCCESSFULLY!")
        print(f"📄 Output: {output_path}")
        print("\n🔍 VERIFICATION CHECKLIST:")
        print("1. Open the generated PDF")
        print("2. Check that the compass/scale box is the same size as the legend box")
        print("3. Verify that the compass and scale containers fill more of the box space")
        print("4. Confirm that the content doesn't appear smaller than other boxes")
        
        # Check if file was actually created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"📊 File size: {file_size:,} bytes")
            return True
        else:
            print("❌ Output file was not created")
            return False
    else:
        print("❌ Failed to generate test map")
        return False

if __name__ == "__main__":
    success = test_compass_fix()
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1)
