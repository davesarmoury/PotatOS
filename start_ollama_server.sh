#!/bin/bash

# Ollama Network Server Startup Script

echo "🤖 Starting PotatOS Ollama Server..."

# Get IP address
IP=$(hostname -I | awk '{print $1}')
echo "📡 Server IP address: $IP"

# Check port
PORT=11434
if netstat -ln | grep -q ":$PORT "; then
    echo "⚠️  Port $PORT already in use!"
    echo "Stopping existing Ollama process..."
    pkill ollama
    sleep 2
fi

# Check model
MODEL="llama3.2:3b"
echo "🔍 Model check: $MODEL"
if ! ollama list | grep -q "$MODEL"; then
    echo "📥 Downloading model: $MODEL"
    ollama pull "$MODEL"
else
    echo "✅ Model available: $MODEL"
fi

# Set environment variable for network access
export OLLAMA_HOST=0.0.0.0

echo "🚀 Starting Ollama server..."
echo "📍 Access URL: http://$IP:$PORT"
echo "⏹️  Use Ctrl+C to stop"
echo ""

# Start server
ollama serve
