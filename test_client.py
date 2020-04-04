import socket, ssl
import time

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind(('0', 500))
    sock.listen(5)
    with ssl.wrap_socket(sock, server_side=True) as ssock:
        connection, address = ssock.accept()
        ssock.setblocking(0)
        while True:
            print("Sleeping for 1s")
            time.sleep(1)
