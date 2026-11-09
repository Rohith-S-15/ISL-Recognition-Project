"""
Helper functions to integrate the Similarity Engine with Flask routes.
Replaces the old PyTorch/LSTM inference with cosine-distance matching.
"""

import sys
import os
import time
from pathlib import Path

# Add parent directory to path so we can import src.similarity_engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.config import Config


class InferenceManager:
    """Manages inference on videos using the Similarity Engine."""
    
    def __init__(self):
        self.engine = None
        self.load_engine()
    
    def load_engine(self):
        """Load the Similarity Engine with templates."""
        try:
            from src.similarity_engine import SimilarityEngine
            
            templates_dir = Config.SIGN_TEMPLATES_DIR
            print(f"Loading Similarity Engine from: {templates_dir}")
            
            self.engine = SimilarityEngine(templates_dir)
            
            count = self.engine.get_template_count()
            names = self.engine.get_template_names()
            print(f"Similarity Engine loaded: {count} templates")
            if names:
                print(f" Available signs: {', '.join(names)}")
            else:
                print(" WARNING: No templates found! Use record_templates.py to create some.")
            
            return True
            
        except Exception as e:
            print(f"Error loading Similarity Engine: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_video(self, video_path, mode='continuous'):
        """
        Process a single video and return results.
        
        Args:
            video_path: Path to video file
            mode: 'single' for single sign detection, 'continuous' for multi-sign detection (default)
        
        Returns: (words, sentence, processing_time, detailed_results)
        Matches the return signature expected by all Flask routes.
        """
        if self.engine is None:
            print("ERROR: Similarity Engine not initialized")
            return None, None, None, None
        
        # Check if video file exists
        if not os.path.exists(video_path):
            print(f"ERROR: Video file not found: {video_path}")
            return None, None, None, None
        
        # Reload templates in case new ones were added
        self.engine.reload_templates()
        
        if self.engine.get_template_count() == 0:
            print("ERROR: No templates loaded. Please record some templates first.")
            return None, None, None, None
        
        try:
            print(f"\nProcessing video: {os.path.basename(video_path)}")
            print(f"Available templates: {self.engine.get_template_count()}")
            print(f"Mode: {mode}")
            
            start_time = time.time()
            
            if mode == 'continuous':
                # Continuous sign detection - detect multiple signs in sequence
                words, sentence, all_probs = self._process_continuous(video_path)
                confidence = 0.0  # Not used in continuous mode
            else:
                # Single sign detection - detect one sign (original behavior)
                # Use threshold=0.40 to accommodate differences between template recording
                # conditions and test video conditions (different camera distance, lighting, hand size)
                # This allows the system to return the "best available match" even if not perfect
                word, confidence, all_probs = self.engine.process_video(video_path, threshold=0.40)
                words = [word] if word else []
                sentence = word if word else "Unknown"
            
            processing_time = time.time() - start_time
            
            print(f"Result: {sentence}")
            if mode == 'continuous':
                print(f"Signs detected: {len(words)}")
            else:
                print(f"Confidence: {confidence:.4f}")
            print(f"Time: {processing_time:.2f}s")
            
            # Detailed results
            detailed_results = {
                'predicted_word': sentence,
                'words': words,
                'mode': mode,
                'confidence': round(confidence, 4) if mode != 'continuous' else None,
                'model_version': 'Similarity (Cosine Distance with Bidirectional Matching)',
                'templates_count': self.engine.get_template_count(),
                'all_probabilities': {w: round(p, 4) for w, p in 
                                    sorted(all_probs.items(), key=lambda x: x[1], reverse=True)}
            }
            
            return words, sentence, processing_time, detailed_results
            
        except Exception as e:
            print(f"ERROR processing video: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None, None
    
    def _process_continuous(self, video_path):
        """
        Process video for continuous sign detection.
        Detects multiple signs in sequence by analyzing video in chunks.
        
        Returns: (words_list, sentence, all_probs)
        """
        import cv2
        import numpy as np
        import mediapipe as mp
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return [], "Unknown", {}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            fps = 30  # Default fallback
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Initialize MediaPipe
        mp_holistic = mp.solutions.holistic
        holistic = mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Process every frame for better detection
        # But sample every 5th frame to avoid too many detections
        frame_count = 0
        sample_rate = max(1, int(fps / 5))  # Sample 5 times per second
        
        detected_signs = []
        last_sign = None
        last_sign_time = 0
        min_sign_duration = 1.5  # Minimum time between sign changes
        
        # Threshold for sign detection
        threshold = 0.40
        
        print(f"\nProcessing {total_frames} frames at {fps:.1f} FPS")
        print(f"Sampling every {sample_rate} frames")
        print(f"{'='*70}\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Sample frames
            if frame_count % sample_rate != 0:
                continue
            
            # Get landmarks
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(rgb)
            landmarks = extract_and_normalize(results)
            
            # Check if hands visible
            if not np.any(landmarks[132:]):
                continue
            
            # Match against templates
            word, dist, all_dists = self.engine.match_landmarks(landmarks, threshold=threshold, bidirectional=True)
            
            timestamp = frame_count / fps
            
            if word and dist < threshold:
                confidence = 1.0 - dist
                
                # Only add if different from last sign and enough time passed
                if word != last_sign or (timestamp - last_sign_time) > min_sign_duration:
                    detected_signs.append({
                        'word': word,
                        'timestamp': timestamp,
                        'confidence': confidence,
                        'dist': dist,
                        'distances': all_dists
                    })
                    last_sign = word
                    last_sign_time = timestamp
                    print(f"  [{timestamp:6.2f}s] Detected: {word:15s} (dist: {dist:.4f}, conf: {confidence:.2%})")
        
        cap.release()
        holistic.close()
        
        print(f"\n{'='*70}")
        print(f"Raw detections: {len(detected_signs)}")
        
        # Group consecutive similar signs
        if len(detected_signs) == 0:
            return [], "Unknown", {}
        
        grouped = []
        current_group = [detected_signs[0]]
        
        for i in range(1, len(detected_signs)):
            sign = detected_signs[i]
            prev_sign = detected_signs[i-1]
            
            # If same word or very close in time, group together
            if sign['word'] == prev_sign['word'] or (sign['timestamp'] - prev_sign['timestamp']) < 2.0:
                current_group.append(sign)
            else:
                # Find best (lowest distance) in current group
                if current_group:
                    best = min(current_group, key=lambda x: x['dist'])
                    grouped.append(best)
                current_group = [sign]
        
        # Don't forget last group
        if current_group:
            best = min(current_group, key=lambda x: x['dist'])
            grouped.append(best)
        
        print(f"Grouped detections: {len(grouped)}")
        print(f"\nFinal sequence:")
        for i, sign in enumerate(grouped, 1):
            print(f"  {i}. {sign['word']} at {sign['timestamp']:.2f}s (conf: {sign['confidence']:.2%})")
        
        # Return results
        words = [sign['word'] for sign in grouped]
        sentence = ', '.join(words) if words else "Unknown"
        
        # Combine all probabilities from last detection
        all_probs = {}
        if grouped:
            all_probs = grouped[-1].get('distances', {})
        
        return words, sentence, all_probs


def extract_and_normalize(results):
    """Extract and normalize landmarks from MediaPipe results."""
    from src.similarity_engine import extract_and_normalize
    return extract_and_normalize(results)


# Global inference manager (singleton)
_inference_manager = None

def get_inference_manager():
    """Get or create the inference manager."""
    global _inference_manager
    if _inference_manager is None:
        _inference_manager = InferenceManager()
    return _inference_manager

def process_video(video_path, mode='continuous'):
    """Process a video using the inference manager."""
    manager = get_inference_manager()
    return manager.process_video(video_path, mode=mode)
