@echo off
chcp 65001 >nul
title TOUR-LANG - Servidor Prototipo PHP (UNA Puno - EPIS)
cd /d "%~dp0"
echo ==============================================================
echo   Abriendo Analizador Sintactico PHP en http://localhost:8080
echo ==============================================================
start http://localhost:8080/graficador-sintactico.php
if exist "C:\xampp\php\php.exe" (
    "C:\xampp\php\php.exe" -S localhost:8080 -t GRAFICADOR
) else (
    php -S localhost:8080 -t GRAFICADOR
)
pause
