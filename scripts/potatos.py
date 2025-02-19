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
import time
import board
import neopixel_spi as neopixel

NUM_PIXELS = 3
PIXEL_ORDER = neopixel.RGB
COLORS = {"OFF": 0x000000, "IDLE": 0xFF0000, "EYE": 0xFF9999, "THINKING": 0x66B2FF, "SPEAKING": 0x66FF66, "ERROR": 0xFF33FF, "LISTENING": 0xFF0000, "MUTED": 0x00FF00}

piper_url = "localhost:5001"
rag_url = "http://localhost:5000/chat?query="

def mute():
    os.system("pactl set-source-mute 0 on 2> /dev/null")
    os.system("pactl set-source-mute 1 on 2> /dev/null")
    os.system("pactl set-source-mute 2 on 2> /dev/null")
    os.system("pactl set-source-mute 3 on 2> /dev/null")
    os.system("pactl set-source-mute 4 on 2> /dev/null")
    os.system("pactl set-source-mute 5 on 2> /dev/null")

def unmute():
    os.system("pactl set-source-mute 0 off 2> /dev/null")
    os.system("pactl set-source-mute 1 off 2> /dev/null")
    os.system("pactl set-source-mute 2 off 2> /dev/null")
    os.system("pactl set-source-mute 3 off 2> /dev/null")
    os.system("pactl set-source-mute 4 off 2> /dev/null")
    os.system("pactl set-source-mute 5 off 2> /dev/null")

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    loop.call_soon_threadsafe(audio_queue.put_nowait, bytes(indata))

def set_pixels(pixels, vals=[COLORS["ERROR"], COLORS["ERROR"], COLORS["ERROR"]]):
    for i in range(NUM_PIXELS):
        pixels[i] = vals[i]

    pixels.show()

async def run_test():
    global pixels

    unmute()

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 4096, device=args.device, dtype='int16',
                           channels=1, callback=callback) as device:

        async with websockets.connect(args.uri) as websocket:
            await websocket.send('{ "config" : { "sample_rate" : %d } }' % (device.samplerate))

            while True:
                set_pixels(pixels, [COLORS["EYE"], COLORS["IDLE"], COLORS["LISTENING"]])

                data = await audio_queue.get()
                await websocket.send(data)

                rec = await websocket.recv()
                rec2 = json.loads(rec)

                if "text" in rec2.keys():
                    asr_in = rec2["text"].strip()

                    if len(asr_in) > 2:
                        set_pixels(pixels, [COLORS["EYE"], COLORS["THINKING"], COLORS["MUTED"]])
                        print("-------------")
                        print(asr_in)

                        mute()

                        response = asr_in
                        query_url = rag_url + urllib.parse.quote_plus(asr_in)
                        r = requests.get(query_url)

                        response = str(r.text)
                        response = response.replace("GLaDOS", "glados")

                        print(response)
                        set_pixels(pixels, [COLORS["EYE"], COLORS["SPEAKING"], COLORS["MUTED"]])

                        ps = subprocess.run(["curl", "-sG", "--data-urlencode", "text=\"" + response.strip() + "\"", "--output", "-", piper_url], check=True, capture_output=True)
                        aplay = subprocess.run(['aplay', '-q'], input=ps.stdout, capture_output=True)

                        unmute()

                        set_pixels(pixels, [COLORS["EYE"], COLORS["IDLE"], COLORS["LISTENING"]])

            await websocket.send('{"eof" : 1}')
            print (await websocket.recv())

async def main():
    global args
    global loop
    global audio_queue
    global pixels

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-l', '--list-devices', action='store_true',
                        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    spi = board.SPI()

    pixels = neopixel.NeoPixel_SPI(
        spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False
    )

    set_pixels(pixels)

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
