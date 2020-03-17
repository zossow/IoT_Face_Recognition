from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--dataset", required=True,
                        help="path to directory with face images")
    parser.add_argument("-f", "--face-encodings", required=True,
                        help="path to output file with face encodings")
    return parser.parse_args()


def get_face_encodings(path_to_images):
    # Initialize data structure that will contain list of names and list of face encodings
    names = []
    face_encodings = []
    
    # Write a loop over the image files (use os.walk, imutils.paths or other function to iterate over image files)
    for image_path in paths.list_images(path_to_images):
        # Read person's name from image file (name of subdirectory or beginning of filename)
        name = image_path.replace("_", os.path.sep).split(os.path.sep)[-2]

        print("processing image {image} for person: {person}".format(image=image_path, person=name))

        # Load image using OpenCV and convert from BGR (OpenCV) to RGB (face_recognition)
        image = cv2.imread(image_path)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Search for face locations in the image using HOG method
        face_locations = face_recognition.face_locations(rgb_image, model="hog")
        print("found {number} faces in the image, should be 1!".format(number=len(face_locations)))

        # Compute the face encoding for the face (make sure each image only contains one)
        # or add all the face encodings existing in the file.
        # Be aware that face_recognition.face_encodings() returns a list!
        encodings = face_recognition.face_encodings(rgb_image, face_locations)

        # Add face encoding and person's name to previously initialized structure
        for encoding in encodings:
            names.append(name)
            face_encodings.append(encoding)

    # In the end, names and face_encodings should look as follows:
    # names = ["adam",           | face_encodings = [array([...]), - encoding from image adam_001.jpg
    #          "adam",           |                  [array([...]), - encoding from image adam_002.jpg
    #          "adam",           |                  [array([...]), - etc.
    #          "adam",           |                  [array([...]),
    #          "adam",           |                  [array([...]),
    #          "roman",          |                  [array([...]), - encoding from image roman_01.jpg
    #          ...               |                  ...
    #
    # Make sure they are the same size!
    return names, face_encodings


if __name__ == "__main__":
    args = parse_args()

    # Get path to the directory containing face images from script arguments
    path_to_images = args.dataset
    # Get path to the output file containing names and face encodings in binary format
    face_encodings_filename = args.face_encodings

    # Get face encodings
    names, face_encodings = get_face_encodings(path_to_images)
    
    data = {"encodings": face_encodings, "names": names}
    # Save all the names and encodings to a binary file
    with open(face_encodings_filename, "wb") as file:
        # Save the dictionary containing all the names and encodings to a binary file
        file.write(pickle.dumps(data))
