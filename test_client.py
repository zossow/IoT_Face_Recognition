import socket, ssl
import time

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind(('0', 5000))
    sock.listen(5)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    with context.wrap_socket(sock, server_side=True) as ssock:
        connection, address = ssock.accept()
        ssock.setblocking(0)
        while True:
            print("Sleeping for 1s")
            time.sleep(1)
