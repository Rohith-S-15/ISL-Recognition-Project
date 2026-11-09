# 🤟 ISL Similarity Discovery: Comprehensive Project Report

This document provides a highly detailed breakdown of the Indian Sign Language (ISL) recognition project, transitioning from deep learning to a high-precision, training-free geometric matching system.

---

## 1. Project Vision & Core Logic

**The Idea:** To create a "Zero-Shot" sign language recognition system that performs with 100% mathematical precision by comparing human gestures against a library of pre-recorded "Gold Standards" (Templates).

### The Math (Algorithm Details)

Contrary to traditional Machine Learning (ML) models that use "probability" and "guessing," this system uses **Vector Geometry**:

1. **Extraction:** MediaPipe Holistic (Machine Learning based) converts a 2D video image into 258 3D coordinates $(x, y, z)$.
2. **Normalization:** The system "centers" the body. It subtracts the Nose coordinates from all pose dots and the Wrist coordinates from all hand dots. This ensures that where you stand in the camera doesn't change the numbers.
3. **Cosine Similarity:** We calculate the cosine of the angle between your live hand vector and the saved template vector.
   - **Formula:** $Similarity = \frac{A \cdot B}{\|A\| \|B\|}$
   - **Logic:** If the angle is $0^\circ$, the similarity is $1.0$ (a perfect match). If the "Distance" ($1 - Similarity$) is smaller than our threshold (0.15), the word is recognized.

---

## 2. System Architecture & Component Mapping

The project is built as a modular ecosystem where the "Engine" is independent of the "Interface."

### A. Integrated File Structure (`C:\Projects\ISL_Similarity_App\`)

This is the central location for the entire project.

| Directory / File | Type | Purpose |
| :--- | :--- | :--- |
| `sign_studio.py` | **Standalone App** | Desktop tool for live webcam testing and recording new `.npy` templates. |
| `run_dashboard.py` | **Web Launcher** | Launches the Flask-based local dashboard for video uploads and batch testing. |
| `src/similarity_engine.py`| **Core Engine** | The math library containing the Cosine Distance and normalization logic. Used by BOTH the desktop app and the web app. |
| `Sign_Templates/` | **Database** | Folder containing `.npy` files. Each file represents one sign (e.g., `hello.npy`). |
| `app/` | **Web Backend** | Contains the Flask logic (Blueprints, Config, Routes). |
| `app/templates/` | **Web Frontend** | HTML files for Home, Test, Batch Testing, and Results history. |
| `app/static/` | **UI Styling** | Premium Dark Mode CSS and Main JavaScript for the dashboard. |
| `database/results.db` | **History Log** | SQLite database that stores every video test result for future review. |
| `test_videos/` | **Test Lab** | Folder where you drop videos you want to test in the Batch Testing UI. |

---

## 3. How Everything Works Together (Logic Flow)

### Scenario 1: Recording a New Word

1. User opens `sign_studio.py`.
2. Mediapipe draws a skeleton over the webcam.
3. User poses and clicks **"Record"**.
4. The system captures the **Normalized 258-point array**.
5. It saves the array as `Sign_Templates/<word>.npy`.

### Scenario 2: Testing a Video on the Dashboard

1. User opens `run_dashboard.py` and goes to `localhost:5000/test`.
2. User uploads a video file.
3. The request goes to `app/routes/test_routes.py`.
4. It calls `app/utils/inference_helper.py`, which initializes the `SimilarityEngine`.
5. The Engine loops through the video, finds the best matching template in `Sign_Templates/`, and calculates the **Confidence**.
6. Results are saved to `database/results.db` and displayed on the UI.

---

## 4. Current Progress & Pending Tasks

### ✅ Completed (Done)

- **Core Math:** Cosine distance matching logic is 100% functional.
- **Engine Integration:** The `SimilarityEngine` class is built and shared by all tools.
- **Infrastructure:** Full Flask dashboard with Database, Static Assets, and 5 separate pages.
- **Desktop App:** Teammate's CustomTkinter app is isolated and runs independently.
- **Styling:** Implementation of a Premium Dark-Theme (Glassmorphism) for the web dashboard.

### ⏳ Pending (To Be Done)

1. **Ambidextrous Logic (Critical):**
   - Currently, the math is sensitive to Left vs. Right hand usage.
   - *Plan:* Add a mathematical "Flip" function or allow `hello_L.npy` and `hello_R.npy` to group under one word.
2. **Dataset Ingest Script:**
   - Create `src/dataset_processor.py` to allow you to drag-and-drop your existing video library to generate templates automatically.
3. **Old Model Review:**
   - Review `StoS` project files to ensure all previous UI features (like TTS) are migrated if needed.
4. **Gemini API Integration:**
   - Establish a connection to Gemini to convert detected word sequences into proper English sentences.
5. **Multi-Hand Logic:**
   - Ensure the system handles one-handed vs. two-handed signs gracefully.

---

## 5. Summary Table

| Feature | Location | Status |
| :--- | :--- | :--- |
| Hand Recording | `sign_studio.py` | 🟢 Active |
| Similarity Brain | `src/similarity_engine.py` | 🟢 Active |
| Web UI (Home/Test) | `localhost:5000` | 🟢 Active |
| Batch Testing | `localhost:5000/batch` | 🟢 Active |
| Left/Right Handling| `src/similarity_engine.py` | 🔴 Pending |
| Multi-Video Import | `src/dataset_processor.py` | 🔴 Pending |
| Gemini API | `app/utils/gemini_helper.py`| 🔴 Pending |
