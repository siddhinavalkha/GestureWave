import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, detectionCon=0.5, maxHands=1):  # Set maxHands=1 to detect only one hand
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=maxHands,  # Allow only one hand detection
            min_detection_confidence=detectionCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)#Converts the image from BGR (used by OpenCV) to RGB (used by MediaPipe).
        self.results = self.hands.process(imgRGB)
        
        if self.results.multi_hand_landmarks:
            # Draw landmarks for only one hand if detected
            handLms = self.results.multi_hand_landmarks[0]
            self.mpDraw.draw_landmarks(img, handLms, mp.solutions.hands.HAND_CONNECTIONS)
        
        return img

    def getPosition(self, img, draw=True):
        lmList = []
        if self.results and self.results.multi_hand_landmarks:
            # Only consider the first detected hand
            myHand = self.results.multi_hand_landmarks[0]
            for id, lm in enumerate(myHand.landmark):
                h, w = img.shape[:2]
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return lmList
