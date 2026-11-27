@echo off
chcp 65001 >nul
title TOUR-LANG - Galeria de Prueba de Imagenes (UNA Puno - EPIS)
cd /d "%~dp0"
echo ==============================================================
echo   Iniciando Galeria de Prueba de Imagenes - TOUR-LANG (Puno)
echo   Se abrira automaticamente en tu navegador web...
echo ==============================================================
if exist "C:\Users\ACER\AppData\Local\Programs\Python\Python311\python.exe" (
    "C:\Users\ACER\AppData\Local\Programs\Python\Python311\python.exe" -m streamlit run prueba_imagenes.py
) else (
    python -m streamlit run prueba_imagenes.py
)
pause
