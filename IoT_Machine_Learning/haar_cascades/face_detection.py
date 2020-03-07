import cv2

CASC_PATH = "haarcascade_frontalface_default.xml"
IMAGE_PATH = "../images/Patryk_1.jpg"

image = cv2.imread(IMAGE_PATH)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

faceCascade = cv2.CascadeClassifier(CASC_PATH)

while True:

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(20,20),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Face" , image)
    key = cv2.waitKey(0)
    if key == 27:  # The Esc key
        cv2.imwrite("../images/face_detected.jpg", image)
        break

cv2.destroyAllWindows()