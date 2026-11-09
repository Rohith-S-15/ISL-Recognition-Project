# 🤟 ISL Similarity Studio — Indian Sign Language Recognition System

> **Real-time Indian Sign Language (ISL) recognition using MediaPipe Holistic and Cosine Similarity, with AI-powered sentence formation and bilingual (English/Hindi) audio output.**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Installation & Setup](#installation--setup)
6. [How to Run](#how-to-run)
7. [How It Works](#how-it-works)
8. [Supported Signs](#supported-signs)
9. [File Structure](#file-structure)
10. [Adding New Signs](#adding-new-signs)
11. [API Keys Configuration](#api-keys-configuration)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

This project implements a **real-time Indian Sign Language (ISL) recognition system** that:

1. **Captures** live webcam video and processes it with MediaPipe Holistic
2. **Extracts** 258-dimensional body + hand landmark vectors
3. **Matches** gestures against pre-recorded sign templates using cosine similarity
4. **Forms sentences** from detected sign words using AI (OpenRouter / Gemini)
5. **Translates** sentences to Hindi (Devanagari script)
6. **Speaks** both English and Hindi audio output using gTTS

The system uses a **template-matching** approach — no deep learning training required. You simply record a reference pose for each sign, and the system matches live gestures against those references in real time.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎥 **Live Webcam Detection** | Real-time sign detection via webcam |
| 🦴 **Colored Skeleton Overlay** | Purple body, green left hand, red right hand |
| 🎯 **11 Pre-recorded Signs** | break, come, cry, good, hello, morning, one, stop, thankyou, three, two |
| ⏱️ **10-Second Auto-Sentence** | Automatically forms sentences after 10s of no hand detection |
| 🤖 **AI Sentence Formation** | Uses OpenRouter (free) or Gemini to create grammatically correct sentences |
| 🇮🇳 **Hindi Translation** | Devanagari script translation with built-in dictionary fallback |
| 🔊 **Bilingual Audio** | English and Hindi text-to-speech using gTTS |
| ➕ **Template Recorder** | GUI tool to record new sign templates |
| 📊 **Web Dashboard** | Modern dark-themed Flask web interface |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser (UI)                       │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  │
│  │ Video   │  │ Detected │  │ AI      │  │ Audio    │  │
│  │ Feed    │  │ Words    │  │ Sentence│  │ Buttons  │  │
│  └────┬────┘  └────┬─────┘  └────┬────┘  └────┬─────┘  │
└───────┼────────────┼────────────┼────────────┼──────────┘
        │            │            │            │
┌───────┼────────────┼────────────┼────────────┼──────────┐
│       ▼            ▼            ▼            ▼          │
│              Flask Server (Python)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Camera Thread (Background)                       │   │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────┐  │   │
│  │  │ OpenCV   │→ │ MediaPipe │→ │ Cosine       │  │   │
│  │  │ Capture  │  │ Holistic  │  │ Matching     │  │   │
│  │  └──────────┘  └───────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  AI Pipeline                                      │   │
│  │  OpenRouter (free) → Gemini (fallback) → Dict     │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Audio Pipeline                                   │   │
│  │  gTTS Hindi → gTTS English (fallback)             │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
        │
┌───────┴──────────────────────────────────────────────────┐
│  Sign_Templates/  (Pre-recorded .npy files)              │
│  hello.npy  stop.npy  good.npy  morning.npy  ...        │
└──────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Pose Estimation** | MediaPipe Holistic | 258 body + hand landmarks |
| **Matching** | Cosine Similarity (SciPy) | Template matching (threshold: 0.15) |
| **Web Framework** | Flask 3.1 | Dashboard & API server |
| **Computer Vision** | OpenCV 4.8 | Webcam capture & frame processing |
| **AI (Primary)** | OpenRouter API (free) | Sentence formation & Hindi translation |
| **AI (Fallback)** | Google Gemini API | Backup AI provider |
| **Text-to-Speech** | gTTS | English & Hindi audio generation |
| **Frontend** | HTML/CSS/JavaScript | Modern dark-themed dashboard |
| **Template Recorder** | CustomTkinter | Desktop GUI for recording signs |

---

## 📦 Installation & Setup

### Prerequisites

- **Python 3.10+** (tested on Python 3.10.11)
- **Webcam** (built-in or USB)
- **Internet connection** (for AI sentence formation & gTTS audio)

### Step-by-Step Setup

```bash
# 1. Extract the ZIP file to a folder
#    (e.g., C:\Projects\ISL-Recognition-Studio)

# 2. Open a terminal/command prompt in that folder

# 3. (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 4. Install all dependencies
pip install -r requirements.txt

# 5. Run the application
python run_dashboard.py
```

Then open your browser to: **http://localhost:5000**

---

## 🚀 How to Run

### Main Application (Web Dashboard)

```bash
python run_dashboard.py
```
Opens the full web dashboard with live webcam detection, AI sentence formation, and audio output.

### Template Recorder (Desktop GUI)

```bash
python record_templates.py
```
Opens a CustomTkinter desktop app to record new sign templates.

---

## 🧠 How It Works

### 1. Landmark Extraction
MediaPipe Holistic detects **33 pose landmarks** + **21 left hand** + **21 right hand** landmarks from each video frame. These are normalized into a **258-dimensional vector** (x, y, z coordinates × landmarks, with wrist-relative hand normalization).

### 2. Template Matching
Each pre-recorded sign is stored as a `.npy` file (a 258-element numpy array). During live detection, the system computes the **cosine distance** between the current frame's landmark vector and each template. If the distance is below **0.15** (configurable threshold), it's a match.

### 3. Sentence Formation
After **10 seconds** of no hand detection, the accumulated words are sent to an AI model:
- **Primary**: OpenRouter API (free model: `google/gemma-4-26b-a4b-it:free`)
- **Fallback**: Google Gemini API (`gemini-2.0-flash`)
- **Offline fallback**: Simple comma-separated word list

### 4. Hindi Translation
The English sentence is translated to Hindi:
- **Primary**: AI-generated Hindi (Devanagari script) via OpenRouter/Gemini
- **Offline fallback**: Built-in Hindi dictionary for all 11 signs

### 5. Audio Output
- **English**: gTTS with `lang='en'`
- **Hindi**: gTTS with `lang='hi'` (speaks Devanagari text natively)

---

## 🤟 Supported Signs (11 Total)

| # | Sign | Hindi | Description |
|---|------|-------|-------------|
| 1 | BREAK | रुको | Pause/break gesture |
| 2 | COME | आओ | Beckoning gesture |
| 3 | CRY | रोना | Crying gesture |
| 4 | GOOD | अच्छा | Thumbs up / good gesture |
| 5 | HELLO | नमस्ते | Waving hello |
| 6 | MORNING | सुबह | Morning greeting gesture |
| 7 | ONE | एक | Holding up one finger |
| 8 | STOP | रुको | Stop hand gesture |
| 9 | THANKYOU | धन्यवाद | Thank you gesture |
| 10 | THREE | तीन | Holding up three fingers |
| 11 | TWO | दो | Holding up two fingers |

---

## 📁 File Structure

```
ISL-Recognition-Studio/
│
├── run_dashboard.py          # 🚀 Main entry point - starts the web app
├── record_templates.py       # ➕ GUI tool to record new sign templates
├── requirements.txt          # 📦 Python dependencies
├── README.md                 # 📖 This file
│
├── app/                      # Flask web application
│   ├── __init__.py
│   ├── app.py                # Flask app factory
│   ├── config.py             # Configuration (API keys, paths)
│   ├── routes/               # Route handlers
│   │   ├── __init__.py
│   │   ├── live_routes.py    # ★ Core: camera, detection, AI, audio
│   │   ├── test_routes.py    # Video testing routes
│   │   └── batch_routes.py   # Batch processing routes
│   ├── templates/            # HTML templates (Jinja2)
│   │   ├── base.html         # Base layout
│   │   └── index.html        # ★ Main dashboard page
│   ├── static/               # CSS, JS, images
│   └── utils/                # Helper utilities
│
├── src/                      # Core engine
│   ├── __init__.py
│   └── similarity_engine.py  # ★ Landmark extraction & normalization
│
├── Sign_Templates/           # Pre-recorded sign templates (.npy)
│   ├── hello.npy
│   ├── stop.npy
│   ├── good.npy
│   └── ... (11 templates)
│
├── test_videos/              # Test video files
├── uploads/                  # Uploaded video storage
└── database/                 # SQLite results database
```

### Key Files Explained

| File | Purpose |
|------|---------|
| `run_dashboard.py` | Entry point — starts Flask server and camera thread |
| `app/routes/live_routes.py` | **Core file** — camera capture, MediaPipe processing, cosine matching, AI sentence formation, Hindi translation, audio generation |
| `src/similarity_engine.py` | Landmark extraction & wrist-relative normalization from MediaPipe results |
| `app/config.py` | API keys (OpenRouter, Gemini), file paths, Flask settings |
| `record_templates.py` | Desktop GUI (CustomTkinter) to record new sign templates |
| `Sign_Templates/*.npy` | Pre-recorded 258-dimensional landmark vectors for each sign |

---

## ➕ Adding New Signs

1. Run the **Template Recorder**:
   ```bash
   python record_templates.py
   ```
2. Position your hands in the sign gesture
3. Click **"Record New Sign"**
4. Enter the sign name (e.g., `water`, `help`)
5. The template is saved as `Sign_Templates/<name>.npy`
6. Restart the web dashboard — the new sign is automatically loaded

---

## 🔑 API Keys Configuration

API keys are stored in `app/config.py`:

### OpenRouter (Primary — Free)
1. Sign up at https://openrouter.ai (free)
2. Get your API key from https://openrouter.ai/keys
3. Paste it in `config.py` → `OPENROUTER_API_KEY`

### Gemini (Secondary — Free Tier)
1. Go to https://aistudio.google.com/apikey
2. Create an API key
3. Paste it in `config.py` → `GEMINI_API_KEY`

### Offline Mode
The system works **without any API keys** — it will use the built-in Hindi word dictionary and simple comma-separated sentences as fallbacks.

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Camera not showing** | Close other apps using the camera. Refresh the browser page (F5). |
| **Camera hangs on startup** | The system has an 8-second timeout. Wait for it to retry automatically. |
| **Hindi audio not playing** | Make sure you have internet (gTTS needs it). Check that a sentence has been formed first. |
| **"No sentence available"** | Show signs to the camera, then remove your hands. Wait 10 seconds for sentence formation. |
| **AI sentence not forming** | Check API keys in `app/config.py`. The system falls back to simple word lists if APIs are down. |
| **`pip install` errors** | Make sure you're using Python 3.10+. Try `pip install --upgrade pip` first. |
| **MediaPipe not installing** | On Windows, try: `pip install mediapipe --no-cache-dir` |

---

## 📝 Notes for Peers

- The project is **self-contained** — all sign templates are included
- **No GPU required** — runs entirely on CPU
- **No model training needed** — uses template matching, not deep learning
- Internet is needed for AI sentence formation and Hindi audio, but the system gracefully falls back to offline mode
- The web dashboard auto-detects signs and forms sentences — just show your hands!

---

## 👨‍💻 Developed By

**Rohith S** — Indian Sign Language Recognition System (2026)

Built with ❤️ using Python, MediaPipe, Flask, and AI
