@echo off
echo Starting ApexAgent...

:: Start backend
start cmd /c "cd app\backend && python main.py"

:: Wait a moment for backend to initialize
timeout /t 2 /nobreak > nul

:: Open frontend in browser
start http://localhost:5000

echo ApexAgent is running!
