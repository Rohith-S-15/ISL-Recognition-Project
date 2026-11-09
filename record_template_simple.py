"""
Simple Template Recorder - Record templates one at a time
This ensures each template is recorded cleanly
"""

import os
import cv2
import numpy as np
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.similarity_engine import extract_and_normalize
import mediapipe as mp

mp_holistic = mp.solutions.holistic

def record_template(word_name, duration=5):
    """
    Record a template for the given word.
    Captures video for `duration` seconds and averages the landmarks.
    """
    print(f"\n{'='*70}")
    print(f"Recording template for: '{word_name}'")
    print(f"{'='*70}")
    print(f"\nInstructions:")
    print(f"1. Position your hand in front of the camera")
    print(f"2. Make the sign for '{word_name}'")
    print(f"3. Hold still while recording (3 seconds)")
    print(f"4. Press 'q' to quit early")
    print(f"\nStarting in 3 seconds...")
    
    # Countdown
    for i in range(3, 0, -1):
        print(i)
        cv2.waitKey(1000)
    
    # Open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot open camera")
        return False
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    holistic = mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    print(f"\nRecording... (Press 'q' to stop)")
    
    landmarks_list = []
    start_time = cv2.getTickCount()
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Check time
        current_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        if current_time > duration:
            print(f"\nTime's up!")
            break
        
        # Process frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(rgb)
        landmarks = extract_and_normalize(results)
        
        # Check if hands detected
        if np.any(landmarks[132:]):
            landmarks_list.append(landmarks)
            frame_count += 1
            
            # Draw on frame
            cv2.putText(frame, f"Recording: {current_time:.1f}s", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Frames: {frame_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No hands detected", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show frame
        cv2.imshow('Recording - Press q to stop', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nStopped by user")
            break
    
    cap.release()
    holistic.close()
    cv2.destroyAllWindows()
    
    if len(landmarks_list) == 0:
        print(f"\nERROR: No valid frames recorded!")
        print("Try again with better lighting and hand positioning.")
        return False
    
    # Average the landmarks
    template = np.mean(landmarks_list, axis=0)
    
    # Normalize
    template = template / np.linalg.norm(template)
    
    # Save template
    templates_dir = os.path.join(os.path.dirname(__file__), 'Sign_Templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    filename = f"{word_name}.npy"
    filepath = os.path.join(templates_dir, filename)
    np.save(filepath, template)
    
    print(f"\n{'='*70}")
    print(f"Template saved successfully!")
    print(f"{'='*70}")
    print(f"  Word: {word_name}")
    print(f"  File: {filename}")
    print(f"  Frames recorded: {frame_count}")
    print(f"  Template shape: {template.shape}")
    print(f"  Location: {filepath}")
    print(f"\nYou can now test this template or record another one.")
    
    return True


if __name__ == '__main__':
    print("\n" + "="*70)
    print("SIMPLE TEMPLATE RECORDER")
    print("="*70)
    print("\nThis tool helps you record sign language templates.")
    print("Record one sign at a time.")
    print("Type 'quit' to exit.\n")
    
    while True:
        word = input("Enter the sign name (e.g., 'hello', 'come', 'cry'): ").strip()
        
        if word.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not word:
            print("Please enter a valid name.\n")
            continue
        
        # Record the template
        success = record_template(word)
        
        if success:
            print(f"\nTemplate '{word}' recorded successfully!")
            print("Would you like to record another? (y/n)")
            again = input("> ").strip().lower()
            if again != 'y':
                print("\nGoodbye!")
                break
        else:
            print(f"\nFailed to record template '{word}'.")
            print("Would you like to try again? (y/n)")
            again = input("> ").strip().lower()
            if again != 'y':
                break
