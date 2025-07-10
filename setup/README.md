# GLaDOS Setup Instructions

Welcome to GLaDOS setup! Choose your platform for detailed instructions:

## 🖥️ Platform-Specific Setup Guides

### 📱 **Single Board Computers (SBC)**
- **[Jetson Nano/Orin Setup](jetson-setup.md)** - Complete guide for NVIDIA Jetson devices
- **[Raspberry Pi Setup](raspberry-pi-setup.md)** - Complete guide for Raspberry Pi 4/5

### 💻 **Desktop/Laptop Computers**
- **[Windows Setup](windows-setup.md)** - Complete guide for Windows 10/11
- **[Linux Setup](linux-setup.md)** - Complete guide for Ubuntu/Debian systems
- **[macOS Setup](macos-setup.md)** - Complete guide for macOS (Intel/Apple Silicon)

### 🐳 **Containerized Deployment**
- **[Docker Setup](docker-setup.md)** - Run GLaDOS in containers (All platforms)

---

## 🏗️ Architecture Overview

The GLaDOS system uses a distributed architecture for optimal performance:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Powerful PC   │    │   Jetson SBC    │    │   Web Client    │
│                 │    │                 │    │                 │
│  🧠 Ollama LLM  │◄──►│  🎤 Voice Rec   │    │  🌐 Portal UI   │
│  📡 API Server  │    │  🔊 TTS (Piper) │◄──►│  🎮 Controls    │
│                 │    │  📚 RAG System  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Why this architecture?**
- **Resource Optimization**: Heavy AI models run on powerful PCs
- **Cost Effective**: No need for expensive high-end SBCs
- **Scalable**: Easy to add more devices or upgrade components
- **Reliable**: Distributed load prevents single points of failure

**Why Ollama locally instead of Docker?**
- **Hardware Flexibility**: Direct access to GPU acceleration
- **Resource Efficiency**: No containerization overhead for heavy models
- **Development Speed**: Faster iteration and debugging
- **Cost Optimization**: Use existing hardware efficiently (old Jetson + powerful PC)

**Note**: Docker deployment is also supported for users who prefer containerized environments!

---

## 🚀 Quick Start

1. **Choose your hardware setup**:
   - **Recommended**: Jetson Nano + Windows/Linux PC
   - **Alternative**: Single powerful PC for everything
   - **Advanced**: Multiple Jetson devices + dedicated AI server

2. **Follow the platform-specific guides**:
   - Start with your AI server (usually Windows/Linux PC)
   - Then setup your SBC (Jetson Nano recommended)
   - Finally configure the web interface

3. **Test your setup**:
   - Verify network connectivity
   - Test voice recognition
   - Test text-to-speech
   - Access the Portal-themed web UI

---

## 📋 Prerequisites

### **For AI Server (PC/Laptop)**
- Windows 10/11, Linux, or macOS
- 8GB+ RAM (16GB+ recommended)
- NVIDIA GPU (optional, but recommended)
- Stable internet connection

### **For Voice/TTS Device (SBC)**
- Jetson Nano/Orin or Raspberry Pi 4+
- 4GB+ RAM (8GB+ recommended)
- MicroSD card (64GB+ recommended)
- USB microphone
- Speakers or headphones

### **For Web Interface**
- Any device with a modern web browser
- Same network as other components

---

## 🆘 Need Help?

- **Issues**: Check the troubleshooting section in each platform guide
- **Community**: Join our discussions on GitHub
- **Updates**: Star the repository to get notified of new features

Choose your platform above to get started! 🎮
