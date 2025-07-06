# PotatOS

## Network Setup

The PotatOS system consists of components running on different devices:

1. **Ollama Server** (On your powerful computer)
2. **RAG Server** (On Jetson device)
3. **Main Coordinator** (On Jetson device)

### Quick Setup

1. Update IP addresses in **config.json** file
2. **On your computer**: Run `start_ollama_server.bat` (Windows) or `start_ollama_server.sh` (Linux/Mac)
3. **On Jetson**: Start the RAG server
4. **On Jetson**: Run the main coordinator

For detailed setup instructions: [NETWORK_SETUP.md](NETWORK_SETUP.md)

---

## Setup

    git clone --recursive git@github.com:davesarmoury/PotatOS.git
    cd PotatOS

    pip3 install -r requirements.txt
    sudo groupadd -f -r gpio
    sudo usermod -a -G $USER

    sudo cp lib/python/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d/
    #sudo reboot

## Jetson Containers

    bash jetson-containers/install.sh

## Patch platform detect (optional)

    cd patch/
    ./patch_platformdetect.sh
    cd ..

## LLM (Network Setup)

With the new network configuration, Ollama runs on your powerful computer instead of Jetson:

**On your computer:**
- Run `start_ollama_server.bat` (Windows) or `start_ollama_server.sh` (Linux/Mac)
- This will start Ollama with network access

**Previous Jetson setup (deprecated):**
    jetson-containers run --name ollama $(autotag ollama)
    ollama run llama3.2:3b --keepalive 60m

## RAG Server

    cd wiki_rag/
    pip3 install -r requirements.txt

    # Choose one of the following RAG implementations:
    
    # Option 1: Simple Ollama-based RAG (Recommended)
    python3 wiki_ollama.py
    
    # Option 2: LlamaIndex-based RAG (More advanced)
    #python3 wiki_llamaindex_preprocess.py
    #python3 wiki_llamaindex.py

Both implementations now connect to the network Ollama server configured in config.json

## Audio

See [https://developer.nvidia.com/embedded/learn/tutorials/connecting-bluetooth-audio](https://developer.nvidia.com/embedded/learn/tutorials/connecting-bluetooth-audio), then pair a bluetooth speaker with bluetoothctl.  Then set the volume

    sudo nano /lib/systemd/system/bluetooth.service.d/nv-bluetooth-service.conf


    amixer -D pulse sset Master 50%

## VOSK

    pip3 install -r vosk-server/requirements.txt 
    pip3 install sounddevice
    sudo apt install libportaudio2

    cd vosk-server/websocket
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15
    rm vosk-model-small-en-us-0.15.zip
    mv vosk-model-small-en-us-0.15 model

    python3 asr_server.py

## Run Piper Server

Train or download the GLaDOS Piper voice.  See [train_piper](train_piper) for more details.  If you don't want to train you own, you can download pre-trained models using

    cd jetson-containers/data/models/piper/
    wget https://huggingface.co/DavesArmoury/GLaDOS_TTS/resolve/main/glados_piper_medium.onnx.json
    wget https://huggingface.co/DavesArmoury/GLaDOS_TTS/resolve/main/glados_piper_medium.onnx

On the jetson, put the onnx and onnx.json files into jetson-containers/data/models/piper, then run the command below

    docker pull dustynv/piper-tts:r36.2.0
    jetson-containers run $(autotag piper-tts) python3 -m piper.http_server --port 5001 -m /data/models/piper/glados_piper_medium.onnx

Run a quick test with

    curl -G --data-urlencode 'text=I like big butts, I cannot lie.' --output - 'localhost:5001' | aplay

## Coordinator

    python3 potatos.py -r 44100 -d 0

## PulseAudio Quirk

PulseAudio will automatically disconnect when no one is logged into the machine.  That means if you are trying to run it headless, your audio will break.  This is gross, but just ssh the terminal into itself so the machine sees a "remote" connection

    ssh localhost
