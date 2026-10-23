@echo off
cd /d "%~dp0"
if not exist venv (
  py -m venv venv 2>nul || python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
if exist keys.bat call keys.bat
echo.
echo Open http://127.0.0.1:5000 in Chrome. Press Ctrl+C to stop.
echo.
python app.py
pause
