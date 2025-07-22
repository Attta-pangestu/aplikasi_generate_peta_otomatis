import geopandas as gpd

files = {
    "batas_desa_belitung": "batas_desa_belitung.shp",
    "clipBelitung": "clipBelitung.shp",
    "kajian_utama": "NAMA_FILE_KAJIAN_UTAMA.shp"  # Ganti dengan nama file shapefile utama Anda
}

for name, path in files.items():
    try:
        gdf = gpd.read_file(path)
        print(f"{name}:")
        print(f"  CRS: {gdf.crs}")
        print(f"  Bounds: {gdf.total_bounds}")
        print()
    except Exception as e:
        print(f"{name}: ERROR - {e}")