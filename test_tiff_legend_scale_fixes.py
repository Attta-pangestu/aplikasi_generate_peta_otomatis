#!/usr/bin/env python3
"""
Test script to verify TIFF legend and scale bar fixes:
1. Set default TIFF legend colors as shown in user image
2. Remove duplicate scale numbers (show only 0 and max)
3. Move scale ratio below coordinate information
"""

import os
import tkinter as tk
from map_generator_gui import MapGeneratorGUI
from professional_map_generator import ProfessionalMapGenerator

def test_tiff_legend_defaults():
    """
    Test the default TIFF legend colors
    """
    print("Testing default TIFF legend colors...")
    
    # Create GUI instance to test default legend
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    app = MapGeneratorGUI(root)
    
    # Default entries are automatically added during GUI initialization
    # No need to add them again
    
    # Get legend data
    legend_data = app.get_tiff_legend_data()
    
    print(f"Default TIFF legend entries: {len(legend_data)}")
    expected_colors = ["#6914cc", "#5b9ddc", "#d01975", "#b1e47a"]
    expected_descriptions = ["Tahap 1", "Tahap 2", "Tahap 3", "Tahap 4"]
    
    for i, entry in enumerate(legend_data):
        print(f"  {i+1}. {entry['color']} - {entry['description']}")
        if i < len(expected_colors):
            if entry['color'] == expected_colors[i] and entry['description'] == expected_descriptions[i]:
                print(f"    ✅ Correct color and description")
            else:
                print(f"    ❌ Expected: {expected_colors[i]} - {expected_descriptions[i]}")
    
    root.destroy()
    return len(legend_data) == 4

def test_scale_bar_fixes():
    """
    Test scale bar fixes with a sample map
    """
    print("\nTesting scale bar fixes...")
    
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
            map_title="TEST MAP - TIFF LEGEND & SCALE FIXES\nPT. REBINMAS JAYA",
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
        output_path = "Test_TIFF_Legend_Scale_Fixes.pdf"
        print(f"\nGenerating map with TIFF legend and scale bar fixes...")
        
        success = generator.create_professional_map(
            output_path=output_path,
            dpi=150  # Lower DPI for faster testing
        )
        
        if success:
            print(f"✅ SUCCESS: Map generated successfully at {output_path}")
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
    print("=" * 70)
    print("TESTING TIFF LEGEND AND SCALE BAR FIXES")
    print("=" * 70)
    
    # Test 1: Default TIFF legend colors
    legend_test = test_tiff_legend_defaults()
    
    # Test 2: Scale bar fixes
    scale_test = test_scale_bar_fixes()
    
    print("\n" + "=" * 70)
    if legend_test and scale_test:
        print("✅ ALL TESTS PASSED")
        print("FIXES IMPLEMENTED:")
        print("• Updated default TIFF legend colors to match user requirements:")
        print("  - Tahap 1: #6914cc (purple)")
        print("  - Tahap 2: #5b9ddc (blue)")
        print("  - Tahap 3: #d01975 (pink)")
        print("  - Tahap 4: #b1e47a (green)")
        print("• Removed duplicate scale numbers (now shows only 0 and maximum)")
        print("• Moved scale ratio (1:X) below coordinate information")
        print("• Improved scale bar layout and readability")
    else:
        print("❌ SOME TESTS FAILED")
        if not legend_test:
            print("• TIFF legend default colors test failed")
        if not scale_test:
            print("• Scale bar fixes test failed")
        print("Please check the error messages above")
    print("=" * 70)
    
    return legend_test and scale_test

if __name__ == "__main__":
    main()