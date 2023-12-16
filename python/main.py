import asyncio
import pyaudio
import socket
import cv2
import os
import signal
import sys
import sounddevice as sd
import threading
import json
import base64
from typing import Tuple

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 4410
CHUNK_SIZE = 512

DEST_IP = "127.0.0.1"
DEST_PORT = 12345

audio_interface = pyaudio.PyAudio()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

stream = audio_interface.open(format=FORMAT, channels=CHANNELS,
                              rate=RATE, input=True,
                              frames_per_buffer=CHUNK_SIZE)

cap: cv2.VideoCapture = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 20)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

colorset: str = "MWNB89RKYUV0JL7kbh1mwngpasexznocv?{}()jftrl!i*=<>~^++--::::;;;;;;\"\"\"\"\"\"''''''''````````````                                     "
target_address = ('127.0.0.1', 12345)

count = 0

async def send_audio():
    while True:
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        base64_data = base64.b64encode(data).decode('utf-8')
        json_data = {
            "type": "audio",
            "header": {
                "room_id": "String",
                "want_client_id": "String",
            },
            "body": {
                "content": base64_data
            }
        }
        json_str = json.dumps(json_data)
        json_bytes = json_str.encode('utf-8')
        client_socket.sendto(json_bytes, (DEST_IP, DEST_PORT))
        await asyncio.sleep(0.01)

async def udp_sender(data, address):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    base64_data = data
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
    udp_socket.sendto(json_bytes, address)

async def receive_data():
    count = 0
    while True:
        data, addr = server_socket.recvfrom(65535)
        try:
            json_data = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(data)

        if 'type' in json_data:
            message_type = json_data['type']
            if message_type == "AA":
                content = json_data["body"]["content"]
                h, w = get_terminal_size()
                count += 1
                if count == 60:
                    count = 0
                    os.system('clear')
                print("\033[{}A{}".format(h - 5, content), end="")
            elif message_type == "audio":
                base64_content = json_data['body']['content']
                audio_data = base64.b64decode(base64_content.encode('utf-8'))
                stream.write(audio_data)
            else:
                print("ERROR")
        else:
            print("Error: 'type' field not found in the received JSON data.")

def signal_handler(signum: int, frame) -> None:
    sys.exit(0)

def get_terminal_size() -> Tuple[int, int]:
    rows, cols = map(int, os.popen('stty size', 'r').read().split())
    return rows, cols

async def main():
    global stream, cap

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    sd.default.samplerate = 4410
    sd.default.channels = 1

    stream = audio_interface.open(format=FORMAT, channels=CHANNELS,
                                  rate=RATE, input=True,
                                  frames_per_buffer=CHUNK_SIZE)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 20)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    asyncio.create_task(send_audio())
    asyncio.create_task(receive_data())

try:
    while True:
        h, w = get_terminal_size()
        ret, frame = cap.read()

        # Existing code for sending strings
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        base64_data = base64.b64encode(data).decode('utf-8')
        json_data = {
            "type": "audio",
            "header": {
                "room_id": "String",
                "want_client_id": "String",
            },
            "body": {
                "content": base64_data
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
        if count == 60:
            count = 0
            os.system('clear')
        print("\033[{}A{}".format(h - 5, output), end="")

        threading.Thread(target=udp_sender, args=(output, target_address)).start()
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
    server_socket.close()

if __name__ == "__main__":
    asyncio.run(main())
