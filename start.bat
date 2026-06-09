@echo off
title AI Newsroom Assistant
echo ============================================
echo   AI Newsroom Assistant - Starting Up
echo ============================================
echo.

:: Check for .env
if not exist "%~dp0backend\.env" (
  echo [!] backend\.env not found!
  echo [!] Create it with:  ANTHROPIC_API_KEY=sk-ant-...
  echo.
  pause
  exit /b 1
)

:: Start Backend
echo [1/2] Starting FastAPI Backend on port 8000...
start "AI Newsroom Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: Wait for backend
timeout /t 3 /nobreak > nul

:: Open standalone HTML app (no npm needed)
echo [2/2] Opening Application in browser...
start "" "%~dp0frontend\app.html"

echo.
echo =============================================
echo  App:      frontend\app.html (open in browser)
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo =============================================
echo.
echo Press any key to stop the backend...
pause > nul
taskkill /fi "WINDOWTITLE eq AI Newsroom Backend" /t /f > nul 2>&1
