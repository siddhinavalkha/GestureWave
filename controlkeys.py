import ctypes

# Define the input structures
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),  # Virtual Key code
        ("wScan", ctypes.c_ushort),  # Hardware scan code
        ("dwFlags", ctypes.c_ulong),  # Flags indicating key state
        ("time", ctypes.c_ulong),  # Timestamp for key press
        ("dwExtraInfo", PUL)  # Additional data
    ]

class Input_I(ctypes.Union):
    _fields_ = [
        ("ki", KeyBdInput),  # Keyboard input
    ]

class Input(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),  # Type of input (keyboard)
        ("ii", Input_I)  # Input details (keyboard)
    ]

# Get the input function
SendInput = ctypes.windll.user32.SendInput

# Key scan codes for arrow keys
up_scan = 0x48    # Up Arrow
down_scan = 0x50  # Down Arrow
left_scan = 0x4B  # Left Arrow
right_scan = 0x4D # Right Arrow

def KeyOn(scanCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, scanCode, 0x0008, 0, ctypes.pointer(extra))  # 0x0008 = KEYEVENTF_SCANCODE (press)
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def KeyOff(scanCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, scanCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))  # 0x0002 = KEYEVENTF_KEYUP (release)
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
