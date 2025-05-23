from pynput.keyboard import Controller
import time

keyboard = Controller()

print("Sắp nhấn W trong 2 giây...")
time.sleep(2)
keyboard.press('w')
print("Đang giữ phím W...")
time.sleep(2)
keyboard.release('w')
print("Đã nhả phím W.")
