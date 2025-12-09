#!/bin/bash
# Quick Start Script for Agentic Text-to-SQL

echo "=========================================="
echo "Agentic Text-to-SQL - Quick Start"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ "$(uname)" == "Darwin" ] || [ "$(uname)" == "Linux" ]; then
    source .venv/bin/activate
else
    .venv/Scripts/activate
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your GOOGLE_API_KEY"
    echo "Get your key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Press Enter after you've added your API key..."
fi

# Initialize database
echo "🗄️  Initializing database..."
python -m src.database.db_manager

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Chainlit application..."
echo "   The app will open in your browser at http://localhost:8000"
echo ""

# Run Chainlit
chainlit run app.py
