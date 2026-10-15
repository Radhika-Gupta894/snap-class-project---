@echo off
title SnapClass AI Launcher
echo ===================================================
echo           Starting SnapClass AI Servers
echo ===================================================
echo.

cd /d "%~dp0"

echo [1/2] Launching Streamlit Dashboard (Port 8501)...
start "SnapClass - Streamlit Dashboard (Port 8501)" cmd /k ".\venv312\Scripts\streamlit.exe run app.py"

echo [2/2] Launching Flask Landing Page (Port 5002)...
start "SnapClass - Flask Landing Page (Port 5002)" cmd /k ".\venv312\Scripts\python.exe frontend\app.py"

echo.
echo ===================================================
echo Both servers have been launched in separate windows!
echo - Landing Page:  http://localhost:5002
echo - Dashboard:     http://localhost:8501
echo ===================================================
echo Opening Landing Page in default browser...
timeout /t 3 >nul
start http://localhost:5002
