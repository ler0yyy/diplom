@echo off
cd /d "%~dp0"

echo ========================================
echo  PollPoint - setup database
echo ========================================
echo.

if not exist .venv goto no_venv

call .venv\Scripts\activate.bat

if not exist server\.env (
  copy server\.env.example server\.env >nul
  echo Created server\.env - edit PGPASSWORD before continue!
  echo.
  pause
)

echo Testing PostgreSQL connection ...
python -m server.check_db
if errorlevel 1 goto db_fail

echo Creating tables ...
python -m server.init_db
if errorlevel 1 goto db_fail

echo.
echo Creating test users ...
python -m server.seed
if errorlevel 1 goto seed_fail

echo.
echo DONE. Run run_server.bat
pause
exit /b 0

:no_venv
echo ERROR: Run install_dependencies.bat first.
pause
exit /b 1

:db_fail
echo ERROR: Database setup failed. Edit server\.env - set PGPASSWORD to your postgres password.
pause
exit /b 1

:seed_fail
echo ERROR: seed failed.
pause
exit /b 1
