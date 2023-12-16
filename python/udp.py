import socket
import pyaudio
import json
import os
import base64
from typing import Tuple

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 4410
CHUNK_SIZE = 512

HOST = '0.0.0.0'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

audio_interface = pyaudio.PyAudio()
stream = audio_interface.open(format=FORMAT, channels=CHANNELS,
                              rate=RATE, output=True,
                              frames_per_buffer=CHUNK_SIZE)

count = 0

def get_terminal_size() -> Tuple[int, int]:
    rows, cols = map(int, os.popen('stty size', 'r').read().split())
    return rows, cols

print("Listening on {}:{}".format(HOST, PORT))
try:
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
                data = json_data["body"]["content"]
                h, w = get_terminal_size()
                count += 1
                if(count == 60):
                    count = 0
                    os.system('clear')
                print("\033[{}A{}".format(h - 5, data), end="")
            elif(message_type == "audio"):
                base64_content = json_data['body']['content']
                audio_data = base64.b64decode(base64_content.encode('utf-8'))
                stream.write(audio_data)
            else:
                print("ERROR")
        else:
            print("Error: 'type' field not found in the received JSON data.")
except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    print("Closing stream and socket.")
    stream.stop_stream()
    stream.close()
    audio_interface.terminate()
    server_socket.close()
    