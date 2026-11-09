#!/usr/bin/env python
import subprocess
import time
import sys

print("[MONITOR] Starting Flask app...")
proc = subprocess.Popen(
    [sys.executable, "run_dashboard.py"],
    cwd=r"C:\Projects\New Approach\ISL_Similarity_App",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

print("[MONITOR] Monitoring output...")
line_count = 0
start_time = time.time()

for line in proc.stdout:
    line_count += 1
    elapsed = time.time() - start_time
    print(f"[{elapsed:6.1f}s] {line.rstrip()}")
    
    # Print every 50 lines
    if line_count % 50 == 0:
        print(f"[MONITOR] ===== Line {line_count} =====")
    
    # Check if we see success messages
    if "[OK] MediaPipe Holistic initialized" in line:
        print("[MONITOR] !!! CAMERA THREAD PROGRESS !!!")
    elif "GET /status HTTP/1.1" in line:
        print("[MONITOR] !!! FIRST WEB REQUEST !!!")
    
    # Stop after 60 seconds or 200 lines
    if elapsed > 60 or line_count > 200:
        print(f"[MONITOR] Timeout/limit reached")
        proc.terminate()
        break
