import cv2
import threading
import time

print("[TEST] Testing camera with timeout...")

def read_camera():
    print("[THREAD] Starting camera read in thread...")
    cap = cv2.VideoCapture(0)
    print("[THREAD] VideoCapture created")
    ret, frame = cap.read()
    print("[THREAD] Read result: " + str(ret) + ", frame: " + str(type(frame)))
    cap.release()

thread = threading.Thread(target=read_camera, daemon=True)
thread.start()

print("[MAIN] Waiting for thread to complete...")
thread.join(timeout=5)

if thread.is_alive():
    print("[MAIN] ERROR: Thread is still alive after 5 seconds!")
else:
    print("[MAIN] Thread completed")
