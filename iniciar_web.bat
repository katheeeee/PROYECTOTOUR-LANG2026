@echo off
chcp 65001 >nul
title TOUR-LANG | Compilador y Plataforma Web (UNA Puno - EPIS)
cd /d "%~dp0"
echo ==============================================================
echo   Iniciando Plataforma Web Interactiva TOUR-LANG (UNA Puno)
echo ==============================================================
if exist "C:\Users\ACER\AppData\Local\Programs\Python\Python311\python.exe" (
    "C:\Users\ACER\AppData\Local\Programs\Python\Python311\python.exe" -m streamlit run app.py
) else (
    python -m streamlit run app.py
)
pause
