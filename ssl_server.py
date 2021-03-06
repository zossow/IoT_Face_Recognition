import logging
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
from tqdm import tqdm

from config import config
from image_augmentation import image_data_augmentation, transformations
from transfer_files import transfer_files_to_main_directory
from trigger_function import TriggerFunction, set_env


class FirebaseObserverApp(threading.Thread):
    def __init__(self, _qFirebase):
        threading.Thread.__init__(self)
        self.qFirebase = _qFirebase

    def run(self):
        while True:
            set_env()
            trigger = TriggerFunction()
            bool_value, files_name = trigger.check_if_new_file()
            if bool_value:
                set_env()
                trigger.images_to_download(files_name)
                # Bambiego Funckje
                image_data_augmentation(folder_with_images=config.tmp_picture_folder, transformations=transformations)
                transfer_files_to_main_directory()
                print(datetime.datetime.now().strftime("%H:%M:%S"),
                      "Thread-FirebaseObserverApp: New pictures, letting now FaceRecognitionApp to create new model")

                '''If this queue is not empty, it means that FaceRecognitionApp should,
                 but didn't started creating model yet. Don't have to said it again :)'''
                if self.qFirebase.empty():
                    self.qFirebase.put(1)
            time.sleep(120)


class FaceRecognitionApp(threading.Thread):
    def __init__(self, _qSocket, _qFirebase):
        threading.Thread.__init__(self)
        self.qSocket = _qSocket
        self.qFirebase = _qFirebase
        self.path_to_images = "Pictures"

    def run(self):
        if os.path.exists('dumped_model.bin'):
            with open('dumped_model.bin', 'rb') as fid:
                data = pickle.load(fid)
                model = pickle.dumps(data)
                print(datetime.datetime.now().strftime("%H:%M:%S"),
                      "Thread-FaceRecognitionApp: Put saved model to queue:", hashlib.sha224(model).hexdigest())
                self.qSocket.put(model)
        else:
            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FaceRecognitionApp: No saved model on a server, training new model")
            model = self.encode()
            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FaceRecognitionApp: Put new model to queue:", hashlib.sha224(model).hexdigest())
            self.qSocket.put(model)

        while True:
            if self.qFirebase.empty():
                continue
            while not self.qFirebase.empty():
                self.qFirebase.get()

            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FaceRecognitionApp: Got signal from FirebaseObserverApp to train new model")
            model = self.encode()
            '''names, face_encodings = self.get_face_encodings(self.path_to_images)
            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FaceRecognitionApp: Training completed")

            data = {"encodings": face_encodings, "names": names}
            model = pickle.dumps(data)

            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FaceRecognitionApp: Saving model to: dumped_model.bin")
            with open('dumped_model.bin', 'wb') as fid:
                pickle.dump(data, fid)'''

            print(datetime.datetime.now().strftime("%H:%M:%S"),
                  "Thread-FaceRecognitionApp: Put new model to queue:", hashlib.sha224(model).hexdigest())
            self.qSocket.put(model)

    def encode(self):
        names, face_encodings = self.get_face_encodings(self.path_to_images)
        print(datetime.datetime.now().strftime("%H:%M:%S"),
              "Thread-FaceRecognitionApp: Training completed")

        data = {"encodings": face_encodings, "names": names}
        model = pickle.dumps(data)

        print(datetime.datetime.now().strftime("%H:%M:%S"),
              "Thread-FaceRecognitionApp: Saving model to: dumped_model.bin")
        with open('dumped_model.bin', 'wb') as fid:
            pickle.dump(data, fid)
        return model

    def get_face_encodings(self, path_to_images):
        names = []
        face_encodings = []

        for image_path in tqdm(paths.list_images(path_to_images)):
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
    logging.basicConfig(level=logging.INFO)

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


    firebaseApp = FirebaseObserverApp(qFirebase)
    firebaseApp.start()

    serverApp.join()
    faceRecognitionModel.join()
    firebaseApp.join()


main()



