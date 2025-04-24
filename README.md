# PotatOS

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

## LLM

    jetson-containers run --name ollama $(autotag ollama)
    ollama run llama3.2:3b --keepalive 60m

## RAG Server

    cd wiki_rag/
    pip3 install -r requirements.txt

    #python3 wiki_llamaindex_preprocess.py
    #python3 wiki_llamaindex.py
    python3 wiki_ollama.py

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

