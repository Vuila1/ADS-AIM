@echo off
chcp 65001 >nul
echo ========================================
echo    ADS AIMBOT - SNAP MODE LAUNCHER
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [LOI] Khong tim thay moi truong ao!
    echo Chay install.bat truoc
    pause
    exit /b 1
)

call venv\Scripts\activate
python lunar.py

pause