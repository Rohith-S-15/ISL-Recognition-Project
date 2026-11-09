"""
Debug Script for ISL Similarity Engine
Analyzes video frames and template matching to diagnose why videos return "Unknown"
"""

import cv2
import numpy as np
import mediapipe as mp
import os
import sys
from scipy.spatial.distance import cosine

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.similarity_engine import extract_and_normalize, flip_horizontal

mp_holistic = mp.solutions.holistic

def analyze_video(video_path, templates_dir, output_report=True):
    """
    Analyze a video and provide detailed debug information
    
    Args:
        video_path: Path to video file
        templates_dir: Path to templates directory
        output_report: Print detailed report
    """
    print("\n" + "="*70)
    print(f"VIDEO DEBUG ANALYSIS: {os.path.basename(video_path)}")
    print("="*70)
    
    # Load templates
    templates = {}
    if os.path.exists(templates_dir):
        for file in os.listdir(templates_dir):
            if file.endswith(".npy"):
                word = file.replace(".npy", "")
                templates[word] = np.load(os.path.join(templates_dir, file))
    
    print(f"\nTemplates loaded: {len(templates)}")
    if templates:
        print(f"Available words: {', '.join(sorted(templates.keys()))}")
    else:
        print("WARNING: No templates found!")
        return None
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open video file")
        return None
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"\nVideo Properties:")
    print(f"  Total Frames: {total_frames}")
    print(f"  FPS: {fps}")
    print(f"  Duration: {duration:.2f}s")
    
    # Process frames
    holistic = mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    frame_count = 0
    frames_with_hands = 0
    frame_distances = []
    best_distance = float('inf')
    best_word = None
    best_all_distances = {}
    
    print(f"\nProcessing frames...")
    
    sample_rate = 3
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Sample every Nth frame
        if frame_count % sample_rate != 0:
            continue
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(rgb)
        landmarks = extract_and_normalize(results)
        
        # Check if hands visible
        hands_visible = bool(np.any(landmarks[132:]))
        
        if not hands_visible:
            continue
        
        frames_with_hands += 1
        
        # Calculate distances
        all_dists = {}
        frame_best_dist = float('inf')
        frame_best_word = None
        
        for word, template_coords in templates.items():
            dist = cosine(landmarks, template_coords)
            
            # Try flipped version
            flipped = flip_horizontal(landmarks)
            dist_flipped = cosine(flipped, template_coords)
            dist = min(dist, dist_flipped)
            
            all_dists[word] = dist
            if dist < frame_best_dist:
                frame_best_dist = dist
                frame_best_word = word
        
        frame_distances.append((frame_count, frame_best_word, frame_best_dist, all_dists))
        
        if frame_best_dist < best_distance:
            best_distance = frame_best_dist
            best_word = frame_best_word
            best_all_distances = all_dists
    
    cap.release()
    holistic.close()
    
    # Generate report
    print(f"\nAnalysis Results:")
    print(f"  Frames with hand detection: {frames_with_hands}/{frame_count}")
    print(f"  Hand detection rate: {(frames_with_hands/frame_count*100):.1f}%" if frame_count > 0 else "  Hand detection rate: 0%")
    
    if frames_with_hands == 0:
        print("\n  ⚠️  WARNING: No hands detected in any frame!")
        print("      Possible causes:")
        print("      - Camera distance too far")
        print("      - Poor lighting conditions")
        print("      - Hand not clearly visible")
        return None
    
    print(f"\n  Best Match: {best_word} (distance: {best_distance:.4f})")
    print(f"  Threshold: 0.15")
    print(f"  Match Status: {'✓ PASS' if best_distance < 0.15 else '✗ FAIL (Too far from template)'}")
    
    if output_report and frame_distances:
        print(f"\n  Top 5 Best Distances:")
        sorted_frames = sorted(frame_distances, key=lambda x: x[2])[:5]
        for idx, (frame_num, word, dist, _) in enumerate(sorted_frames, 1):
            status = "✓" if dist < 0.15 else "✗"
            print(f"    {idx}. Frame {frame_num}: {word} ({dist:.4f}) {status}")
    
    if best_distance >= 0.15:
        print(f"\n  📊 Distance Analysis (all templates on best frame):")
        sorted_words = sorted(best_all_distances.items(), key=lambda x: x[1])
        for word, dist in sorted_words[:10]:
            threshold_marker = " <- threshold" if dist < 0.15 else ""
            print(f"    {word}: {dist:.4f}{threshold_marker}")
    
    print("\n" + "="*70 + "\n")
    
    return {
        'frames_with_hands': frames_with_hands,
        'total_frames': frame_count,
        'best_word': best_word,
        'best_distance': best_distance,
        'passed_threshold': best_distance < 0.15,
        'all_distances': best_all_distances
    }


if __name__ == '__main__':
    # Configuration
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'Sign_Templates')
    SAMPLE_VIDEOS_DIR = r"C:\Users\rohit\Downloads\Sample Videos"
    
    print("\n🔍 ISL SIMILARITY ENGINE - DEBUG MODE")
    print("Analyzing sample videos...")
    
    # Analyze cry.mp4 and come.mp4
    if os.path.exists(SAMPLE_VIDEOS_DIR):
        test_videos = ['cry.mp4', 'come.mp4']
        
        for video_name in test_videos:
            video_path = os.path.join(SAMPLE_VIDEOS_DIR, video_name)
            if os.path.exists(video_path):
                analyze_video(video_path, TEMPLATES_DIR)
            else:
                print(f"Video not found: {video_path}")
    else:
        print(f"Sample videos folder not found: {SAMPLE_VIDEOS_DIR}")
