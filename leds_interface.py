import datetime
import socket

RED_LED = 0x02
YELLOW_LED = 0x01
GREEN_LED = 0x00


class LedInterface:
    def __init__(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind(('0', 5000))
            sock.listen(5)
            self.connection, address = sock.accept()
            sock.setblocking(False)

    def RED(self):
        self.connection.send(bytes([RED_LED]))
        print(datetime.datetime.now().strftime("%H:%M:%S"), "LedInterface: Send RED to ESP")

    def YELLOW(self):
        self.connection.send(bytes([YELLOW_LED]))
        print(datetime.datetime.now().strftime("%H:%M:%S"), "LedInterface: Send YELLOW to ESP")

    def GREEN(self):
        self.connection.send(bytes([GREEN_LED]))
        print(datetime.datetime.now().strftime("%H:%M:%S"), "LedInterface: Send GREEN to ESP")
