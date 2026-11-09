# File-by-File Explanation - Complete Project Structure

## 📁 Root Directory Files

### 1. `run_dashboard.py` ⭐ MAIN ENTRY POINT
**Purpose**: Starts the Flask web server for live detection

**What it does**:
- Imports Flask app from `app.app`
- Creates Flask application instance
- Starts inference thread for background processing
- Runs Flask development server on `http://localhost:5000`

**Key Code**:
```python
app = create_app()
app.run(debug=False, host='0.0.0.0', port=5000)
```

**Why it exists**: Single entry point to start the entire system

**Usage**: `python run_dashboard.py`

---

### 2. `record_templates.py` ⭐ TEMPLATE RECORDER
**Purpose**: GUI application to record new sign templates

**What it does**:
- Opens webcam and displays live feed
- Shows MediaPipe skeleton overlay
- Captures current pose when user clicks "Record"
- Prompts for sign name
- Saves normalized 258-element array as `.npy` file
- Auto-detects and loads new templates

**Key Features**:
- CustomTkinter GUI (modern dark theme)
- Real-time skeleton visualization
- Confidence scoring on recording
- Template validation

**Why it exists**: To create training templates without coding

**Usage**: `python record_templates.py`

---

### 3. `sign_studio.py`
**Purpose**: Alternative desktop application (similar to record_templates)

**What it does**: Full-featured desktop GUI for template recording and testing

**Why it exists**: Alternative UI for users who prefer desktop app

---

### 4. `verify_setup.py`
**Purpose**: Diagnostic tool to verify installation

**What it does**:
- Checks Python version
- Verifies all required packages installed
- Tests webcam access
- Checks folder structure
- Validates template loading
- Reports any issues

**Usage**: `python verify_setup.py` (run first if errors occur)

---

### 5. `debug_video_analysis.py`
**Purpose**: Advanced debugging tool for video analysis

**What it does**:
- Processes uploaded videos frame-by-frame
- Shows which frames have hands detected
- Displays confidence scores for each template
- Identifies why detection failed
- Provides recommendations

**Why it exists**: Troubleshoot false negatives/positives

---

### 6. `requirements.txt` ⭐ DEPENDENCIES
**Purpose**: Lists all Python packages needed

**Contents**:
```
flask
flask-cors
opencv-python
mediapipe
numpy
scipy
customtkinter
pillow
google-generativeai
```

**Usage**: `pip install -r requirements.txt`

---

### 7. `README.md` ⭐ MAIN DOCUMENTATION
**Purpose**: Project overview, installation, ML justification

**Contains**:
- Project description
- ML classification justification
- Performance metrics
- Installation guide
- Usage instructions
- Algorithm details

---

## 📁 app/ Directory (Flask Application)

### `app/app.py` ⭐ FLASK APP CREATOR
**Purpose**: Creates and configures Flask application

**What it does**:
- Initializes Flask app
- Configures CORS for cross-origin requests
- Initializes database
- Registers all blueprints (routes)
- Starts inference thread
- Returns configured app instance

**Key Code**:
```python
def create_app():
    app = Flask(__name__)
    CORS(app)
    init_db()
    # Register blueprints
    app.register_blueprint(live_routes.bp)
    # Start background thread
    live_routes.start_inference_thread()
    return app
```

**Why it exists**: Central configuration point for Flask app

---

### `app/config.py` ⚙️ CONFIGURATION
**Purpose**: Central configuration management

**What it stores**:
- Secret keys
- Upload folder paths
- Database location
- Template directory
- Gemini API key
- File upload limits

**Key Configuration**:
```python
GEMINI_API_KEY = 'your-api-key-here'
SIGN_TEMPLATES_DIR = '/path/to/Sign_Templates'
MAX_CONTENT_LENGTH = 500MB
```

**Why it exists**: Single source of truth for all settings

---

### `app/routes/live_routes.py` ⭐ LIVE DETECTION ENGINE
**Purpose**: Real-time webcam detection logic and API endpoints

**What it does**:
1. **Background Thread**: Runs inference loop continuously
2. **Webcam Capture**: Opens and reads from webcam
3. **MediaPipe Processing**: Extracts landmarks from each frame
4. **Template Matching**: Compares with all templates
5. **State Management**: Maintains detected words, sentence, timers
6. **Sentence Formation**: Calls Gemini AI after 10s inactivity
7. **MJPEG Streaming**: Encodes frames for browser display

**Key Functions**:
- `inference_loop()`: Main processing loop (runs in background)
- `form_sentence_gemini()`: Calls Gemini API
- `generate_mjpeg()`: Creates video stream
- `get_status()`: Returns current detection state (JSON)
- `get_templates()`: Returns available templates list

**API Endpoints**:
- `/` - Main page
- `/video_feed` - MJPEG video stream
- `/status` - Real-time detection status
- `/templates` - List of templates
- `/reset` - Clear detection state

**Why it exists**: Core detection logic and API

---

### `app/routes/main_routes.py`
**Purpose**: Main page and utility routes

**What it does**:
- Serves main landing page
- Handles general navigation
- Provides helper functions

---

### `app/routes/test_routes.py`
**Purpose**: Video upload and testing routes

**What it does**:
- Handles video file uploads
- Processes uploaded videos
- Stores results in database
- Returns detection results

**Key Features**:
- File validation
- Progress tracking
- Result persistence

---

### `app/routes/batch_routes.py`
**Purpose**: Batch processing of multiple videos

**What it does**:
- Processes multiple videos at once
- Generates comparison reports
- Exports results to CSV/JSON

---

### `app/routes/results_routes.py`
**Purpose**: View and manage detection results

**What it does**:
- Displays detection history
- Shows video playback
- Manages database queries
- Exports results

**API Endpoints**:
- `/results/api/video/<id>` - Stream stored video
- `/results/api/list` - List all results

---

### `app/utils/db_helper.py`
**Purpose**: Database operations helper

**What it does**:
- Initializes SQLite database
- Creates results table
- Inserts detection results
- Queries historical data

**Database Schema**:
```sql
CREATE TABLE results (
    id INTEGER PRIMARY KEY,
    video_path TEXT,
    predicted_sign TEXT,
    confidence REAL,
    timestamp DATETIME
)
```

---

### `app/templates/base.html`
**Purpose**: Base HTML template with common layout

**What it contains**:
- HTML header with meta tags
- CSS imports (Bootstrap, custom styles)
- Navigation bar
- Footer
- Common JavaScript

**Why it exists**: Consistent layout across all pages

---

### `app/templates/index.html` ⭐ LIVE DETECTION UI
**Purpose**: Main live detection interface

**What it contains**:
- Video feed display (`<img src="/video_feed">`)
- Current detection card
- Detected words list
- AI sentence display
- Available templates showcase
- Reset button
- Real-time JavaScript polling (100ms intervals)

**Key JavaScript**:
```javascript
// Poll status every 100ms
setInterval(() => {
    fetch('/status')
        .then(r => r.json())
        .then(data => {
            // Update UI with detection results
        })
}, 100);

// Poll templates every 3 seconds
setInterval(() => {
    fetch('/templates')
        .then(r => r.json())
        .then(data => {
            // Update templates list
        })
}, 3000);
```

**Why it exists**: User interface for live detection

---

### `app/static/` Directory
**Purpose**: Static assets (CSS, JavaScript, images)

**Contents**:
- `css/style.css` - Custom styles
- `js/main.js` - Client-side JavaScript
- `images/` - Logos, icons

---

## 📁 src/ Directory (Core ML Engine)

### `src/similarity_engine.py` ⭐ CORE ML ENGINE
**Purpose**: Template matching and recognition logic

**Key Classes**:
- `SimilarityEngine`: Main recognition engine

**Key Functions**:

1. **`extract_and_normalize(results)`**
   - Extracts 258 landmarks from MediaPipe results
   - Normalizes pose to nose position
   - Normalizes hands to wrist position
   - Returns: 258-element normalized array

2. **`flip_horizontal(landmarks)`**
   - Flips landmarks horizontally
   - Swaps left/right hands
   - Enables bidirectional matching

3. **`mask_inactive_hands(landmarks, template)`**
   - Zeros out hands not present in template
   - Prevents false matches from extra hands

4. **`match_landmarks(landmarks, threshold, bidirectional)`**
   - Computes cosine similarity to all templates
   - Tests both original and flipped versions
   - Returns best match if distance < threshold

5. **`process_frame(frame_bgr)`**
   - Processes single video frame
   - Returns normalized landmarks

6. **`process_video(video_path, threshold, sample_rate)`**
   - Processes entire video file
   - Samples every Nth frame
   - Returns best overall match

**Why it exists**: Core ML/recognition logic

---

### `src/__init__.py`
**Purpose**: Python package marker

**What it does**: Makes `src` a Python package for imports

---

## 📁 Sign_Templates/ Directory

### `*.npy` Files (break.npy, cry.npy, etc)
**Purpose**: Pre-recorded sign templates

**Format**: NumPy binary file containing 258-element array

**Structure**:
- Elements 0-131: Pose landmarks (33 points × 4 values)
- Elements 132-194: Left hand landmarks (21 points × 3 values)
- Elements 195-257: Right hand landmarks (21 points × 3 values)

**How created**: By `record_templates.py` when user records a sign

**Why they exist**: Reference patterns for comparison

**Current templates**:
- break.npy
- cry.npy
- good.npy
- hello.npy
- morning.npy
- one.npy
- stop.npy
- thankyou.npy
- two.npy

---

## 📁 database/ Directory

### `results.db`
**Purpose**: SQLite database for detection history

**Tables**:
- `results`: Stores all detection results

**Why it exists**: Persistent storage of results

---

## 📁 uploads/ Directory
**Purpose**: Temporary storage for uploaded videos

**Lifecycle**:
1. User uploads video → stored here
2. Video processed → results saved to database
3. Video kept for viewing in results page

---

## 📁 test_videos/ Directory
**Purpose**: Sample test videos for demonstration

**Usage**: Pre-recorded ISL signs for testing without recording

---

## 📁 DOCUMENTATION/ Directory ⭐

### `01_PROJECT_OVERVIEW.md`
What the project is about, objectives, scope

### `02_FILE_BY_FILE_EXPLANATION.md`
This file - explains what each file does

### `03_HOW_IT_WORKS.md`
Detailed technical workflow and algorithms

### `04_ML_JUSTIFICATION.md`
Why this counts as ML project (for professors)

### `05_INSTALLATION_AND_USAGE.md`
Complete installation and usage guide

---

## 📊 File Dependencies

```\nrun_dashboard.py\n    └── app/app.py\n            ├── app/config.py\n            ├── app/routes/live_routes.py\n            │       ├── src/similarity_engine.py\n            │       └── app/config.py\n            ├── app/routes/main_routes.py\n            ├── app/routes/test_routes.py\n            ├── app/routes/batch_routes.py\n            ├── app/routes/results_routes.py\n            └── app/utils/db_helper.py\n\nrecord_templates.py\n    └── src/similarity_engine.py\n    └── app/config.py\n```\n\n---

## 🎯 Key Files Summary

| File | Purpose | Critical? |
|------|---------|-----------|
| `run_dashboard.py` | Start web server | ⭐⭐⭐ |
| `record_templates.py` | Record new signs | ⭐⭐⭐ |
| `app/routes/live_routes.py` | Detection logic | ⭐⭐⭐ |
| `src/similarity_engine.py` | Core ML engine | ⭐⭐⭐ |
| `app/templates/index.html` | Web UI | ⭐⭐⭐ |
| `app/config.py` | Configuration | ⭐⭐ |
| `Sign_Templates/*.npy` | Sign templates | ⭐⭐⭐ |
| `requirements.txt` | Dependencies | ⭐⭐ |
| `README.md` | Documentation | ⭐⭐ |

---

**Next**: Read `03_HOW_IT_WORKS.md` to understand the detailed technical workflow.
