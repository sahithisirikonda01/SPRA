@echo off
SETLOCAL EnableDelayedExpansion
title SSERA Automatic Setup Wizard

echo ===================================================
echo   🛡️ SSERA: Smart Secure Assistant Setup
echo ===================================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed! Please install Python and try again.
    pause
    exit
)

:: 2. Install Dependencies
echo [1/4] Installing Privacy Engine libraries...
pip install presidio-analyzer presidio-anonymizer spacy --quiet

:: 3. Download Model
echo [2/4] Downloading Context Model (en_core_web_lg)...
python -m spacy download en_core_web_lg --quiet

:: 4. Configure Native Messaging Paths
echo [3/4] Configuring System Bridge...
set "BASE_DIR=%~dp0"
set "HOST_JSON=%BASE_DIR%com.ssera.privacy.json"
set "RUN_BAT=%BASE_DIR%native-host\run_ssera.bat"

:: Use PowerShell to safely update the JSON file path with double backslashes
set "ESCAPED_BAT=!RUN_BAT:\=\\!"
powershell -Command "(Get-Content '!HOST_JSON!') -replace '\"path\": \".*\"', '\"path\": \"!ESCAPED_BAT!\"' | Set-Content '!HOST_JSON!'"

:: 5. Register with Windows
echo [4/4] Writing to Windows Registry...
REG ADD "HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts\com.ssera.privacy" /ve /t REG_SZ /d "!HOST_JSON!" /f >nul

echo ===================================================
echo ✅ INSTALLATION COMPLETE!
echo 1. Open Chrome Extensions and get your Extension ID.
echo 2. Update 'allowed_origins' in native-host\com.ssera.privacy.json.
echo 3. Restart Chrome completely.
echo ===================================================
pause