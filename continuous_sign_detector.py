"""
Continuous Sign Detection - Detects multiple signs in a single video
This processes a video in chunks and returns all detected signs in sequence
"""

import os
import sys
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.similarity_engine import SimilarityEngine, extract_and_normalize

def detect_signs_in_chunks(video_path, chunk_duration=2.0, threshold=0.40):
    """
    Process video in chunks and detect signs in each chunk.
    
    Args:
        video_path: Path to video file
        chunk_duration: Duration of each chunk in seconds (default 2.0s)
        threshold: Cosine distance threshold for matching
    
    Returns:
        List of (timestamp, word, confidence) tuples
    """
    if not os.path.exists(video_path):
        print(f"ERROR: Video not found: {video_path}")
        return []
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {video_path}")
        return []
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    
    print(f"\nVideo: {os.path.basename(video_path)}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  FPS: {fps}")
    print(f"  Total frames: {total_frames}")
    print(f"  Chunk duration: {chunk_duration}s")
    
    # Load engine
    templates_dir = os.path.join(os.path.dirname(__file__), 'Sign_Templates')
    engine = SimilarityEngine(templates_dir)
    
    if engine.get_template_count() == 0:
        print("ERROR: No templates loaded")
        return []
    
    # Initialize MediaPipe holistic model
    import mediapipe as mp
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Process video in chunks
    chunk_frames = int(fps * chunk_duration)
    frame_count = 0
    chunk_num = 0
    
    detected_signs = []
    last_sign = None
    
    print(f"\n{'='*70}")
    print("PROCESSING VIDEO IN CHUNKS")
    print(f"{'='*70}\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Process every Nth frame to save time (every 3rd frame)
        if frame_count % 3 != 0:
            continue
        
        # Get landmarks for this frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(rgb)
        
        landmarks = extract_and_normalize(results)
        
        # Check if hands visible
        if not np.any(landmarks[132:]):
            continue
        
        # Match against templates
        word, dist, all_probs = engine.match_landmarks(landmarks, threshold=threshold, bidirectional=True)
        
        if word and dist < threshold:
            confidence = 1.0 - dist
            timestamp = frame_count / fps
            
            # Only add if different from last sign (avoid duplicates)
            if word != last_sign:
                detected_signs.append({
                    'timestamp': timestamp,
                    'word': word,
                    'confidence': confidence,
                    'chunk': chunk_num
                })
                last_sign = word
                print(f"  [{timestamp:.2f}s] Detected: {word} (conf: {confidence:.2%})")
        
        # Reset last_sign every chunk to allow re-detection
        if frame_count % (3 * chunk_frames) == 0:
            chunk_num += 1
            last_sign = None  # Reset to allow same sign detection in new chunk
    
    cap.release()
    holistic.close()
    engine.close()
    
    print(f"\n{'='*70}")
    print(f"DETECTION COMPLETE")
    print(f"{'='*70}")
    print(f"Total signs detected: {len(detected_signs)}")
    
    return detected_signs


def process_video_sequence(video_path, chunk_duration=2.0, threshold=0.40):
    """
    Alternative: Process video and group consecutive similar signs
    
    Returns a list of sign sequences with timestamps
    """
    signs = detect_signs_in_chunks(video_path, chunk_duration, threshold)
    
    if not signs:
        return []
    
    # Group consecutive similar signs
    grouped = []
    current_group = None
    
    for sign in signs:
        if current_group is None or sign['word'] != current_group['word']:
            # Start new group
            if current_group:
                grouped.append(current_group)
            current_group = {
                'word': sign['word'],
                'start': sign['timestamp'],
                'end': sign['timestamp'],
                'confidence': sign['confidence'],
                'count': 1
            }
        else:
            # Continue group
            current_group['end'] = sign['timestamp']
            current_group['count'] += 1
            # Update confidence (running average)
            current_group['confidence'] = (
                current_group['confidence'] * (current_group['count'] - 1) + 
                sign['confidence']
            ) / current_group['count']
    
    if current_group:
        grouped.append(current_group)
    
    return grouped


if __name__ == '__main__':
    # Test with a sample video
    test_video = input("Enter video path (or press Enter for default test): ").strip()
    
    if not test_video:
        test_video = r"C:\Users\rohit\Downloads\Sample Videos\cry.mp4"
    
    if os.path.exists(test_video):
        print(f"\nTesting continuous sign detection on: {test_video}")
        signs = process_video_sequence(test_video, chunk_duration=2.0, threshold=0.40)
        
        print(f"\n{'='*70}")
        print("DETECTED SIGNS SEQUENCE:")
        print(f"{'='*70}")
        
        if signs:
            for i, sign in enumerate(signs, 1):
                print(f"{i}. {sign['word']}")
                print(f"   Time: {sign['start']:.2f}s - {sign['end']:.2f}s")
                print(f"   Confidence: {sign['confidence']:.2%}")
                print(f"   Duration: {sign['end'] - sign['start']:.2f}s")
        else:
            print("No signs detected!")
    else:
        print(f"Video not found: {test_video}")
