#!/bin/bash

# Script to run the Mister White Game API server

echo "🚀 Starting Mister White Game API..."
echo "📡 Server will be available at http://localhost:8001"
echo "📚 API documentation at http://localhost:8001/docs"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Please create a .env file with your API keys:"
    echo "   OPENAI_API_KEY=your_key"
    echo "   MISTRAL_API_KEY=your_key"
    echo ""
fi

# Run the server
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

