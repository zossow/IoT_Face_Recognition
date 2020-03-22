import socket
import threading
import ssl
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import cv2
import time, datetime

class FaceRecognitionCameraApp(threading.Thread):
    def __init__(self, args):
        print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-FaceRecognitionCameraApp: Init start")
        threading.Thread.__init__(self)
        self.haar_cascade_path = args.haar_cascade
        self.face_encodings_filepath = args.face_encodings

    def run(self):
        print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-FaceRecognitionCameraApp: Run start")
        # Load the known faces and embeddings along with OpenCV's Haar
        # cascade classifier for face detection
        with open(self.face_encodings_filepath, "rb") as file:
            face_data = pickle.loads(file.read(), encoding='latin1')
        #with open(self.haar_cascade_path, "rb") as file:
        #    haar_data = file.read()

        stream = imutils.video.VideoStream(src=0, usePiCamera=False).start()
        # Load image from image file
        #    image = cv2.imread(image_file_path)
        cascadeClassifier = cv2.CascadeClassifier(self.haar_cascade_path)
        while True:
            image = stream.read()
            # Convert the input image from BGR to grayscale (for face detection - Haar cascade classifier)
            # and from BGR to RGB (for face recognition - face_recognition package)
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Detect faces in the grayscale image using Haar cascade classifier
            # cascadeClassifier = cv2.CascadeClassifier(self.haar_cascade_path)
            print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-FaceRecognitionCameraApp: face_locations start")
            # face_locations = cascadeClassifier.detectMultiScale(image_gray)
            # face_locations = cascadeClassifier.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
            face_locations = cascadeClassifier.detectMultiScale(image_gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
            print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-FaceRecognitionCameraApp: face_locations end")

            # Translate OpenCV coordinates from (x, y, w, h) to (top, right, bottom, left)
            # Translation formula: (top, right, bottom, left) = (y, x + w, y + h, x)
            face_locations = [(y, x + w, y + h, x) for x, y, w, h in face_locations]

            # Compute the facial embeddings for each face using translated coordinates and
            # RGB image. Be aware that face_recognition.face_encodings() function returns
            # returns a list!
            #names = face_data["names"]
            embeddings = face_data["encodings"]

            preds = []
            recogn_embeddings = face_recognition.face_encodings(image, face_locations)
            for recogn_embedding in recogn_embeddings:
                face_matrix = face_recognition.compare_faces(embeddings, recogn_embedding)
                name = "Unknown"

                if True in face_matrix:
                    matchedIdxs = [i for (i, b) in enumerate(face_matrix) if b]
                    counts = {}
                    for i in matchedIdxs:
                        name = face_data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)
                preds.append(name)
                print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-FaceRecognitionCameraApp:!See:", name)

            #   Find the indexes of all matched faces then count how many times each person was matched
            #   to detected face - assign their name to the face. If nothing was matched, assign "unknown"
            #   to the face.

            # Loop over the recognized faces
            # boxes are locations of faces detected by Haar classifier and translated
            # to different format and names are the corresponding names assigned in the
            # previous step

            #for ((top, right, bottom, left), pred) in zip(face_locations, preds):
                #   Draw rectangles around the detected faces and display a person's name
                #image = cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                #image = cv2.putText(image, pred, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 0, 0), 7)

            #image = cv2.resize(image, (1000, 800))
            #im = cv2.imshow('asda', image)
            #f = cv2.waitKey(33)
            #if f == 27:
            #    break
            #elif f == -1:
            #    continue

        #cv2.destroyAllWindows()

        # Display the image to the screen


class ClientSocketApp(threading.Thread):
    print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-ClientSocketApp: Init start")
    def __init__(self, _context, _host, _port):
        threading.Thread.__init__(self)
        self.context = _context
        self.host = _host
        self.port = _port

    def run(self):
        print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-ClientSocketApp: Run start")
        with socket.create_connection((self.host, self.port)) as sock:
            with self.context.wrap_socket(sock, server_hostname=self.host) as ssock:
                print(ssock.version())
                while True:
                    print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-ClientSocketApp: Sleeping for 10s")
                    time.sleep(10)
                    # TODO tutaj bedzie odbieranie nowego modelu od serwera
                    # TODO i aktualizowanie modelu do nowego watku


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--haar-cascade", required=True, help="path to where the face cascade resides")
    parser.add_argument("-f", "--face-encodings", required=True, help="path to serialized db of facial encodings")
    return parser.parse_args()


def main():
    print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-Main: start")
    print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-Main: parse_args start")
    cameraArgs = parse_args()
    print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-Main: parse_args end")

    print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-Main: context start")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations('client.cer')
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    print(datetime.datetime.now().strftime("%H:%M:%S"), "Thread-Main: context end")

    host = 'localhost'
    port = 51000

    clientApp = ClientSocketApp(context, host, port)
    clientApp.start()
    cameraApp = FaceRecognitionCameraApp(cameraArgs)
    cameraApp.start()

    clientApp.join()
    cameraApp.join()


main()
