@echo off
setlocal enabledelayedexpansion

echo ======================================
echo Maxwell EM Theory Processor Setup
echo ======================================
echo.

REM Colors for output - Windows 10+ supports ANSI escape codes
set RED=[31m
set GREEN=[32m
set YELLOW=[33m
set NC=[0m

REM Check Python version
echo Checking Python version...
for /f "tokens=2 delims= " %%a in ('python --version 2^>^&1') do set python_version=%%a
set required_version=3.9

if "%python_version%"=="" (
    echo %RED%✗%NC% Python not found. Please install Python 3.9 or higher.
    exit /b 1
)

REM Simple version check - this is basic but works for major/minor comparison
for /f "delims=." %%a in ("%python_version%") do set py_major=%%a
for /f "delims=." %%a in ("%python_version%") do for /f "tokens=2 delims=." %%b in ("%%a") do set py_minor=%%b
for /f "delims=." %%a in ("%required_version%") do set req_major=%%a
for /f "delims=." %%a in ("%required_version%") do for /f "tokens=2 delims=." %%b in ("%%a") do set req_minor=%%b

if %py_major% lss %req_major% (
    echo %RED%✗%NC% Python 3.9+ required, found %python_version%
    exit /b 1
) else if %py_major% equ %req_major% (
    if %py_minor% lss %req_minor% (
        echo %RED%✗%NC% Python 3.9+ required, found %python_version%
        exit /b 1
    )
)

echo %GREEN%✓%NC% Python %python_version% detected

REM Check if .env exists
echo.
echo Checking configuration...
if exist ".env" (
    echo %GREEN%✓%NC% .env file found
    
    REM Check if API keys are configured
    findstr /i "your-mathpix-app-id" ".env" > nul
    if %errorlevel% equ 0 (
        echo %YELLOW%⚠%NC%  Warning: Mathpix API keys not configured in .env
        echo    Please edit .env and add your Mathpix API keys
        echo.
        set /p "edit_env=Do you want to edit .env now? (y/n) "
        if /i "!edit_env!"=="y" (
            if exist "%ProgramFiles%\Notepad++\notepad++.exe" (
                start "" "%ProgramFiles%\Notepad++\notepad++.exe" ".env"
            ) else (
                notepad ".env"
            )
        )
    ) else (
        echo %GREEN%✓%NC% API keys appear to be configured
    )
) else (
    echo %YELLOW%⚠%NC%  .env file not found
    echo    Creating from .env.example...
    copy ".env.example" ".env" > nul
    echo %GREEN%✓%NC% Created .env file
    echo.
    echo    Please edit .env and add your Mathpix API keys:
    echo    - MATHPIX_APP_ID
    echo    - MATHPIX_APP_KEY
    echo.
    set /p "edit_env=Do you want to edit .env now? (y/n) "
    if /i "!edit_env!"=="y" (
        if exist "%ProgramFiles%\Notepad++\notepad++.exe" (
            start "" "%ProgramFiles%\Notepad++\notepad++.exe" ".env"
        ) else (
            notepad ".env"
        )
    ) else (
        echo Please edit .env before running the pipeline
        exit /b 1
    )
)

REM Check if virtual environment should be created
echo.
echo Checking virtual environment...
if exist "venv\" (
    echo %GREEN%✓%NC% Virtual environment exists
) else (
    echo Virtual environment not found
    set /p "create_venv=Create virtual environment? (recommended) (y/n) "
    if /i "!create_venv!"=="y" (
        echo Creating virtual environment...
        python -m venv venv
        if %errorlevel% equ 0 (
            echo %GREEN%✓%NC% Virtual environment created
        ) else (
            echo %RED%✗%NC% Failed to create virtual environment
            exit /b 1
        )
    )
)

REM Activate virtual environment if it exists
if exist "venv\" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo %GREEN%✓%NC% Virtual environment activated
)

REM Install dependencies
echo.
echo Installing dependencies...
pip install --upgrade pip > nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%✗%NC% Failed to upgrade pip
    exit /b 1
)

pip install -r requirements.txt > nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✓%NC% Dependencies installed
) else (
    echo %RED%✗%NC% Failed to install dependencies
    exit /b 1
)

REM Create input directory
echo.
echo Setting up directories...
mkdir input > nul 2>&1
mkdir output > nul 2>&1
echo %GREEN%✓%NC% Directories created

REM Test configuration
echo.
echo Testing configuration...
python config\config.py > nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✓%NC% Configuration is valid
) else (
    echo %RED%✗%NC% Configuration test failed
    echo Please check your .env file
    exit /b 1
)

REM Success message
echo.
echo ======================================
echo %GREEN%Setup Complete!%NC%
echo ======================================
echo.
echo Next steps:
echo 1. Place your Maxwell PDF in the 'input\' directory
echo 2. Run the pipeline:
echo.
echo %YELLOW%   python main_pipeline.py --pdf input\your_pdf.pdf --volume 1 --stage full%NC%
echo.
echo For more options, see:
echo    - README.md for project overview
echo    - USAGE_GUIDE.md for detailed usage
echo    - OPENROUTER_REMOVAL.md for latest updates
echo.
echo Quick test with sample pages:
echo %YELLOW%   python main_pipeline.py --pdf input\maxwell_vol1.pdf --volume 1 --page-ranges "1-10"%NC%
echo.

endlocal