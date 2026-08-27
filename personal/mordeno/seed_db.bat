@echo off
echo ========================================================
echo   Mordeno Banking System - Seeding Database
echo ========================================================
echo.
cd /d %~dp0appserver
python seed.py
pause
