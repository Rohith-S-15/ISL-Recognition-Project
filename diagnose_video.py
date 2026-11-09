"""
Diagnostic script to analyze why videos are returning "Unknown"
"""

import os
import cv2
import numpy as np
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.similarity_engine import SimilarityEngine
import mediapipe as mp

mp_holistic = mp.solutions.holistic

def diagnose_video(video_path):
    """Detailed diagnosis of video processing"""
    print(f"\n{'='*70}")
    print(f"DIAGNOSING: {os.path.basename(video_path)}")
    print(f"{'='*70}")
    
    # Check file
    if not os.path.exists(video_path):
        print(f"ERROR: File not found: {video_path}")
        return
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open video")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"\nVideo Properties:")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    print(f"  Total Frames: {total_frames}")
    print(f"  Duration: {total_frames/fps:.2f}s")
    
    # Analyze frames
    print(f"\n{'='*70}")
    print("FRAME ANALYSIS (sampling every 3rd frame)")
    print(f"{'='*70}\n")
    
    holistic = mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    frame_num = 0
    frames_analyzed = 0
    frames_with_pose = 0
    frames_with_left_hand = 0
    frames_with_right_hand = 0
    frames_with_both_hands = 0
    hand_detection_confidences = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_num += 1
        
        # Sample every 3rd frame
        if frame_num % 3 != 0:
            continue
        
        frames_analyzed += 1
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(rgb)
        
        has_pose = results.pose_landmarks is not None
        has_lh = results.left_hand_landmarks is not None
        has_rh = results.right_hand_landmarks is not None
        
        if has_pose:
            frames_with_pose += 1
        if has_lh:
            frames_with_left_hand += 1
            # Get confidence of left hand detection
            if hasattr(results, 'left_hand_landmarks'):
                hand_detection_confidences.append('LH')
        if has_rh:
            frames_with_right_hand += 1
            if hasattr(results, 'right_hand_landmarks'):
                hand_detection_confidences.append('RH')
        
        if has_lh and has_rh:
            frames_with_both_hands += 1
        
        # Print first 10 frames
        if frames_analyzed <= 10:
            status = ""
            if has_pose:
                status += "POSE "
            if has_lh:
                status += "LEFT_HAND "
            if has_rh:
                status += "RIGHT_HAND "
            if not status:
                status = "NOTHING"
            
            print(f"Frame {frame_num:4d}: {status}")
    
    cap.release()
    holistic.close()
    
    print(f"\n{'='*70}")
    print("DETECTION SUMMARY")
    print(f"{'='*70}")
    print(f"Frames analyzed: {frames_analyzed}")
    print(f"Frames with pose: {frames_with_pose} ({100*frames_with_pose/frames_analyzed:.1f}%)")
    print(f"Frames with left hand: {frames_with_left_hand} ({100*frames_with_left_hand/frames_analyzed:.1f}%)")
    print(f"Frames with right hand: {frames_with_right_hand} ({100*frames_with_right_hand/frames_analyzed:.1f}%)")
    print(f"Frames with BOTH hands: {frames_with_both_hands} ({100*frames_with_both_hands/frames_analyzed:.1f}%)")
    
    if frames_with_both_hands < frames_analyzed * 0.3:
        print(f"\n[ISSUE] Hand detection is poor! Only {100*frames_with_both_hands/frames_analyzed:.1f}% of frames have both hands.")
        print("  Try: Recording templates closer to camera, better lighting, or increasing min_detection_confidence")
    
    # Now test with engine
    print(f"\n{'='*70}")
    print("ENGINE ANALYSIS")
    print(f"{'='*70}\n")
    
    templates_dir = os.path.join(os.path.dirname(__file__), 'Sign_Templates')
    engine = SimilarityEngine(templates_dir)
    
    print(f"Templates loaded: {engine.get_template_count()}")
    print(f"Available: {engine.get_template_names()}")
    
    word, confidence, all_probs = engine.process_video(video_path)
    
    print(f"\n{'='*70}")
    print("ENGINE RESULT")
    print(f"{'='*70}")
    print(f"Recognized: {word}")
    print(f"Confidence: {confidence:.4f} ({confidence*100:.2f}%)")
    print(f"\nAll distances (lower = better match):")
    
    distances = {w: 1.0 - p for w, p in all_probs.items()}
    for w in sorted(distances.keys(), key=lambda x: distances[x]):
        d = distances[w]
        p = all_probs[w]
        threshold_mark = " [ABOVE THRESHOLD]" if d >= 0.15 else " [VALID]"
        print(f"  {w:12s}: distance={d:.4f}, prob={p:.4f}{threshold_mark}")
    
    print(f"\nThreshold: 0.15")
    print(f"Result: {'UNKNOWN (all distances > 0.15)' if word == 'Unknown' else 'RECOGNIZED'}")

if __name__ == '__main__':
    # Test both videos
    test_dir = r"C:\Users\rohit\Downloads\Sample Videos"
    
    for video_file in ['cry.mp4', 'come.mp4']:
        video_path = os.path.join(test_dir, video_file)
        if os.path.exists(video_path):
            diagnose_video(video_path)
        else:
            print(f"Video not found: {video_path}")
