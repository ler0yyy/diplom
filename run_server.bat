@echo off
cd /d "%~dp0"

echo ========================================
echo  PollPoint - start server
echo ========================================
echo.

if not exist .venv goto no_venv

if not exist server\.env (
  echo Creating server\.env from .env.example ...
  copy server\.env.example server\.env >nul
  echo Edit server\.env and set PostgreSQL password in DATABASE_URL
  echo.
)

call .venv\Scripts\activate.bat

python -c "import flask" 2>nul
if errorlevel 1 goto no_flask

echo Server URL: http://localhost:5000
echo Stop with Ctrl+C
echo.

python -m server.run
pause
exit /b 0

:no_venv
echo ERROR: .venv not found. Run install_dependencies.bat first.
pause
exit /b 1

:no_flask
echo ERROR: Flask not installed. Run install_dependencies.bat first.
pause
exit /b 1
