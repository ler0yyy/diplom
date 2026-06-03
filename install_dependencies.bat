@echo off
cd /d "%~dp0"

echo ========================================
echo  PollPoint - install Python dependencies
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 goto no_python

if not exist .venv (
  echo Creating .venv ...
  python -m venv .venv
  if errorlevel 1 goto venv_fail
)

call .venv\Scripts\activate.bat

echo Upgrading pip ...
python -m pip install --upgrade pip --default-timeout=300
echo.

set PIP_DEFAULT_TIMEOUT=300

echo [1/3] Install from PyPI timeout 300s ...
pip install -r server\requirements.txt --default-timeout=300
if not errorlevel 1 goto verify

echo.
echo [2/3] PyPI failed. Trying Tsinghua mirror ...
pip install -r server\requirements.txt --default-timeout=300 -i https://pypi.tuna.tsinghua.edu.cn/simple
if not errorlevel 1 goto verify

echo.
echo [3/3] Installing packages one by one ...
pip install flask --default-timeout=300
pip install flask-cors --default-timeout=300
pip install flask-sqlalchemy --default-timeout=300
pip install flask-jwt-extended --default-timeout=300
pip install flask-bcrypt --default-timeout=300
pip install pg8000 --default-timeout=300
pip install python-dotenv --default-timeout=300
pip install flask-migrate --default-timeout=300

:verify
echo.
echo Checking imports ...
python -c "import flask; import flask_cors; import flask_sqlalchemy; import flask_jwt_extended; import flask_bcrypt; import pg8000; import dotenv; print('OK')"
if errorlevel 1 goto install_fail

echo.
echo ========================================
echo  DONE. Next steps:
echo  1) Edit server\.env - set PostgreSQL password
echo  2) Run setup_db.bat
echo  3) Run run_server.bat
echo ========================================
pause
exit /b 0

:no_python
echo ERROR: Python not found. Install Python 3.10+ from python.org
echo        Check "Add Python to PATH" during install.
pause
exit /b 1

:venv_fail
echo ERROR: Could not create .venv
pause
exit /b 1

:install_fail
echo.
echo ERROR: Some packages failed. Check internet / VPN / antivirus.
echo Try: pip install flask --default-timeout=300 -i https://pypi.tuna.tsinghua.edu.cn/simple
pause
exit /b 1
