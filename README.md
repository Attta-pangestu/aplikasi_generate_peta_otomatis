# Professional Map Generator - Palm Oil Plantation

Aplikasi profesional untuk generate peta kebun kelapa sawit dengan layout standar surveyor dan fitur-fitur canggih.

## Fitur Utama

### ✅ Layout Profesional
- Layout sesuai standar peta surveyor profesional
- Panel kanan terorganisir dengan komponen terpisah
- Border biru untuk tampilan profesional
- Ukuran A3 landscape untuk printing berkualitas tinggi

### ✅ Sistem Koordinat
- **Koordinat dalam derajat** (WGS84) bukan UTM
- Format koordinat seperti: 107.916836
- Precision tinggi untuk akurasi maksimal

### ✅ Grid System
- **Tanda plus kecil** sebagai pengganti grid penuh
- Lebih bersih dan profesional
- Interval otomatis berdasarkan extent peta

### ✅ Peta Overview Belitung
- Menggunakan shapefile Belitung: `batas_desa_belitung.shp`
- Kategorisasi berdasarkan field **WADMKK**:
  - Belitung (warna hijau muda)
  - Belitung Timur (warna biru muda)
- Marker merah menunjukkan lokasi area kerja
- Overlay dengan sub divisi yang dipilih

### ✅ Sub Divisi Management
- **Default subdivisions** sesuai gambar:
  - SUB DIVISI AIR CENDONG
  - SUB DIVISI AIR KANDIS
  - SUB DIVISI AIR RAYA
- Tombol "Select Default" untuk kemudahan
- Filter otomatis berdasarkan pilihan

### ✅ Legenda Profesional
- Warna sesuai standar:
  - DIVISI GUNUNG PANJANG (Pink muda)
  - DIVISI GUNUNG RUM (Hijau muda)
  - DIVISI PADANG TEMBALUN (Coklat sandy)
- Layout panel terpisah dengan border

### ✅ Komponen Peta
- **Panel Judul**: Nama peta utama
- **Panel North Arrow & Scale**: Kompas dan skala 1:77.000
- **Panel Legenda**: Klasifikasi warna divisi
- **Panel Overview**: Peta Belitung dengan lokasi
- **Panel Logo**: Logo perusahaan dan info teknis

### ✅ Fitur Teknis
- Label BLOK pada setiap area
- Scale bar dengan segmen hitam-putih
- North arrow dengan simbol kompas
- Auto-zoom ke area yang dipilih
- Export ke PDF/PNG dengan DPI tinggi

## Installation

1. Install Python 3.8 atau lebih baru
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Via GUI (Recommended)
```bash
python map_generator_gui.py
```

### Via Command Line
```bash
python professional_map_generator.py
```

## Configuration

### Shapefile Input
- **Main data**: Shapefile dengan data sub divisi dan blok
- **Belitung overview**: `D:\...\batas_desa_belitung\batas_desa_belitung.shp`

### Default Settings
- **Koordinat**: WGS84 degrees (EPSG:4326)
- **DPI**: 300 (untuk kualitas printing)
- **Format**: PDF (recommended) atau PNG
- **Sub divisi default**: AIR CENDONG, AIR KANDIS, AIR RAYA

## File Structure

```
Create_Peta_PDF/
├── map_generator_gui.py           # GUI utama
├── professional_map_generator.py  # Core map engine
├── requirements.txt               # Dependencies
├── rebinmas_logo.jpg             # Logo perusahaan
├── run_map_generator.bat         # Windows shortcut
└── README.md                     # Dokumentasi ini
```

## Output Features

Peta yang dihasilkan memiliki:

1. **Main Map Area (70%)**:
   - Koordinat derajat di tepi
   - Tanda plus sebagai grid
   - Label BLOK pada setiap area
   - Warna berdasarkan sub divisi

2. **Right Panel (30%)**:
   - Judul peta (atas)
   - North arrow + scale
   - Legenda dengan warna
   - Peta overview Belitung
   - Logo + info perusahaan

## Troubleshooting

### Shapefile Belitung tidak ditemukan
- Pastikan path benar: `D:\...\batas_desa_belitung\batas_desa_belitung.shp`
- Check field WADMKK ada dalam shapefile
- Aplikasi akan tetap jalan tanpa overview jika tidak ada

### Koordinat tidak akurat
- Pastikan shapefile dalam CRS yang benar
- Aplikasi auto-convert ke WGS84
- Check extent data tidak terlalu jauh dari Belitung

### Memory Error
- Reduce DPI dari 1200 ke 300
- Pilih subset area yang lebih kecil
- Simplify geometri jika terlalu kompleks

## Customization

### Mengubah Warna Divisi
Edit di `professional_map_generator.py`:
```python
self.colors = {
    'SUB DIVISI AIR RAYA': '#FFB6C1',      # Pink
    'SUB DIVISI AIR CENDONG': '#98FB98',   # Green
    'SUB DIVISI AIR KANDIS': '#F4A460',    # Sandy Brown
}
```

### Mengubah Default Subdivisions
Edit di `map_generator_gui.py`:
```python
default_subdivisions = ['NAMA_SUB_DIVISI_1', 'NAMA_SUB_DIVISI_2']
```

### Mengubah Scale
Edit di `professional_map_generator.py`:
```python
ax.text(0.7, 0.7, 'Skala\n1:50.000', ...)  # Ubah dari 1:77.000
```

## Author

Generated for **Tree Counting Project - PT Rebinmas Jaya**
2025

## License

Internal use - PT Rebinmas Jaya