@echo off
cd /d "%~dp0"
if not exist venv (
  py -m venv venv 2>nul || python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
if exist keys.bat call keys.bat
set HOST=0.0.0.0
set IP=
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
set IP=%IP: =%
echo.
echo ===== USE ON YOUR PHONE (same Wi-Fi as this computer) =====
echo Open this on the phone:   http://%IP%:5000
echo If Windows asks about the firewall, click Allow access for Python.
echo ==========================================================
echo.
python app.py
pause
