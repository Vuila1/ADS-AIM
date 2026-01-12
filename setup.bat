@echo off
echo ========================================
echo    ADS AIMBOT PROJECT SETUP
echo ========================================
echo.
echo [1/5] Creating project structure...

REM Tạo thư mục
mkdir lib\models 2>nul
mkdir lib\config 2>nul
mkdir lib\mouse 2>nul
mkdir lib\utils 2>nul
mkdir docs 2>nul
mkdir scripts 2>nul
mkdir tests 2>nul
mkdir backups 2>nul

echo [2/5] Creating configuration files...

REM Tạo config.json
echo { > lib\config\config.json
echo   "version": "2.0.0", >> lib\config\config.json
echo   "detection": { >> lib\config\config.json
echo     "confidence": 0.45, >> lib\config\config.json
echo     "fov": 350, >> lib\config\config.json
echo     "aim_height": 10 >> lib\config\config.json
echo   }, >> lib\config\config.json
echo   "aim": { >> lib\config\config.json
echo     "smooth_factor": 0.15, >> lib\config\config.json
echo     "max_offset": 100, >> lib\config\config.json
echo     "noise_intensity": 1.5 >> lib\config\config.json
echo   } >> lib\config\config.json
echo } >> lib\config\config.json

echo [3/5] Creating batch scripts...

REM Tạo install.bat
echo @echo off > install.bat
echo echo Installing ADS Aimbot dependencies... >> install.bat
echo python -m pip install --upgrade pip >> install.bat
echo pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 >> install.bat
echo pip install ultralytics opencv-python mss pywin32 pynput termcolor >> install.bat
echo pause >> install.bat

REM Tạo run.bat
echo @echo off > run.bat
echo echo Starting ADS Aimbot... >> run.bat
echo python lunar.py >> run.bat
echo pause >> run.bat

echo [4/5] Creating requirements.txt...

REM Tạo requirements.txt
echo torch>=2.0.0 > requirements.txt
echo torchvision>=0.15.0 >> requirements.txt
echo ultralytics>=8.0.0 >> requirements.txt
echo opencv-python>=4.8.0 >> requirements.txt
echo mss>=7.0.0 >> requirements.txt
echo pywin32>=306 >> requirements.txt
echo pynput>=1.7.6 >> requirements.txt
echo termcolor>=2.3.0 >> requirements.txt

echo [5/5] Creating README.md...

REM Tạo README.md
echo # ADS Aimbot > README.md
echo. >> README.md
echo Project setup complete! >> README.md
echo. >> README.md
echo To install dependencies, run: >> README.md
echo \`\`\` >> README.md
echo install.bat >> README.md
echo \`\`\` >> README.md
echo. >> README.md
echo To run the aimbot, run: >> README.md
echo \`\`\` >> README.md
echo run.bat >> README.md
echo \`\`\` >> README.md

echo.
echo ========================================
echo    SETUP COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Edit lib\config\config.json
echo 2. Place your model at lib\models\best.pt
echo 3. Run install.bat to install dependencies
echo 4. Run run.bat to start the aimbot
echo.
pause