#!/bin/bash

# Bybit Trading Bot Startup Script
# This script activates the virtual environment and starts the webhook server

echo "🚀 Starting Bybit Trading Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import pybit, requests, dotenv" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if config file exists
if [ ! -f "config.env" ]; then
    echo "❌ Configuration file not found. Please create config.env with your Bybit API credentials."
    exit 1
fi

echo "✅ Configuration verified"
echo "🌐 Starting webhook server on port 8080..."
echo "📝 Logs will be written to webhook.log and trading.log"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the webhook server
python webhook_server.py
