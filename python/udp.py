import socket
import pyaudio
from typing import Tuple
import os
import json
import base64

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK_SIZE = 256

count: int = 0

HOST = '127.0.0.1'  # Listen on all available interfaces
PORT = 1025       # Port to listen on (should match the sender's port)

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

# Initialize PyAudio
audio_interface = pyaudio.PyAudio()
stream = audio_interface.open(format=FORMAT, channels=CHANNELS,
                              rate=RATE, output=True,
                              frames_per_buffer=CHUNK_SIZE)

def get_terminal_size() -> Tuple[int, int]:
    rows, cols = map(int, os.popen('stty size', 'r').read().split())
    return rows, cols

def udp_server(host, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))

    print(f"UDP Server listening on {host}:{port}")
    count: int = 0

    while True:
        print("AAhijjs")
        data, addr = server_socket.recvfrom(0)
        print("AA")
        try:
            json_data = json.loads(data.decode('utf-8'))
            print(json_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(data)

        if 'type' in json_data:
            message_type = json_data['type']
            if message_type == "AA":
                data = json_data["body"]["content"]
                data = base64.b64decode(data.decode('utf-8'))
                h, w = get_terminal_size()
                count += 1
                if(count == 60):
                    count = 0
                    os.system('clear')
                print("\033[{}A{}".format(h - 5, data), end="")
            elif(message_type == "audio"):
                stream.write(json_data["body"]["content"])
            else:
                print("ERROR")
        else:
            print("Error: 'type' field not found in the received JSON data.")

if __name__ == "__main__":
    host = '0.0.0.0'  # 受け付けるIPアドレス (0.0.0.0はすべてのアドレスを表します)
    port = 12345       # 受け付けるポート番号 (Senderと合わせてください)

    udp_server(host, port)
