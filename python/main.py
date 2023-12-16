import pyaudio
import socket

from typing import Tuple

import cv2
import numpy as np
import os
import signal
import sys
import sounddevice as sd
import socket
import threading
import json
import base64

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK_SIZE = 256

DEST_IP = "127.0.0.1"  # Change to the intended destination IP
DEST_PORT = 12345 

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize PyAudio
audio_interface = pyaudio.PyAudio()
stream = audio_interface.open(format=FORMAT, channels=CHANNELS,
                              rate=RATE, input=True,
                              frames_per_buffer=CHUNK_SIZE)

print("Sending audio to {}:{}".format(DEST_IP, DEST_PORT))


def signal_handler(signum: int, frame) -> None:
    sys.exit(0)

colorset: str = "MWNB89RKYUV0JL7kbh1mwngpasexznocv?{}()jftrl!i*=<>~^++--::::;;;;;;\"\"\"\"\"\"''''''''````````````                                     "
target_address = ('127.0.0.1', 12345)

cap: cv2.VideoCapture = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 20)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def get_terminal_size() -> Tuple[int, int]:
    rows, cols = map(int, os.popen('stty size', 'r').read().split())
    return rows, cols

def udp_sender(data, address):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    base64_data = base64.b64encode(data).decode('utf-8')
    json_data = {
                "type": "AA",
                "header": {
                    "room_id": "String",
                    "want_client_id": "String",
                },
                "body": {
                    "content":base64_data
                }
            }
    json_str = json.dumps(json_data)
    json_bytes = json_str.encode('utf-8')
    message = udp_socket.sendto(json_bytes, address)
    print(message)

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    udp_sender(indata.tobytes(), target_address)


def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    sd.default.samplerate = 4410
    sd.default.channels = 1

    count: int = 0

    while True:
        h, w = get_terminal_size()
        ret, frame = cap.read()

        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        base64_data = base64.b64encode(data).decode('utf-8')
        json_data = {
            "type": "audio",
            "header": {
                "room_id": "String",
                "want_client_id": "String",
            },
            "body": {
                "content":base64_data
            }
        }
        json_str = json.dumps(json_data)
        json_bytes = json_str.encode('utf-8')
        client_socket.sendto(json_bytes, (DEST_IP, DEST_PORT))

        if not ret:
            break

        frame = cv2.resize(frame, (w // 2, h - 5))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        output: str = ""
        for row in gray:
            for pixel in row:
                output += colorset[pixel // 2] + colorset[pixel // 2]
            output += "\n"

        count += 1
        if(count == 60):
            count = 0
            os.system('clear')
        print("\033[{}A{}".format(h - 5, output), end="")

        threading.Thread(target=udp_sender, args=(output.encode(), target_address)).start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("Exit")
        cap.release()
        sd.stop()
        print("Closing stream and socket.")
        stream.stop_stream()
        stream.close()
        audio_interface.terminate()
        client_socket.close()