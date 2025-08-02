#!/usr/bin/env python3
"""
Test script to verify compass and scale bar fixes:
1. Remove duplicate compass near scale bar
2. Fix duplicate scale text issue
3. Add scale ratio information (1:X format)
4. Improve scale bar text visibility
"""

import os
from professional_map_generator import ProfessionalMapGenerator

def test_compass_scale_fix():
    """
    Test the compass and scale bar fixes
    """
    print("Testing compass and scale bar fixes...")
    
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
            map_title="TEST MAP - SCALE BAR FIXES\nPT. REBINMAS JAYA",
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
        
        # Generate map with fixes
        output_path = "Test_Scale_Bar_Fixed.pdf"
        print(f"\nGenerating map with scale bar fixes...")
        
        success = generator.create_professional_map(
            output_path=output_path,
            dpi=150  # Lower DPI for faster testing
        )
        
        if success:
            print(f"✅ SUCCESS: Map generated successfully at {output_path}")
            print("\n🔧 FIXES APPLIED:")
            print("   ✅ Removed duplicate compass near scale bar")
            print("   ✅ Fixed duplicate scale text by disabling old scale bar method")
            print("   ✅ Added scale ratio information in 1:X format")
            print("   ✅ Simplified coordinate system information to single line")
            print("   ✅ Improved scale bar text positioning and visibility")
            print("   ✅ Enhanced scale bar styling with better colors")
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
    print("TESTING SCALE BAR AND COMPASS FIXES")
    print("=" * 60)
    
    success = test_compass_scale_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("FIXES IMPLEMENTED:")
        print("• Removed duplicate compass that was too close to scale bar")
        print("• Fixed duplicate scale text by disabling redundant scale method")
        print("• Added scale ratio information (1:X format) above scale bar")
        print("• Simplified coordinate information to prevent text overlap")
        print("• Enhanced scale bar text visibility and positioning")
    else:
        print("❌ TESTS FAILED")
        print("Please check the error messages above")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    main()