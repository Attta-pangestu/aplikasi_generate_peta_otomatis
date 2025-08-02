# Advanced Map Layout Builder System

## Overview

The Advanced Map Layout Builder System provides a comprehensive GUI-based solution for customizing the layout, positioning, and styling of map elements in professional surveyor-style maps. This system extends the existing `professional_map_generator.py` with drag-and-drop functionality, real-time preview, and extensive customization options.

## Features

### 🎨 **Visual Layout Editor**
- **Drag-and-Drop Interface**: Move map elements by dragging them in the preview canvas
- **Click-and-Drag Element Creation**: Add new elements (compass, scale bar, text boxes) by clicking and dragging to define their position and size
- **Real-time Preview**: See changes instantly as you modify element positions and styles
- **Element Selection**: Click on elements to select and edit their properties
- **Grid System**: Optional grid overlay for precise positioning
- **Keyboard Shortcuts**: ESC to cancel creation mode, Delete to remove selected elements

### 🛠️ **Comprehensive Styling Options**
- **Position Control**: Precise positioning with numerical input fields
- **Size Adjustment**: Modify width and height of elements
- **Color Customization**: Change background colors, text colors, and border colors
- **Typography**: Adjust font sizes, weights, and styles
- **Border Control**: Enable/disable borders and customize border properties

### 💾 **Layout Management**
- **Save Layouts**: Export custom layouts to JSON files
- **Load Layouts**: Import previously saved layout configurations
- **Reset Options**: Reset individual elements or entire layout to defaults
- **Template System**: Create and reuse layout templates

### 🗺️ **Map Elements**

The system supports customization of all major map elements:

1. **Main Map Area**
   - Position and size adjustment
   - Border styling
   - Background customization

2. **Title Element**
   - Custom title text
   - Font size and weight
   - Text and background colors
   - Border styling

3. **Legend Element**
   - Legend title customization
   - Font size adjustments
   - Background and border styling
   - Item spacing control

4. **Belitung Overview Map**
   - Position and size control
   - Title customization
   - Styling options

5. **Logo and Info Panel**
   - Company information editing
   - Font size adjustment
   - Layout customization

6. **Compass and Scale Bar**
   - Visibility toggle
   - Size adjustment
   - Position control (overlay on main map)
   - Multiple instances supported (can add multiple instances)

7. **Text Box Elements** (NEW)
   - Custom text elements with configurable styling
   - Dynamic creation and positioning
   - Individual styling options

## File Structure

```
Create_Peta_PDF/
├── layout_builder.py              # Main layout builder GUI application
├── custom_layout_generator.py     # Enhanced map generator with custom layouts
├── map_layout_editor.py          # Enhanced version of existing editor
├── professional_map_generator.py  # Original map generator (unchanged)
├── map_elements.py               # Modular map elements (unchanged)
├── run_layout_builder.bat        # Batch file to run layout builder
├── run_layout_editor.bat         # Batch file to run enhanced editor
└── README_LAYOUT_BUILDER.md      # This documentation file
```

## Getting Started

### Prerequisites

Ensure you have all required Python packages installed:

```bash
pip install geopandas matplotlib tkinter rasterio contextily matplotlib-scalebar
```

### Running the Layout Builder

#### Option 1: Using Batch File (Recommended)
```bash
# Double-click or run from command line
run_layout_builder.bat
```

#### Option 2: Direct Python Execution
```bash
python layout_builder.py
```

### Basic Usage Workflow

1. **Launch the Application**
   - Run `run_layout_builder.bat` or execute `python layout_builder.py`

2. **Load Input Files**
   - Select your shapefile or TIFF file using the "Browse" button
   - Optionally select a logo file
   - Specify output file name and location

3. **Customize Layout**
   - Select elements from the dropdown list
   - Drag elements in the preview canvas to reposition them
   - Use the properties panel to modify styling options
   - Adjust position and size using numerical input fields
   - **Add New Elements**: Click "Add Compass", "Add Scale Bar", or "Add Text Box" buttons
   - **Click-and-Drag Creation**: Click and drag on canvas to define new element position and size
   - **Element Management**: Use Delete key to remove selected elements (core elements protected)

4. **Preview Changes**
   - Changes are reflected in real-time in the preview canvas
   - Selected elements are highlighted with red borders
   - Use "Refresh Preview" button if needed

5. **Generate Final Map**
   - Click "Generate Map" to create the final PDF
   - The map will be saved to your specified output location

6. **Save/Load Layouts**
   - Use "Save Layout" to export your custom configuration
   - Use "Load Layout" to import previously saved configurations

## Advanced Features

### Interactive Element Creation
- **Click-and-Drag Creation**: Define element boundaries by clicking start point and dragging to end point
- **Visual Feedback**: Real-time rectangle preview during creation
- **Size Validation**: Minimum size requirements prevent accidentally small elements
- **Automatic Naming**: New elements get unique names (compass_1, scale_bar_2, text_box_1, etc.)
- **Cancellation Support**: ESC key or Cancel button to abort creation
- **Element Management**: Delete key removes selected elements (except core elements)
- **Keyboard Shortcuts**: ESC (cancel creation), Delete (remove element)

### Custom Layout Configuration

Layout configurations are stored as JSON files with the following structure:

```json
{
  "main_map": {
    "position": [0.05, 0.05, 0.60, 0.93],
    "border": true,
    "border_color": "black",
    "border_width": 2
  },
  "title": {
    "position": [0.66, 0.88, 0.32, 0.10],
    "text": "PETA KEBUN 1 B\nPT. REBINMAS JAYA",
    "font_size": 14,
    "font_weight": "bold",
    "text_color": "black",
    "background_color": "white",
    "border": true
  },
  "legend": {
    "position": [0.66, 0.38, 0.32, 0.18],
    "title": "LEGENDA",
    "title_font_size": 12,
    "item_font_size": 10,
    "background_color": "white",
    "border": true
  }
  // ... other elements
}
```

### Position Coordinate System

All positions use matplotlib's figure coordinate system:
- **X-axis (left)**: 0.0 = left edge, 1.0 = right edge
- **Y-axis (bottom)**: 0.0 = bottom edge, 1.0 = top edge
- **Format**: [left, bottom, width, height]

### Dynamic Element Support

The system now supports multiple instances of certain elements:

```json
{
  "compass_1": {
    "position": [0.85, 0.85, 0.08, 0.08],
    "type": "compass"
  },
  "compass_2": {
    "position": [0.10, 0.85, 0.06, 0.06],
    "type": "compass"
  },
  "text_box_1": {
    "position": [0.70, 0.15, 0.25, 0.10],
    "type": "text_box",
    "text": "Custom Text Element",
    "font_size": 12,
    "text_color": "black",
    "background_color": "white"
  }
}
```

### Programmatic Usage

You can also use the custom layout generator programmatically:

```python
from custom_layout_generator import CustomLayoutMapGenerator

# Create generator with custom layout
generator = CustomLayoutMapGenerator(
    input_path="your_shapefile.shp",
    layout_config=your_custom_layout
)

# Load data
generator.load_data()
generator.load_belitung_data()

# Generate map
generator.create_custom_layout_map("output_map.pdf")
```

## Customization Examples

### Example 1: Moving Title to Bottom

```python
# Modify title position to bottom of page
layout_config = {
    "title": {
        "position": [0.66, 0.02, 0.32, 0.10],  # Bottom position
        "text": "CUSTOM TITLE\nBOTTOM POSITION",
        "font_size": 16,
        "text_color": "darkblue"
    }
}
```

### Example 2: Larger Legend with Custom Colors

```python
# Create larger legend with custom styling
layout_config = {
    "legend": {
        "position": [0.66, 0.30, 0.32, 0.30],  # Larger height
        "title": "CUSTOM LEGEND",
        "title_font_size": 14,
        "item_font_size": 11,
        "background_color": "lightgray",
        "border": true
    }
}
```

### Example 3: Side-by-Side Layout

```python
# Create side-by-side layout with main map on left, elements on right
layout_config = {
    "main_map": {
        "position": [0.05, 0.05, 0.45, 0.90]  # Narrower main map
    },
    "title": {
        "position": [0.55, 0.80, 0.40, 0.15]  # Right side, top
    },
    "legend": {
        "position": [0.55, 0.50, 0.40, 0.25]  # Right side, middle
    },
    "belitung_overview": {
        "position": [0.55, 0.25, 0.40, 0.20]  # Right side, lower
    },
    "logo_info": {
        "position": [0.55, 0.05, 0.40, 0.15]  # Right side, bottom
    }
}
```

## Troubleshooting

### Common Issues

1. **"No module named 'tkinter'"**
   - Install tkinter: `pip install tk` (usually included with Python)

2. **"File not found" errors**
   - Ensure all file paths are correct
   - Check that shapefile and associated files (.shx, .dbf, .prj) are present

3. **Layout elements not visible**
   - Check position coordinates are within 0.0-1.0 range
   - Ensure width and height are positive values
   - Verify elements don't overlap excessively

4. **Preview not updating**
   - Click "Refresh Preview" button
   - Check console for error messages

### Performance Tips

1. **Large Datasets**
   - Consider filtering data before loading
   - Use lower DPI for preview, higher for final output

2. **Complex Layouts**
   - Save layouts frequently during design
   - Test with simple layouts first

3. **Memory Usage**
   - Close preview windows when not needed
   - Restart application for very large datasets

## Default Layout Reference

The system maintains the exact same default layout as `professional_map_generator.py`:

- **Main Map**: Left side, 60% width, full height with margins
- **Title**: Top right, 32% width, 10% height
- **Legend**: Middle right, 32% width, 18% height
- **Belitung Overview**: Upper right, 32% width, 28% height
- **Logo/Info**: Bottom right, 32% width, 14% height
- **Compass**: Overlay on main map, top-right corner
- **Scale Bar**: Overlay on main map, bottom-left corner

## Integration with Existing System

The layout builder system is designed to be fully compatible with the existing codebase:

- **Backward Compatibility**: Original `professional_map_generator.py` remains unchanged
- **Modular Design**: Uses existing `map_elements.py` components
- **File Format Support**: Supports both shapefiles and TIFF files
- **Output Compatibility**: Generates identical output format (PDF)

## Future Enhancements

Potential future improvements:

1. **Template Library**: Pre-designed layout templates
2. **Batch Processing**: Apply layouts to multiple files
3. **Advanced Styling**: Gradients, shadows, advanced typography
4. **Export Options**: Additional output formats (PNG, SVG)
5. **Collaboration Features**: Share and import layouts from team members

## Support and Contribution

For questions, issues, or contributions:

1. Check the troubleshooting section above
2. Review existing code comments and documentation
3. Test with the provided example files
4. Create detailed issue reports with error messages and steps to reproduce

---

**Author**: Generated for Tree Counting Project  
**Date**: 2025  
**Version**: 1.0