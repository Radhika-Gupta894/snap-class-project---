@echo off
title Push SnapClass to GitHub
echo ===================================================
echo           Pushing Code to GitHub
echo ===================================================
echo.
cd /d "%~dp0"

echo [1/3] Staging all changes...
git add .

echo [2/3] Committing changes...
git commit -m "Fix database schema mismatches, restore clean UI dashboard layout, and connect landing page assets"

echo [3/3] Pushing to main branch on GitHub...
git push origin main

echo.
echo ===================================================
echo Push complete!
echo ===================================================
pause
