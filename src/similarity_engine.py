"""
Similarity Engine for ISL Recognition
Uses MediaPipe Holistic to extract 258 landmarks, normalizes them,
and compares against saved .npy templates using cosine distance.

Based on the approach provided by the teammate.
"""

import cv2
import numpy as np
import mediapipe as mp
import os
from scipy.spatial.distance import cosine

# --- MediaPipe Setup ---
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


def flip_horizontal(landmarks):
    """
    Flip landmarks horizontally to handle left/right hand mirroring.
    This allows matching left-hand performance against right-hand templates and vice versa.
    
    Args:
        landmarks: 258-element array (pose:132, lh:63, rh:63)
    
    Returns:
        Flipped landmarks array
    """
    flipped = landmarks.copy()
    
    # Flip pose landmarks (x-coordinate negation)
    # Pose has 33 landmarks with 4 values each (x, y, z, visibility)
    pose = flipped[:132].reshape(33, 4)
    pose[:, 0] = -pose[:, 0]  # Flip x-coordinate
    flipped[:132] = pose.flatten()
    
    # Extract left and right hands
    lh = flipped[132:195].reshape(21, 3).copy()
    rh = flipped[195:258].reshape(21, 3).copy()
    
    # Swap and flip x-coordinates
    rh[:, 0] = -rh[:, 0]  # Flip x of right hand
    lh[:, 0] = -lh[:, 0]  # Flip x of left hand
    
    # Swap: right hand goes to left position, left hand goes to right position
    flipped[132:195] = rh.flatten()  # Right hand to left
    flipped[195:258] = lh.flatten()  # Left hand to right
    
    return flipped


def mask_inactive_hands(landmarks, template):
    """
    Zero out hand portions that are not active in the template.
    This prevents mismatches when one video has both hands and template only has one.
    
    Args:
        landmarks: Test video landmarks (258,)
        template: Template landmarks (258,)
    
    Returns:
        Masked landmarks array with same shape as input
    """
    masked = landmarks.copy()
    
    # Check which hands are active in template
    lh_active_in_template = np.any(template[132:195])  # Left hand
    rh_active_in_template = np.any(template[195:258])  # Right hand
    
    # If left hand not in template, zero it out
    if not lh_active_in_template:
        masked[132:195] = 0
    
    # If right hand not in template, zero it out
    if not rh_active_in_template:
        masked[195:258] = 0
    
    return masked


def extract_and_normalize(results):
    """
    Extracts 258 landmark points (pose=132, left_hand=63, right_hand=63)
    and normalizes them relative to body reference points.

    Pose: 33 landmarks × 4 values (x, y, z, visibility) = 132
    Left Hand: 21 landmarks × 3 values (x, y, z) = 63
    Right Hand: 21 landmarks × 3 values (x, y, z) = 63
    Total: 258 values
    """
    # Extract raw landmarks
    pose = np.array([[res.x, res.y, res.z, res.visibility]
                     for res in results.pose_landmarks.landmark]).flatten() \
        if results.pose_landmarks else np.zeros(132)

    lh = np.array([[res.x, res.y, res.z]
                   for res in results.left_hand_landmarks.landmark]).flatten() \
        if results.left_hand_landmarks else np.zeros(63)

    rh = np.array([[res.x, res.y, res.z]
                   for res in results.right_hand_landmarks.landmark]).flatten() \
        if results.right_hand_landmarks else np.zeros(63)

    landmarks = np.concatenate([pose, lh, rh])

    # If no landmarks detected at all, return zeros
    if not np.any(landmarks):
        return landmarks

    # Normalize pose relative to nose
    pose_part = landmarks[:132]
    if np.any(pose_part):
        pose_reshaped = pose_part.reshape(33, 4)
        nose = pose_reshaped[0, :3].copy()
        pose_reshaped[:, :3] -= nose
        max_val = np.max(np.abs(pose_reshaped[:, :3]))
        if max_val > 0:
            pose_reshaped[:, :3] /= max_val
        landmarks[:132] = pose_reshaped.flatten()

    # Normalize left hand relative to wrist
    lh_part = landmarks[132:195]
    if np.any(lh_part):
        lh_reshaped = lh_part.reshape(21, 3)
        wrist = lh_reshaped[0].copy()
        lh_reshaped -= wrist
        max_val = np.max(np.abs(lh_reshaped))
        if max_val > 0:
            lh_reshaped /= max_val
        landmarks[132:195] = lh_reshaped.flatten()

    # Normalize right hand relative to wrist
    rh_part = landmarks[195:]
    if np.any(rh_part):
        rh_reshaped = rh_part.reshape(21, 3)
        wrist = rh_reshaped[0].copy()
        rh_reshaped -= wrist
        max_val = np.max(np.abs(rh_reshaped))
        if max_val > 0:
            rh_reshaped /= max_val
        landmarks[195:] = rh_reshaped.flatten()

    return landmarks


class SimilarityEngine:
    """
    Sign Language Recognition Engine using cosine similarity.

    Loads .npy template files from a directory and compares live/video
    landmarks against them to find the best matching sign.
    """

    def __init__(self, templates_dir):
        """
        Args:
            templates_dir: Path to directory containing .npy template files.
            Each file should be named <word>.npy and contain
            a 258-element normalized landmark array.
        """
        self.templates_dir = templates_dir
        self.templates = {}
        self.holistic = None
        self.load_templates()

    def load_templates(self):
        """Load all .npy template files from the templates directory."""
        self.templates = {}
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            print(f"Created templates directory: {self.templates_dir}")
            return

        for file in os.listdir(self.templates_dir):
            if file.endswith(".npy"):
                word = file.replace(".npy", "")
                try:
                    self.templates[word] = np.load(os.path.join(self.templates_dir, file))
                    print(f" Loaded template: {word}")
                except Exception as e:
                    print(f" Error loading template {file}: {e}")

        print(f"Total templates loaded: {len(self.templates)}")

    def reload_templates(self):
        """Reload templates from disk (call after adding new templates)."""
        self.load_templates()

    def get_template_count(self):
        """Return number of loaded templates."""
        return len(self.templates)

    def get_template_names(self):
        """Return list of template word names."""
        return sorted(self.templates.keys())

    def _get_holistic(self):
        """Lazy-initialize MediaPipe Holistic model."""
        if self.holistic is None:
            self.holistic = mp_holistic.Holistic(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        return self.holistic

    def match_landmarks(self, landmarks, threshold=0.15, bidirectional=True):
        """
        Match a normalized 258-element landmark array against all templates.
        Supports bidirectional matching (left/right hand agnostic).

        Args:
            landmarks: numpy array of shape (258,) — normalized landmarks
            threshold: cosine distance threshold (lower = stricter match)
            bidirectional: If True, also test flipped version for left/right hand matching

        Returns:
            (best_word, distance, all_distances) or (None, None, {}) if no match
        """
        if not self.templates:
            return None, None, {}

        # Check if hands are visible (landmarks[132:] has hand data)
        if not np.any(landmarks[132:]):
            return None, None, {}

        all_distances = {}
        best_match = None
        lowest_distance = float('inf')

        # Test original landmarks
        for word, template_coords in self.templates.items():
            # Mask out hands that aren't in template to avoid mismatches
            masked_landmarks = mask_inactive_hands(landmarks, template_coords)
            
            dist = cosine(masked_landmarks, template_coords)
            
            # If bidirectional, also test flipped version
            if bidirectional:
                flipped = flip_horizontal(masked_landmarks)
                dist_flipped = cosine(flipped, template_coords)
                dist = min(dist, dist_flipped)  # Use best of both
            
            all_distances[word] = round(float(dist), 4)
            if dist < lowest_distance:
                lowest_distance = dist
                best_match = word

        if lowest_distance < threshold:
            return best_match, lowest_distance, all_distances
        else:
            return None, lowest_distance, all_distances

    def process_frame(self, frame_bgr):
        """
        Process a single BGR frame through MediaPipe and return normalized landmarks.

        Args:
            frame_bgr: OpenCV BGR image

        Returns:
            (landmarks_258, hands_visible) tuple
        """
        holistic = self._get_holistic()
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = holistic.process(rgb)
        landmarks = extract_and_normalize(results)
        hands_visible = bool(np.any(landmarks[132:]))
        return landmarks, hands_visible

    def process_video(self, video_path, threshold=0.15, sample_rate=3, bidirectional=True):
        """
        Process an entire video file. Samples frames and finds the best
        overall match by taking the frame with the lowest cosine distance.

        Args:
            video_path: Path to the video file
            threshold: Cosine distance threshold for a valid match
            sample_rate: Process every Nth frame (3 = every 3rd frame)
            bidirectional: If True, test both normal and flipped versions

        Returns:
            (predicted_word, confidence, all_probabilities) tuple
            confidence is computed as (1 - cosine_distance) to match the
            old Flask UI's expectation of a 0-1 confidence value.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        # Use a fresh holistic instance per video to avoid state leakage
        holistic = mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        best_word = None
        best_distance = float('inf')
        best_all_distances = {}
        frame_count = 0
        frames_with_hands = 0

        try:
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
                hands_visible = bool(np.any(landmarks[132:]))

                if not hands_visible:
                    continue

                frames_with_hands += 1

                word, dist, all_dists = self.match_landmarks(landmarks, threshold=1.0, bidirectional=bidirectional)
                # We use threshold=1.0 here so we always get a result per frame,
                # then we pick the best across all frames.

                if word and dist < best_distance:
                    best_distance = dist
                    best_word = word
                    best_all_distances = all_dists
        finally:
            cap.release()
            holistic.close()

        # If no hands were detected in any frame
        if frames_with_hands == 0 or best_word is None:
            return "Unknown", 0.0, {}

        # Convert distances to "probabilities" (1 - distance)
        # so the UI can display them as confidence percentages
        all_probabilities = {}
        for w, d in best_all_distances.items():
            all_probabilities[w] = round(max(0, 1.0 - d), 4)

        confidence = round(max(0, 1.0 - best_distance), 4)

        # Apply threshold check on the best result
        if best_distance >= threshold:
            return "Unknown", confidence, all_probabilities

        return best_word, confidence, all_probabilities

    def close(self):
        """Release MediaPipe resources."""
        if self.holistic:
            self.holistic.close()
            self.holistic = None
