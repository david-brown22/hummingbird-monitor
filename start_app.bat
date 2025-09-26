@echo off
echo 🐦 Starting Hummingbird Monitor Application...
echo.

echo 📋 Step 1: Starting Backend Server...
cd backend
start "Hummingbird Backend" cmd /k "venv\Scripts\activate && python main.py"
cd ..

echo.
echo 📋 Step 2: Starting Frontend Server...
cd frontend
start "Hummingbird Frontend" cmd /k "npm start"
cd ..

echo.
echo 📋 Step 3: Waiting for servers to start...
timeout /t 10 /nobreak >nul

echo.
echo 📋 Step 4: Opening browser to dashboard...
start http://localhost:3000

echo.
echo ✅ Hummingbird Monitor is starting up!
echo.
echo 📊 Backend API: http://localhost:8000
echo 🌐 Frontend Dashboard: http://localhost:3000
echo.
echo 💡 Use 'stop_app.bat' to stop the applications
echo.
pause
