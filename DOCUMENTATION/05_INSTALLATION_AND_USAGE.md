# Installation and Usage Guide

## 📋 Prerequisites

Before installing, ensure you have:

- ✅ **Python 3.8 or higher** (tested on Python 3.10.11)
- ✅ **Webcam** (for live detection)
- ✅ **Modern web browser** (Chrome, Firefox, Edge)
- ✅ **Internet connection** (for Gemini AI features)
- ✅ **500 MB free disk space**

---

## 🚀 Quick Start (Windows)

### Step 1: Install Python

Download from: https://www.python.org/downloads/

**During installation**:
- ✅ Check "Add Python to PATH"
- ✅ Install for all users
- ✅ Install pip

### Step 2: Extract Project

```bash
# Navigate to project folder
cd C:\Projects\New Approach\ISL_Similarity_App
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed**:
- Flask (web framework)
- OpenCV (image processing)
- MediaPipe (pose detection)
- NumPy (numerical operations)
- SciPy (similarity metrics)
- CustomTkinter (GUI)
- Google Generative AI (sentence formation)

### Step 4: Verify Installation

```bash
python verify_setup.py
```

**Expected output**:
```
✓ Python version: 3.10.11
✓ Flask installed
✓ OpenCV installed
✓ MediaPipe installed
✓ NumPy installed
✓ SciPy installed
✓ Webcam accessible
✓ Templates loaded: 9
✓ Database ready
```

### Step 5: Run Application

```bash
python run_dashboard.py
```

### Step 6: Open Browser

Navigate to: **http://localhost:5000**

---

## 🖥️ Usage Guide

### Live Detection (Main Feature)

1. **Start the application**:
   ```bash
   python run_dashboard.py
   ```

2. **Open browser**: http://localhost:5000

3. **Show hand gestures** to webcam

4. **Watch detection happen in real-time**:
   - Current word appears with confidence %
   - Detected words list updates
   - After 10 seconds of no hand, AI forms sentence

5. **Reset** (optional):
   - Click "Clear All" button
   - Or wait for auto-reset after sentence

### Recording New Signs

1. **Run template recorder**:
   ```bash
   python record_templates.py
   ```

2. **Click "Record New Sign"**

3. **Show the gesture** you want to record

4. **Enter sign name** (e.g., "hello")

5. **Template saved automatically** to `Sign_Templates/`

6. **Dashboard auto-detects** new template within 3 seconds

### Testing with Videos

1. **Go to**: http://localhost:5000/test

2. **Upload video file** (mp4, avi, mov, etc.)

3. **View results**:
   - Predicted sign
   - Confidence score
   - All template distances

4. **Check Results page** for history

---

## 🔧 Configuration

### Update Gemini API Key

1. Open `app/config.py`

2. Replace API key:
   ```python
   GEMINI_API_KEY = 'your-api-key-here'
   ```

3. Get API key from: https://aistudio.google.com/app/apikey

### Adjust Detection Threshold

In `app/routes/live_routes.py`:
```python
threshold = 0.15  # Lower = stricter, Higher = more lenient
```

### Change Camera Resolution

In `app/routes/live_routes.py`:
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

### Modify Sentence Formation Timer

In `app/routes/live_routes.py`:
```python
if absence >= 10.0:  # Change to desired seconds
```

---

## 📁 Project Structure Reference

```
ISL_Similarity_App/
├── run_dashboard.py              # Main entry point
├── record_templates.py           # Template recorder
├── sign_studio.py                # Desktop app
├── verify_setup.py               # Setup verification
├── requirements.txt              # Dependencies
│
├── app/                          # Flask application
│   ├── app.py                    # Flask app creator
│   ├── config.py                 # Configuration
│   ├── routes/                   # API routes
│   │   ├── live_routes.py        # Live detection
│   │   ├── main_routes.py        # Main page
│   │   ├── test_routes.py        # Video testing
│   │   └── batch_routes.py       # Batch processing
│   ├── templates/                # HTML templates
│   │   ├── base.html             # Base layout
│   │   └── index.html            # Live detection UI
│   ├── static/                   # CSS, JS, images
│   └── utils/                    # Utilities
│       └── db_helper.py          # Database helper
│
├── src/                          # Core ML engine
│   ├── __init__.py
│   └── similarity_engine.py      # Recognition logic
│
├── Sign_Templates/               # Sign templates
│   ├── break.npy
│   ├── cry.npy
│   ├── good.npy
│   ├── hello.npy
│   ├── morning.npy
│   ├── one.npy
│   ├── stop.npy
│   ├── thankyou.npy
│   └── two.npy
│
├── test_videos/                  # Sample videos
├── uploads/                      # Uploaded videos
├── database/                     # SQLite database
│   └── results.db
│
└── DOCUMENTATION/                # Documentation
    ├── 01_PROJECT_OVERVIEW.md
    ├── 02_FILE_BY_FILE_EXPLANATION.md
    ├── 03_HOW_IT_WORKS.md
    ├── 04_ML_JUSTIFICATION.md
    └── 05_INSTALLATION_AND_USAGE.md
```

---

## 🐛 Troubleshooting

### Problem: "Module not found" error

**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

### Problem: "Cannot open camera"

**Solutions**:
1. Close other apps using webcam (Zoom, Skype)
2. Check camera permissions in Windows settings
3. Try different camera index in code:
   ```python
   cap = cv2.VideoCapture(1)  # Try 1, 2, etc.
   ```

### Problem: "No templates loaded"

**Solution**:
1. Check `Sign_Templates/` folder exists
2. Verify `.npy` files are present
3. Re-record templates if needed

### Problem: Low confidence scores

**Solutions**:
1. Improve lighting
2. Reduce distance from camera
3. Ensure full hand visibility
4. Re-record templates with clearer gestures
5. Lower threshold (not recommended)

### Problem: Slow performance (<5 FPS)

**Solutions**:
1. Close other applications
2. Reduce camera resolution
3. Use smaller video size
4. Upgrade hardware (if possible)

### Problem: Gemini API errors

**Solutions**:
1. Check API key is valid
2. Verify internet connection
3. Check API quota limits
4. Ensure API key is properly formatted in config

---

## 📊 Testing Guide

### Test 1: Basic Detection

1. Start application
2. Show "STOP" sign to camera
3. Verify "STOP" appears with >90% confidence
4. Repeat for all 9 signs

**Expected**: All signs detected with >90% confidence

### Test 2: Template Recording

1. Run `python record_templates.py`
2. Record new sign (e.g., "test")
3. Check `Sign_Templates/test.npy` exists
4. Restart dashboard
5. Verify "test" appears in available templates

**Expected**: New template detected and usable

### Test 3: Sentence Formation

1. Show multiple signs (e.g., "hello", "good", "morning")
2. Wait 10 seconds with no hand
3. Verify AI forms sentence: "Good morning, hello!"

**Expected**: Natural sentence formed

### Test 4: Bidirectional Matching

1. Record template with right hand
2. Show left hand gesture
3. Verify detection still works

**Expected**: Same detection regardless of hand used

---

## 🎯 Best Practices

### For Best Detection Accuracy:

1. **Lighting**: Well-lit environment, avoid backlighting
2. **Distance**: 0.5-2 meters from camera
3. **Background**: Plain, contrasting background
4. **Gesture clarity**: Clear, distinct hand shapes
5. **Camera angle**: Front-facing, full body visible

### For Recording Templates:

1. **Multiple samples**: Record 3-5 times, use best
2. **Consistent positioning**: Same distance each time
3. **Clear gestures**: Exaggerate hand shapes
4. **Good lighting**: Avoid shadows on hands
5. **Steady camera**: Use tripod or stable surface

### For Performance:

1. **Close other apps**: Free up CPU/RAM
2. **Use wired connection**: For stable API calls
3. **Regular restarts**: Clear memory leaks
4. **Monitor FPS**: Adjust resolution if needed

---

## 📝 Command Reference

### Essential Commands:

```bash
# Start live detection
python run_dashboard.py

# Record new signs
python record_templates.py

# Verify installation
python verify_setup.py

# Debug video analysis
python debug_video_analysis.py

# Install dependencies
pip install -r requirements.txt

# Upgrade packages
pip install --upgrade flask opencv-python mediapipe
```

### Optional Commands:

```bash
# Desktop app
python sign_studio.py

# Check Python version
python --version

# List installed packages
pip list

# Uninstall all (clean slate)
pip uninstall -y flask opencv-python mediapipe numpy scipy
```

---

## 🌐 API Endpoints Reference

### Live Detection:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main page |
| `/video_feed` | GET | MJPEG video stream |
| `/status` | GET | Detection status (JSON) |
| `/templates` | GET | Available templates |
| `/reset` | POST | Clear detection state |

### Video Testing:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/test` | GET | Upload page |
| `/api/test` | POST | Upload video |
| `/results` | GET | Results page |
| `/api/video/<id>` | GET | Stream video |

---

## 📞 Support Resources

### Documentation Files:

1. **01_PROJECT_OVERVIEW.md** - What and why
2. **02_FILE_BY_FILE_EXPLANATION.md** - File purposes
3. **03_HOW_IT_WORKS.md** - Technical workflow
4. **04_ML_JUSTIFICATION.md** - ML classification
5. **05_INSTALLATION_AND_USAGE.md** - This file

### Diagnostic Tools:

- `verify_setup.py` - Check installation
- `debug_video_analysis.py` - Analyze videos
- Console output - Detailed error messages

### External Resources:

- MediaPipe docs: https://google.github.io/mediapipe/
- Flask docs: https://flask.palletsprojects.com/
- OpenCV docs: https://docs.opencv.org/

---

## ✅ Installation Checklist

Before submitting/using project:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Webcam accessible
- [ ] Templates loaded (9 signs)
- [ ] Database initialized
- [ ] API key configured (if using Gemini)
- [ ] Live detection working
- [ ] Template recording working
- [ ] Documentation complete
- [ ] All files present

**All checked?** → Project ready for use/submission!

---

**Next**: Review `PROJECT_ARCHITECTURE_DETAILED.md` for complete technical details.
