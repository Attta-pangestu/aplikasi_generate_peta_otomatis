# Map Layout Editor

A visual editor for arranging map components with drag-and-drop functionality, designed to work with the Professional Map Generator.

## Features

- **Visual Canvas**: Drag and drop interface for arranging map elements
- **Element Positioning**: Move elements anywhere on the canvas
- **Scaling**: Resize elements with intuitive controls
- **Preview**: Real-time preview of your map layout
- **Export**: Generate professional maps with custom layouts
- **Save/Load**: Save your layouts for later use

## How to Use

1. **Run the Editor**:
   ```bash
   python map_layout_editor.py
   ```

2. **Select Input File**:
   - Choose between Shapefile (polygon-based) or TIFF (raster image) input
   - Browse for your input file using the file dialogs

3. **Adjust Layout Elements**:
   - Use the "Layout Elements" tab to see all map components
   - Select elements from the list to adjust their properties
   - Drag elements directly on the canvas to reposition them

4. **Customize Properties**:
   - Use the "Properties" tab to adjust position, size, and scale
   - Use keyboard shortcuts for quick scaling:
     - Ctrl++ to scale up
     - Ctrl+- to scale down
     - Ctrl+0 to reset scale

5. **Preview Your Layout**:
   - Click "Refresh Preview" to see your changes
   - Use the canvas toolbar to zoom and pan

6. **Export Your Map**:
   - Set your output file path
   - Choose resolution (DPI)
   - Click "Export Map" to generate your professional map

7. **Save Your Layout**:
   - Save your layout configuration for later use
   - Load previously saved layouts to continue working

## Requirements

- Python 3.6+
- tkinter (usually included with Python)
- matplotlib
- geopandas
- rasterio
- numpy
- contextily
- matplotlib-scalebar

## Installation

```bash
pip install -r requirements.txt
```

## Layout Elements

The editor includes the following map components:

1. **Main Map Area**: The primary map display
2. **Title Box**: Map title and subtitle
3. **Legend Box**: Color legend for map features
4. **Belitung Overview**: Location context map
5. **Logo and Info**: Company logo and information

Each element can be positioned and sized independently to create your perfect map layout.

## Customization

The layout editor allows you to:

- Move any element to any position on the canvas
- Resize elements to fit your needs
- Adjust the overall layout proportions
- Save custom layouts for reuse
- Export maps with your custom layouts

## Integration with Professional Map Generator

The layout editor works seamlessly with the Professional Map Generator, allowing you to:

- Use all the professional features of the base generator
- Apply custom layouts to any map project
- Maintain consistency across different maps
- Quickly iterate on layout designs

## Keyboard Shortcuts

- **Ctrl++**: Scale selected element up by 10%
- **Ctrl+-**: Scale selected element down by 10%
- **Ctrl+0**: Reset scale of selected element