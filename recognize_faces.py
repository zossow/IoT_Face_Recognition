from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--haar-cascade", required=True,
        help = "path to where the face cascade resides")
    parser.add_argument("-f", "--face-encodings", required=True,
        help="path to serialized db of facial encodings")
    parser.add_argument("-i", "--image-file", required=True,
        help="path to input image file for file detection")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    haar_cascade_path = args.haar_cascade
    face_encodings_filepath = args.face_encodings
    image_file_path = args.image_file

    # Load the known faces and embeddings along with OpenCV's Haar
    # cascade classifier for face detection
    with open(face_encodings_filepath, "rb") as file:
        face_data = pickle.loads(file.read())
    with open(haar_cascade_path, "rb") as file:
        haar_data = file.read()


    # Load image from image file
    image = cv2.imread(image_file_path)
    # Convert the input image from BGR to grayscale (for face detection - Haar cascade classifier)
    # and from BGR to RGB (for face recognition - face_recognition package)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Detect faces in the grayscale image using Haar cascade classifier
    cascadeClassifier = cv2.CascadeClassifier(haar_cascade_path)
    face_locations = cascadeClassifier.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30), flags=cv2.CASCADE_SCALE_IMAGE)
    
    # Translate OpenCV coordinates from (x, y, w, h) to (top, right, bottom, left)
    # Translation formula: (top, right, bottom, left) = (y, x + w, y + h, x)
    face_locations = [(y, x + w, y + h, x) for x, y, w, h in face_locations]
    
    # Compute the facial embeddings for each face using translated coordinates and
    # RGB image. Be aware that face_recognition.face_encodings() function returns
    # returns a list!
    names = face_data["names"]
    embeddings = face_data["encodings"]
    
    preds = []
    recogn_embeddings = face_recognition.face_encodings(image, face_locations)
    for recogn_embedding in recogn_embeddings:
        face_matrix = face_recognition.compare_faces(embeddings, recogn_embedding)
        
        # Loop over the facial embeddings
        kubabryl = 0
        patrykszelag = 0
        for name, match in zip(names, face_matrix):
         #   Attempt to match each face in the input image to our known encodings
           if match == True:
                if name == 'kubabryl':
                    kubabryl += 1
                elif name == 'patrykszelag':
                    patrykszelag +=1

        # name_list = [kubabryl, patrykszelag]  

        # if sum(name_list) == 0:
        #     pred = "Unknown"
        # else:
        #     name_list.sort()
        #     pred = name_list[-1]    
        if kubabryl > patrykszelag:
            pred = 'Kuba Bryl'        
        elif patrykszelag >kubabryl:
            pred = "Patryk Szelag"
        else:
            pred = 'Unknown'
            
        preds.append(pred)
    
    #   Find the indexes of all matched faces then count how many times each person was matched
    #   to detected face - assign their name to the face. If nothing was matched, assign "unknown"
    #   to the face.

    # Loop over the recognized faces
    # boxes are locations of faces detected by Haar classifier and translated
    # to different format and names are the corresponding names assigned in the
    # previous step
    #
    for ((top, right, bottom, left), pred) in zip(face_locations, preds):

    #   Draw rectangles around the detected faces and display a person's name
        image = cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        image = cv2.putText(image, pred, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 10, (255,0,0), 7)

    image = cv2.resize(image, (1000, 800))
    im = cv2.imshow(pred, image)
    cv2.waitKey(-1)
    cv2.destroyAllWindows()

    # Display the image to the screen
