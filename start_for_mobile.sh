#!/bin/bash

# Get local IP address
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)

echo "🚀 Starting Mental Health Coach for mobile access"
echo "📱 Your local IP address is: $LOCAL_IP"
echo ""
echo "To access from your phone:"
echo "  Frontend: http://$LOCAL_IP:3000"
echo "  Backend API: http://$LOCAL_IP:8000"
echo ""
echo "Make sure your phone is on the same WiFi network!"
echo ""

# Start backend in background
echo "Starting backend server..."
cd /Users/Q/Projects/AI-mental-health-coach
python3 -m uvicorn src.mental_health_coach.app:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd Frontend/mindful-app
npm run dev -- --hostname 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are running!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait 