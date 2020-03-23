import socket
import threading
import ssl
import queue
import time
import datetime


class FirebaseObserverApp(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # TODO kod Wiolci

    def run(self):
        pass
        # TODO


class FaceRecognitionApp(threading.Thread):
    def __init__(self, _q):
        threading.Thread.__init__(self)
        self.q = _q
        # TODO kod Bambo i Zoski

    def run(self):
        model = 10
        self.q.put(model)
        print(datetime.datetime.now().strftime("%H:%M:%S"),
              "Thread-FaceRecognitionApp: Put model to queue, sleeping for 10s")
        time.sleep(10)


class ServerSocketApp(threading.Thread):
    def __init__(self, _context, _host, _port, _q):
        threading.Thread.__init__(self)
        self.context = _context
        self.host = _host
        self.port = _port
        self.q = _q

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind((self.host, self.port))
            sock.listen(5)
            with self.context.wrap_socket(sock, server_side=True) as ssock:
                connection, address = ssock.accept()
                ssock.setblocking(0)
                print("RPi connection from:", connection.getpeername()[0])
                while True:
                    model = self.q.get()
                    print(datetime.datetime.now().strftime("%H:%M:%S"),
                          "Thread-ServerSocketApp: Received model from queue")
                    connection.send(model)
                    print(datetime.datetime.now().strftime("%H:%M:%S"),
                          "Thread-ServerSocketApp: Send file to RPi, sleeping for 10s")
                    time.sleep(10)
                    # TODO tutaj jak bedzie nowy model
                    # TODO to wysle sie go do RPi za pomoca connection.sendfile()


def main():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('ca.pem', 'ca.key')

    host = '0'
    port = 15007

    q = queue.Queue()

    serverApp = ServerSocketApp(context, host, port, q)
    serverApp.start()

    faceRecognitionModel = FaceRecognitionApp(q)

    serverApp.join()


main()

