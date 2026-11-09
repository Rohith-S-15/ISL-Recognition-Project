"""
Sign Language Template Recorder
================================
Standalone tool with CustomTkinter GUI to record sign templates.

How it works:
1. Opens webcam and runs MediaPipe Holistic in real time
2. Shows skeleton overlay on the video feed
3. Click "Record New Sign" when your hands are in the gesture position
4. Enter the name of the sign (e.g., "hello", "thank_you")
5. The 258-element normalized landmark array is saved as a .npy file
6. The Flask dashboard automatically picks up new templates

Usage:
    python record_templates.py
"""

import cv2
import numpy as np
import mediapipe as mp
import os
import sys

# Add project root to path so we can import the engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import customtkinter as ctk
    from PIL import Image, ImageTk
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Run: pip install customtkinter pillow")
    sys.exit(1)

from src.similarity_engine import extract_and_normalize
from scipy.spatial.distance import cosine

# --- Configuration ---
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sign_Templates")
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- MediaPipe Setup ---
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


class SignStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ISL Similarity Studio - Template Recorder")
        self.geometry("1100x650")
        self.configure(fg_color="#0f1117")
        
        # Application State
        self.templates = self.load_templates()
        self.translation_mode = False
        self.current_landmarks = np.zeros(258)
        self.hands_visible = False
        
        # --- UI Layout ---
        # Left Panel: Video Feed
        self.video_frame = ctk.CTkFrame(self, width=700, height=550, fg_color="#1a1d27", corner_radius=12)
        self.video_frame.pack(side="left", padx=15, pady=15, fill="both", expand=True)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(expand=True, fill="both")
        
        # Right Panel: Controls
        self.control_frame = ctk.CTkFrame(self, width=350, fg_color="#1e2130", corner_radius=12)
        self.control_frame.pack(side="right", padx=15, pady=15, fill="y")
        
        self.title_label = ctk.CTkLabel(
            self.control_frame, text="🤟 Template Recorder", 
            font=("Inter", 22, "bold"), text_color="#e8eaf0"
        )
        self.title_label.pack(pady=(20, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self.control_frame, text="Record & test sign templates", 
            font=("Inter", 12), text_color="#9ca3b4"
        )
        self.subtitle_label.pack(pady=(0, 20))
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self.control_frame, fg_color="#252838", corner_radius=10)
        self.status_frame.pack(pady=10, fill="x", padx=20)
        
        self.hands_status = ctk.CTkLabel(
            self.status_frame, text="👋 No Hands Detected", 
            font=("Inter", 13), text_color="#ff6b6b"
        )
        self.hands_status.pack(pady=10)
        
        # Result display
        self.result_label = ctk.CTkLabel(
            self.control_frame, text="Ready", 
            font=("Inter", 26, "bold"), text_color="#a29bfe"
        )
        self.result_label.pack(pady=15)
        
        # Buttons
        self.toggle_btn = ctk.CTkButton(
            self.control_frame, text="▶  Start Live Testing", 
            font=("Inter", 14, "bold"), height=48, corner_radius=10,
            fg_color="#667eea", hover_color="#764ba2",
            command=self.toggle_translation
        )
        self.toggle_btn.pack(pady=8, fill="x", padx=20)
        
        self.record_btn = ctk.CTkButton(
            self.control_frame, text="➕  Record New Sign", 
            font=("Inter", 14, "bold"), height=48, corner_radius=10,
            fg_color="#6c5ce7", hover_color="#5a4bd1",
            command=self.record_sign
        )
        self.record_btn.pack(pady=8, fill="x", padx=20)
        
        # Separator
        sep = ctk.CTkFrame(self.control_frame, height=1, fg_color="#333")
        sep.pack(pady=15, fill="x", padx=20)
        
        # Dictionary info
        self.dict_label = ctk.CTkLabel(
            self.control_frame, 
            text=f"📚 {len(self.templates)} template(s) loaded", 
            font=("Inter", 13), text_color="#9ca3b4"
        )
        self.dict_label.pack(pady=5)
        
        # Template list
        if self.templates:
            names = ", ".join(sorted(self.templates.keys()))
            self.names_label = ctk.CTkLabel(
                self.control_frame, 
                text=f"Signs: {names}", 
                font=("Inter", 11), text_color="#6b7280",
                wraplength=280
            )
            self.names_label.pack(pady=(0, 10))
        else:
            self.names_label = ctk.CTkLabel(
                self.control_frame, 
                text="No templates yet. Record your first sign!", 
                font=("Inter", 11), text_color="#f39c12",
                wraplength=280
            )
            self.names_label.pack(pady=(0, 10))
        
        # Threshold slider
        self.thresh_label = ctk.CTkLabel(
            self.control_frame, text="Match Threshold: 0.15", 
            font=("Inter", 12), text_color="#9ca3b4"
        )
        self.thresh_label.pack(pady=(10, 2))
        
        self.threshold_slider = ctk.CTkSlider(
            self.control_frame, from_=0.05, to=0.40, number_of_steps=35,
            command=self.update_threshold,
            progress_color="#6c5ce7", button_color="#a29bfe"
        )
        self.threshold_slider.set(0.15)
        self.threshold_slider.pack(pady=(0, 15), padx=20, fill="x")

        # --- OpenCV Video Setup ---
        self.cap = cv2.VideoCapture(0)
        self.holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.threshold = 0.15
        
        # Start the video loop
        self.update_video()

    def load_templates(self):
        templates = {}
        for file in os.listdir(TEMPLATE_DIR):
            if file.endswith(".npy"):
                word = file.replace(".npy", "")
                templates[word] = np.load(os.path.join(TEMPLATE_DIR, file))
        return templates

    def update_threshold(self, value):
        self.threshold = round(value, 2)
        self.thresh_label.configure(text=f"Match Threshold: {self.threshold}")

    def toggle_translation(self):
        self.translation_mode = not self.translation_mode
        if self.translation_mode:
            self.toggle_btn.configure(
                text="⏸  Stop Live Testing", 
                fg_color="#c0392b", hover_color="#922b21"
            )
        else:
            self.toggle_btn.configure(
                text="▶  Start Live Testing", 
                fg_color="#667eea", hover_color="#764ba2"
            )
            self.result_label.configure(text="Standby", text_color="#9ca3b4")

    def record_sign(self):
        if not self.hands_visible:
            self.result_label.configure(text="Show hands first!", text_color="#ff6b6b")
            return
            
        # Freeze current landmarks before dialog
        frozen_landmarks = self.current_landmarks.copy()
        
        dialog = ctk.CTkInputDialog(text="Enter the name for this sign:", title="Save New Sign Template")
        word_name = dialog.get_input()
        
        if word_name:
            word_name = word_name.strip().lower()
            save_path = os.path.join(TEMPLATE_DIR, f"{word_name}.npy")
            np.save(save_path, frozen_landmarks)
            self.templates = self.load_templates()
            self.dict_label.configure(text=f"📚 {len(self.templates)} template(s) loaded")
            names = ", ".join(sorted(self.templates.keys()))
            self.names_label.configure(text=f"Signs: {names}", text_color="#6b7280")
            self.result_label.configure(text=f"Saved: {word_name}!", text_color="#38ef7d")

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.holistic.process(rgb)
            
            # Draw skeleton
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            if results.left_hand_landmarks:
                mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            if results.right_hand_landmarks:
                mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            self.current_landmarks = extract_and_normalize(results)
            self.hands_visible = bool(np.any(self.current_landmarks[132:]))
            
            # Update hands status
            if self.hands_visible:
                self.hands_status.configure(text="✅ Hands Detected", text_color="#38ef7d")
            else:
                self.hands_status.configure(text="👋 No Hands Detected", text_color="#ff6b6b")

            # Translation Engine
            if self.translation_mode and self.hands_visible and self.templates:
                best_match = None
                lowest_distance = float('inf')
                
                for word, template_coords in self.templates.items():
                    dist = cosine(self.current_landmarks, template_coords)
                    if dist < lowest_distance:
                        lowest_distance = dist
                        best_match = word
                
                if lowest_distance < self.threshold:
                    conf = round((1 - lowest_distance) * 100, 1)
                    self.result_label.configure(
                        text=f"{best_match.upper()} ({conf}%)", 
                        text_color="#38ef7d"
                    )
                else:
                    self.result_label.configure(text="Unknown", text_color="#9ca3b4")
            elif self.translation_mode and not self.hands_visible:
                self.result_label.configure(text="Show Hands", text_color="#ff6b6b")

            # Convert to UI Image
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Loop the video update every 15 milliseconds
        self.after(15, self.update_video)

    def on_closing(self):
        self.cap.release()
        self.destroy()


if __name__ == "__main__":
    app = SignStudioApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
