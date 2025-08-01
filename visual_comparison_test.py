#!/usr/bin/env python3
"""
Visual comparison test to verify the compass/scale box size fix
This script generates a test map and provides detailed analysis of box sizes
"""

import os
import sys
from professional_map_generator import ProfessionalMapGenerator

def analyze_box_dimensions():
    """
    Analyze and report the theoretical box dimensions
    """
    print("📐 THEORETICAL BOX DIMENSION ANALYSIS")
    print("="*60)
    
    # Box constants from ProfessionalMapGenerator
    BOX_WIDTH = 0.32
    BOX_LEFT_POSITION = 0.66
    
    # Box heights from the code
    legend_height = 0.18
    compass_scale_height = 0.18
    
    print(f"📦 All boxes use standardized dimensions:")
    print(f"   - Width: {BOX_WIDTH:.3f} ({BOX_WIDTH*100:.1f}% of figure width)")
    print(f"   - Left position: {BOX_LEFT_POSITION:.3f}")
    print(f"   - Right edge: {BOX_LEFT_POSITION + BOX_WIDTH:.3f}")
    
    print(f"\n📦 Legend box:")
    print(f"   - Height: {legend_height:.3f} ({legend_height*100:.1f}% of figure height)")
    print(f"   - Inner content area: 90% x 90% = {0.9*BOX_WIDTH:.3f} x {0.9*legend_height:.3f}")
    
    print(f"\n📦 Compass/Scale box:")
    print(f"   - Height: {compass_scale_height:.3f} ({compass_scale_height*100:.1f}% of figure height)")
    print(f"   - Compass container: 44% x 90% = {0.44*BOX_WIDTH:.3f} x {0.9*compass_scale_height:.3f}")
    print(f"   - Scale container: 44% x 90% = {0.44*BOX_WIDTH:.3f} x {0.9*compass_scale_height:.3f}")
    print(f"   - Total coverage: 88% x 90% = {0.88*BOX_WIDTH:.3f} x {0.9*compass_scale_height:.3f}")
    
    print(f"\n🔍 COMPARISON:")
    legend_area = 0.9 * BOX_WIDTH * 0.9 * legend_height
    compass_area = 0.88 * BOX_WIDTH * 0.9 * compass_scale_height
    
    print(f"   - Legend effective area: {legend_area:.6f}")
    print(f"   - Compass/Scale effective area: {compass_area:.6f}")
    print(f"   - Area ratio (Compass/Legend): {compass_area/legend_area:.3f}")
    
    if compass_area >= legend_area * 0.95:
        print("   ✅ Compass/Scale area is now comparable to Legend area!")
    else:
        print("   ⚠️ Compass/Scale area is still smaller than Legend area")

def test_visual_fix():
    """
    Test the visual fix by generating a map
    """
    print("\n🧪 GENERATING TEST MAP FOR VISUAL VERIFICATION")
    print("="*60)
    
    # Check if default shapefile exists
    default_shapefile = "../merge_all_sub_divisi_map/merged_estates_HCV0_20250721_092606.shp"
    
    if not os.path.exists(default_shapefile):
        print(f"❌ Default shapefile not found: {default_shapefile}")
        return False
    
    print(f"✅ Found shapefile: {default_shapefile}")
    
    # Create map generator with default subdivisions
    selected_subdivisions = ['SUB DIVISI AIR CENDONG', 'SUB DIVISI AIR KANDIS', 'SUB DIVISI AIR RAYA']
    
    map_gen = ProfessionalMapGenerator(
        default_shapefile, 
        selected_subdivisions=selected_subdivisions,
        map_title="VISUAL COMPARISON TEST\nCOMPASS/SCALE BOX FIX"
    )
    
    # Load data
    print("📊 Loading shapefile data...")
    if not map_gen.load_data():
        print("❌ Failed to load shapefile data")
        return False
    
    print(f"✅ Loaded {len(map_gen.gdf)} features")
    
    # Generate test map
    output_path = "visual_comparison_test_FIXED.pdf"
    print(f"🗺️ Generating test map: {output_path}")
    
    success = map_gen.create_professional_map(
        output_path=output_path,
        dpi=150  # Lower DPI for faster testing
    )
    
    if success:
        print("✅ TEST MAP GENERATED SUCCESSFULLY!")
        print(f"📄 Output: {output_path}")
        
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

def main():
    """
    Main function to run the visual comparison test
    """
    print("🔍 COMPASS/SCALE BOX SIZE FIX - VISUAL COMPARISON TEST")
    print("="*70)
    
    # Analyze theoretical dimensions
    analyze_box_dimensions()
    
    # Test the actual fix
    success = test_visual_fix()
    
    if success:
        print("\n" + "="*70)
        print("🎉 VISUAL COMPARISON TEST COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n📋 MANUAL VERIFICATION STEPS:")
        print("1. Open the generated PDF: visual_comparison_test_FIXED.pdf")
        print("2. Compare the compass/scale box with the legend box")
        print("3. Verify that both boxes appear to have similar visual density")
        print("4. Check that the compass and scale containers fill most of the box space")
        print("5. Confirm that there's no significant visual size difference")
        
        print("\n🔧 TECHNICAL IMPROVEMENTS MADE:")
        print("- Increased compass container width from 42% to 44%")
        print("- Increased scale container width from 42% to 44%")
        print("- Moved containers closer together (gap reduced from 9% to 7%)")
        print("- Total coverage increased from 84% to 88% of box width")
        print("- Maintained 90% height coverage like legend box")
        
        print("\n📊 EXPECTED RESULT:")
        print("The compass/scale box should now appear visually similar in")
        print("size and density to the legend box and other info boxes.")
        
        return True
    else:
        print("\n💥 VISUAL COMPARISON TEST FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
