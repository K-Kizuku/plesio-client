import pyaudio
import socket

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK_SIZE = 1024

# Network configuration
DEST_IP = "127.0.0.1"  # Change to the intended destination IP
DEST_PORT = 12345       # Change to the intended destination port

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize PyAudio
audio_interface = pyaudio.PyAudio()
stream = audio_interface.open(format=FORMAT, channels=CHANNELS,
                              rate=RATE, input=True,
                              frames_per_buffer=CHUNK_SIZE)

print("Sending audio to {}:{}".format(DEST_IP, DEST_PORT))
try:
    # Continuously record audio and send it
    while True:
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        client_socket.sendto(data, (DEST_IP, DEST_PORT))
        print("send")
except KeyboardInterrupt:
    # Stop and close everything properly
    print("Interrupted by user")
finally:
    print("Closing stream and socket.")
    stream.stop_stream()
    stream.close()
    audio_interface.terminate()
    client_socket.close()
