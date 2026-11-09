""" Live webcam detection with robust camera, colored skeleton, and bilingual audio """
import cv2
import numpy as np
import time
import threading
import base64
import os
from flask import Blueprint, Response, render_template, jsonify
from app.config import Config
from src.similarity_engine import extract_and_normalize
import mediapipe as mp
import io

bp = Blueprint('live', __name__)

# ═══════════════════════════════════════════════════════════════
# GLOBAL STATE
# ═══════════════════════════════════════════════════════════════

state = {
    'word': '',
    'confidence': 0.0,
    'words': [],
    'sentence': '',
    'hindi_sentence': '',
    'hand_detected': False,
    'fps': 0,
    'status': 'initializing',
    'hand_lost_time': None,
    'running': True,
    'error': None,
    'sentence_triggered': False,
}

state_lock = threading.Lock()
latest_frame = None
frame_lock = threading.Lock()
inference_thread = None

# ═══════════════════════════════════════════════════════════════
# COSINE DISTANCE
# ═══════════════════════════════════════════════════════════════

def cosine(a, b):
    """Calculate cosine distance between two vectors"""
    a = np.array(a, dtype=np.float64)
    b = np.array(b, dtype=np.float64)
    min_len = min(len(a), len(b))
    a = a[:min_len]
    b = b[:min_len]
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 1.0
    return 1 - (dot_product / (norm_a * norm_b))

# ═══════════════════════════════════════════════════════════════
# COLORED SKELETON DRAWING
# ═══════════════════════════════════════════════════════════════

def draw_colored_skeleton(frame, results):
    """Draw skeleton with purple body, green left hand, red right hand"""
    mp_holistic = mp.solutions.holistic
    mp_drawing = mp.solutions.drawing_utils
    drawing_spec_landmark = mp_drawing.DrawingSpec

    # Purple body (pose)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=drawing_spec_landmark(color=(180, 105, 255), thickness=2, circle_radius=2),
            connection_drawing_spec=drawing_spec_landmark(color=(180, 105, 255), thickness=2),
        )

    # Green left hand
    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
            landmark_drawing_spec=drawing_spec_landmark(color=(0, 255, 0), thickness=2, circle_radius=2),
            connection_drawing_spec=drawing_spec_landmark(color=(0, 255, 0), thickness=2),
        )

    # Red right hand
    if results.right_hand_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
            landmark_drawing_spec=drawing_spec_landmark(color=(0, 0, 255), thickness=2, circle_radius=2),
            connection_drawing_spec=drawing_spec_landmark(color=(0, 0, 255), thickness=2),
        )

# ═══════════════════════════════════════════════════════════════
# CAMERA THREAD
# ═══════════════════════════════════════════════════════════════

def camera_thread():
    """Dedicated thread for camera access"""
    global latest_frame, state

    print('[CAMERA] ========== STARTING CAMERA THREAD ==========')

    # --- ROBUST CAMERA OPEN WITH TIMEOUT ---
    cap = None

    def _try_open(idx, backend, result_holder):
        """Open camera in a sub-thread so we can timeout if it hangs"""
        try:
            if backend is not None:
                c = cv2.VideoCapture(idx, backend)
            else:
                c = cv2.VideoCapture(idx)
            if c.isOpened():
                ret, frm = c.read()
                if ret and frm is not None and frm.size > 0:
                    result_holder['cap'] = c
                    result_holder['shape'] = frm.shape
                    return
                c.release()
            else:
                try:
                    c.release()
                except Exception:
                    pass
        except Exception:
            pass

    # Try DEFAULT first (less likely to hang), then CAP_DSHOW
    attempts = [
        (0, None, 'DEFAULT idx=0'),
        (0, cv2.CAP_DSHOW, 'CAP_DSHOW idx=0'),
        (1, None, 'DEFAULT idx=1'),
        (1, cv2.CAP_DSHOW, 'CAP_DSHOW idx=1'),
    ]

    for idx, backend, label in attempts:
        print(f'[CAMERA] Trying {label} (8s timeout)...')
        result = {}
        t = threading.Thread(target=_try_open, args=(idx, backend, result), daemon=True)
        t.start()
        t.join(timeout=8)
        if 'cap' in result:
            cap = result['cap']
            print(f'[CAMERA] SUCCESS with {label} - frame shape: {result["shape"]}')
            break
        else:
            print(f'[CAMERA] {label} - failed or timed out')

    if cap is None or not cap.isOpened():
        print('[CAMERA] ERROR: Cannot open any camera!')
        with state_lock:
            state['status'] = 'error'
            state['error'] = 'Camera not available - close other apps using camera and restart'
        return

    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f'[CAMERA] Resolution: {w}x{h}')

    with state_lock:
        state['status'] = 'camera_ready'

    # --- MediaPipe setup ---
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    print('[CAMERA] MediaPipe Holistic initialized')

    # --- Load templates ---
    templates_dir = Config.SIGN_TEMPLATES_DIR
    templates = {}
    for file in os.listdir(templates_dir):
        if file.endswith(".npy"):
            word = file.replace(".npy", "")
            templates[word] = np.load(os.path.join(templates_dir, file))
    print(f'[CAMERA] Loaded {len(templates)} templates: {list(templates.keys())}')

    if not templates:
        print('[CAMERA] ERROR: No templates found!')
        with state_lock:
            state['status'] = 'error'
            state['error'] = 'No sign templates found'
        cap.release()
        return

    threshold = 0.15
    last_word = None
    last_word_time = 0
    cooldown = 1.0
    hand_was_present = False
    fps_counter = 0
    fps_time = time.time()
    frame_count = 0
    SENTENCE_TIMEOUT = 10.0
    consecutive_failures = 0

    print('[CAMERA] Starting main capture loop...')

    try:
        while state['running']:
            ret, frame = cap.read()
            if not ret or frame is None:
                consecutive_failures += 1
                if consecutive_failures > 30:
                    print('[CAMERA] Too many consecutive read failures, restarting camera...')
                    cap.release()
                    time.sleep(1)
                    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    if not cap.isOpened():
                        cap = cv2.VideoCapture(0)
                    consecutive_failures = 0
                    if not cap.isOpened():
                        print('[CAMERA] Camera restart failed')
                        with state_lock:
                            state['status'] = 'error'
                            state['error'] = 'Camera disconnected'
                        break
                time.sleep(0.01)
                continue

            consecutive_failures = 0
            frame_count += 1
            now = time.time()

            # FPS counter
            fps_counter += 1
            if now - fps_time > 1.0:
                with state_lock:
                    state['fps'] = int(fps_counter / (now - fps_time))
                fps_counter = 0
                fps_time = now

            # Process frame
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(rgb)

            # Draw colored skeleton
            draw_colored_skeleton(frame, results)

            # Extract landmarks
            current_landmarks = extract_and_normalize(results)

            # Check if hands are visible
            hands_visible = bool(np.any(current_landmarks[132:]))

            with state_lock:
                state['hand_detected'] = hands_visible

            # Track hand presence and 10-second sentence trigger
            if hand_was_present and not hands_visible:
                with state_lock:
                    state['hand_lost_time'] = now
                print('[CAMERA] Hand lost - starting 10s timer')
            elif hands_visible:
                with state_lock:
                    state['hand_lost_time'] = None
                    state['sentence_triggered'] = False

            # Check 10-second timeout for sentence formation
            with state_lock:
                lost_time = state['hand_lost_time']
                words_collected = list(state['words'])
                already_triggered = state['sentence_triggered']

            if (lost_time is not None
                    and not hands_visible
                    and len(words_collected) > 0
                    and not already_triggered
                    and (now - lost_time) >= SENTENCE_TIMEOUT):
                print(f'[SENTENCE] 10s timeout! Forming sentence from: {words_collected}')
                try:
                    sentence = form_sentence_gemini(words_collected)
                    with state_lock:
                        state['sentence'] = sentence
                        state['sentence_triggered'] = True
                    print(f'[SENTENCE] English: {sentence}')
                    with state_lock:
                        hindi = state.get('hindi_sentence', '')
                    print(f'[SENTENCE] Hindi: {hindi}')
                except Exception as e:
                    print(f'[SENTENCE] Error forming sentence: {e}')
                    with state_lock:
                        state['sentence_triggered'] = True

            # Detection logic
            if hands_visible and len(templates) > 0:
                best_match = None
                lowest_distance = float('inf')

                for word, template_coords in templates.items():
                    dist = cosine(current_landmarks, template_coords)
                    if dist < lowest_distance:
                        lowest_distance = dist
                        best_match = word

                if lowest_distance < threshold:
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
                else:
                    with state_lock:
                        state['word'] = ''
                        state['confidence'] = 0
                    last_word = None
            else:
                with state_lock:
                    state['word'] = ''
                    state['confidence'] = 0
                last_word = None

            hand_was_present = hands_visible

            # Encode frame for MJPEG stream
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            with frame_lock:
                latest_frame = buffer.tobytes()

            if frame_count % 200 == 0:
                print(f'[CAMERA] Frame {frame_count}, FPS: {state["fps"]}')

            time.sleep(0.015)

    except Exception as e:
        print(f'[CAMERA] Camera thread error: {e}')
        import traceback
        traceback.print_exc()
        with state_lock:
            state['status'] = 'error'
            state['error'] = str(e)
    finally:
        cap.release()
        holistic.close()
        print('[CAMERA] Camera thread stopped')

# ═══════════════════════════════════════════════════════════════
# HINDI DICTIONARY FOR OFFLINE FALLBACK
# ═══════════════════════════════════════════════════════════════

HINDI_WORDS = {
    'break':    'रुको',
    'come':     'आओ',
    'cry':      'रोना',
    'good':     'अच्छा',
    'hello':    'नमस्ते',
    'morning':  'सुबह',
    'one':      'एक',
    'stop':     'रुको',
    'thankyou': 'धन्यवाद',
    'three':    'तीन',
    'two':      'दो',
}

def _build_hindi_fallback(words):
    """Build a Hindi sentence from the word dictionary (no Gemini needed)"""
    hindi_parts = []
    for w in words:
        w_lower = w.lower()
        if w_lower in HINDI_WORDS:
            hindi_parts.append(HINDI_WORDS[w_lower])
        else:
            hindi_parts.append(w)
    return ', '.join(hindi_parts) + '।'

# ═══════════════════════════════════════════════════════════════
# AI SENTENCE FORMATION (OpenRouter + Gemini + Dictionary fallback)
# ═══════════════════════════════════════════════════════════════

import json
import urllib.request
import urllib.error

def _call_openrouter(prompt):
    """Call OpenRouter API (free models, no SDK needed)"""
    api_key = getattr(Config, 'OPENROUTER_API_KEY', '')
    if not api_key:
        return None

    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:5000',
    }
    # Use a free model
    data = json.dumps({
        'model': 'google/gemma-4-26b-a4b-it:free',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 200,
        'temperature': 0.3,
    }).encode('utf-8')

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            text = result['choices'][0]['message']['content'].strip()
            if text:
                print(f'[AI] OpenRouter response: {text[:80]}')
                return text
    except Exception as e:
        print(f'[AI] OpenRouter error: {e}')
    return None

def _call_gemini(prompt):
    """Call Gemini API as fallback"""
    try:
        import google.generativeai as genai
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            return None
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text:
            print(f'[AI] Gemini response: {text[:80]}')
            return text
    except Exception as e:
        print(f'[AI] Gemini error: {e}')
    return None

def _call_ai(prompt):
    """Try OpenRouter first, then Gemini"""
    result = _call_openrouter(prompt)
    if result:
        return result
    return _call_gemini(prompt)

def form_sentence_gemini(words):
    """Form sentence using AI (OpenRouter/Gemini), with offline Hindi fallback"""
    if not words:
        return ''

    # Remove consecutive duplicates
    cleaned = [words[0]]
    for w in words[1:]:
        if w != cleaned[-1]:
            cleaned.append(w)

    # Always build Hindi fallback first (works without internet/API)
    hindi_fallback = _build_hindi_fallback(cleaned)

    # Try AI for English sentence
    eng_prompt = f"""Convert these Indian Sign Language words into ONE natural English sentence.
Rules: Use proper grammar. Output ONLY the sentence.
Words: {', '.join(cleaned)}
Sentence:"""

    english_sentence = _call_ai(eng_prompt)

    if not english_sentence:
        # AI unavailable — use simple fallback
        with state_lock:
            state['hindi_sentence'] = hindi_fallback
        return ', '.join(cleaned).capitalize() + '.'

    if not english_sentence.endswith(('.', '!', '?')):
        english_sentence += '.'

    # Try AI for Hindi translation
    hindi_prompt = f"""Translate to Hindi (Devanagari script). Output ONLY the Hindi sentence.
English: {english_sentence}
Hindi:"""

    hindi_sentence = _call_ai(hindi_prompt)

    if hindi_sentence and len(hindi_sentence) > 2:
        if not hindi_sentence.endswith(('.', '!', '?', '।')):
            hindi_sentence += '।'
    else:
        hindi_sentence = hindi_fallback

    with state_lock:
        state['hindi_sentence'] = hindi_sentence

    return english_sentence

# ═══════════════════════════════════════════════════════════════
# AUDIO GENERATION
# ═══════════════════════════════════════════════════════════════

def generate_audio(sentence, lang='en'):
    """Generate audio from text using gTTS"""
    if not sentence or not isinstance(sentence, str) or not sentence.strip():
        return None

    sentence = sentence.strip()
    # Use ASCII-safe print to avoid Windows cp1252 crashes with Devanagari
    print(f'[AUDIO] Generating {lang} audio ({len(sentence)} chars)')

    try:
        from gtts import gTTS

        if lang == 'hi':
            # gTTS handles Devanagari text natively with lang='hi'
            try:
                tts = gTTS(text=sentence, lang='hi', slow=False)
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                buf.seek(0)
                data = buf.read()
                if data and len(data) > 0:
                    print(f'[AUDIO] Hindi gTTS success: {len(data)} bytes')
                    return base64.b64encode(data).decode('utf-8')
            except Exception as e:
                print(f'[AUDIO] Hindi gTTS failed: {e}')

            # Fallback: speak sentence in English voice
            try:
                tts = gTTS(text=sentence, lang='en', slow=False)
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                buf.seek(0)
                data = buf.read()
                if data and len(data) > 0:
                    print(f'[AUDIO] English fallback for Hindi: {len(data)} bytes')
                    return base64.b64encode(data).decode('utf-8')
            except Exception as e:
                print(f'[AUDIO] English fallback also failed: {e}')

            return None
        else:
            # English audio
            tts = gTTS(text=sentence, lang='en', slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            data = buf.read()
            if data and len(data) > 0:
                print(f'[AUDIO] English success: {len(data)} bytes')
                return base64.b64encode(data).decode('utf-8')
            return None

    except Exception as e:
        print(f'[AUDIO] Fatal error: {e}')
        return None

# ═══════════════════════════════════════════════════════════════
# FLASK ROUTES
# ═══════════════════════════════════════════════════════════════

def generate_mjpeg():
    """MJPEG stream generator"""
    while True:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.05)
                continue
            frame_bytes = latest_frame
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.033)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/status')
def get_status():
    with state_lock:
        return jsonify({
            'word': state['word'],
            'confidence': round(state['confidence'], 2),
            'words': list(state['words']),
            'sentence': state['sentence'],
            'hindi_sentence': state['hindi_sentence'],
            'hand_detected': state['hand_detected'],
            'fps': state['fps'],
            'status': state['status'],
            'error': state.get('error'),
        })

@bp.route('/reset', methods=['POST'])
def reset():
    with state_lock:
        state['words'] = []
        state['sentence'] = ''
        state['hindi_sentence'] = ''
        state['word'] = ''
        state['confidence'] = 0
        state['hand_lost_time'] = None
        state['sentence_triggered'] = False
    return jsonify({'ok': True})

@bp.route('/templates')
def get_templates():
    """Get list of available templates"""
    try:
        templates_dir = Config.SIGN_TEMPLATES_DIR
        templates = []
        for file in os.listdir(templates_dir):
            if file.endswith(".npy"):
                templates.append(file.replace(".npy", ""))
        return jsonify({'templates': templates})
    except Exception as e:
        return jsonify({'templates': [], 'error': str(e)})

@bp.route('/audio/english')
def get_english_audio():
    with state_lock:
        sentence = state.get('sentence', '')

    if not sentence or sentence.strip() == '':
        return jsonify({'audio': None, 'success': False, 'error': 'No sentence available'})

    try:
        audio_b64 = generate_audio(sentence, lang='en')
        if audio_b64:
            return jsonify({'audio': audio_b64, 'success': True})
        else:
            return jsonify({'audio': None, 'success': False, 'error': 'Audio generation failed'})
    except Exception as e:
        return jsonify({'audio': None, 'success': False, 'error': str(e)})

@bp.route('/audio/hindi')
def get_hindi_audio():
    with state_lock:
        sentence = state.get('sentence', '')
        hindi_sentence = state.get('hindi_sentence', '')

    if not sentence or sentence.strip() == '':
        return jsonify({'audio': None, 'success': False, 'error': 'No sentence available'})

    try:
        text_to_speak = hindi_sentence if (hindi_sentence and hindi_sentence.strip()) else sentence
        print(f'[AUDIO/HI] Speaking hindi text ({len(text_to_speak)} chars)')
        audio_b64 = generate_audio(text_to_speak, lang='hi')
        if audio_b64:
            return jsonify({'audio': audio_b64, 'success': True})
        else:
            return jsonify({'audio': None, 'success': False, 'error': 'Hindi audio generation failed'})
    except Exception as e:
        return jsonify({'audio': None, 'success': False, 'error': str(e)})

@bp.route('/audio/test')
def test_audio():
    """Test endpoint to verify audio works"""
    try:
        audio_b64 = generate_audio("Hello, this is a test.", lang='en')
        if audio_b64:
            return jsonify({'audio': audio_b64, 'success': True, 'message': 'Test audio OK'})
        else:
            return jsonify({'audio': None, 'success': False, 'error': 'Test audio failed'})
    except Exception as e:
        return jsonify({'audio': None, 'success': False, 'error': str(e)})

def start_inference_thread():
    global inference_thread
    if inference_thread is None or not inference_thread.is_alive():
        inference_thread = threading.Thread(target=camera_thread, daemon=True)
        inference_thread.start()
        print('[LIVE] Inference thread started')