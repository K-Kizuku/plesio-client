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
DATE = None

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

def receive_data(sock):
    global DATE
    while True:
        data, address = sock.recvfrom(65535)
        print(data)
        decoded_data = json.loads(data.decode('utf-8'))
        print(f"Received data from {address}: {data}")
        DATE = decoded_data

# 送信用のスレッド
def send_data(sock, json_data, address):
    json_str = json.dumps(json_data)
    json_bytes = json_str.encode('utf-8')
    
    sock.sendto(json_bytes, address)
    print(f"Sent data to {address}: {json_data}")

def create_room(address):
    global DATE
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_thread = threading.Thread(target=receive_data, args=(udp_socket,), daemon=True)
    receive_thread.start()

    json_data = {
        "type": "create_room",
        "header": {
            "room_id": ""
        },
        "body": {
            "content": ""
        }
    }

    send_thread = threading.Thread(target=send_data, args=(udp_socket, json_data, address))
    send_thread.start()

    send_thread.join()
    receive_thread.join()
    udp_socket.close()

    if DATE is not None:
        try:
            json_data = json.loads(DATE)
            if 'type' in json_data:
                message_type = json_data['type']
                if message_type == "create_room":
                    print(json_data["header"]["room_id"])
                else:
                    print("Failed room create!")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(DATE)
    else:
        print("No data received.")


def join_room(room_id:str, address):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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

def signal_handler(signum: int, frame) -> None:
    sys.exit(0)

def get_terminal_size() -> Tuple[int, int]:
    rows, cols = map(int, os.popen('stty size', 'r').read().split())
    return rows, cols

def run_udp_sender(output, target_address, room_id):
    asyncio.run(udp_sender(output, target_address, room_id))

async def main():
    args = sys.argv[1:]
    if not args:
        display_help()
        sys.exit(1)
    elif "--create" in args:
        create_room(address=target_address)
        sys.exit(1)
    elif "--join" in args and len(args) > 1:
        global ROOM_ID
        index = args.index("--join")
        arg = args[index + 1]
        ROOM_ID = arg
        print("HEKSOW")
        join_room(room_id=ROOM_ID,address=target_address)
    else:
        display_help()
        sys.exit(1)

    global stream, cap

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    sd.default.samplerate = 4410
    sd.default.channels = 1

    stream = audio_interface.open(format=FORMAT, channels=CHANNELS,
                                  rate=RATE, input=True,
                                  frames_per_buffer=CHUNK_SIZE)

    print(cap)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 20)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    task1 = asyncio.create_task(send_audio(room_id=ROOM_ID))
    task2 = asyncio.create_task(receive_data())
    task3 = asyncio.create_task(udp_sender(address=target_address,room_id=ROOM_ID))
    await asyncio.gather(task1, task2,task3)

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
