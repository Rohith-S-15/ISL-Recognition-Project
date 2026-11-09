"""
Extract Templates from Sample Videos
This script extracts sign language templates from video files.
Use this to create templates that match your test video conditions.
"""

import os
import sys
import cv2
import numpy as np
import mediapipe as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.similarity_engine import extract_and_normalize

mp_holistic = mp.solutions.holistic

def extract_template_from_video(video_path, output_path=None):
    """
    Extract a template from a video by averaging landmarks from middle frames.
    
    Args:
        video_path: Path to the video file
        output_path: Optional path to save the template (.npy file)
    
    Returns:
        Extracted template array or None if extraction fails
    """
    if not os.path.exists(video_path):
        print(f"ERROR: Video not found: {video_path}")
        return None
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {video_path}")
        return None
    
    holistic = mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"\nProcessing: {os.path.basename(video_path)}")
    print(f"  Total frames: {total_frames}, FPS: {fps}")
    
    # Extract landmarks from middle 50% of frames (avoid start/end transitions)
    start_frame = int(total_frames * 0.25)
    end_frame = int(total_frames * 0.75)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    landmarks_list = []
    frames_processed = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        if current_frame > end_frame:
            break
        
        # Process frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(rgb)
        
        # Check if hands detected
        if results.left_hand_landmarks or results.right_hand_landmarks:
            landmarks = extract_and_normalize(results)
            if np.any(landmarks[132:]):  # At least one hand visible
                landmarks_list.append(landmarks)
                frames_processed += 1
        
        # Limit to 30 samples for efficiency
        if len(landmarks_list) >= 30:
            break
    
    cap.release()
    holistic.close()
    
    if len(landmarks_list) == 0:
        print(f"  ERROR: No valid landmarks found")
        return None
    
    # Average the landmarks
    template = np.mean(landmarks_list, axis=0)
    
    # Normalize the template
    template = template / np.linalg.norm(template)
    
    print(f"  Extracted {len(landmarks_list)} frames")
    print(f"  Template shape: {template.shape}")
    
    # Save if output path provided
    if output_path:
        np.save(output_path, template)
        print(f"  Saved to: {output_path}")
    
    return template


def main():
    """Main function to extract templates from sample videos."""
    
    sample_dir = r"C:\Users\rohit\Downloads\Sample Videos"
    templates_dir = os.path.join(os.path.dirname(__file__), 'Sign_Templates')
    
    if not os.path.exists(sample_dir):
        print(f"Sample directory not found: {sample_dir}")
        return
    
    os.makedirs(templates_dir, exist_ok=True)
    
    # Get list of video files
    video_files = [f for f in os.listdir(sample_dir) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    
    if not video_files:
        print(f"No video files found in {sample_dir}")
        return
    
    print(f"\n{'='*70}")
    print("TEMPLATE EXTRACTION FROM SAMPLE VIDEOS")
    print(f"{'='*70}")
    print(f"Source: {sample_dir}")
    print(f"Target: {templates_dir}")
    print(f"Videos found: {len(video_files)}")
    print()
    
    extracted = 0
    skipped = 0
    
    for video_file in video_files:
        video_path = os.path.join(sample_dir, video_file)
        
        # Extract sign name from filename (e.g., "cry.mp4" -> "cry")
        sign_name = os.path.splitext(video_file)[0]
        template_path = os.path.join(templates_dir, f"{sign_name}.npy")
        
        # Skip if template already exists
        if os.path.exists(template_path):
            print(f"\nSkipping {video_file} (template already exists)")
            skipped += 1
            continue
        
        # Extract template
        template = extract_template_from_video(video_path, template_path)
        
        if template is not None:
            extracted += 1
        else:
            print(f"  FAILED to extract template from {video_file}")
    
    print(f"\n{'='*70}")
    print(f"Extraction complete!")
    print(f"  Extracted: {extracted}")
    print(f"  Skipped: {skipped}")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
