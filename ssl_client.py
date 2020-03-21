import socket
import threading
import sys
import ssl


# Wait for incoming data from server
# decode is used to turn the message in bytes to a string
def receive(socket, signal):
    while signal:
        try:
            while True:
                pass
            data = socket.recv(32)
            print(str(data.decode("utf-8")))
        except:
            print("You have been disconnected from the server")
            signal = False
            break


# Get host and port
hostname = 'localhost'
port = 51000

# PROTOCOL_TLS_CLIENT requires valid cert chain and hostname
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations('client.cer')
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# Attempt connection to server
try:
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(ssock.version())
except:
    print("Could not make a connection to the server")
    input("Press enter to quit")
    sys.exit(0)

# Create new thread to wait for data
receiveThread = threading.Thread(target = receive, args = (sock, True))
receiveThread.start()

# Send data to server
# str.encode is used to turn the string message into bytes so it can be sent across the network
while True:
    message = input()
    sock.sendall(str.encode(message))

