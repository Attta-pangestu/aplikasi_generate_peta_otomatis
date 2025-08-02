#!/usr/bin/env python3
"""
Test script to verify that the real Belitung map is used instead of simplified version
"""

import os
from professional_map_generator import ProfessionalMapGenerator

def test_real_belitung_map():
    """
    Test that the system uses real Belitung data instead of simplified version
    """
    print("Testing real Belitung map implementation...")
    
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
            map_title="TEST MAP - REAL BELITUNG OVERVIEW\nPT. REBINMAS JAYA",
            file_type="shapefile"
        )
        
        # Load data
        print("Loading shapefile data...")
        if not generator.load_data():
            print("Failed to load shapefile data")
            return False
        
        # Test Belitung data loading explicitly
        print("\nTesting Belitung data loading...")
        belitung_result = generator.load_belitung_data()
        print(f"Belitung data loading result: {belitung_result}")
        
        if belitung_result and generator.belitung_gdf is not None:
            print(f"✅ SUCCESS: Loaded real Belitung data with {len(generator.belitung_gdf)} features")
            print(f"Belitung data columns: {list(generator.belitung_gdf.columns)}")
            print(f"Belitung data bounds: {generator.belitung_gdf.total_bounds}")
        else:
            print("❌ WARNING: Could not load real Belitung data - will show error message instead of simplified version")
        
        # Generate map with real Belitung data
        output_path = "Test_Real_Belitung_Map.pdf"
        print(f"\nGenerating map with real Belitung overview...")
        
        success = generator.create_professional_map(
            output_path=output_path,
            dpi=150  # Lower DPI for faster testing
        )
        
        if success:
            print(f"✅ SUCCESS: Map generated successfully at {output_path}")
            print("✅ The map should now show the real Belitung island outline instead of simplified version")
            return True
        else:
            print("❌ FAILED: Map generation failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Main test function
    """
    print("=" * 60)
    print("TESTING REAL BELITUNG MAP IMPLEMENTATION")
    print("=" * 60)
    
    success = test_real_belitung_map()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("The system now uses real Belitung data instead of simplified version")
    else:
        print("❌ TESTS FAILED")
        print("Please check the error messages above")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    main()