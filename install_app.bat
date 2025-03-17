@echo off
setlocal EnableDelayedExpansion

REM Check if app name is provided
if "%~1"=="" (
    echo Usage: %0 ^<app_name^>
    exit /b 1
)

set "APP_NAME=%~1"
set "API_URL=http://localhost:8000/api/install/%APP_NAME%/"

echo Calling API for %APP_NAME%...
curl -X POST "%API_URL%" > response.json

REM Parse JSON response using PowerShell and extract install_url
for /f "tokens=*" %%i in ('powershell -Command "Get-Content response.json | ConvertFrom-Json | Select-Object -ExpandProperty install_url"') do (
    set "INSTALL_URL=%%i"
)

REM Check if INSTALL_URL is empty
if "!INSTALL_URL!"=="" (
    echo Error: No install URL returned from API. Check response.json.
    type response.json
    exit /b 1
)

echo Triggering installation for %APP_NAME% with URL: !INSTALL_URL!...
"C:\localapp\LocalApp.exe" "!INSTALL_URL!"

del response.json
endlocal