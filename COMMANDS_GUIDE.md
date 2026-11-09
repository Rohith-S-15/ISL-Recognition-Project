# ISL Similarity App - Command Guide

## Running the Application

### 1. Start the Web Dashboard

**Command:**
```bash
cd "C:\Projects\New Approach\ISL_Similarity_App"
python run_dashboard.py
```

**What happens:**
- Flask server starts on `http://localhost:5000`
- Loads all templates from `Sign_Templates/` folder
- Opens dashboard in browser

**Access in Browser:**
- Home: `http://localhost:5000/`
- Test: `http://localhost:5000/test`
- Batch: `http://localhost:5000/batch`
- Results: `http://localhost:5000/results`

**To stop:**
- Press `Ctrl+C` in terminal

---

### 2. Start Desktop App (Sign Studio)

**Command:**
```bash
cd "C:\Projects\New Approach\ISL_Similarity_App"
python sign_studio.py
```

**What it does:**
- Opens desktop app with live webcam
- Shows skeleton overlay
- "▶ Start Translating" button - Live recognition
- "➕ Record New Sign" button - Save new templates
- Shows detected words in real-time

---

### 3. Debug Video Analysis

**Command:**
```bash
cd "C:\Projects\New Approach\ISL_Similarity_App"
python debug_video_analysis.py
```

**What it does:**
- Analyzes `cry.mp4` and `come.mp4` from Sample Videos folder
- Shows hand detection rate
- Shows distances to each template
- Recommends fixes if returns "Unknown"

---

### 4. Record Templates Manually

**Command:**
```bash
cd "C:\Projects\New Approach\ISL_Similarity_App"
python record_templates.py
```

**What it does:**
- Record new sign templates
- Save as `.npy` files in `Sign_Templates/`

---

## Important Directories

```
C:\Projects\New Approach\ISL_Similarity_App\
├── Sign_Templates/          ← Your templates (hello.npy, cry.npy, etc.)
├── app/                     ← Web app code
│   ├── routes/             ← API endpoints
│   ├── templates/          ← HTML pages
│   └── static/             ← CSS, JS
├── src/
│   └── similarity_engine.py ← Core matching logic (NOW WITH BIDIRECTIONAL!)
├── uploads/                ← Temporary upload storage
├── database/
│   └── results.db          ← Test history
├── run_dashboard.py        ← Start web app HERE
├── sign_studio.py          ← Start desktop app HERE
├── debug_video_analysis.py ← Debug tool
└── requirements.txt        ← Dependencies
```

---

## Installing Dependencies

If dependencies not installed:

```bash
pip install -r requirements.txt
```

**Required packages:**
- flask 3.1.3
- opencv-python 4.8.1.78
- mediapipe 0.10.14
- numpy 1.26.4
- scipy 1.15.3
- customtkinter 5.2.2
- pillow 12.2.0
- pyttsx3 2.99

---

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Port 5000 already in use
```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F

# Then restart
python run_dashboard.py
```

### No templates found
1. Check `Sign_Templates/` folder exists
2. Record templates using desktop app or `record_templates.py`
3. Templates should be `.npy` files

### Videos return "Unknown"
1. Run debug script: `python debug_video_analysis.py`
2. Check hand detection rate
3. Try recording new templates closer to camera
4. Ensure good lighting

---

## New Features (Recently Added)

### ✨ Bidirectional Hand Matching
- Record template with RIGHT hand → Works with LEFT hand too!
- Enabled automatically, no configuration needed
- Works with all existing templates

### ✨ Video Viewer in Results
- Click eye icon to view uploaded video
- Beautiful modal player with metadata
- Shows confidence and processing time

### ✨ Debug Analysis Tool
- Detailed video analysis
- Frame-by-frame breakdown
- Distance visualization
- Troubleshooting recommendations

---

## Quick Start

**First time?**

1. **Start the web app:**
   ```bash
   python run_dashboard.py
   ```

2. **Record a sign** using desktop app:
   ```bash
   python sign_studio.py
   ```
   - Click "Start Translating"
   - Make a sign
   - Click "Record New Sign"
   - Name it (e.g., "hello")

3. **Test it:**
   - Go to `http://localhost:5000/test`
   - Upload a video of the same sign
   - Check results page to view video and see detection

---

## Video Upload Specifications

**Supported formats:**
- MP4, AVI, MOV, MKV, FLV, WMV, WebM

**Recommendations:**
- 30 FPS minimum
- 720p or higher resolution
- Good lighting
- Hand clearly visible
- 2-5 seconds long

---

## File Paths to Remember

**All work happens in:**
```
C:\Projects\New Approach\ISL_Similarity_App\
```

**Run these files:**
- `python run_dashboard.py` ← Web app
- `python sign_studio.py` ← Desktop app
- `python debug_video_analysis.py` ← Debug tool

**Check these folders:**
- `Sign_Templates/` ← Your templates
- `database/results.db` ← History
- `uploads/` ← Temporary files

---

## Questions?

- Check `FIXES_IMPLEMENTED.md` for technical details
- Check `project_status_report.md` for project overview
- Run debug script for video analysis

Good luck! 🚀
