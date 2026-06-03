@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================
echo  PollPoint - Start Script (Windows)
echo ========================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH.
        echo Please install Python from python.org and try again.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

:: 2. Setup Virtual Environment
if not exist .venv (
    echo [1/5] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [1/5] Virtual environment found.
)

:: Activate venv
call .venv\Scripts\activate.bat

:: 3. Install Dependencies
%PYTHON_CMD% -c "import flask, flask_sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo [2/6] Installing dependencies...
    %PYTHON_CMD% -m pip install --upgrade pip >nul 2>&1
    %PYTHON_CMD% -m pip install -r server\requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies.
        echo Trying with longer timeout and mirror...
        %PYTHON_CMD% -m pip install --default-timeout=300 -r server\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        if errorlevel 1 (
            echo ERROR: Still failed. Check internet connection or VPN.
            pause
            exit /b 1
        )
    )
) else (
    echo [2/6] Dependencies are already installed.
)

:: 4. Check PostgreSQL and create database
echo [3/6] Checking PostgreSQL...

:: Check if psql exists
where psql >nul 2>&1
if errorlevel 1 (
    echo ========================================================
    echo  ERROR: PostgreSQL is not installed or not in PATH.
    echo.
    echo  Please install PostgreSQL:
    echo  1. Download from https://www.postgresql.org/download/windows/
    echo  2. Install with default settings
    echo  3. Remember the password you set for 'postgres' user
    echo  4. Add PostgreSQL bin folder to PATH or restart this script
    echo ========================================================
    pause
    exit /b 1
)

:: Check if database exists, create if not
echo Checking database 'pollpoint'...
psql -U postgres -d postgres -c "SELECT 1 FROM pg_database WHERE datname='pollpoint';" >nul 2>&1
if errorlevel 1 (
    echo Creating database 'pollpoint'...
    createdb -U postgres pollpoint
    if errorlevel 1 (
        echo ERROR: Failed to create database. Check your postgres password.
        echo Run: createdb -U postgres pollpoint
        pause
        exit /b 1
    )
    echo Database created.
) else (
    echo Database already exists.
)

:: 5. Environment Variables
if not exist server\.env (
    echo [4/6] Creating server\.env from example...
    copy server\.env.example server\.env >nul
    echo ========================================================
    echo  WARNING: server\.env created.
    echo  Please open server\.env in Notepad and set your PGPASSWORD.
    echo  ^<The password you entered during PostgreSQL installation^>
    echo ========================================================
    pause
) else (
    echo [4/6] Environment file found.
)

:: 6. Database Setup
:check_db
echo [5/6] Checking database connection...
%PYTHON_CMD% -m server.check_db
if errorlevel 1 (
    echo ========================================================
    echo  ERROR: Database connection failed.
    echo  1. Make sure PostgreSQL is running
    echo  Check services.msc if necessary
    echo  2. Open server\.env and check your PGPASSWORD.
    echo  Fix the issue, then press any key to try again.
    echo ========================================================
    pause
    goto check_db
)

echo Initializing database tables and test users...
%PYTHON_CMD% -m server.init_db >nul 2>&1
%PYTHON_CMD% -m server.seed >nul 2>&1


:: 7. Start Server
echo.
echo [6/6] Setup complete!
echo ========================================
echo  Starting PollPoint Server...
echo  URL: http://localhost:5001
echo  Stop with Ctrl+C
echo ========================================
%PYTHON_CMD% -m server.run

pause
