````markdown
# 🐧 Linux Setup Guide (Ubuntu/Debian)

Complete setup guide for running GLaDOS on Linux systems (Ubuntu 20.04+, Debian 11+).

## 🎯 Role in GLaDOS System

Your Linux system can serve as either:
- 🧠 **AI Server** - Running Ollama LLM (recommended for powerful machines)
- 🎤 **Voice Interface** - Running Piper TTS + Voice Recognition
- 🌐 **Web Interface** - Portal-themed control interface
- 🔄 **All-in-One** - Complete GLaDOS system on single machine

## 📋 Prerequisites

### **System Requirements**
- Ubuntu 20.04+ or Debian 11+ (64-bit)
- 8GB+ RAM (16GB+ recommended for all-in-one setup)
- 10GB+ free disk space
- NVIDIA GPU (optional, but recommended for Ollama)

### **Software Requirements**
- Python 3.8+ (usually pre-installed)
- Git
- curl/wget
- Audio drivers (ALSA/PulseAudio)

## 🚀 Installation Steps

### Step 1: System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git curl wget htop nano screen
sudo apt install -y python3-pip python3-venv python3-dev
sudo apt install -y build-essential cmake pkg-config
sudo apt install -y portaudio19-dev python3-pyaudio
sudo apt install -y espeak espeak-data libespeak1 libespeak-dev
sudo apt install -y pulseaudio pavucontrol alsa-utils
sudo apt install -y ffmpeg libavcodec-extra
```

### Step 2: Install Ollama (AI Server Mode)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Configure Ollama for network access
sudo systemctl edit ollama
```

**Add to override file:**
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
```

```bash
# Restart Ollama
sudo systemctl restart ollama

# Download GLaDOS personality model
ollama pull llama3.2:3b

# Verify installation
ollama list
```

### Step 3: Clone Repository

```bash
# Clone GLaDOS repository
git clone https://github.com/your-username/GLaDOS.git
cd GLaDOS
```

### Step 4: Setup Python Environment

```bash
# Navigate to voice_ollama directory
cd voice_ollama

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
aplay test.wav
```

### Step 6: Setup Voice Recognition (Optional)

```bash
# Install Vosk for speech recognition
pip install vosk

# Download Vosk model
cd ../vosk-server
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
mv vosk-model-en-us-0.22 model
```

### Step 7: Configure Audio

```bash
# Test audio devices
arecord -l
aplay -l

# Install additional audio tools
sudo apt install -y pulseaudio-utils

# Test microphone (if using voice recognition)
arecord -f cd -t wav -d 3 test_mic.wav
aplay test_mic.wav
```

### Step 8: Setup RAG System

```bash
# Navigate to RAG directory
cd ../wiki_rag

# Install RAG dependencies
pip install -r requirements.txt

# Download and process Portal wiki data
python wiki_llamaindex_preprocess.py
```

### Step 9: Configure Network Settings

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
  "jetson": {
    "ip": "0.0.0.0",
    "rag_port": 5000,
    "piper_port": 5001,
    "vosk_port": 5002
  },
  "web": {
    "port": 8000
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
  "jetson": {
    "ip": "192.168.1.101",
    "rag_port": 5000,
    "piper_port": 5001
  },
  "web": {
    "port": 8000
  }
}
```

### Step 10: Configure Firewall

```bash
# Allow necessary ports through firewall
sudo ufw allow 11434/tcp  # Ollama API
sudo ufw allow 8000/tcp   # Web interface
sudo ufw allow 5000/tcp   # RAG system
sudo ufw allow 5001/tcp   # Piper TTS

# Enable firewall (if not already enabled)
sudo ufw enable
```

### Step 11: Setup Systemd Services

```bash
# Create Ollama service override (if needed)
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo nano /etc/systemd/system/ollama.service.d/override.conf
```

**Override content:**
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
```

```bash
# Create GLaDOS web service
sudo nano /etc/systemd/system/glados-web.service
```

**Service file content:**
```ini
[Unit]
Description=GLaDOS Web Interface
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername/GLaDOS/ui
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable ollama glados-web
sudo systemctl start ollama glados-web
```

## 🎮 Running GLaDOS

### Check Services Status

```bash
# Check Ollama status
sudo systemctl status ollama

# Check GLaDOS web interface
sudo systemctl status glados-web

# Check all GLaDOS services
sudo systemctl status glados-*
```

### Start Individual Components (Manual)

```bash
# Activate virtual environment
source glados_env/bin/activate

# Start Ollama (if not using systemd)
OLLAMA_HOST=0.0.0.0 ollama serve &

# Start web interface
cd ui
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start RAG system (if running locally)
cd ../voice_ollama/wiki_rag
python wiki_ollama.py &

# Start Piper TTS server (if running locally)
cd ../train_piper
python piper_server.py &
```

### Use the Start Script

```bash
# Make script executable
chmod +x scripts/start_linux.sh

# Run GLaDOS
./scripts/start_linux.sh
```

## 🔧 Testing Your Setup

### Test Ollama API

```bash
# Test local connection
curl http://localhost:11434/api/version

# Test network connection
curl http://your-ip:11434/api/version

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
```

### Test TTS System

```bash
# Test Piper TTS
echo "The enrichment center is now ready for testing" | python -m piper --model glados.onnx --output_file test.wav
aplay test.wav
```

## 🌐 Network Configuration

### Find Your IP Address

```bash
# Get IP address
ip addr show
hostname -I

# Example output: 192.168.1.100
```

### Configure Other Devices

Update other devices (Jetson, etc.) to point to your Linux IP:
```json
{
  "ollama": {
    "host": "192.168.1.100",
    "port": 11434
  }
}
```

## 🛠️ Troubleshooting

### **Issue**: "Ollama service failed to start"
**Solution**:
```bash
# Check Ollama logs
sudo journalctl -u ollama -f

# Restart Ollama
sudo systemctl restart ollama

# Check if port is already in use
sudo netstat -tlnp | grep :11434
```

### **Issue**: "Permission denied" errors
**Solution**:
```bash
# Fix permissions for user
sudo chown -R $USER:$USER /home/$USER/GLaDOS

# Add user to audio group
sudo usermod -a -G audio $USER

# Logout and login again
```

### **Issue**: "Audio not working"
**Solution**:
```bash
# Check audio devices
aplay -l
arecord -l

# Test PulseAudio
pulseaudio --check
pulseaudio --start

# Reset audio
pulseaudio -k
sudo alsa force-reload
```

### **Issue**: "NVIDIA GPU not detected"
**Solution**:
```bash
# Install NVIDIA drivers
sudo apt install -y nvidia-driver-470

# Install CUDA (for better performance)
sudo apt install -y nvidia-cuda-toolkit

# Reboot system
sudo reboot
```

### **Issue**: "Cannot connect from other devices"
**Solution**:
```bash
# Check firewall status
sudo ufw status

# Check if services are binding to correct interface
sudo netstat -tlnp | grep :11434
sudo netstat -tlnp | grep :8000

# Test connectivity
ping your-linux-ip
```

## 📊 Performance Optimization

### **For CPU-Only Systems**
```bash
# Use CPU-optimized models
ollama pull llama3.2:1b  # Smaller model for better performance

# Monitor CPU usage
htop
```

### **For GPU Systems**
```bash
# Check GPU usage
nvidia-smi

# Install CUDA-optimized packages
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### **Memory Management**
```bash
# Monitor memory usage
free -h
watch -n 1 free -h

# Increase swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 🎨 Web Interface Features

Access the Portal-themed web interface at: `http://your-ip:8000`

Features include:
- 🎵 **Audio Player**: "Want You Gone" background music
- 🎬 **Boot Sequence**: GLaDOS startup animation
- 💬 **Terminal**: Interactive GLaDOS commands
- 📹 **Camera System**: Surveillance camera simulator
- 🔔 **Notifications**: System status updates

## 🔄 Next Steps

1. **✅ Linux Setup Complete!**
2. **🔗 Connect Other Devices**: Configure Jetson/other devices
3. **🎤 Test Voice Commands**: If using voice recognition
4. **🌐 Access Web Interface**: Portal-themed controls
5. **🎮 Full Integration**: Complete GLaDOS experience

## 🆘 Need Help?

- **System Issues**: Check Ubuntu/Debian forums
- **GLaDOS Issues**: GitHub Issues page
- **Community**: Join GLaDOS discussions
- **Documentation**: Check other platform guides

Your Linux system is now ready to serve as GLaDOS's AI brain! 🤖
````
