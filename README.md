# PotatOS

## Setup

    git clone --recursive git@github.com:davesarmoury/PotatOS.git
    cd PotatOS

## Jetson Containers

    bash jetson-containers/install.sh

## LLM

    jetson-containers run --name ollama $(autotag ollama)
    ollama run gemma:2b --keepalive 60m

## RAG Server

    cd Potatos/wiki_rag/
    pip3 install -r requirements.txt

    python3 wiki_llamaindex_preprocess.py
    python3 wiki_llamaindex.py

## Audio

See [https://developer.nvidia.com/embedded/learn/tutorials/connecting-bluetooth-audio](https://developer.nvidia.com/embedded/learn/tutorials/connecting-bluetooth-audio), then pair a bluetooth speaker with bluetoothctl.  Then set the volume

    amixer -D pulse sset Master 50%

## VOSK

    pip3 install -r vosk-server/requirements.txt 
    pip3 install sounddevice
    sudo apt install libportaudio2

    cd vosk-server/websocket
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15
    mv vosk-model-small-en-us-0.15 model

    python3 asr_server.py

## Run Piper Server

Train or download the GLaDOS Piper voice.  See [train_piper](train_piper) for more details

On the jetson, put the onnx and onnx.json files into jetson-containers/data/models/piper, then run the command below

    jetson-containers run $(autotag piper-tts) python3 -m piper.http_server --port 5001 -m /data/models/piper/glados_piper_medium.onnx

Run a quick test with

    curl -G --data-urlencode 'text=I like big butts, I cannot lie.' --output - 'localhost:5001' | aplay
