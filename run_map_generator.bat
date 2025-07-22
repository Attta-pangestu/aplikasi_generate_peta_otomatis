@echo off
echo ================================================
echo Professional Map Generator for Palm Oil Plantation
echo ================================================
echo.

echo Installing required packages...
pip install -r requirements.txt

echo.
echo Generating professional map...
python professional_map_generator.py

echo.
echo Map generation completed!
echo Check the output file: Peta_Profesional_Sub_Divisi.pdf
echo.
pause