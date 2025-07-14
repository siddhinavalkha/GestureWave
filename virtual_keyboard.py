import cv2
import numpy as np
import pyautogui
import pyperclip #Used to read copied text from clipboard.
import time
import webbrowser
from handTracker import HandTracker
from keys import Key

#Web Search
def perform_search():
    """Function to perform a web search based on the last typed text."""
    pyautogui.hotkey("ctrl", "a")  # Select all text
    pyautogui.hotkey("ctrl", "c")  # Copy text
    time.sleep(0.2)
    copied_text = pyperclip.paste()

    if copied_text.strip():  # Check if text is available
        search_url = f"https://www.google.com/search?q={copied_text}"
        webbrowser.open(search_url)

# Main Function
def start_virtual_keyboard():
    # Define keyboard layout dimensions
    key_width, key_height = 90, 90
    start_x, start_y = 50, 200
    row_spacing, column_spacing = 10, 10

    keys = []
    letters = list("QWERTYUIOPASDFGHJKLZXCVBNM")
    numbers = list("1234567890")
    symbols = list("!@#$%^&*()_+-=[]{}|;:',.<>?/")

    current_mode = "letters"
    caps_lock = False
    shift_pressed = False

    # Function to create a new layout based on the current mode
    def create_keys(mode):
        keys.clear()
        if mode == "letters":
            for i, letter in enumerate(letters):
                row = i // 10
                col = i % 10
                x = start_x + col * (key_width + column_spacing)
                y = start_y + (row + 1) * (key_height + row_spacing)
                keys.append(Key(x, y, key_width, key_height, letter))

            # Special keys
            keys.append(Key(start_x, start_y - (key_height + row_spacing), 2 * key_width, key_height, "Shift"))
            keys.append(Key(start_x + 200, start_y - (key_height + row_spacing), 2 * key_width, key_height, "CapsLock"))
            keys.append(Key(start_x + 400, start_y - (key_height + row_spacing), 2 * key_width, key_height, "Switch"))
            keys.append(Key(start_x + 600, start_y - (key_height + row_spacing), 2 * key_width, key_height, "Search"))

            keys.append(Key(start_x, start_y + 4 * (key_height + row_spacing), 2 * key_width, key_height, "Space"))
            keys.append(Key(start_x + 250, start_y + 4 * (key_height + row_spacing), 2 * key_width, key_height, "<--"))
            keys.append(Key(start_x + 500, start_y + 4 * (key_height + row_spacing), 2 * key_width, key_height, "Enter"))
            keys.append(Key(start_x + 750, start_y + 4 * (key_height + row_spacing), key_width, key_height, "clr"))

    # Initialize webcam and hand tracker
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        return

    tracker = HandTracker(detectionCon=0.8)
    prev_click_time = time.time()
    click_delay = 0.5

    create_keys(current_mode)
    #main loop
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Warning: Empty frame received.")
            break

        frame = cv2.resize(frame, (1280, 720))
        frame = cv2.flip(frame, 1)

        frame = tracker.findHands(frame)
        lmList = tracker.getPosition(frame, draw=False)

        #gesture detection
        clicked_key = None
        if lmList:
            index_tip = lmList[8][1], lmList[8][2]
            thumb_tip = lmList[4][1], lmList[4][2]
            distance = np.linalg.norm(np.array(index_tip) - np.array(thumb_tip))

            if distance < 50 and time.time() - prev_click_time > click_delay:
                for key in keys:
                    if key.isOver(*index_tip):
                        clicked_key = key.text
                        prev_click_time = time.time()
                        break

        for key in keys:
            key.drawKey(frame, (173, 216, 230), (0, 0, 139), alpha=0.7)

        if clicked_key:
            if clicked_key == "<--":
                pyautogui.press('backspace')
            elif clicked_key == "clr":
                pyautogui.hotkey("ctrl", "a")
                pyautogui.press("backspace")
            elif clicked_key == "Space":
                pyautogui.write(" ")
            elif clicked_key == "Enter":
                pyautogui.press("enter")
            elif clicked_key == "Shift":
                shift_pressed = not shift_pressed
            elif clicked_key == "CapsLock":
                caps_lock = not caps_lock
            elif clicked_key == "Switch":
                current_mode = "numbers" if current_mode == "letters" else "symbols" if current_mode == "numbers" else "letters"
                create_keys(current_mode)
            elif clicked_key == "Search":
                perform_search()
            else:
                pyautogui.write(clicked_key.upper() if shift_pressed or caps_lock else clicked_key.lower())
                shift_pressed = False

        #Show Frame & Exit
        cv2.imshow("Virtual Keyboard", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #Cleanup
    cap.release()
    cv2.destroyAllWindows()

#Run Script
if __name__ == "__main__" :
    start_virtual_keyboard()
