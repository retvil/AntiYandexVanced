@echo off
setlocal
chcp 65001 >nul

echo ===========================================
echo   AntiYandex Build Script (both editions)
echo ===========================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Install Python from python.org
    pause
    exit /b
)

echo [1/4] Installing dependencies (psutil, ttkbootstrap, pyinstaller)...
python -m pip install --upgrade pip >nul
python -m pip install psutil ttkbootstrap pyinstaller >nul

echo [2/4] Building AntiYandexVanced.exe...
python -m PyInstaller --onefile --windowed --name AntiYandexVanced --hidden-import=psutil --collect-all ttkbootstrap --icon=logo.ico --add-data "logo.ico;." main.py
if %errorlevel% neq 0 (
    echo [ERROR] AntiYandexVanced build failed.
    pause
    exit /b
)

echo [3/4] Building AntiYandexExtended.exe...
python -m PyInstaller --onefile --windowed --name AntiYandexExtended --hidden-import=psutil --collect-all ttkbootstrap --icon=logo.ico --add-data "logo.ico;." main_extended.py
if %errorlevel% neq 0 (
    echo [ERROR] AntiYandexExtended build failed.
    pause
    exit /b
)

echo ===========================================
echo [4/4] Done! EXE files are in the dist folder
pause
