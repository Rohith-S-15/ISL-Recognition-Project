"""Test continuous sign detection on uploaded video"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from continuous_sign_detector import process_video_sequence

test_video = r"C:\Projects\New Approach\ISL_Similarity_App\uploads\Test_Video.mp4"

if os.path.exists(test_video):
    print(f"Testing: {test_video}\n")
    signs = process_video_sequence(test_video, chunk_duration=2.0, threshold=0.40)
    
    print("\n" + "="*70)
    print("DETECTED SIGNS SEQUENCE:")
    print("="*70)
    
    if signs:
        for i, sign in enumerate(signs, 1):
            word = sign["word"]
            start = sign["start"]
            end = sign["end"]
            conf = sign["confidence"]
            print(f"{i}. {word}")
            print(f"   Time: {start:.2f}s - {end:.2f}s")
            print(f"   Confidence: {conf:.2%}")
            print()
    else:
        print("No signs detected!")
else:
    print(f"Video not found: {test_video}")
