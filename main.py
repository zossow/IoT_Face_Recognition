import machine
import time
import socket

RED = machine.Pin(4, machine.Pin.OUT)
YELLOW = machine.Pin(5, machine.Pin.OUT)
GREEN = machine.Pin(15, machine.Pin.OUT)

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.0.185', 5000))
        print("Connected to:", s)
        while True:
            try:
                data = s.recv(4096)[0]
                print("Received:", data)
                if data == 0x02:
                    RED.on()
                    time.sleep_ms(700)
                    RED.off()
                elif data == 0x01:
                    YELLOW.on()
                    time.sleep_ms(700)
                    YELLOW.off()
                elif data == 0x00:
                    GREEN.on()
                    time.sleep_ms(700)
                    GREEN.off()
            except Exception as e:
                print(e)
                time.sleep_ms(1000)

    except Exception as e:
        print(e)
        time.sleep_ms(1000)
        pass

