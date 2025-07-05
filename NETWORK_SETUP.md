# PotatOS Network Configuration

This file is used to configure the components of the PotatOS system running on different devices.

## Configuration File: config.json

### IP Addresses

1. **Ollama Server (Your Computer)**:
   - `ollama.host`: IP address of the computer running Ollama
   - `ollama.port`: Ollama port (default: 11434)
   
2. **Jetson Device**:
   - `jetson.ip`: IP address of the Jetson device
   - `jetson.rag_port`: RAG server port (default: 5000)
   - `jetson.piper_port`: Piper TTS server port (default: 5001)

### Setup Steps

#### 1. On Your Computer (Ollama Server)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download the model
ollama pull llama3.2:3b

# Start Ollama for network access
OLLAMA_HOST=0.0.0.0 ollama serve
```

#### 2. On Jetson Device (RAG Server)

```bash
cd wiki_rag/
pip3 install -r requirements.txt

# Check persona file
ls persona.txt

# Start RAG server
python3 wiki_ollama.py
```

#### 3. Main Script (potatos.py)

```bash
cd scripts/
python3 potatos.py -r 44100 -d 0
```

### Finding IP Addresses

#### On Windows:
```cmd
ipconfig
```

#### On Linux/Mac:
```bash
ip addr show
# or
ifconfig
```

### Firewall Settings

Make sure the following ports are open:

- **Ollama**: 11434
- **RAG Server**: 5000
- **Piper TTS**: 5001
- **VOSK**: 2700

#### Windows Firewall:
```powershell
New-NetFirewallRule -DisplayName "Ollama" -Direction Inbound -Protocol TCP -LocalPort 11434 -Action Allow
```

#### Linux UFW:
```bash
sudo ufw allow 11434
sudo ufw allow 5000
sudo ufw allow 5001
sudo ufw allow 2700
```

### Testing

#### Ollama Test:
```bash
curl http://192.168.1.100:11434/api/version
```

#### RAG Server Test:
```bash
curl "http://192.168.1.101:5000/chat?query=Hello"
```

### Troubleshooting

1. **Connection Refused**: Check IP addresses and firewall settings
2. **Model Not Found**: Make sure the model is loaded in Ollama
3. **Persona Cannot Be Loaded**: Check that `persona.txt` file is in the correct location

### Example config.json:

```json
{
  "ollama": {
    "host": "192.168.1.100",
    "port": 11434,
    "model": "llama3.2:3b"
  },
  "jetson": {
    "ip": "192.168.1.101",
    "rag_port": 5000,
    "piper_port": 5001
  },
  "vosk": {
    "host": "localhost",
    "port": 2700
  },
  "audio": {
    "sample_rate": 16000
  }
}
```
