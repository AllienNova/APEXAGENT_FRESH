#!/bin/bash
echo "Starting ApexAgent..."

# Start backend
cd app/backend && python3 main.py &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# Open frontend in browser
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000
elif command -v open > /dev/null; then
    open http://localhost:5000
else
    echo "Frontend available at: http://localhost:5000"
fi

echo "ApexAgent is running!"
echo "Press Ctrl+C to stop"

# Wait for user to stop the process
trap "kill $BACKEND_PID; echo 'ApexAgent stopped.'; exit 0" INT
wait
