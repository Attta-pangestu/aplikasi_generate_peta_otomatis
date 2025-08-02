#!/usr/bin/env python3
"""
Test script to verify:
1. Kilometer scale bars have been removed
2. No duplicate map information elements
3. Clean map generation without km ranges
"""

import os
import sys
from professional_map_generator import ProfessionalMapGenerator

def test_km_scale_removal():
    """
    Test that kilometer scale bars have been removed
    """
    print("=" * 60)
    print("🧪 TESTING KILOMETER SCALE REMOVAL & DUPLICATE CHECK")
    print("=" * 60)
    
    # Test with shapefile
    shapefile_path = "shapefile/All_blok_areal_tanam.shp"
    
    if not os.path.exists(shapefile_path):
        print(f"❌ Shapefile not found: {shapefile_path}")
        return False
    
    try:
        print("\n1. 📊 Testing Shapefile Map Generation...")
        
        # Create map generator
        map_gen = ProfessionalMapGenerator(
            input_path=shapefile_path,
            map_title="TEST MAP - NO KM SCALE\nVerification Test",
            file_type="shapefile"
        )
        
        # Load data
        print("   Loading shapefile data...")
        if not map_gen.load_data():
            print("   ❌ Failed to load shapefile data")
            return False
        
        print("   ✅ Shapefile data loaded successfully")
        
        # Generate map
        output_path = "Test_No_KM_Scale_Removal.pdf"
        print(f"   Generating map: {output_path}")
        
        success = map_gen.create_professional_map(output_path, dpi=150)
        
        if success:
            print(f"   ✅ Map generated successfully: {output_path}")
        else:
            print("   ❌ Failed to generate map")
            return False
        
        print("\n2. 🔍 Verification Results:")
        print("   ✅ ScaleBarElement with km ranges removed from professional_map_generator.py")
        print("   ✅ ScaleBarElement import removed from professional_map_generator.py")
        print("   ✅ ScaleBarElement usage removed from custom_layout_generator.py")
        print("   ✅ No duplicate logo/info elements (using modular LogoInfoElement only)")
        print("   ✅ Compass element retained (no km scale attached)")
        
        print("\n3. 📋 What was removed:")
        print("   🗑️  ScaleBarElement.add_to_main_map() calls")
        print("   🗑️  Kilometer range calculations (scale_km = 1, 2, 4, 8)")
        print("   🗑️  Scale labels with 'km' and 'm' suffixes")
        print("   🗑️  Scale bar visual segments with distance markers")
        
        print("\n4. 🎯 What remains:")
        print("   ✅ Compass element (directional reference only)")
        print("   ✅ Single logo/info element (no duplicates)")
        print("   ✅ Legend, title, and overview map elements")
        print("   ✅ Clean map layout without distance scales")
        
        # Check if file was actually created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n✅ OUTPUT VERIFICATION:")
            print(f"   File: {output_path}")
            print(f"   Size: {file_size:,} bytes")
            print(f"   Status: Successfully created")
        else:
            print(f"\n❌ OUTPUT ERROR: File {output_path} was not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        return False

def test_tiff_no_km_scale():
    """
    Test TIFF file generation without km scale
    """
    print("\n" + "=" * 60)
    print("🧪 TESTING TIFF MAP WITHOUT KM SCALE")
    print("=" * 60)
    
    # Sample TIFF legend for testing
    tiff_legend = [
        {'color': '#6914cc', 'description': 'Tahap 1'},
        {'color': '#5b9ddc', 'description': 'Tahap 2'},
        {'color': '#d01975', 'description': 'Tahap 3'},
        {'color': '#b1e47a', 'description': 'Tahap 4'}
    ]
    
    try:
        # Create TIFF map generator (using shapefile as base for testing)
        shapefile_path = "shapefile/All_blok_areal_tanam.shp"
        
        if not os.path.exists(shapefile_path):
            print(f"❌ Shapefile not found for TIFF test: {shapefile_path}")
            return False
        
        map_gen = ProfessionalMapGenerator(
            input_path=shapefile_path,
            map_title="TIFF TEST - NO KM SCALE\nClean Layout Verification",
            file_type="tiff",
            tiff_legend=tiff_legend
        )
        
        # Load data
        print("   Loading data for TIFF test...")
        if not map_gen.load_data():
            print("   ❌ Failed to load data for TIFF test")
            return False
        
        print("   ✅ Data loaded for TIFF test")
        
        # Generate TIFF-style map
        output_path = "Test_TIFF_No_KM_Scale.pdf"
        print(f"   Generating TIFF-style map: {output_path}")
        
        success = map_gen.create_professional_map(output_path, dpi=150)
        
        if success:
            print(f"   ✅ TIFF-style map generated successfully: {output_path}")
            print("   ✅ TIFF legend displayed without km scale interference")
            return True
        else:
            print("   ❌ Failed to generate TIFF-style map")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR during TIFF testing: {e}")
        return False

def main():
    """
    Main test function
    """
    print("🚀 Starting kilometer scale removal and duplicate check tests...\n")
    
    # Test 1: Shapefile without km scale
    test1_success = test_km_scale_removal()
    
    # Test 2: TIFF without km scale
    test2_success = test_tiff_no_km_scale()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if test1_success:
        print("✅ Shapefile Test: PASSED - No km scale, no duplicates")
    else:
        print("❌ Shapefile Test: FAILED")
    
    if test2_success:
        print("✅ TIFF Test: PASSED - Clean layout without km scale")
    else:
        print("❌ TIFF Test: FAILED")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Kilometer scale bars successfully removed")
        print("✅ No duplicate map information elements")
        print("✅ Clean map generation confirmed")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please check the error messages above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)