@echo off
set ZIP=%1
if "%ZIP%"=="" for /f "delims=" %%a in ('dir /b /od backups\NeoAutonomous_Backup_*.zip 2^>nul') do set ZIP=backups\%%a
echo Verifierar...
py ewa\safeguard.py verify "%ZIP%"
if not "%ZIP%"=="" (
  echo Återställer...
  py ewa\safeguard.py restore "%ZIP%"
)
py -m venv .venv
call .venv\Scripts\activate
py -m pip install -U pip
py -m pip install -r requirements.txt
uvicorn ewa.server:app --host 127.0.0.1 --port 8123

