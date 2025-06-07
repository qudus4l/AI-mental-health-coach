#!/bin/bash
# Build script for Railway - Backend only

echo "🔨 Building Python Backend..."

# Ensure we have pip
if ! command -v pip &> /dev/null; then
    echo "❌ pip not found, installing..."
    python -m ensurepip --upgrade
fi

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build complete!" 