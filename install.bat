@echo off
chcp 65001 >nul
echo ========================================
echo    ADS AIMBOT - INSTALLATION (SNAP MODE)
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Khong tim thay Python!
    echo Cai dat Python 3.8+ tu python.org
    pause
    exit /b 1
)

REM Tao virtual environment
echo [1/5] Tao moi truong ao...
python -m venv venv

REM Kich hoat
echo [2/5] Kich hoat moi truong...
call venv\Scripts\activate

REM Upgrade pip
echo [3/5] Nang cap pip...
python -m pip install --upgrade pip

REM Cai dat dependencies
echo [4/5] Cai dat thu vien...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install ultralytics opencv-python mss pywin32 pynput termcolor numpy Pillow

REM Tao thu muc
echo [5/5] Tao cau truc thu muc...
if not exist "lib\models" mkdir lib\models
if not exist "lib\config" mkdir lib\config
if not exist "lib\mouse" mkdir lib\mouse

echo.
echo ========================================
echo    CAI DAT HOAN TAT!
echo ========================================
echo.
echo Huong dan:
echo 1. Dat model YOLO vao: lib\models\best.pt
echo 2. Chinh sua cai dat: lib\config\config.json
echo 3. Chay: python lunar.py
echo.
echo Dieu khien:
echo   INSERT - Mo menu
echo   F1     - Bat/tat aimbot
echo   F2     - Thoat
echo   RMB    - Giu de ngam
echo.
pause