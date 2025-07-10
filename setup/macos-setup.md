````markdown
# 🍎 macOS Setup Guide

Complete setup guide for running GLaDOS on macOS systems.

## 🎯 Role in GLaDOS System

Your macOS system can serve as:
- 🧠 **AI Server** - Running Ollama LLM (excellent for M1/M2 Macs)
- 🌐 **Web Interface** - Portal-themed control interface
- 🎤 **Voice Interface** - TTS and Voice Recognition (limited)
- 🔄 **All-in-One** - Complete GLaDOS system

## 📋 Prerequisites

### **System Requirements**
- macOS 11.0+ (Big Sur or later)
- 8GB+ RAM (16GB+ recommended)
- 10GB+ free disk space
- Apple Silicon (M1/M2) or Intel Mac

### **Software Requirements**
- Xcode Command Line Tools
- Homebrew package manager
- Python 3.8+

## 🚀 Installation Steps

### Step 1: Install Prerequisites

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install essential packages
brew install git curl wget htop nano python3 portaudio ffmpeg
```

### Step 2: Install Ollama

```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Or install via Homebrew
brew install ollama

# Start Ollama service
brew services start ollama

# Download GLaDOS personality model
ollama pull llama3.2:3b

# Verify installation
ollama list
```

### Step 3: Clone Repository

```bash
# Clone GLaDOS repository
git clone https://github.com/your-username/GLaDOS.git
cd GLaDOS/voice_ollama
```

### Step 4: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv glados_env
source glados_env/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 5: Install Piper TTS

```bash
# Navigate to Piper directory
cd train_piper

# Install Piper dependencies
pip install -r requirements.txt

# Download GLaDOS voice model
python download_glados.py

# Test Piper installation
echo "Hello, this is GLaDOS speaking" | python -m piper --model glados.onnx --output_file test.wav
afplay test.wav
```

### Step 6: Configure Audio (Optional)

```bash
# Test audio output
afplay /System/Library/Sounds/Ping.aiff

# Install audio utilities
brew install sox

# Test microphone (if using voice recognition)
rec -t wav -c 1 -r 16000 test_mic.wav trim 0 3
afplay test_mic.wav
```

### Step 7: Configure Network Settings

```bash
# Edit configuration file
nano config.json
```

**Example config.json (All-in-One setup):**
```json
{
  "ollama": {
    "host": "localhost",
    "port": 11434,
    "model": "llama3.2:3b"
  },
  "web": {
    "port": 8000
  },
  "rag": {
    "port": 5000
  },
  "piper": {
    "port": 5001
  },
  "audio": {
    "input_device": 0,
    "output_device": 0,
    "sample_rate": 16000
  }
}
```

**Example config.json (AI Server only):**
```json
{
  "ollama": {
    "host": "0.0.0.0",
    "port": 11434,
    "model": "llama3.2:3b"
  },
  "web": {
    "port": 8000
  },
  "external_devices": {
    "jetson_ip": "192.168.1.101"
  }
}
```

### Step 8: Configure Ollama for Network Access

```bash
# Configure Ollama to accept network connections
echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.zshrc
source ~/.zshrc

# Restart Ollama
brew services restart ollama
```

### Step 9: Setup RAG System

```bash
# Navigate to RAG directory
cd ../wiki_rag

# Install RAG dependencies
pip install -r requirements.txt

# Download and process Portal wiki data
python wiki_llamaindex_preprocess.py
```

### Step 10: Create Launch Scripts

```bash
# Create start script
cat > start_glados_mac.sh << 'EOF'
#!/bin/bash

# Activate virtual environment
source glados_env/bin/activate

# Set Ollama host
export OLLAMA_HOST=0.0.0.0

# Start Ollama if not running
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Start web interface
echo "Starting GLaDOS Web Interface..."
cd ui
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# Start RAG system
echo "Starting RAG System..."
cd ../voice_ollama/wiki_rag
python wiki_ollama.py &

echo "GLaDOS is now running!"
echo "Web Interface: http://localhost:8000"
echo "Ollama API: http://localhost:11434"
echo ""
echo "Press Ctrl+C to stop all services"
wait
EOF

chmod +x start_glados_mac.sh
```

## 🎮 Running GLaDOS

### Start All Services

```bash
# Use the start script
./start_glados_mac.sh

# Or start manually
source glados_env/bin/activate
export OLLAMA_HOST=0.0.0.0
ollama serve &
cd ui && uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### Start Individual Services

```bash
# Start only Ollama
export OLLAMA_HOST=0.0.0.0
ollama serve

# Start only Web Interface
cd ui
uvicorn main:app --host 0.0.0.0 --port 8000

# Start RAG system
cd wiki_rag
python wiki_ollama.py
```

## 🔧 Testing Your Setup

### Test Ollama API

```bash
# Test local connection
curl http://localhost:11434/api/version

# Test network connection
curl http://your-mac-ip:11434/api/version

# Test model inference
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "You are GLaDOS. Say hello.",
  "stream": false
}'
```

### Test Web Interface

```bash
# Test system info endpoint
curl http://localhost:8000/system-info

# Test music endpoint
curl http://localhost:8000/want_you_gone.mp3

# Open in browser
open http://localhost:8000
```

### Test TTS System

```bash
# Test Piper TTS
cd train_piper
echo "The enrichment center is now ready for testing" | python -m piper --model glados.onnx --output_file test.wav
afplay test.wav
```

## 🌐 Network Configuration

### Find Your Mac's IP Address

```bash
# Get IP address
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}'

# Or use system preferences
# System Preferences > Network > Wi-Fi/Ethernet > Advanced > TCP/IP
```

### Configure Firewall

```bash
# Allow incoming connections (System Preferences > Security & Privacy > Firewall)
# Or use command line:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/ollama
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
```

## 🛠️ Troubleshooting

### **Issue**: "Ollama command not found"
**Solution**:
```bash
# Add Ollama to PATH
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Or reinstall Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

### **Issue**: "Permission denied" errors
**Solution**:
```bash
# Fix permissions
chmod +x start_glados_mac.sh
chmod -R 755 GLaDOS/

# Run with proper permissions
sudo chown -R $(whoami):staff GLaDOS/
```

### **Issue**: "Port already in use"
**Solution**:
```bash
# Check what's using the port
lsof -i :11434
lsof -i :8000

# Kill the process
kill -9 PID_NUMBER

# Or change port in config
```

### **Issue**: "Audio not working"
**Solution**:
```bash
# Check audio devices
system_profiler SPAudioDataType

# Test system audio
afplay /System/Library/Sounds/Ping.aiff

# Check microphone permissions
# System Preferences > Security & Privacy > Privacy > Microphone
```

### **Issue**: "Cannot connect from other devices"
**Solution**:
```bash
# Check if Ollama is binding to correct interface
netstat -an | grep :11434

# Ensure OLLAMA_HOST is set correctly
export OLLAMA_HOST=0.0.0.0
ollama serve

# Check macOS firewall settings
```

## 📊 Performance Optimization

### **For Apple Silicon (M1/M2)**
```bash
# M1/M2 Macs have excellent performance for LLMs
# Use larger models if you have enough RAM
ollama pull llama3.2:7b

# Monitor performance
top -o cpu
```

### **For Intel Macs**
```bash
# Use smaller models for better performance
ollama pull llama3.2:1b

# Monitor temperature
sudo powermetrics --samplers smc_temp -n 1 -i 1000
```

### **Memory Management**
```bash
# Monitor memory usage
memory_pressure

# Free up memory if needed
sudo purge
```

## 🔄 Automation

### **Create Launch Agent (Auto-start)**

```bash
# Create launch agent
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.glados.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.glados</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/path/to/GLaDOS/start_glados_mac.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load launch agent
launchctl load ~/Library/LaunchAgents/com.glados.plist
```

### **Menu Bar App (Optional)**

```bash
# Install simple menu bar app
brew install --cask menumeters

# Or create simple AppleScript app
cat > GLaDOS.applescript << 'EOF'
tell application "Terminal"
    do script "cd /path/to/GLaDOS && ./start_glados_mac.sh"
end tell
EOF

osacompile -o GLaDOS.app GLaDOS.applescript
```

## 🎨 Web Interface Features

Access the Portal-themed web interface at: `http://localhost:8000`

Features optimized for macOS:
- 🎵 **Audio Player**: Works with macOS audio system
- 🎬 **Boot Sequence**: Smooth animations on Retina displays
- 💬 **Terminal**: macOS-style terminal interface
- 📹 **Camera System**: Safari-optimized interface
- 🔔 **Notifications**: macOS-style notifications

## 🔄 Next Steps

1. **✅ macOS Setup Complete!**
2. **🔗 Connect Other Devices**: Configure Jetson or other devices
3. **🌐 Access Web Interface**: Portal-themed controls
4. **🎮 Optimize Performance**: Adjust models for your Mac
5. **🔄 Setup Automation**: Auto-start services

## 🆘 Need Help?

- **macOS Issues**: Check Apple Support or Stack Overflow
- **GLaDOS Issues**: GitHub Issues page
- **Community**: Join GLaDOS discussions
- **Performance**: Check Activity Monitor

Your macOS system is now ready to serve as GLaDOS's AI brain! 🤖🍎
````
