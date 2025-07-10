````markdown
# 🐳 Docker Setup Guide

Complete setup guide for running GLaDOS using Docker containers.

## 🎯 Role in GLaDOS System

Docker deployment provides:
- 🔧 **Easy Deployment** - One-command setup
- 📦 **Isolated Environment** - No dependency conflicts
- 🔄 **Reproducible Builds** - Same environment everywhere
- 🚀 **Scalable Architecture** - Easy to add more services

## 📋 Prerequisites

### **System Requirements**
- Docker 20.10+ and Docker Compose 2.0+
- 8GB+ RAM (16GB+ recommended)
- 10GB+ free disk space
- NVIDIA Docker runtime (optional, for GPU acceleration)

### **Supported Platforms**
- Linux (Ubuntu, Debian, CentOS, etc.)
- Windows 10/11 with WSL2
- macOS with Docker Desktop

## 🚀 Installation Steps

### Step 1: Install Docker

#### **Linux (Ubuntu/Debian)**
```bash
# Update package index
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose-plugin

# Logout and login again
```

#### **Windows**
```powershell
# Download Docker Desktop for Windows
# https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

# Install and restart Windows
# Enable WSL2 integration
```

#### **macOS**
```bash
# Download Docker Desktop for Mac
# https://desktop.docker.com/mac/main/amd64/Docker.dmg

# Install and start Docker Desktop
```

### Step 2: Install NVIDIA Docker (Optional)

Only needed for GPU acceleration:

```bash
# Install NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-docker2
sudo systemctl restart docker
```

### Step 3: Clone Repository

```bash
# Clone GLaDOS repository
git clone https://github.com/your-username/GLaDOS.git
cd GLaDOS/voice_ollama
```

### Step 4: Configure Docker Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env
```

**Example .env file:**
```env
# Network Configuration
OLLAMA_HOST=0.0.0.0
OLLAMA_PORT=11434
WEB_PORT=8000
RAG_PORT=5000
PIPER_PORT=5001
VOSK_PORT=5002

# Model Configuration
OLLAMA_MODEL=llama3.2:3b
GLADOS_VOICE_MODEL=glados.onnx

# Audio Configuration
AUDIO_INPUT_DEVICE=0
AUDIO_OUTPUT_DEVICE=0
AUDIO_SAMPLE_RATE=16000

# GPU Configuration (set to 'false' if no GPU)
ENABLE_GPU=true
GPU_DEVICE=0
```

### Step 5: Build Docker Images

```bash
# Build all services
docker-compose build

# Or build specific services
docker-compose build ollama
docker-compose build web
docker-compose build rag
docker-compose build piper
```

## 🎮 Running GLaDOS

### Start All Services

```bash
# Start all GLaDOS services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Start Individual Services

```bash
# Start only Ollama (AI Server)
docker-compose up -d ollama

# Start only Web Interface
docker-compose up -d web

# Start voice services
docker-compose up -d piper vosk
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop ollama
```

## 📁 Docker Compose Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  ollama:
    build:
      context: .
      dockerfile: docker/Dockerfile.ollama
    ports:
      - "${OLLAMA_PORT:-11434}:11434"
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_MODEL=${OLLAMA_MODEL:-llama3.2:3b}
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    profiles:
      - ollama
      - all

  web:
    build:
      context: .
      dockerfile: docker/Dockerfile.web
    ports:
      - "${WEB_PORT:-8000}:8000"
    environment:
      - OLLAMA_HOST=ollama
      - OLLAMA_PORT=11434
    depends_on:
      - ollama
    volumes:
      - ./ui:/app/ui
    restart: unless-stopped
    profiles:
      - web
      - all

  rag:
    build:
      context: .
      dockerfile: docker/Dockerfile.rag
    ports:
      - "${RAG_PORT:-5000}:5000"
    environment:
      - OLLAMA_HOST=ollama
      - OLLAMA_PORT=11434
    depends_on:
      - ollama
    volumes:
      - ./wiki_rag:/app/wiki_rag
      - rag_data:/app/data
    restart: unless-stopped
    profiles:
      - rag
      - all

  piper:
    build:
      context: .
      dockerfile: docker/Dockerfile.piper
    ports:
      - "${PIPER_PORT:-5001}:5001"
    environment:
      - GLADOS_VOICE_MODEL=${GLADOS_VOICE_MODEL:-glados.onnx}
    volumes:
      - ./train_piper:/app/train_piper
      - piper_models:/app/models
    devices:
      - /dev/snd:/dev/snd
    restart: unless-stopped
    profiles:
      - voice
      - all

  vosk:
    build:
      context: .
      dockerfile: docker/Dockerfile.vosk
    ports:
      - "${VOSK_PORT:-5002}:5002"
    volumes:
      - ./vosk-server:/app/vosk-server
      - vosk_models:/app/models
    devices:
      - /dev/snd:/dev/snd
    restart: unless-stopped
    profiles:
      - voice
      - all

volumes:
  ollama_data:
  rag_data:
  piper_models:
  vosk_models:

networks:
  default:
    name: glados_network
```

## 🐳 Dockerfile Examples

### **Ollama Dockerfile**
```dockerfile
# docker/Dockerfile.ollama
FROM ollama/ollama:latest

# Install additional tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration
COPY config.json /etc/ollama/config.json

# Expose port
EXPOSE 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:11434/api/version || exit 1

# Start Ollama
CMD ["ollama", "serve"]
```

### **Web Interface Dockerfile**
```dockerfile
# docker/Dockerfile.web
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ui/ ./ui/
COPY scripts/ ./scripts/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "ui.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 Testing Your Setup

### Test Individual Services

```bash
# Test Ollama API
curl http://localhost:11434/api/version

# Test Web Interface
curl http://localhost:8000/system-info

# Test RAG System
curl -X POST http://localhost:5000/query -d '{"question": "What is GLaDOS?"}'

# Test Piper TTS
curl -X POST http://localhost:5001/speak -d '{"text": "Hello from GLaDOS"}'
```

### Test Service Communication

```bash
# Check if services can communicate
docker-compose exec web curl http://ollama:11434/api/version
docker-compose exec rag curl http://ollama:11434/api/version
```

### View Service Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs ollama
docker-compose logs web
docker-compose logs -f piper  # Follow logs
```

## 🌐 Network Configuration

### Access from Other Devices

```bash
# Find your host IP
ip addr show  # Linux
ipconfig      # Windows

# Access services from other devices:
# Web Interface: http://your-ip:8000
# Ollama API: http://your-ip:11434
```

### Configure External Access

```yaml
# In docker-compose.yml, bind to all interfaces
ports:
  - "0.0.0.0:8000:8000"  # Web interface
  - "0.0.0.0:11434:11434"  # Ollama API
```

## 🛠️ Troubleshooting

### **Issue**: "Port already in use"
**Solution**:
```bash
# Check what's using the port
sudo netstat -tlnp | grep :11434

# Stop conflicting services
sudo systemctl stop ollama

# Or change port in .env file
OLLAMA_PORT=11435
```

### **Issue**: "GPU not detected in container"
**Solution**:
```bash
# Install NVIDIA Docker runtime
sudo apt install -y nvidia-docker2

# Test GPU in container
docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi
```

### **Issue**: "Audio not working in containers"
**Solution**:
```bash
# Add audio devices to container
devices:
  - /dev/snd:/dev/snd

# Install PulseAudio in container
RUN apt-get install -y pulseaudio
```

### **Issue**: "Service won't start"
**Solution**:
```bash
# Check service logs
docker-compose logs service-name

# Check service health
docker-compose ps

# Restart service
docker-compose restart service-name
```

## 📊 Performance Optimization

### **GPU Acceleration**
```yaml
# Enable GPU for Ollama
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### **Memory Management**
```yaml
# Limit memory usage
deploy:
  resources:
    limits:
      memory: 4G
    reservations:
      memory: 2G
```

### **Storage Optimization**
```bash
# Clean up unused images
docker system prune -a

# Monitor disk usage
docker system df
```

## 🔄 Deployment Profiles

### **AI Server Only**
```bash
# Start only Ollama and Web interface
docker-compose --profile ollama --profile web up -d
```

### **Voice Interface Only**
```bash
# Start only voice services
docker-compose --profile voice up -d
```

### **Complete Setup**
```bash
# Start all services
docker-compose --profile all up -d
```

## 🆘 Need Help?

- **Docker Issues**: Check Docker documentation
- **GLaDOS Issues**: GitHub Issues page
- **Community**: Join GLaDOS discussions
- **Logs**: Always check service logs first

Your GLaDOS Docker setup is now ready! 🤖🐳
````
