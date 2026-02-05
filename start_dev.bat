@echo off
title Este Dev Launcher
color 0A
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║     ESTE AI Kiosk - Development Mode     ║
echo  ╚══════════════════════════════════════════╝
echo.

:: 1. Check for Ollama (Port 11434)
echo [1/4] Checking Ollama...
netstat -ano | find "11434" | find "LISTENING" >nul
if "%ERRORLEVEL%"=="0" (
    echo       ✓ Ollama is running
) else (
    color 0C
    echo       ✗ Ollama is NOT running!
    echo       Please start Ollama first, then re-run this script.
    echo.
    pause
    exit /b 1
)

:: 2. Start Backend (in background window)
echo [2/4] Starting Backend Server...
start "Este Server" cmd /k "cd server && if exist venv\Scripts\activate (call venv\Scripts\activate) else (echo Using global python...) && uvicorn main:app --host 0.0.0.0 --port 8000"

:: 3. Wait for backend to be ready (poll health endpoint)
echo [3/4] Waiting for server to initialize...
echo       (This may take 1-2 minutes on first run)
echo.

:wait_loop
ping -n 2 127.0.0.1 >nul
curl -s http://localhost:8000/ >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo       ✓ Server is READY!
    goto server_ready
)
echo|set /p="."
goto wait_loop

:server_ready
echo.

:: 4. Start Frontend
echo [4/4] Starting Frontend...
start "Este Client" cmd /k "cd client && npm run dev"

:: 5. Wait a moment for Vite to start, then open browser
ping -n 4 127.0.0.1 >nul
start http://localhost:5173

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║           ALL SYSTEMS GO! 🚀             ║
echo  ╠══════════════════════════════════════════╣
echo  ║  Frontend: http://localhost:5173         ║
echo  ║  Backend:  http://localhost:8000         ║
echo  ╚══════════════════════════════════════════╝
echo.
echo Press any key to close this window (servers will keep running)...
pause >nul
