import socket
import threading
import ssl
import queue
import time
import datetime
import random
from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os
import hashlib
import signal


class FirebaseObserverApp(threading.Thread):
    def __init__(self, _qFirebase):
        threading.Thread.__init__(self)
        self.qFirebase = _qFirebase
        # TODO kod Wiolci

    def run(self):
        while True:
            # TODO observer - jak beda nowe pliki to odpali ponizszy kod
            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FirebaseObserverApp: New pictures, letting now FaceRecognitionApp to create new model")

            '''If this queue is not empty, it means that FaceRecognitionApp should,
             but didn't started creating model yet. Don't have to said it again :)'''
            if self.qFirebase.empty():
                self.qFirebase.put(1)

            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FirebaseObserverApp: Temporary sleeping for 200s")
            time.sleep(200)


class FaceRecognitionApp(threading.Thread):
    def __init__(self, _qSocket, _qFirebase):
        threading.Thread.__init__(self)
        self.qSocket = _qSocket
        self.qFirebase = _qFirebase
        self.path_to_images = "Pictures/"

    def run(self):
        while True:
            if self.qFirebase.empty():
                continue
            while not self.qFirebase.empty():
                self.qFirebase.get()

            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FaceRecognitionApp: Got signal from FirebaseObserverApp to train new model")
            names, face_encodings = self.get_face_encodings(self.path_to_images)
            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FaceRecognitionApp: Training completed")

            data = {"encodings": face_encodings, "names": names}
            model = pickle.dumps(data)

            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FaceRecognitionApp: Put new model to queue:", hashlib.sha224(model).hexdigest())
            self.qSocket.put(model)

    @classmethod
    def keyboardInterruptHandler(signal, frame, arg):
        print(signal, frame, arg)
        print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
        exit(0)

    def get_face_encodings(self, path_to_images):
        names = []
        face_encodings = []

        for image_path in paths.list_images(path_to_images):
            name = image_path.replace("_", os.path.sep).split(os.path.sep)[-2]

            image = cv2.imread(image_path)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_image, model="hog")

            encodings = face_recognition.face_encodings(rgb_image, face_locations)

            for encoding in encodings:
                names.append(name)
                face_encodings.append(encoding)

        return names, face_encodings


class ServerSocketApp(threading.Thread):
    def __init__(self, _context, _host, _port, _qSocket):
        threading.Thread.__init__(self)
        self.context = _context
        self.host = _host
        self.port = _port
        self.qSocket = _qSocket

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind((self.host, self.port))
            sock.listen(5)
            with self.context.wrap_socket(sock, server_side=True) as ssock:
                connection, address = ssock.accept()
                ssock.setblocking(0)
                print(datetime.datetime.now().strftime("%H:%M:%S"),
                      "Thread-ServerSocketApp: RPi connection from:", connection.getpeername()[0])
                while True:
                    if self.qSocket.empty():
                        continue
                    while not self.qSocket.empty():
                        model = self.qSocket.get()
                    print(datetime.datetime.now().strftime("%H:%M:%S"),
                          "Thread-ServerSocketApp: Received model from queue")

                    connection.sendall(model)
                    print(datetime.datetime.now().strftime("%H:%M:%S"),
                          "Thread-ServerSocketApp: Send model to RPi")


def main():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('ca.pem', 'ca.key')

    host = '0'
    port = 15007

    qSocket = queue.Queue()
    qFirebase = queue.Queue()

    serverApp = ServerSocketApp(context, host, port, qSocket)
    serverApp.start()

    faceRecognitionModel = FaceRecognitionApp(qSocket, qFirebase)
    faceRecognitionModel.start()
    signal.signal(signal.SIGINT, FaceRecognitionApp.keyboardInterruptHandler)

    firebaseApp = FirebaseObserverApp(qFirebase)
    firebaseApp.start()

    serverApp.join()
    faceRecognitionModel.join()
    firebaseApp.join()


main()

