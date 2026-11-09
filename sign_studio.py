import cv2
import numpy as np
import mediapipe as mp
import os
import customtkinter as ctk
from PIL import Image, ImageTk
from scipy.spatial.distance import cosine

# --- Configuration ---
TEMPLATE_DIR = "Sign_Templates"
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- MediaPipe Setup ---
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

def extract_and_normalize(results):
    """Extracts 258 points and normalizes them."""
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(132)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(63)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(63)
    
    landmarks = np.concatenate([pose, lh, rh])
    
    if not np.any(landmarks): return landmarks
    
    pose_part = landmarks[:132]
    if np.any(pose_part):
        pose_reshaped = pose_part.reshape(33, 4)
        nose = pose_reshaped[0, :3].copy()
        pose_reshaped[:, :3] -= nose
        max_val = np.max(np.abs(pose_reshaped[:, :3]))
        if max_val > 0: pose_reshaped[:, :3] /= max_val
        landmarks[:132] = pose_reshaped.flatten()

    lh_part = landmarks[132:195]
    if np.any(lh_part):
        lh_reshaped = lh_part.reshape(21, 3)
        wrist = lh_reshaped[0].copy()
        lh_reshaped -= wrist
        max_val = np.max(np.abs(lh_reshaped))
        if max_val > 0: lh_reshaped /= max_val
        landmarks[132:195] = lh_reshaped.flatten()

    rh_part = landmarks[195:]
    if np.any(rh_part):
        rh_reshaped = rh_part.reshape(21, 3)
        wrist = rh_reshaped[0].copy()
        rh_reshaped -= wrist
        max_val = np.max(np.abs(rh_reshaped))
        if max_val > 0: rh_reshaped /= max_val
        landmarks[195:] = rh_reshaped.flatten()

    return landmarks

class SignStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sign Language Studio - Pro Edition")
        self.geometry("1000x600")
        
        # Application State
        self.templates = self.load_templates()
        self.translation_mode = False
        self.current_landmarks = np.zeros(258)
        self.hands_visible = False
        
        # --- UI Layout ---
        # Left Panel: Video Feed
        self.video_frame = ctk.CTkFrame(self, width=660, height=500)
        self.video_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(expand=True, fill="both")
        
        # Right Panel: Controls
        self.control_frame = ctk.CTkFrame(self, width=300)
        self.control_frame.pack(side="right", padx=20, pady=20, fill="y")
        
        self.title_label = ctk.CTkLabel(self.control_frame, text="Control Panel", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=(20, 30))
        
        self.result_label = ctk.CTkLabel(self.control_frame, text="Waiting...", font=("Arial", 28, "bold"), text_color="#00FF00")
        self.result_label.pack(pady=20)
        
        self.toggle_btn = ctk.CTkButton(self.control_frame, text="▶ Start Translating", font=("Arial", 16), height=50, command=self.toggle_translation)
        self.toggle_btn.pack(pady=10, fill="x", padx=20)
        
        self.record_btn = ctk.CTkButton(self.control_frame, text="➕ Record New Sign", font=("Arial", 16), height=50, fg_color="#E67E22", hover_color="#D35400", command=self.record_sign)
        self.record_btn.pack(pady=10, fill="x", padx=20)
        
        self.dict_label = ctk.CTkLabel(self.control_frame, text=f"Words in Dictionary: {len(self.templates)}", font=("Arial", 14))
        self.dict_label.pack(side="bottom", pady=20)

        # --- OpenCV Video Setup ---
        self.cap = cv2.VideoCapture(0)
        self.holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        # Start the video loop
        self.update_video()

    def load_templates(self):
        templates = {}
        for file in os.listdir(TEMPLATE_DIR):
            if file.endswith(".npy"):
                word = file.replace(".npy", "")
                templates[word] = np.load(os.path.join(TEMPLATE_DIR, file))
        return templates

    def toggle_translation(self):
        self.translation_mode = not self.translation_mode
        if self.translation_mode:
            self.toggle_btn.configure(text="⏸ Stop Translating", fg_color="#C0392B", hover_color="#922B21")
        else:
            self.toggle_btn.configure(text="▶ Start Translating", fg_color="#1F6AA5", hover_color="#144870")
            self.result_label.configure(text="Standby", text_color="#FFFFFF")

    def record_sign(self):
        if not self.hands_visible:
            self.result_label.configure(text="No Hands Detected!", text_color="#E74C3C")
            return
            
        # Freeze current math coordinates before asking for the name
        frozen_landmarks = self.current_landmarks.copy()
        
        dialog = ctk.CTkInputDialog(text="Enter the name for this sign:", title="Save New Sign")
        word_name = dialog.get_input()
        
        if word_name:
            word_name = word_name.strip().lower()
            save_path = os.path.join(TEMPLATE_DIR, f"{word_name}.npy")
            np.save(save_path, frozen_landmarks)
            self.templates = self.load_templates()
            self.dict_label.configure(text=f"Words in Dictionary: {len(self.templates)}")
            self.result_label.configure(text=f"Saved: {word_name}", text_color="#F1C40F")

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.holistic.process(rgb)
            
            # Draw skeleton
            if results.pose_landmarks: mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            if results.left_hand_landmarks: mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            if results.right_hand_landmarks: mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            self.current_landmarks = extract_and_normalize(results)
            self.hands_visible = np.any(self.current_landmarks[132:])

            # Translation Engine
            if self.translation_mode and self.hands_visible and self.templates:
                best_match = None
                lowest_distance = float('inf')
                
                for word, template_coords in self.templates.items():
                    dist = cosine(self.current_landmarks, template_coords)
                    if dist < lowest_distance:
                        lowest_distance = dist
                        best_match = word
                
                if lowest_distance < 0.15:
                    self.result_label.configure(text=best_match.upper(), text_color="#2ECC71")
                else:
                    self.result_label.configure(text="Unknown", text_color="#95A5A6")
            elif self.translation_mode and not self.hands_visible:
                self.result_label.configure(text="Show Hands", text_color="#E74C3C")

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
