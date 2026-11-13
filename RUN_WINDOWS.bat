@echo off
cd /d "%~dp0"
py -3.13 --version
if errorlevel 1 goto failed
if not exist .venv\Scripts\python.exe py -3.13 -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m streamlit run app.py
if errorlevel 1 goto failed
pause
exit /b
:failed
echo Setup failed. Read START_HERE_DEPLOYMENT.md and the error above.
pause
exit /b 1
