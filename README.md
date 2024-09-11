# PotatOS

## Orin AGX

### Setup

    git clone --recursive git@github.com:davesarmoury/PotatOS.git
    cd PotatOS
    bash jetson-containers/install.sh

### LLM

    jetson-containers run --name ollama $(autotag ollama)
    ollama run llama3

### RAG Server

    cd Potatos/wiki_rag/
    pip3 install -r requirements.txt

    python3 wiki_llamaindex_preprocess.py
    python3 wiki_llamaindex.py

## Orin Nano

### GLaDOS Voice Models

    cd ~
    mkdir RIVA
    cd RIVA
    mkdir artifacts
    mkdir riva_repo
    cd artifacts

    wget https://huggingface.co/DavesArmoury/GLaDOS_TTS/resolve/main/glados_fastpitch.riva
    wget https://huggingface.co/DavesArmoury/GLaDOS_TTS/resolve/main/glados_hifigan.riva
    cd ..

    docker run --gpus all -it --rm \
        -v /home/davesarmoury/RIVA/artifacts:/servicemaker-dev \
        -v /home/davesarmoury/RIVA/riva_repo:/data \
        --entrypoint="/bin/bash" \
        nvcr.io/nvidia/riva/riva-speech:2.13.1-servicemaker-l4t-aarch64

    riva-build speech_synthesis \
        /servicemaker-dev/glados.rmir:tlt_encode \
        /servicemaker-dev/glados_fastpitch.riva:tlt_encode \
        /servicemaker-dev/glados_hifigan.riva:tlt_encode \
        --voice_name=GLaDOS \
        --sample_rate 22050

    riva-deploy /servicemaker-dev/glados.rmir:tlt_encode /data/models

    exit

### Riva

Then, get the Quickstart for Riva.  This example is for Jetson (arm64), but will change for different architectures

    ngc registry resource download-version nvidia/riva/riva_quickstart_arm64:2.13.1
    cd riva_quickstart_arm64_v2.13.1

Edit the config.sh file and change *service_enabled_nlp*, *service_enabled_tts*, and *service_enabled_nmt* to false.  This isn't necessary, but will speed things up if you aren't using them.  Then, download all of the models with the command below

    bash riva_init.sh

Move in the GLaDOS models

    sudo cp -r ~/RIVA/riva_repo/models/* model_repository/models

Start the RIVA server

    bash riva_start.sh

