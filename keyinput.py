import ctypes
import time

# Sử dụng Virtual Key Codes thay vì scan code để đảm bảo tương thích
VK_CODES = {
    "w": 0x57,  # VK_W
    "a": 0x41,  # VK_A
    "s": 0x53,  # VK_S
    "d": 0x44,  # VK_D
}

# Cấu trúc dữ liệu cho Input
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]

class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort),
    ]

class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]

class Input_I(ctypes.Union):
    _fields_ = [
        ("ki", KeyBdInput),
        ("mi", MouseInput),
        ("hi", HardwareInput),
    ]

class Input(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("ii", Input_I),
    ]

def press_key(key):
    """Nhấn phím ảo"""
    try:
        key_code = VK_CODES[key.lower()]
    except KeyError:
        raise ValueError(f"Không hỗ trợ phím {key}")
    
    extra = ctypes.c_ulong(0)
    ii = Input_I()
    ii.ki = KeyBdInput(key_code, 0, 0, 0, ctypes.pointer(extra))
    x = Input(1, ii)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    time.sleep(0.05)  # Thêm delay ngắn

def release_key(key):
    """Nhả phím ảo"""
    try:
        key_code = VK_CODES[key.lower()]
    except KeyError:
        raise ValueError(f"Không hỗ trợ phím {key}")
    
    extra = ctypes.c_ulong(0)
    ii = Input_I()
    ii.ki = KeyBdInput(key_code, 0, 0x0002, 0, ctypes.pointer(extra))  # KEYEVENTF_KEYUP
    x = Input(1, ii)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    time.sleep(0.05)  # Thêm delay ngắn