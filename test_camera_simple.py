import cv2
import time

print("[TEST] Starting camera test...")

# Test 1: Check available cameras
for i in range(5):
    print(f"[TEST] Trying camera {i}...")
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"[TEST] Camera {i} WORKS! Frame shape: {frame.shape}")
            cap.release()
            break
        else:
            print(f"[TEST] Camera {i} opened but cant read frames")
            cap.release()
    else:
        print(f"[TEST] Camera {i} not available")

print("[TEST] Done")
