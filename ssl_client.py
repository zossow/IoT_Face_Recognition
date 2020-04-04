import socket
import threading
import ssl
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import cv2
import time
import datetime
import hashlib
import queue
from leds_interface import LedInterface
import signal


def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
    exit(0)


class FaceRecognitionCameraApp(threading.Thread):
    def __init__(self, _q):
        threading.Thread.__init__(self)
        self.haar_cascade_path = "haar_cascades/haarcascade_frontalface_default.xml"
        self.q = _q
        self.led = LedInterface()

    def run(self):
        stream = imutils.video.VideoStream(src=0, usePiCamera=False).start()
        cascadeClassifier = cv2.CascadeClassifier(self.haar_cascade_path)
        dumped_model = None
        face_data = None

        while self.q.empty():
            pass

        while True:
            if not self.q.empty():
                while not self.q.empty():
                    dumped_model = self.q.get()
                face_data = pickle.loads(dumped_model)
                print(datetime.datetime.now().strftime("%H:%M:%S"),
                      "Thread-FaceRecognitionCameraApp: Received new model from the queue")

            image = stream.read()
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_locations = cascadeClassifier.detectMultiScale(image_gray, scaleFactor=1.2, minNeighbors=6,
                                                                minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

            face_locations = [(y, x + w, y + h, x) for x, y, w, h in face_locations]

            embeddings = face_data["encodings"]

            preds = []
            recogn_embeddings = face_recognition.face_encodings(image, face_locations)
            for recogn_embedding in recogn_embeddings:
                face_matrix = face_recognition.compare_faces(embeddings, recogn_embedding)
                name = "Unknown"
                count = 0
                if True in face_matrix:
                    matchedIdxs = [i for (i, b) in enumerate(face_matrix) if b]
                    counts = {}
                    for i in matchedIdxs:
                        name = face_data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                        count += 1
                    name = max(counts, key=counts.get)
                preds.append(name)
                print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-FaceRecognitionCameraApp: See:", name)

            if not preds:
                pass
            elif "Unknown" not in preds:
                self.led.GREEN()
            else:
                if len(set(preds)) == 1:
                    self.led.RED()
                else:
                    self.led.YELLOW()

            # Uncomment below to have live view from camera
            '''for ((top, right, bottom, left), pred) in zip(face_locations, preds):
                #   Draw rectangles around the detected faces and display a person's name
                image = cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                image = cv2.putText(image, pred, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 0, 0), 7)

            image = cv2.resize(image, (1000, 800))
            im = cv2.imshow('asda', image)
            f = cv2.waitKey(33)
            if f == 27:
                break
            elif f == -1:
                continue

        cv2.destroyAllWindows()'''


class ClientSocketApp(threading.Thread):
    def __init__(self, _context, _host, _port, _q):
        threading.Thread.__init__(self)
        self.context = _context
        self.host = _host
        self.port = _port
        self.q = _q

    def run(self):
        with socket.create_connection((self.host, self.port)) as sock:
            with self.context.wrap_socket(sock, server_hostname=self.host) as ssock:
                print(datetime.datetime.now().strftime("%H:%M:%S"),
                      "Thread-ClientSocketApp: Connected to server using:", ssock.version())
                while True:
                    model = recvall(ssock)
                    print(datetime.datetime.now().strftime("%H:%M:%S"),
                          "Thread-ClientSocketApp: Received model from server:", hashlib.sha224(model).hexdigest())
                    time.sleep(1)

                    self.q.put(model)
                    print(datetime.datetime.now().strftime("%H:%M:%S"),
                          "Thread-ClientSocketApp: Put model to the queue")


def recvall(sock):
    data = b''
    bufsize = 4096
    while True:
        packet = sock.recv(bufsize)
        data += packet
        if len(packet) < bufsize:
            break
    return data


def main():
    signal.signal(signal.SIGINT, keyboardInterruptHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations('client.cer')
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    host = 'localhost'
    port = 51000

    q = queue.Queue()

    clientApp = ClientSocketApp(context, host, port, q)
    clientApp.start()
    cameraApp = FaceRecognitionCameraApp(q)
    cameraApp.start()

    clientApp.join()
    cameraApp.join()


main()
