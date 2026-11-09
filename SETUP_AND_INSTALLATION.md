# Setup & Installation Guide

## 🎯 Overview

This guide will help you install and run the ISL Similarity Recognition project on your system.

---

## 📋 SYSTEM REQUIREMENTS

### **Minimum Requirements**
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 500MB
- **Webcam**: Any USB webcam or built-in laptop camera
- **Internet**: Required for Google Gemini API (sentence formation)

### **Recommended Setup**
- **Python**: 3.10+
- **RAM**: 4GB+
- **Disk Space**: 1GB
- **GPU**: Optional (not required)
- **Processor**: Intel i5 or equivalent

---

## 🔧 INSTALLATION STEPS

### **Step 1: Install Python**

#### On Windows:
1. Download from https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Choose Python 3.10+ (latest stable)

#### On macOS:
```bash
brew install python3
```

#### On Linux (Ubuntu):
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

**Verify Installation:**
```bash
python --version
pip --version
```

---

### **Step 2: Extract Project Files**

1. Extract `ISL_ML_Project_Final_Draft.zip` to a folder
2. Navigate to the extracted folder:
```bash
cd ISL_ML_Project_Final_Draft
```

---

### **Step 3: Create Virtual Environment (RECOMMENDED)**

Virtual environments keep dependencies isolated from your system Python.

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

You'll see `(venv)` prefix in terminal when activated.

---

### **Step 4: Install Dependencies**

```bash
pip install -r requirements.txt
```

**This installs:**
- flask (web framework)
- opencv-python (video processing)
- mediapipe (pose detection ML model)
- numpy (numerical computations)
- scipy (similarity calculations)
- customtkinter (GUI for template recording)
- google-generativeai (Gemini AI API)
- pillow (image processing)

**Installation Time**: 3-10 minutes (first time)

---

### **Step 5: Add Gemini API Key**

The project uses Google's Gemini AI for natural sentence formation.

#### Get Your API Key:
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Select "Create API key in new project"
4. Copy the generated key

#### Add to Project:
Open `app/config.py` and find this line:
```python
GEMINI_API_KEY = 'AIzaSyCHaI6IAVHaOnoaSK6_5ijmLYbLwNpEHdw'
```

Replace with your API key:
```python
GEMINI_API_KEY = 'YOUR_API_KEY_HERE'
```

**⚠️ DO NOT commit or share your API key!**

---

### **Step 6: Verify Setup**

Run the verification script:
```bash
python verify_setup.py
```

This will check:
- ✅ Python version
- ✅ All dependencies installed
- ✅ MediaPipe model loaded
- ✅ Webcam detected
- ✅ Sign templates found
- ✅ Database initialized

---

## 🚀 RUNNING THE PROJECT

### **Option 1: Run Live Dashboard (RECOMMENDED)**

```bash
python run_dashboard.py
```

You'll see:
```
============================================================
  ISL Similarity Studio - Web Dashboard
============================================================

  Starting Flask server...
  Open your browser to: http://localhost:5000

  Press Ctrl+C to stop the server.
============================================================
```

**Then:**
1. Open browser to `http://localhost:5000`
2. You should see the live detection dashboard
3. Show hand signs to camera
4. Watch words detected in real-time!

---

### **Option 2: Record New Signs**

```bash
python record_templates.py
```

This opens a GUI where you can:
1. Show your hand in a sign gesture
2. Click "Record New Sign"
3. Enter the sign name (e.g., "goodbye")
4. Template automatically saved and recognized by dashboard

---

## 📊 Project Structure After Installation

```
ISL_ML_Project_Final_Draft/
├── app/                          # Flask web app
├── src/                          # ML engine
├── Sign_Templates/               # 9 pre-loaded signs
├── database/                     # Results database
├── uploads/                      # Uploaded videos
├── record_templates.py           # Recording GUI
├── run_dashboard.py              # Start dashboard
├── requirements.txt              # Dependencies
├── README.md                     # Overview
├── SETUP_AND_INSTALLATION.md     # This file
├── PERFORMANCE_METRICS.md        # Metrics
└── PROJECT_ARCHITECTURE_DETAILED.md  # Technical docs
```

---

## ✅ VERIFICATION CHECKLIST

After installation, verify everything works:

- [ ] All dependencies installed (`pip list` shows all packages)
- [ ] Webcam detected and accessible
- [ ] Dashboard starts without errors
- [ ] Web UI loads in browser (`http://localhost:5000`)
- [ ] Live video feed shows camera
- [ ] Signs are recognized (show hand gestures)
- [ ] Sentence forms after 10 seconds of no hands
- [ ] All 9 templates loaded (visible in UI)

---

## 🐛 TROUBLESHOOTING

### **Issue: "Python is not recognized"**
**Solution**: 
- Windows: Re-install Python and CHECK "Add Python to PATH"
- Restart terminal after installation

### **Issue: "pip install fails"**
**Solution**:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### **Issue: "No module named 'mediapipe'"**
**Solution**:
```bash
pip install mediapipe==0.10.14
```

### **Issue: "Webcam not detected"**
**Solution**:
- Check if another app is using camera (e.g., Zoom)
- Restart the script
- Check camera permissions (Windows/macOS)

### **Issue: "Port 5000 already in use"**
**Solution**:
```bash
# Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

### **Issue: "Gemini API key error"**
**Solution**:
- Verify key is correct in `app/config.py`
- Check internet connection
- Get new key from https://aistudio.google.com/app/apikey

### **Issue: "Detection not working / blank screen"**
**Solution**:
- Check webcam lighting
- Ensure MediaPipe can see hands clearly
- Test with `python record_templates.py` first
- Check camera permissions

---

## 📦 DEPENDENCIES EXPLANATION

| Package | Version | Purpose |
|---------|---------|---------|
| flask | 3.1.3 | Web server framework |
| flask-cors | 5.0.1 | Allow cross-origin requests |
| opencv-python | 4.8.1.78 | Video processing & encoding |
| mediapipe | 0.10.14 | **ML model for pose detection** |
| numpy | 1.26.4 | Numerical computations |
| scipy | 1.15.3 | Cosine similarity calculations |
| customtkinter | 5.2.2 | Modern GUI for template recorder |
| pillow | 12.2.0 | Image processing |
| google-generativeai | 0.5.4 | Gemini AI API |

**Total Download Size**: ~800MB (first install)

---

## 🌐 INTERNET REQUIREMENTS

The project needs internet for:
1. **MediaPipe Model**: Downloaded first run (~300MB)
2. **Gemini API**: Sentence formation requires API call
3. **Google Fonts** (optional): CSS styling

**Works offline?** Yes, but:
- ❌ First run needs internet (model download)
- ❌ Sentence formation disabled without API key
- ✅ Detection works offline after initial setup

---

## 🔄 UPDATING DEPENDENCIES

To update all packages to latest versions:
```bash
pip install --upgrade -r requirements.txt
```

To check for outdated packages:
```bash
pip list --outdated
```

---

## 📱 RUNNING ON DIFFERENT SYSTEMS

### **Windows**
```bash
python run_dashboard.py
```

### **macOS**
```bash
python3 run_dashboard.py
```

### **Linux (Ubuntu)**
```bash
python3 run_dashboard.py
```

---

## 🎯 QUICK REFERENCE

| Task | Command |
|------|---------|
| Install dependencies | `pip install -r requirements.txt` |
| Run dashboard | `python run_dashboard.py` |
| Record new sign | `python record_templates.py` |
| Verify setup | `python verify_setup.py` |
| Activate venv (Windows) | `venv\Scripts\activate` |
| Activate venv (Mac/Linux) | `source venv/bin/activate` |
| Deactivate venv | `deactivate` |
| View installed packages | `pip list` |

---

## 💻 ENVIRONMENT VARIABLES (OPTIONAL)

You can set API key as environment variable instead of hardcoding:

### **Windows (PowerShell)**
```powershell
$env:GEMINI_API_KEY = "your_api_key_here"
python run_dashboard.py
```

### **macOS/Linux (Bash)**
```bash
export GEMINI_API_KEY="your_api_key_here"
python run_dashboard.py
```

Then in `app/config.py`:
```python
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
```

---

## 📞 GETTING HELP

If you encounter issues:

1. **Check terminal output** - Most errors are printed there
2. **Read error message carefully** - It usually tells you what's wrong
3. **Check internet connection** - Required for MediaPipe & Gemini
4. **Verify webcam works** - Test with another app first
5. **Try virtual environment** - Helps isolate dependency issues

---

## ✨ YOU'RE READY!

Once setup is complete:
```bash
python run_dashboard.py
```

Then open: `http://localhost:5000`

**Enjoy recognizing Indian Sign Language! 🤟**

---

**Last Updated**: May 3, 2026  
**Setup Time**: 10-15 minutes (first run)
