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

DEST_IP = "35.192.191.174"
DEST_PORT = 8088

ROOM_ID = ""

audio_interface = pyaudio.PyAudio()
socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

stream = audio_interface.open(format=FORMAT, channels=CHANNELS,
                              rate=RATE, input=True,
                              frames_per_buffer=CHUNK_SIZE)

cap: cv2.VideoCapture = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 20)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

colorset: str = "MWNB89RKYUV0JL7kbh1mwngpasexznocv?{}()jftrl!i*=<>~^++--::::;;;;;;\"\"\"\"\"\"''''''''````````````                                     "
target_address = (DEST_IP, DEST_PORT)

count = 0

async def send_audio(room_id: str):
    while True:
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        base64_data = base64.b64encode(data).decode('utf-8')
        json_data = {
            "type": "audio",
            "header": {
                "room_id": room_id,
                "want_client_id": "",
            },
            "body": {
                "content": base64_data
            }
        }
        json_str = json.dumps(json_data)
        json_bytes = json_str.encode('utf-8')
        socket1.sendto(json_bytes, (DEST_IP, DEST_PORT))
        await asyncio.sleep(0.01)

async def udp_sender(data, address,room_id: str):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    base64_data = data
    json_data = {
                "type": "AA",
                "header": {
                    "room_id": room_id,
                    "want_client_id": "",
                },
                "body": {
                    "content":base64_data
                }
            }
    json_str = json.dumps(json_data)
    json_bytes = json_str.encode('utf-8')
    udp_socket.sendto(json_bytes, address)

def create_room(address):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    json_data = {
                "type": "create_room",
                "header": {
                    "room_id": ""
                },
                "body": {
                    "content":""
                }
            }
    json_str = json.dumps(json_data)
    json_bytes = json_str.encode('utf-8')
    udp_socket.sendto(json_bytes, address)

    data, addr = socket1.recvfrom(65535)
    try:
        json_data = json.loads(data.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(data)
    if 'type' in json_data:
        message_type = json_data['type']
        if message_type == "create_room":
            print(json_data["body"]["room_id"])
        else:
            print("Failed room create!")

def join_room(room_id:str, address):
    udp_socket = socket1.socket(socket.AF_INET, socket.SOCK_DGRAM)
    json_data = {
                "type": "join_room",
                "header": {
                    "room_id": room_id
                },
                "body": {
                    "content":""
                }
            }
    json_str = json.dumps(json_data)
    json_bytes = json_str.encode('utf-8')
    udp_socket.sendto(json_bytes, address)

def exit_room(room_id:str, address):
    udp_socket = socket1.socket(socket.AF_INET, socket.SOCK_DGRAM)
    json_data = {
                "type": "join_room",
                "header": {
                    "room_id": room_id
                },
                "body": {
                    "content":""
                }
            }
    json_str = json.dumps(json_data)
    json_bytes = json_str.encode('utf-8')
    udp_socket.sendto(json_bytes, address)

def display_help():
    print("Usage: python main.py [--create] [--join <arg>]")
    print("--create : Create Room.")
    print("--join   : Join room.")
    print("           Example: python main.py --join hoge")

async def receive_data():
    count = 0
    while True:
        data, addr = socket1.recvfrom(65535)
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

def run_udp_sender(output, target_address, room_id):
    asyncio.run(udp_sender(output, target_address, room_id))

async def main():
    args = sys.argv[1:]

    if "--create" in args:
        create_room(address=target_address)
        return
    elif "--join" in args and len(args) > 1:
        global ROOM_ID
        index = args.index("--join")
        arg = args[index + 1]
        ROOM_ID = arg
        join_room(room_id=ROOM_ID,address=target_address)
    else:
        display_help()
        return

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

    asyncio.create_task(send_audio(room_id=ROOM_ID))
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
                "room_id": ROOM_ID,
                "want_client_id": "String",
            },
            "body": {
                "content": base64_data
            }
        }
        json_str = json.dumps(json_data)
        json_bytes = json_str.encode('utf-8')
        socket1.sendto(json_bytes, (DEST_IP, DEST_PORT))

        if not ret:
            break

        frame = cv2.resize(frame, (w // 2, h - 5))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        output: str = ""
        for row in gray:
            for pixel in row:
                output += colorset[pixel // 2] + colorset[pixel // 2]
            output += "\n"

        threading.Thread(target=run_udp_sender, args=(output, target_address, ROOM_ID)).start()
except KeyboardInterrupt:
    pass
finally:
    print("Exit")
    exit_room(room_id=ROOM_ID,address=target_address)
    cap.release()
    sd.stop()
    print("Closing stream and socket.")
    stream.stop_stream()
    stream.close()
    audio_interface.terminate()
    socket1.close()

if __name__ == "__main__":
    asyncio.run(main())
