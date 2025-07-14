import cv2
import mediapipe as mp
import time
import ctypes #To access low-level Windows API functions (used here for simulating key presses).
import pyautogui

# Key mappings for arrow keys
up_scan = 0x48    # Up Arrow
down_scan = 0x50  # Down Arrow
left_scan = 0x4B  # Left Arrow
right_scan = 0x4D # Right Arrow

# Control keys using ctypes
SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class Input_I(ctypes.Union):
    _fields_ = [
        ("ki", KeyBdInput),
    ]

class Input(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("ii", Input_I)
    ]

def KeyOn(scanCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, scanCode, 0x0008, 0, ctypes.pointer(extra))  # Press
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def KeyOff(scanCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, scanCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))  # Release
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Mediapipe setup
mp_draw = mp.solutions.drawing_utils
mp_hand = mp.solutions.hands

tip_ids = [4, 8, 12, 16, 20]  # Finger tip IDs
video = cv2.VideoCapture(1)  # Adjust to the correct camera index

time.sleep(2.0)  # Delay to let the camera initialize

with mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        ret, image = video.read()
        if not ret:
            break

        # Convert to RGB for Mediapipe
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        lm_list = []
        if results.multi_hand_landmarks:
            for idx, hand_landmark in enumerate(results.multi_hand_landmarks):
                for id, lm in enumerate(hand_landmark.landmark):
                    h, w, _ = image.shape
                    lm_list.append([id, int(lm.x * w), int(lm.y * h)])

                # Draw landmarks on the hand
                mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)

        key_pressed = None
        if lm_list:
            fingers = [
                1 if lm_list[tip_ids[0]][1] > lm_list[tip_ids[0] - 1][1] else 0
            ] + [
                1 if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id] - 2][2] else 0
                for id in range(1, 5)
            ]

            total_fingers = fingers.count(1)

            # Debug print for total fingers detected
            print(f"Total fingers: {total_fingers}")

            # Map gestures to actions
            if total_fingers == 4:
                print("Gesture detected: Left Arrow")
                key_pressed = left_scan
            elif total_fingers == 5:
                print("Gesture detected: Right Arrow")
                key_pressed = right_scan
            elif total_fingers == 1:
                print("Gesture detected: Up Arrow")
                key_pressed = up_scan
            elif total_fingers == 0:
                print("Gesture detected: Down Arrow")
                key_pressed = down_scan

        # Key press simulation using ctypes or pyautogui
        if key_pressed:
            KeyOn(key_pressed)
            pyautogui.press('up' if key_pressed == up_scan else 'down' if key_pressed == down_scan else 'left' if key_pressed == left_scan else 'right')

        # Release keys
        if key_pressed:
            KeyOff(key_pressed)

        cv2.imshow("Gesture Control", image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

video.release()
cv2.destroyAllWindows()
