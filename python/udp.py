import socket
import os
from typing import Tuple
import os
import time

def get_terminal_size() -> Tuple[int, int]:
    rows, cols = map(int, os.popen('stty size', 'r').read().split())
    return rows, cols

def udp_server(host, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))

    print(f"UDP Server listening on {host}:{port}")
    count: int = 0

    while True:
        data, addr = udp_socket.recvfrom(8192)
        h, w = get_terminal_size()
        count += 1
        if(count == 60):
            count = 0
            os.system('clear')
        # os.system('clear')
        # print(f"Received data from {addr}: {data}")
        print("\033[{}A{}".format(h - 5, data.decode()), end="")

if __name__ == "__main__":
    host = '127.0.0.1'  # 受け付けるIPアドレス (0.0.0.0はすべてのアドレスを表します)
    port = 1025       # 受け付けるポート番号 (Senderと合わせてください)

    udp_server(host, port)
