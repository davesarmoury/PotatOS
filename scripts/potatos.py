#!/usr/bin/env python3

### Based on vosk-server/websocket/test_microphone.py ###

import json
import os
import sys
import asyncio
import websockets
import logging
import sounddevice as sd
import argparse
import subprocess
import urllib.parse
import requests

piper_url = "localhost:5001"
rag_url = "http://localhost:5000/chat?query="

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    loop.call_soon_threadsafe(audio_queue.put_nowait, bytes(indata))

async def run_test():

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 4000, device=args.device, dtype='int16',
                           channels=1, callback=callback) as device:

        async with websockets.connect(args.uri) as websocket:
            await websocket.send('{ "config" : { "sample_rate" : %d } }' % (device.samplerate))

            while True:
                data = await audio_queue.get()
                await websocket.send(data)

                rec = await websocket.recv()
                rec = json.loads(rec)

                if "text" in rec.keys():
                    asr_in = rec["text"].rstrip().lstrip()

                    if len(asr_in) > 2:
                        print("-------------")
                        print(asr_in)

                        os.system("pactl set-source-mute 0 on")


                        query_url = rag_url + urllib.parse.quote_plus(asr_in)
                        r = requests.get(query_url)

                        response = str(r.text)
                        response = response.replace("2", " too ").replace("C-3PO", "see threepio")

                        print(response)

                        ps = subprocess.run(["curl", "-sG", "--data-urlencode", "text=\"" + response.strip() + "\"", "--output", "-", piper_url], check=True, capture_output=True)
                        aplay = subprocess.run(['aplay', '-q'], input=ps.stdout, capture_output=True)

                        os.system("pactl set-source-mute 0 off")

            await websocket.send('{"eof" : 1}')
            print (await websocket.recv())

async def main():

    global args
    global loop
    global audio_queue

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-l', '--list-devices', action='store_true',
                        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    parser = argparse.ArgumentParser(description="ASR Server",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     parents=[parser])
    parser.add_argument('-u', '--uri', type=str, metavar='URL',
                        help='Server URL', default='ws://localhost:2700')
    parser.add_argument('-d', '--device', type=int_or_str,
                        help='input device (numeric ID or substring)')
    parser.add_argument('-r', '--samplerate', type=int, help='sampling rate', default=16000)

    args = parser.parse_args(remaining)
    loop = asyncio.get_running_loop()
    audio_queue = asyncio.Queue()

    logging.basicConfig(level=logging.INFO)
    await run_test()

if __name__ == '__main__':
    asyncio.run(main())
