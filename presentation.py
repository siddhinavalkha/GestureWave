import cv2
import os
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Variables
width, height = 1280, 720
folderPath = "Presentation"

# Camera setup
cap = cv2.VideoCapture(1)
cap.set(3, width)
cap.set(4, height)

# Get the list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
print(pathImages)

# Variables
imgNumber = 0
hs, ws = int(120 * 1), int(213 * 1)
buttonPresssed = False
buttonCounter = 0
buttonDelay = 30
annotations = [[]]
annotationNumber = 0
annotationStart = False

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    # Import images
    success, img = cap.read()
    img = cv2.flip(img,1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    hands, img = detector.findHands(img)

    if hands and buttonPresssed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand) # Returns a list like [1,0,0,0,1]
        cx, cy = hand['center']
        lmList = hand['lmList']

        # Constrain values for easier drawing
        xVal = int(np.interp(lmList[8][0], [0, width], [0, imgCurrent.shape[1]]))
        yVal = int(np.interp(lmList[8][1], [0, height], [0, imgCurrent.shape[0]]))

        indexFinger = (xVal, yVal)

        # Gesture 1 - left
        if fingers == [1, 0, 0, 0, 0]:
            annotationStart = False
            print("Left")
            if imgNumber > 0:
                buttonPresssed = True
                annotations = [[]]
                annotationNumber = 0
                imgNumber -= 1

            # Gesture 2 - right
        if fingers == [0, 0, 0, 0, 1]:
            annotationStart = False
            print("Right")
            if imgNumber < len(pathImages) - 1:
                buttonPresssed = True
                annotations = [[]]
                annotationNumber = 0
                imgNumber += 1        

        # Gesture 3 - show pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotationStart = False

        # Gesture 4 - draw pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False

        # Gesture 5 - erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNumber >= 0:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPresssed = True

    else:
        annotationStart = False

    # Button pressed iterations
    if buttonPresssed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPresssed = False

    # Draw annotations
    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(imgCurrent, annotations[i][j - 1], annotations[i][j], (0, 0, 200), 12)

    # Adding webcam image on the slides
    imgSmall = cv2.resize(img, (ws, hs))
    if imgCurrent is not None:
        h, w, _ = imgCurrent.shape
        if h >= hs and w >= ws:
            imgCurrent[0:hs, w - ws:w] = imgSmall
        else:
            print("Error: Slide image is too small for webcam overlay.")

    cv2.imshow("Image", img)
    cv2.imshow("Slides", imgCurrent)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()  
