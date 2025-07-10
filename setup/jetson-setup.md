````markdown
# 🚀 Jetson Nano/Orin Setup Guide

Complete setup guide for running GLaDOS on NVIDIA Jetson devices.

## 🎯 Role in GLaDOS System

Your Jetson device will serve as the **Voice Interface** handling:
- 🎤 **Voice Recognition** - Converting speech to text
- 🔊 **Text-to-Speech** - GLaDOS voice synthesis using Piper
- 📚 **RAG System** - Retrieval-Augmented Generation for context
- 🌐 **Local Web Server** - Portal-themed interface

## 📋 Prerequisites

### **Hardware Requirements**
- NVIDIA Jetson Nano (4GB) or Jetson Orin
- 64GB+ microSD card (Class 10 or better)
- USB microphone or audio hat
- Speakers or headphones
- Ethernet connection (recommended for stability)

### **Software Requirements**
- JetPack 4.6+ (for Nano) or JetPack 5.0+ (for Orin)
- Python 3.6+ (usually pre-installed)
- Docker (optional, for containerized deployment)

## 🛠️ Installation Steps

### Step 1: Flash JetPack OS

1. **Download JetPack**:
   ```bash
   # Visit: https://developer.nvidia.com/jetpack
   # Download appropriate version for your Jetson
   ```

2. **Flash to microSD**:
   ```bash
   # Use NVIDIA SDK Manager or balenaEtcher
   # Flash JetPack image to microSD card
   ```

3. **Initial Setup**:
   ```bash
   # Insert microSD, boot Jetson
   # Complete initial setup wizard
   # Connect to network
   ```

### Step 2: System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git curl wget htop nano screen
sudo apt install -y python3-pip python3-venv
sudo apt install -y portaudio19-dev python3-pyaudio
sudo apt install -y espeak espeak-data libespeak1 libespeak-dev
sudo apt install -y pulseaudio pavucontrol alsa-utils
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
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
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
```

### Step 6: Setup Voice Recognition

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
# Test microphone
arecord -l

# Test speakers
aplay /usr/share/sounds/alsa/Front_Left.wav

# Set default audio devices
sudo nano /etc/asound.conf
```

**Example asound.conf:**
```
pcm.!default {
    type hw
    card 1
}
ctl.!default {
    type hw
    card 1
}
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

**Example config.json:**
```json
{
  "ollama": {
    "host": "192.168.1.100",
    "port": 11434,
    "model": "llama3.2:3b"
  },
  "jetson": {
    "ip": "0.0.0.0",
    "rag_port": 5000,
    "piper_port": 5001,
    "vosk_port": 5002
  },
  "audio": {
    "input_device": 1,
    "output_device": 1,
    "sample_rate": 16000
  }
}
```

### Step 10: Setup Systemd Services

```bash
# Create service files for auto-start
sudo nano /etc/systemd/system/glados-rag.service
```

**Example service file:**
```ini
[Unit]
Description=GLaDOS RAG System
After=network.target

[Service]
Type=simple
User=jetson
WorkingDirectory=/home/jetson/GLaDOS/voice_ollama/wiki_rag
ExecStart=/home/jetson/GLaDOS/voice_ollama/glados_env/bin/python wiki_ollama.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable glados-rag.service
sudo systemctl start glados-rag.service
```

## 🎮 Running GLaDOS

### Start Individual Components

```bash
# Activate virtual environment
source glados_env/bin/activate

# Start RAG system
cd wiki_rag
python wiki_ollama.py &

# Start Piper TTS server
cd ../train_piper
python piper_server.py &

# Start Vosk speech recognition
cd ../vosk-server
python vosk_server.py &

# Start web interface
cd ../ui
python -m http.server 8080 &
```

### Use the Start Script

```bash
# Make script executable
chmod +x scripts/start_jetson.sh

# Run GLaDOS
./scripts/start_jetson.sh
```

## 🔧 Testing Your Setup

### Test Voice Recognition

```bash
# Test microphone input
python scripts/test_voice_recognition.py
```

### Test Text-to-Speech

```bash
# Test GLaDOS voice
echo "The enrichment center is now ready for testing" | python scripts/test_tts.py
```

### Test RAG System

```bash
# Test knowledge retrieval
curl -X POST http://localhost:5000/query -d '{"question": "What is a portal gun?"}'
```

### Test Web Interface

```bash
# Access web interface
# Open browser: http://jetson-ip:8080
```

## 🌐 Network Configuration

### Find Jetson IP Address

```bash
# Get IP address
ip addr show

# Example output: 192.168.1.101
```

### Configure PC Connection

Update your Windows PC config to point to Jetson IP:
```json
{
  "jetson": {
    "ip": "192.168.1.101",
    "rag_port": 5000,
    "piper_port": 5001
  }
}
```

## 🛠️ Troubleshooting

### **Issue**: "No audio device found"
**Solution**:
```bash
# Check audio devices
arecord -l
aplay -l

# Install audio drivers
sudo apt install -y alsa-utils pulseaudio

# Restart audio service
sudo systemctl restart pulseaudio
```

### **Issue**: "Piper model not found"
**Solution**:
```bash
# Re-download GLaDOS model
cd train_piper
python download_glados.py --force

# Verify model files
ls -la *.onnx *.json
```

### **Issue**: "Cannot connect to Ollama server"
**Solution**:
```bash
# Test PC connectivity
ping 192.168.1.100

# Test Ollama API
curl http://192.168.1.100:11434/api/tags

# Check firewall on PC
```

### **Issue**: "High CPU usage"
**Solution**:
```bash
# Monitor processes
htop

# Reduce model complexity
# Edit config.json - use smaller models
# Reduce sampling rates
```

### **Issue**: "Memory errors"
**Solution**:
```bash
# Check memory usage
free -h

# Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📊 Performance Optimization

### **For Jetson Nano**
```bash
# Enable maximum performance mode
sudo nvpmodel -m 0
sudo jetson_clocks

# Monitor power consumption
sudo tegrastats
```

### **Memory Management**
```bash
# Clear cache regularly
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# Monitor memory usage
watch -n 1 free -h
```

### **Model Optimization**
- Use quantized models when possible
- Reduce batch sizes
- Lower audio sample rates if quality permits
- Cache frequently used responses

## 🔄 Next Steps

1. **✅ Jetson Setup Complete!**
2. **🔗 Connect to Windows PC**: Ensure network connectivity
3. **🎤 Test Voice Commands**: "Hello GLaDOS"
4. **🔊 Test TTS Output**: Verify GLaDOS voice
5. **🌐 Access Web Interface**: Portal-themed controls
6. **🎮 Full Integration**: Complete GLaDOS experience

## 🆘 Need Help?

- **Hardware Issues**: Check NVIDIA Developer Forums
- **Software Issues**: GitHub Issues page
- **Community**: Join GLaDOS Discord/Reddit
- **Documentation**: Check other setup guides

Your Jetson device is now ready to serve as GLaDOS's voice interface! 🤖
````
