import cv2

CASC_PATH = "haarcascade_frontalface_default.xml"

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while(True):

    ret, frame = cap.read()

    cascadeClassifier = cv2.CascadeClassifier(CASC_PATH)
    face_locations = cascadeClassifier.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(30,30),
                                                        flags=cv2.CASCADE_SCALE_IMAGE)

    face_locations = [(y,x + w, y + h, x) for x,y,w,h in face_locations]

    for top, right, bottom, left in face_locations:
        image = cv2.rectangle(frame, (left,top), (right, bottom), (0,255,0),2)
        cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()