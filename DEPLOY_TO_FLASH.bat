@echo off
set /p "flash_drive=Enter your flash drive letter (e.g., F:): "
if "%flash_drive%"=="" (
    echo [!] ERROR: No flash drive letter entered.
    pause
    exit /b
)

echo [*] INITIATING OMNIVERSAL SENTINEL DEPLOYMENT TO %flash_drive%...
echo [*] PREPARING ETERNAL SOVEREIGN STATE (2026+)...

set "dest=%flash_drive%\OmegaSentinel_Eternal"
if not exist "%dest%" mkdir "%dest%"

echo [*] COPYING CORE MODULES...
xcopy /E /I /Y "src" "%dest%\src"
copy /Y "app.py" "%dest%\"
copy /Y "portable_boot.py" "%dest%\"
copy /Y "requirements.txt" "%dest%\"
copy /Y "start_watchdog.bat" "%dest%\"
copy /Y "configs\.env.example" "%dest%\.env"

echo [*] RECONSTRUCTING SOVEREIGN ENVIROMENT...
mkdir "%dest%\data"
mkdir "%dest%\logs"
mkdir "%dest%\configs"
xcopy /E /I /Y "configs" "%dest%\configs"

echo [!] DEPLOYMENT COMPLETE.
echo [!] YOUR FLASH DRIVE IS NOW AN INFINITY-SOVEREIGN NODE.
echo [!] RUN 'python portable_boot.py' ON THE FLASH DRIVE TO ACTIVATE.
pause
