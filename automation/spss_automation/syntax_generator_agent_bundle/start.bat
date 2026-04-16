@echo off
setlocal
chcp 65001 > nul
title SPSS Syntax Web UI

set "SCRIPT_DIR=%~dp0"
set "APP_PATH=%SCRIPT_DIR%app.py"
set "REQ_PATH=%SCRIPT_DIR%requirements.txt"
set "PYTHON_CMD="

call :resolve_python
if not defined PYTHON_CMD (
    echo.
    echo  [ERROR] Python executable was not found.
    echo          Install Python 3.8+ or check PATH / .venv.
    pause
    exit /b 1
)

echo.
echo  ============================================
echo   SPSS Syntax Web UI Launcher
echo  ============================================
echo.
echo  [INFO] Python command: %PYTHON_CMD%

call %PYTHON_CMD% -c "import flask" 1>nul 2>nul
if errorlevel 1 (
    echo  [SETUP] Flask not found. Installing from requirements.txt...
    call %PYTHON_CMD% -m pip install -r "%REQ_PATH%"
    if errorlevel 1 (
        echo  [ERROR] Dependency install failed.
        echo          Run "%PYTHON_CMD% -m pip install -r requirements.txt" manually.
        pause
        exit /b 1
    )
    echo  [DONE] Dependencies installed.
    echo.
)

echo  Your browser will open automatically.
echo  Close this window or press Ctrl+C to stop the server.
echo.

if /I "%SPSS_UI_DRY_RUN%"=="1" (
    echo  [INFO] Dry run complete.
    exit /b 0
)

call %PYTHON_CMD% "%APP_PATH%"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo  [EXIT] App exited with code %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%

:resolve_python
where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto :eof
)
where python >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :eof
)
if exist "%SCRIPT_DIR%..\\..\\..\\.venv\\Scripts\\python.exe" (
    set "PYTHON_CMD="%SCRIPT_DIR%..\\..\\..\\.venv\\Scripts\\python.exe""
    goto :eof
)
if exist "%SCRIPT_DIR%.venv\\Scripts\\python.exe" (
    set "PYTHON_CMD="%SCRIPT_DIR%.venv\\Scripts\\python.exe""
)
goto :eof
