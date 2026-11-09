# How It Works - Detailed Technical Workflow

## 🎯 Complete System Workflow

This document explains exactly how the ISL recognition system works, step by step, from webcam capture to sentence formation.

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Webcam UI  │  │  Words List  │  │  AI Sentence │           │
│  └─────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (Flask Routes)                    │
│  /video_feed  /status  /templates  /reset                       │
└─────────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────────┐
│                   INFERENCE ENGINE (Background Thread)           │
│  Webcam Capture → MediaPipe → Normalization → Template Matching │
└─────────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────────┐
│                    ML MODELS & ALGORITHMS                        │
│  MediaPipe Holistic (CNN)  +  Cosine Similarity                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Detection Pipeline (Frame-by-Frame)

### Step 1: Initialize System (One-time at startup)

**File**: `app/routes/live_routes.py` → `start_inference_thread()`

```python
# When Flask starts, background thread is launched
def start_inference_thread():
    inference_thread = threading.Thread(target=inference_loop, daemon=True)
    inference_thread.start()
```

**What happens**:
1. Flask app starts
2. Creates new daemon thread
3. Calls `inference_loop()` function
4. Thread runs independently in background
5. Main Flask thread continues serving HTTP requests

**Why background thread**:
- Continuous processing (doesn't block web server)
- Real-time detection (runs at camera FPS)
- Independent lifecycle (keeps running while server responds)

---

### Step 2: Load Templates (One-time at thread start)

**File**: `app/routes/live_routes.py` → `inference_loop()` lines 88-103

```python
# Load all .npy templates from Sign_Templates/
templates_dir = Config.SIGN_TEMPLATES_DIR
templates = {}

for file in os.listdir(templates_dir):
    if file.endswith(".npy"):
        word = file.replace(".npy", "")
        templates[word] = np.load(os.path.join(templates_dir, file))
```

**What happens**:
1. Scans `Sign_Templates/` directory
2. For each `.npy` file:
   - Extracts word name from filename
   - Loads 258-element NumPy array
   - Stores in dictionary: `{'hello': array, 'stop': array, ...}`
3. Prints: `Loaded 9 templates: ['break', 'cry', 'good', ...]`

**Why this matters**: Templates are reference patterns for comparison

---

### Step 3: Open Webcam

**File**: `app/routes/live_routes.py` → `inference_loop()` line 111

```python
cap = cv2.VideoCapture(0)  # 0 = default webcam
if not cap.isOpened():
    print('[ERROR] Cannot open camera')
    return

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

**What happens**:
1. Opens default webcam (device 0)
2. Sets resolution to 640×480 (VGA)
3. If camera fails, exits with error
4. Camera stays open for entire session

**Why 640×480**: Balance between speed and accuracy (smaller = faster, larger = more accurate)

---

### Step 4: Main Inference Loop (Runs Continuously)

**File**: `app/routes/live_routes.py` → `inference_loop()` line 140

```python
while state['running']:
    ret, frame = cap.read()
    if not ret:
        print('[WARNING] Failed to read frame')
        time.sleep(0.01)
        continue
```

**What happens** (repeats forever):
1. Read one frame from webcam
2. If frame read fails, skip and retry
3. Process the frame (next steps)
4. Small sleep to control FPS

**Loop runs at**: ~8-10 times per second (with processing)

---

### Step 5: Preprocess Frame

**File**: `app/routes/live_routes.py` → `inference_loop()` lines 159-161

```python
# Flip horizontally (mirror image for natural feel)
frame = cv2.flip(frame, 1)

# Convert BGR (OpenCV format) to RGB (MediaPipe format)
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
```

**Why flip**: Webcams show mirror image - feels more natural

**Why BGR→RGB**: 
- OpenCV uses BGR (Blue-Green-Red) color order
- MediaPipe expects RGB (Red-Green-B)
- Conversion required for correct colors

---

### Step 6: Extract Landmarks with MediaPipe

**File**: `app/routes/live_routes.py` → `inference_loop()` line 161

```python
results = holistic.process(rgb)
```

**What MediaPipe Holistic does internally**:
1. Runs CNN (Convolutional Neural Network) on RGB frame
2. Detects 33 body landmarks (pose)
3. Detects 21 left hand landmarks
4. Detects 21 right hand landmarks
5. Returns 3D coordinates (x, y, z) for each landmark

**Landmark structure**:
```
Pose (33 points):
  - Nose, eyes, ears, shoulders, elbows, wrists
  - Hips, knees, ankles
  - Each point has (x, y, z, visibility)

Left Hand (21 points):
  - Wrist, thumb (4 joints), index (4 joints), middle, ring, pinky
  - Each point has (x, y, z)

Right Hand (21 points):
  - Same as left hand
```

**Output**: `results` object containing all detected landmarks

---

### Step 7: Draw Skeleton Overlay (for visualization)

**File**: `app/routes/live_routes.py` → lines 164-169

```python
if results.pose_landmarks:
    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
if results.left_hand_landmarks:
    mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
if results.right_hand_landmarks:
    mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
```

**What it does**: Draws lines connecting landmarks on video frame

**Why**: User can see what system "sees" (debugging + visualization)

---

### Step 8: Extract and Normalize Landmarks

**File**: `src/similarity_engine.py` → `extract_and_normalize(results)`

**This is the MOST CRITICAL step** - converts raw landmarks to comparable features

```python
def extract_and_normalize(results):
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
    
    landmarks = np.concatenate([pose, lh, rh])  # 258 elements total
```

**Why extract this way**:
- Pose: 33 points × 4 values = 132 elements
- Left hand: 21 points × 3 values = 63 elements
- Right hand: 21 points × 3 values = 63 elements
- **Total: 258 elements**

---

### Step 9: Normalize Features (Scale & Position Invariance)

**File**: `src/similarity_engine.py` → continuation of `extract_and_normalize()`

**Normalization makes detection invariant to**:
- Distance from camera (scale)
- Position in frame (translation)
- Body size differences

**Algorithm**:

```python
# 1. Normalize pose relative to nose
pose_reshaped = pose_part.reshape(33, 4)
nose = pose_reshaped[0, :3].copy()  # Get nose position
pose_reshaped[:, :3] -= nose  # Subtract nose from all points
max_val = np.max(np.abs(pose_reshaped[:, :3]))
if max_val > 0:
    pose_reshaped[:, :3] /= max_val  # Scale to [-1, 1]
landmarks[:132] = pose_reshaped.flatten()

# 2. Normalize left hand relative to wrist
lh_reshaped = lh_part.reshape(21, 3)
wrist = lh_reshaped[0].copy()
lh_reshaped -= wrist
max_val = np.max(np.abs(lh_reshaped))
if max_val > 0:
    lh_reshaped /= max_val
landmarks[132:195] = lh_reshaped.flatten()

# 3. Normalize right hand relative to wrist
rh_reshaped = rh_part.reshape(21, 3)
wrist = rh_reshaped[0].copy()
rh_reshaped -= wrist
max_val = np.max(np.abs(rh_reshaped))
if max_val > 0:
    rh_reshaped /= max_val
landmarks[195:] = rh_reshaped.flatten()
```

**What normalization does**:
1. **Translation invariance**: Subtracts reference point (nose/wrist)
2. **Scale invariance**: Divides by max distance
3. **Result**: All features in range [-1, 1], centered at reference point

**Why this matters**: Person close to camera = same detection as person far away

---

### Step 10: Template Matching (Cosine Similarity)

**File**: `src/similarity_engine.py` → `match_landmarks()` lines 208-253

**Core algorithm**: Compare test landmarks with each template

```python
def match_landmarks(landmarks, threshold=0.15, bidirectional=True):
    best_match = None
    lowest_distance = float('inf')
    
    for word, template_coords in templates.items():
        # Mask out hands not in template
        masked_landmarks = mask_inactive_hands(landmarks, template_coords)
        
        # Compute cosine distance
        dist = cosine(masked_landmarks, template_coords)
        
        # If bidirectional, also test flipped version
        if bidirectional:
            flipped = flip_horizontal(masked_landmarks)
            dist_flipped = cosine(flipped, template_coords)
            dist = min(dist, dist_flipped)
        
        # Track best match
        if dist < lowest_distance:
            lowest_distance = dist
            best_match = word
    
    # Return if below threshold
    if lowest_distance < threshold:
        return best_match, lowest_distance
    else:
        return None, lowest_distance
```

---

### Step 11: Cosine Similarity Calculation

**File**: `scipy.spatial.distance.cosine()`

**Formula**:
```
cosine_distance = 1 - cosine_similarity
cosine_similarity = (A · B) / (||A|| × ||B||)

Where:
- A · B = dot product = Σ(A[i] × B[i])
- ||A|| = magnitude of A = √(Σ A[i]²)
- ||B|| = magnitude of B = √(Σ B[i]²)
```

**What it measures**: Angle between two vectors (not magnitude)

**Interpretation**:
- Distance = 0 → Identical direction (perfect match)
- Distance = 1 → Orthogonal (no similarity)
- Distance = 2 → Opposite direction

**Why cosine similarity**:
- Ignores magnitude differences
- Focuses on pattern/shape
- Perfect for normalized features

**Example**:
```
Test vector:    [0.5, 0.3, 0.8, ...]  (258 elements)
Template hello: [0.48, 0.31, 0.79, ...]
Template stop:  [0.2, 0.9, 0.1, ...]

cosine_distance(hello) = 0.04  ← Best match!
cosine_distance(stop) = 0.65

Result: "hello" with 96% confidence
```

---

### Step 12: Bidirectional Matching (Left/Right Hand Agnostic)

**File**: `src/similarity_engine.py` → `flip_horizontal()` lines 20-51

**Problem**: Template recorded with right hand, but user shows left hand

**Solution**: Test both original and horizontally-flipped versions

```python
def flip_horizontal(landmarks):
    flipped = landmarks.copy()
    
    # Flip pose x-coordinates
    pose = flipped[:132].reshape(33, 4)
    pose[:, 0] = -pose[:, 0]  # Negate x
    flipped[:132] = pose.flatten()
    
    # Swap left and right hands
    lh = flipped[132:195].reshape(21, 3).copy()
    rh = flipped[195:258].reshape(21, 3).copy()
    
    rh[:, 0] = -rh[:, 0]  # Flip right hand x
    lh[:, 0] = -lh[:, 0]  # Flip left hand x
    
    flipped[132:195] = rh.flatten()  # Right → Left
    flipped[195:258] = lh.flatten()  # Left → Right
    
    return flipped
```

**Why it works**:
- Flipping x-coordinate mirrors the pose
- Swapping hands converts left-hand gesture to right-hand equivalent
- Allows matching across handedness

---

### Step 13: Hand Masking (Inactive Hand Suppression)

**File**: `src/similarity_engine.py` → `mask_inactive_hands()` lines 54-81

**Problem**: Template has only right hand, but user shows both hands

**Solution**: Zero out hand coordinates that aren't in template

```python
def mask_inactive_hands(landmarks, template):
    masked = landmarks.copy()
    
    # Check which hands are active in template
    lh_active = np.any(template[132:195])  # Left hand has data?
    rh_active = np.any(template[195:258])  # Right hand has data?
    
    # Zero out hands not in template
    if not lh_active:
        masked[132:195] = 0  # Remove left hand
    if not rh_active:
        masked[195:258] = 0  # Remove right hand
    
    return masked
```

**Why**: Prevents false matches from extra hands

---

### Step 14: Decision Making (Threshold Check)

**File**: `app/routes/live_routes.py` → lines 216-228

```python
if lowest_distance < threshold:  # threshold = 0.15
    conf = round((1 - lowest_distance) * 100, 1)
    
    if best_match != last_word and (now - last_word_time) > cooldown:
        with state_lock:
            state['word'] = best_match.upper()
            state['confidence'] = conf / 100
            if best_match not in state['words']:
                state['words'].append(best_match)
        
        last_word = best_match
        last_word_time = now
        print(f'[DETECT] {best_match.upper()} ({conf}%)')
```

**Threshold logic**:
- Distance < 0.15 → Accept as valid detection
- Distance ≥ 0.15 → Reject (no match)

**Cooldown**: Prevents rapid re-detection of same sign (1 second)

**Confidence calculation**:
```
confidence = (1 - distance) × 100
Example: distance = 0.04 → confidence = 96%
```

---

### Step 15: Encode Frame for MJPEG Stream

**File**: `app/routes/live_routes.py` → line 243

```python
_, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
with frame_lock:
    latest_frame = buffer.tobytes()
```

**What it does**:
1. Encodes processed frame as JPEG
2. Quality = 85% (balance quality/speed)
3. Stores in memory for streaming

**Why MJPEG**: Browser can display as video stream without complex codecs

---

### Step 16: MJPEG Streaming to Browser

**File**: `app/routes/live_routes.py` → `generate_mjpeg()` lines 269-278

```python
def generate_mjpeg():
    while True:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.05)
                continue
            frame_bytes = latest_frame
        
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.033)  # ~30 FPS streaming
```

**How browser displays**:
```html
<img src="/video_feed" style="width: 100%;">
```

**Browser receives**: Continuous stream of JPEG images

**Result**: Real-time video with skeleton overlay

---

### Step 17: Status API (Frontend Polling)

**File**: `app/routes/live_routes.py` → `get_status()` lines 290-302

```python
@bp.route('/status')
def get_status():
    with state_lock:
        return jsonify({
            'word': state['word'],
            'confidence': round(state['confidence'], 2),
            'words': list(state['words']),
            'sentence': state['sentence'],
            'hand_detected': state['hand_detected'],
            'fps': state['fps'],
            'status': state['status'],
            'error': state.get('error'),
        })
```

**Frontend JavaScript** (in `index.html`):
```javascript
setInterval(() => {
    fetch('/status')
        .then(r => r.json())
        .then(data => {
            // Update UI with detected word, confidence, words list, sentence
        })
}, 100);  // Poll every 100ms
```

**What gets updated**:
- Current detected word
- Confidence percentage
- List of detected words
- AI-formed sentence
- Hand detection status
- FPS counter

---

### Step 18: Sentence Formation (After 10 Seconds)

**File**: `app/routes/live_routes.py` → lines 204-221

```python
# Check for sentence formation (10 seconds no hand)
with state_lock:
    hand_lost_time = state.get('hand_lost_time')

if hand_lost_time and not state.get('sentence_triggered'):
    absence = now - hand_lost_time
    if absence >= 10.0 and len(state['words']) > 0:
        state['sentence_triggered'] = True
        
        words = list(state['words'])
        print(f'[SENTENCE] Forming from: {words}')
        
        sentence = form_sentence_gemini(words)
        
        with state_lock:
            state['sentence'] = sentence
            # Auto-reset
            state['words'] = []
            state['hand_lost_time'] = None
            state['sentence_triggered'] = False
        
        print(f'[SENTENCE] {sentence}')
```

**Timer mechanism**:
1. When hand disappears: `hand_lost_time = current_time`
2. Every frame: Check if `current_time - hand_lost_time >= 10 seconds`
3. If yes AND words detected: Form sentence

---

### Step 19: Gemini AI Sentence Formation

**File**: `app/routes/live_routes.py` → `form_sentence_gemini()` lines 49-82

```python
def form_sentence_gemini(words):
    if not words:
        return ''
    
    # Remove consecutive duplicates
    cleaned = [words[0]]
    for w in words[1:]:
        if w != cleaned[-1]:
            cleaned.append(w)
    
    api_key = Config.GEMINI_API_KEY
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""You are a translator for Indian Sign Language (ISL). 
    Create ONE natural English sentence from these ISL words: {', '.join(cleaned)}
    
    Rules:
    1. Remove any duplicate words - use each word only once
    2. Create a grammatically correct, natural English sentence
    3. The sentence should flow naturally as a human would speak it
    4. Keep the meaning and context of the words
    5. Output ONLY the sentence, nothing else
    
    Words: {', '.join(cleaned)}
    Natural sentence:"""
    
    response = model.generate_content(prompt)
    result = response.text.strip()
    
    return result
```

**What happens**:
1. Remove duplicate words: `['stop', 'stop', 'one']` → `['stop', 'one']`
2. Create prompt with instructions
3. Call Google Gemini 2.0 Flash API
4. Receive natural sentence: `"Stop, one time."`
5. Return sentence for display

**Example**:
```
Input words: ['hello', 'good', 'morning']
Gemini output: "Good morning, hello!"
```

---

### Step 20: Auto-Reset After Sentence

**File**: `app/routes/live_routes.py` → lines 218-221

```python
with state_lock:
    state['sentence'] = sentence
    state['words'] = []  # Clear words list
    state['hand_lost_time'] = None  # Reset timer
    state['sentence_triggered'] = False  # Ready for next cycle
```

**Why auto-reset**:
- Prepare for next detection session
- Prevent old words from affecting new sentences
- Clean slate for user

---

## 🎯 Summary: Complete Flow

1. **Start**: Flask launches, inference thread begins
2. **Load**: Templates loaded from `Sign_Templates/`
3. **Capture**: Webcam opens, reads frames continuously
4. **Extract**: MediaPipe extracts 258 landmarks per frame
5. **Normalize**: Features scaled and centered for invariance
6. **Match**: Cosine similarity compared to all templates
7. **Decide**: Best match accepted if distance < 0.15
8. **Display**: Word shown with confidence %
9. **Accumulate**: Words added to list
10. **Wait**: 10-second timer starts when hand disappears
11. **Form**: Gemini AI creates natural sentence
12. **Reset**: Clear state, ready for next detection

**Total processing time per frame**: ~120-150ms  
**Effective FPS**: 5-8 frames per second

---

**Next**: Read `04_ML_JUSTIFICATION.md` to understand why this counts as a Machine Learning project.
