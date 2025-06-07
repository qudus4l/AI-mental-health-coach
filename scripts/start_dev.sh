#!/bin/bash
# Development start script for AI Mental Health Coach

echo "🚀 Starting AI Mental Health Coach in development mode..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Set development environment variables
export ENVIRONMENT=development
export DATABASE_URL=sqlite:///./mental_health_coach.db

# Start the application
echo "🏃 Starting FastAPI application..."
cd src && uvicorn mental_health_coach.main:app --reload --host 0.0.0.0 --port 8000 