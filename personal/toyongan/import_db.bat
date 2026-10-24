@echo off
echo ========================================================
echo   ESPADA Banking System - Importing toyongan.sql to MySQL
echo ========================================================
echo.

if exist "C:\xampp\mysql\bin\mysql.exe" (
    "C:\xampp\mysql\bin\mysql.exe" -u root < "%~dp0toyongan.sql"
    echo [*] Database imported successfully via XAMPP MySQL!
) else (
    mysql -u root < "%~dp0toyongan.sql"
    echo [*] Database imported successfully via system MySQL!
)

echo.
pause
