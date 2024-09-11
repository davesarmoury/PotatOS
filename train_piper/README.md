# GLaDOS with Piper

## Install Piper

  sudo apt install python3-dev
  python3 -m venv piper_venv
  source piper_venv/bin/activate

  cd piper/src/python

  pip3 install --upgrade wheel setuptools
  pip3 install 'pytorch-lightning'

  pip3 install pip==24.0
  pip3 install numpy==1.26.4
  pip3 install -e .

  sudo apt install espeak-ng
  ./build_monotonic_align.sh 
  cd ..

## Download Dataset

  pip3 install -r requirements.txt
  python3 download_glados.py 
  python3 -m piper_train.preprocess   --language en-us   --input-dir dataset_dir/   --output-dir training_dir   --dataset-format ljspeech   --single-speaker   --sample-rate 22050

## Train Network

  wget https://huggingface.co/datasets/rhasspy/piper-checkpoints/resolve/main/en/en_US/lessac/medium/epoch%3D2164-step%3D1355540.ckpt

  python3 -m piper_train --dataset-dir training_dir/ --accelerator 'gpu' --devices 1 --batch-size 32 --max-phoneme-ids 400 --validation-split 0.0 --num-test-examples 0     --max_epochs 1000 --resume_from_checkpoint epoch\=2164-step\=1355540.ckpt --checkpoint-epochs 1 --precision 32

## Verification Audio

  cat piper/etc/test_sentences/test_en-us.jsonl | python3 -m piper_train.infer --sample-rate 22050 --checkpoint training_dir/lightning_logs/version_0/checkpoints/epoch=5308-step=1512740.ckpt --output-dir test_audio

## Save Network

  python3 -m piper_train.export_onnx training_dir/lightning_logs/version_0/checkpoints/epoch=5308-step=1512740.ckpt glados_piper_medium.onnx
  cp training_dir/config.json glados_piper_medium.onnx.json
