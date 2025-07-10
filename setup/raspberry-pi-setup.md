````markdown
# 🍓 Raspberry Pi Setup Guide

Complete setup guide for running GLaDOS on Raspberry Pi 4/5.

## 🎯 Role in GLaDOS System

Your Raspberry Pi can serve as:
- 🎤 **Voice Interface** - Voice recognition and TTS (primary role)
- 🌐 **Web Interface** - Portal-themed control interface
- 📚 **RAG System** - Knowledge retrieval (limited performance)
- 🎮 **Control Hub** - Central coordination point

**Note**: Raspberry Pi is not recommended for running Ollama due to limited performance. Use it with a separate AI server.

## 📋 Prerequisites

### **Hardware Requirements**
- Raspberry Pi 4 (8GB RAM) or Raspberry Pi 5
- 64GB+ microSD card (Class 10 or A2)
- USB microphone or audio HAT
- Speakers or headphones (3.5mm or USB)
- Ethernet connection (recommended)

### **Software Requirements**
- Raspberry Pi OS (64-bit) - Bullseye or Bookworm
- Python 3.9+ (pre-installed)

## 🚀 Installation Steps

### Step 1: Flash Raspberry Pi OS

```bash
# Download Raspberry Pi Imager
# https://www.raspberrypi.com/software/

# Flash 64-bit Raspberry Pi OS to microSD
# Enable SSH in advanced options
# Set username/password
# Configure Wi-Fi if needed
```

### Step 2: Initial Setup

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Update system
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

### Step 3: Configure Audio

```bash
# Test audio output
aplay /usr/share/sounds/alsa/Front_Left.wav

# Test microphone
arecord -f cd -t wav -d 3 test_mic.wav
aplay test_mic.wav

# Configure audio devices
sudo nano /etc/asound.conf
```

**Example asound.conf:**
```
pcm.!default {
    type hw
    card 1
    device 0
}
ctl.!default {
    type hw
    card 1
}
```

### Step 4: Clone Repository

```bash
# Clone GLaDOS repository
git clone https://github.com/your-username/GLaDOS.git
cd GLaDOS/voice_ollama
```

### Step 5: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv glados_env
source glados_env/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Raspberry Pi specific packages
pip install RPi.GPIO gpiozero adafruit-circuitpython-neopixel
```

### Step 6: Install Piper TTS

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

### Step 7: Setup Voice Recognition

```bash
# Install Vosk for speech recognition
pip install vosk

# Download Vosk model
cd ../vosk-server
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
mv vosk-model-en-us-0.22 model

# Test voice recognition
python test_vosk.py
```

### Step 8: Configure Network Settings

```bash
# Edit configuration file
nano config.json
```

**Example config.json (Voice Interface mode):**
```json
{
  "ollama": {
    "host": "192.168.1.100",
    "port": 11434,
    "model": "llama3.2:3b"
  },
  "raspberry_pi": {
    "ip": "0.0.0.0",
    "rag_port": 5000,
    "piper_port": 5001,
    "vosk_port": 5002,
    "web_port": 8080
  },
  "audio": {
    "input_device": 1,
    "output_device": 1,
    "sample_rate": 16000,
    "channels": 1
  },
  "gpio": {
    "led_pin": 18,
    "button_pin": 21,
    "status_led": 24
  }
}
```

### Step 9: Setup GPIO Controls (Optional)

```bash
# Create GPIO control script
cat > gpio_controls.py << 'EOF'
#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import requests

# GPIO setup
LED_PIN = 18
BUTTON_PIN = 21
STATUS_LED = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(STATUS_LED, GPIO.OUT)

def button_callback(channel):
    print("GLaDOS activation button pressed!")
    # Trigger voice recognition
    requests.post("http://localhost:5002/start_listening")

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

# Status LED blink
while True:
    GPIO.output(STATUS_LED, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(STATUS_LED, GPIO.LOW)
    time.sleep(1)
EOF

chmod +x gpio_controls.py
```

### Step 10: Setup Systemd Services

```bash
# Create service files
sudo nano /etc/systemd/system/glados-piper.service
```

**Piper TTS Service:**
```ini
[Unit]
Description=GLaDOS Piper TTS Service
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/GLaDOS/voice_ollama/train_piper
ExecStart=/home/pi/GLaDOS/voice_ollama/glados_env/bin/python piper_server.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/pi/GLaDOS/voice_ollama

[Install]
WantedBy=multi-user.target
```

```bash
# Create other services
sudo nano /etc/systemd/system/glados-vosk.service
sudo nano /etc/systemd/system/glados-web.service

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable glados-piper glados-vosk glados-web
sudo systemctl start glados-piper glados-vosk glados-web
```

## 🎮 Running GLaDOS

### Start All Services

```bash
# Activate virtual environment
source glados_env/bin/activate

# Start all services
./scripts/start_raspberry_pi.sh

# Or start individually
python train_piper/piper_server.py &
python vosk-server/vosk_server.py &
python -m http.server 8080 &
```

### Check Service Status

```bash
# Check systemd services
sudo systemctl status glados-piper
sudo systemctl status glados-vosk
sudo systemctl status glados-web

# Check processes
ps aux | grep glados
```

## 🔧 Testing Your Setup

### Test TTS System

```bash
# Test Piper TTS
cd train_piper
echo "The enrichment center is now ready for testing" | python -m piper --model glados.onnx --output_file test.wav
aplay test.wav

# Test TTS server
curl -X POST http://localhost:5001/speak -d '{"text": "Hello from GLaDOS"}'
```

### Test Voice Recognition

```bash
# Test Vosk recognition
cd vosk-server
python test_vosk.py

# Test voice server
curl http://localhost:5002/status
```

### Test Web Interface

```bash
# Test web interface
curl http://localhost:8080

# Access from browser
# http://raspberry-pi-ip:8080
```

## 🌐 Network Configuration

### Find Raspberry Pi IP

```bash
# Get IP address
hostname -I
ip addr show wlan0

# Set static IP (optional)
sudo nano /etc/dhcpcd.conf
```

**Static IP configuration:**
```
interface wlan0
static ip_address=192.168.1.101/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

### Configure External Access

```bash
# Configure firewall
sudo ufw allow 8080/tcp  # Web interface
sudo ufw allow 5001/tcp  # Piper TTS
sudo ufw allow 5002/tcp  # Vosk recognition
sudo ufw enable
```

## 🛠️ Troubleshooting

### **Issue**: "Audio device not found"
**Solution**:
```bash
# Check audio cards
aplay -l
arecord -l

# Configure audio
sudo raspi-config
# Advanced Options > Audio > Force 3.5mm

# Test audio
speaker-test -t wav -c 2
```

### **Issue**: "Microphone not working"
**Solution**:
```bash
# Check microphone
arecord -l
arecord -f cd -t wav -d 3 test.wav

# Adjust microphone volume
alsamixer
# Press F4 to switch to capture, adjust levels
```

### **Issue**: "Python packages won't install"
**Solution**:
```bash
# Install system dependencies
sudo apt install -y python3-dev libffi-dev libssl-dev
sudo apt install -y portaudio19-dev

# Update pip
pip install --upgrade pip setuptools wheel

# Install packages one by one
pip install vosk
pip install piper-tts
```

### **Issue**: "Service won't start"
**Solution**:
```bash
# Check service logs
sudo journalctl -u glados-piper -f
sudo journalctl -u glados-vosk -f

# Check permissions
sudo chown -R pi:pi /home/pi/GLaDOS
chmod +x scripts/*.py
```

### **Issue**: "High CPU usage"
**Solution**:
```bash
# Monitor CPU
htop

# Reduce model quality
# Use smaller Vosk model
# Lower audio sample rate
# Disable unnecessary services
```

## 📊 Performance Optimization

### **For Raspberry Pi 4**
```bash
# Enable GPU memory split
sudo raspi-config
# Advanced Options > Memory Split > 128

# Overclock (if cooling is adequate)
sudo raspi-config
# Advanced Options > Overclock
```

### **For Raspberry Pi 5**
```bash
# Pi 5 has better performance, less optimization needed
# Monitor temperature
vcgencmd measure_temp

# Use faster storage
# Consider NVMe HAT for better I/O
```

### **Memory Management**
```bash
# Increase swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048

sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 🔌 Hardware Additions

### **LED Status Indicators**
```python
# Add to gpio_controls.py
import board
import neopixel

# NeoPixel LED strip
pixels = neopixel.NeoPixel(board.D18, 8)

def set_status_color(color):
    pixels.fill(color)
    pixels.show()

# Use colors:
# Red: Error
# Orange: Processing
# Blue: Listening
# Green: Ready
```

### **Physical Button Interface**
```python
# Physical GLaDOS activation button
from gpiozero import Button
from signal import pause

button = Button(21)

def glados_activate():
    print("GLaDOS activated!")
    # Trigger voice recognition
    
button.when_pressed = glados_activate
pause()
```

## 🎨 Web Interface Features

Raspberry Pi optimized web interface:
- 🎵 **Audio Player**: Works with Pi audio system
- 🎬 **Boot Sequence**: Optimized for lower-power display
- 💬 **Terminal**: Touch-friendly interface
- 📹 **Camera System**: Can integrate with Pi Camera
- 🔔 **Notifications**: Pi-specific system alerts

## 🔄 Next Steps

1. **✅ Raspberry Pi Setup Complete!**
2. **🔗 Connect to AI Server**: Configure Windows/Linux PC
3. **🎤 Test Voice Commands**: "Hello GLaDOS"
4. **🔊 Test TTS Output**: Verify GLaDOS voice
5. **🌐 Access Web Interface**: Portal-themed controls
6. **🎮 Add Hardware**: LEDs, buttons, sensors

## 🆘 Need Help?

- **Pi Issues**: Check Raspberry Pi Forums
- **Audio Issues**: Check ALSA documentation
- **GLaDOS Issues**: GitHub Issues page
- **Community**: Join GLaDOS discussions

Your Raspberry Pi is now ready to serve as GLaDOS's voice interface! 🤖🍓
````
