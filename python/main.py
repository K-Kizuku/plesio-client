from typing import Tuple

import cv2
import numpy as np
import os
import signal
import sys

def signal_handler(signum: int, frame) -> None:
    sys.exit(0)

colorset: str = "MWNB89RKYUV0JL7kbh1mwngpasexznocv?{}()jftrl!i*=<>~^++--::::;;;;;;\"\"\"\"\"\"''''''''````````````                                     "

cap: cv2.VideoCapture = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 20)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def get_terminal_size() -> Tuple[int, int]:
    rows, cols = map(int, os.popen('stty size', 'r').read().split())
    return rows, cols

def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        h, w = get_terminal_size()
        ret, frame = cap.read()
        
        if not ret:
            break

        frame = cv2.resize(frame, (w // 2, h - 5))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        output: str = ""
        for row in gray:
            for pixel in row:
                output += colorset[pixel // 2] + colorset[pixel // 2]
            output += "\n"

        print("\033[{}A{}".format(h - 5, output), end="")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("Exit")
        cap.release()
