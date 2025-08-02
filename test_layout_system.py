#!/usr/bin/env python3
"""
Test Script for Advanced Map Layout Builder System
Tests the functionality of the layout builder components

Author: Generated for Tree Counting Project
Date: 2025
"""

import os
import sys
import json
from pathlib import Path

def test_imports():
    """
    Test if all required modules can be imported
    """
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✓ matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ matplotlib import failed: {e}")
        return False
    
    try:
        import geopandas as gpd
        print("✓ geopandas imported successfully")
    except ImportError as e:
        print(f"✗ geopandas import failed: {e}")
        return False
    
    try:
        from professional_map_generator import ProfessionalMapGenerator
        print("✓ ProfessionalMapGenerator imported successfully")
    except ImportError as e:
        print(f"✗ ProfessionalMapGenerator import failed: {e}")
        return False
    
    try:
        from map_elements import TitleElement, LegendElement
        print("✓ Map elements imported successfully")
    except ImportError as e:
        print(f"✗ Map elements import failed: {e}")
        return False
    
    try:
        from custom_layout_generator import CustomLayoutMapGenerator
        print("✓ CustomLayoutMapGenerator imported successfully")
    except ImportError as e:
        print(f"✗ CustomLayoutMapGenerator import failed: {e}")
        return False
    
    return True

def test_layout_config():
    """
    Test layout configuration creation and manipulation
    """
    print("\nTesting layout configuration...")
    
    try:
        from custom_layout_generator import CustomLayoutMapGenerator
        
        # Create a generator instance
        generator = CustomLayoutMapGenerator("dummy_path.shp")
        
        # Test default layout
        default_layout = generator.default_layout
        print(f"✓ Default layout has {len(default_layout)} elements")
        
        # Test layout modification
        generator.update_element_config('title', {
            'position': [0.1, 0.1, 0.3, 0.1],
            'font_size': 16
        })
        
        updated_config = generator.get_element_config('title')
        if updated_config['font_size'] == 16:
            print("✓ Layout configuration update successful")
        else:
            print("✗ Layout configuration update failed")
            return False
        
        # Test layout save/load
        test_layout_file = "test_layout.json"
        if generator.save_layout_to_file(test_layout_file):
            print("✓ Layout save successful")
            
            # Test loading
            new_generator = CustomLayoutMapGenerator("dummy_path.shp")
            if new_generator.load_layout_from_file(test_layout_file):
                print("✓ Layout load successful")
                
                # Clean up
                if os.path.exists(test_layout_file):
                    os.remove(test_layout_file)
                    print("✓ Test file cleaned up")
            else:
                print("✗ Layout load failed")
                return False
        else:
            print("✗ Layout save failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Layout configuration test failed: {e}")
        return False

def test_file_structure():
    """
    Test if all required files exist
    """
    print("\nTesting file structure...")
    
    required_files = [
        "layout_builder.py",
        "custom_layout_generator.py",
        "map_layout_editor.py",
        "professional_map_generator.py",
        "map_elements.py",
        "run_layout_builder.bat",
        "run_layout_editor.bat",
        "README_LAYOUT_BUILDER.md"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
            all_exist = False
    
    return all_exist

def test_layout_builder_class():
    """
    Test the MapLayoutBuilder class initialization
    """
    print("\nTesting MapLayoutBuilder class...")
    
    try:
        # Import without creating GUI (to avoid display issues in testing)
        import sys
        from unittest.mock import Mock
        
        # Mock tkinter to avoid GUI creation
        original_tk = sys.modules.get('tkinter')
        mock_tk = Mock()
        mock_tk.Tk = Mock()
        mock_tk.StringVar = Mock(return_value=Mock())
        mock_tk.DoubleVar = Mock(return_value=Mock())
        mock_tk.BooleanVar = Mock(return_value=Mock())
        mock_tk.IntVar = Mock(return_value=Mock())
        
        sys.modules['tkinter'] = mock_tk
        sys.modules['tkinter.ttk'] = Mock()
        sys.modules['tkinter.filedialog'] = Mock()
        sys.modules['tkinter.messagebox'] = Mock()
        sys.modules['tkinter.colorchooser'] = Mock()
        
        from layout_builder import MapLayoutBuilder
        
        # Test default layout structure
        mock_root = Mock()
        builder = MapLayoutBuilder(mock_root)
        
        if hasattr(builder, 'default_layout'):
            print("✓ MapLayoutBuilder has default_layout")
        else:
            print("✗ MapLayoutBuilder missing default_layout")
            return False
        
        if hasattr(builder, 'current_layout'):
            print("✓ MapLayoutBuilder has current_layout")
        else:
            print("✗ MapLayoutBuilder missing current_layout")
            return False
        
        # Restore original tkinter
        if original_tk:
            sys.modules['tkinter'] = original_tk
        
        print("✓ MapLayoutBuilder class test successful")
        return True
        
    except Exception as e:
        print(f"✗ MapLayoutBuilder class test failed: {e}")
        return False

def test_batch_files():
    """
    Test if batch files are properly formatted
    """
    print("\nTesting batch files...")
    
    batch_files = {
        "run_layout_builder.bat": "layout_builder.py",
        "run_layout_editor.bat": "map_layout_editor.py"
    }
    
    all_valid = True
    for batch_file, expected_script in batch_files.items():
        if os.path.exists(batch_file):
            try:
                with open(batch_file, 'r') as f:
                    content = f.read()
                    if expected_script in content:
                        print(f"✓ {batch_file} correctly references {expected_script}")
                    else:
                        print(f"✗ {batch_file} does not reference {expected_script}")
                        all_valid = False
            except Exception as e:
                print(f"✗ Error reading {batch_file}: {e}")
                all_valid = False
        else:
            print(f"✗ {batch_file} does not exist")
            all_valid = False
    
    return all_valid

def create_sample_layout():
    """
    Create a sample layout configuration file for testing
    """
    print("\nCreating sample layout configuration...")
    
    sample_layout = {
        "main_map": {
            "position": [0.05, 0.05, 0.60, 0.93],
            "border": True,
            "border_color": "black",
            "border_width": 2
        },
        "title": {
            "position": [0.66, 0.88, 0.32, 0.10],
            "text": "SAMPLE CUSTOM LAYOUT\nPT. REBINMAS JAYA",
            "font_size": 16,
            "font_weight": "bold",
            "text_color": "darkblue",
            "background_color": "lightgray",
            "border": True
        },
        "legend": {
            "position": [0.66, 0.38, 0.32, 0.25],
            "title": "CUSTOM LEGEND",
            "title_font_size": 14,
            "item_font_size": 11,
            "background_color": "lightyellow",
            "border": True
        },
        "belitung_overview": {
            "position": [0.66, 0.65, 0.32, 0.20],
            "title": "LOKASI DALAM BELITUNG",
            "title_font_size": 10,
            "background_color": "lightcoral",
            "border": True
        },
        "logo_info": {
            "position": [0.66, 0.02, 0.32, 0.14],
            "company_name": "PT. REBINMAS JAYA",
            "production_info": "Diproduksi untuk : PT. REBINMAS JAYA",
            "program_info": "Program: IT Rebinmas | Data: Surveyor RMJ",
            "generated_date": "Generated: July 2025",
            "font_size": 8,
            "background_color": "lightgreen",
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
    
    try:
        with open("sample_custom_layout.json", 'w') as f:
            json.dump(sample_layout, f, indent=2)
        print("✓ Sample layout configuration created: sample_custom_layout.json")
        return True
    except Exception as e:
        print(f"✗ Failed to create sample layout: {e}")
        return False

def main():
    """
    Run all tests
    """
    print("=" * 60)
    print("ADVANCED MAP LAYOUT BUILDER SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("File Structure Test", test_file_structure),
        ("Layout Configuration Test", test_layout_config),
        ("MapLayoutBuilder Class Test", test_layout_builder_class),
        ("Batch Files Test", test_batch_files),
        ("Sample Layout Creation", create_sample_layout)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The layout builder system is ready to use.")
        print("\nTo get started:")
        print("1. Run 'run_layout_builder.bat' to open the advanced layout builder")
        print("2. Or run 'python layout_builder.py' directly")
        print("3. Check 'README_LAYOUT_BUILDER.md' for detailed documentation")
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("- Install missing packages: pip install geopandas matplotlib tkinter")
        print("- Ensure all files are in the correct directory")
        print("- Check Python version compatibility")
    
    print("=" * 60)

if __name__ == "__main__":
    main()