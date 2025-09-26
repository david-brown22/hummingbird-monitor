@echo off
echo 🛑 Stopping Hummingbird Monitor Application...
echo.

echo 📋 Step 1: Stopping Frontend Server (Node.js)...
taskkill /f /im node.exe 2>nul
if %errorlevel% equ 0 (
    echo ✅ Frontend server stopped
) else (
    echo ℹ️  No frontend server found running
)

echo.
echo 📋 Step 2: Stopping Backend Server (Python)...
taskkill /f /im python.exe 2>nul
if %errorlevel% equ 0 (
    echo ✅ Backend server stopped
) else (
    echo ℹ️  No backend server found running
)

echo.
echo 📋 Step 3: Clearing ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    taskkill /f /pid %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /f /pid %%a 2>nul
)

echo.
echo ✅ Hummingbird Monitor has been stopped!
echo.
echo 💡 Use 'start_app.bat' to start the applications again
echo.
pause
