import socket
import pyaudio

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK_SIZE = 1024

# Network configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 12345       # Port to listen on (should match the sender's port)

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

# Initialize PyAudio
audio_interface = pyaudio.PyAudio()
stream = audio_interface.open(format=FORMAT, channels=CHANNELS,
                              rate=RATE, output=True,
                              frames_per_buffer=CHUNK_SIZE)

print("Listening on {}:{}".format(HOST, PORT))
try:
    # Continuously receive audio and play it
    while True:
        data, addr = server_socket.recvfrom(65535)
        stream.write(data)
except KeyboardInterrupt:
    # Stop and close everything properly
    print("Interrupted by user")
finally:
    print("Closing stream and socket.")
    stream.stop_stream()
    stream.close()
    audio_interface.terminate()
    server_socket.close()

