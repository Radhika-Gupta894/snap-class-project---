@echo off
title SnapClass AI Dashboard
echo ===================================================
echo      Starting SnapClass Streamlit Dashboard
echo ===================================================
echo.
cd /d "%~dp0"
echo Launching SnapClass Dashboard at http://localhost:8501 ...
start "" "http://localhost:8501"
.\venv312\Scripts\streamlit.exe run app.py
pause
