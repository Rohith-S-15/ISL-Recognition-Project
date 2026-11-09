# ISL Similarity App - Error Resolution Guide

## Common Errors & Fixes

---

## Error 1: "Error processing video" (Generic Error)

### What to do:

1. **Check if templates exist:**
   ```bash
   ls Sign_Templates/
   ```
   Should show `.npy` files like: `hello.npy`, `cry.npy`, etc.

2. **Check video file:**
   - Is it a valid MP4/AVI/MOV file?
   - Try a different video file
   - Check file size (should be less than 500MB)

3. **Check console output:**
   - Look at terminal where Flask is running
   - You'll see detailed error messages there

---

## Error 2: "No hands detected in any frame"

### Why it happens:
- Video quality too low
- Hands too far from camera
- Poor lighting
- Hand not clearly visible

### Fix:
1. Record a NEW template that looks like your test video
2. Move CLOSER to camera
3. Improve lighting (use a lamp if needed)
4. Ensure hand is in frame for entire video

---

## Error 3: "Video file not found"

### Why it happens:
- File was deleted
- Wrong file path
- Upload folder has issue

### Fix:
1. Upload video again
2. Check `uploads/` folder exists
3. Check disk space available

---

## Error 4: View button doesn't work / Video plays but with no audio

### Why it happens:
- Video file was deleted after processing
- File permissions issue
- Browser cache

### Fix:
1. **IMPORTANT: Don't delete uploaded videos!**
   - Uploaded videos are now KEPT in `uploads/` folder
   - This fix was applied in latest version
   - Re-upload your video

2. Clear browser cache:
   - Press F12 → Application → Clear Storage → Clear all

3. Try different browser

---

## Error 5: Result shows "Unknown" even though it matched

### Why it happens:
- Distance threshold too strict (0.15)
- Template and test video too different
- Wrong hand (but now fixed with bidirectional!)

### Fix:
1. **Use bidirectional matching:**
   - Already enabled by default
   - Works with left AND right hands now

2. **Record better template:**
   - Record when you're EXACTLY as you perform test
   - Same distance from camera
   - Same hand position
   - Same lighting

3. **Run debug script:**
   ```bash
   python debug_video_analysis.py
   ```
   - See exact distances
   - Check hand detection rate

---

## Error 6: "No file selected" or "No file provided"

### Why it happens:
- Didn't select file in upload
- File selection got cleared

### Fix:
1. Click on drop zone
2. Select valid video file
3. Wait for preview to show
4. Then click "Process Video"

---

## Error 7: Application won't start / "Address already in use"

### Why it happens:
- Port 5000 already in use
- Flask server didn't close properly

### Fix:
```bash
# Kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Then restart
python run_dashboard.py
```

---

## Error 8: "No templates loaded"

### Why it happens:
- `Sign_Templates/` folder is empty
- Wrong folder path

### Fix:
1. **Record templates:**
   ```bash
   python sign_studio.py
   ```
   - Click "Start Translating"
   - Make a sign
   - Click "Record New Sign"
   - Enter name and save

2. **OR use debug script to see templates:**
   ```bash
   python debug_video_analysis.py
   ```

---

## Error 9: Flask shows "Traceback" or "AttributeError"

### Why it happens:
- Code issue or missing import
- Database corruption

### Fix:
1. **Delete database and recreate:**
   ```bash
   rm database/results.db
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Restart Flask:**
   ```bash
   python run_dashboard.py
   ```

---

## Error 10: Video plays but with glitches / Very slow

### Why it happens:
- Large video file
- Slow disk
- Browser issue

### Fix:
1. Use smaller video (under 50MB)
2. Convert to optimized MP4:
   ```bash
   ffmpeg -i video.mp4 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k output.mp4
   ```
3. Try Chrome instead of Firefox

---

## Debugging Steps

### Step 1: Check Flask Console
Look at terminal where Flask runs:
```
Error processing video: [specific error message here]
```

Copy this error message to understand what went wrong.

### Step 2: Run Debug Script
```bash
python debug_video_analysis.py
```
This analyzes cry.mp4 and come.mp4, showing:
- Hand detection rate
- Distances to each template
- Whether it passed threshold

### Step 3: Check Database
```bash
# View all results
sqlite3 database/results.db "SELECT * FROM test_results;"

# Delete problematic results
sqlite3 database/results.db "DELETE FROM test_results WHERE recognized_words='Unknown';"
```

### Step 4: Verify Templates
```bash
ls -la Sign_Templates/
# Should show .npy files
# Example: hello.npy, cry.npy, come.npy
```

---

## Recent Fixes Applied (v2)

### 1. ✅ Video File Storage
- **Before:** Videos were deleted after processing → View button broke
- **After:** Videos now kept in `uploads/` folder → View button works!

### 2. ✅ Better Error Messages
- **Before:** Generic "error processing video" → Hard to debug
- **After:** Detailed error messages in console → Easy to diagnose

### 3. ✅ Bidirectional Matching
- **Before:** Right-hand template only matched right-hand videos
- **After:** Works with BOTH left and right hands!

### 4. ✅ Template Validation
- **Before:** Silently failed if no templates
- **After:** Clear error message if no templates found

---

## If Everything Fails

### Complete Reset:

```bash
# Stop Flask (Ctrl+C)

# Delete database
rm database/results.db

# Delete uploads
rm uploads/*

# Delete any corrupted files
rm database/*

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Restart Flask
python run_dashboard.py
```

### Verify Setup:

```bash
# Check Python version (should be 3.9+)
python --version

# Check pip packages
pip list | grep -E "flask|mediapipe|opencv|scipy"

# Check templates exist
ls Sign_Templates/*.npy

# Check database path
ls -la database/
```

---

## Support

If you still get errors:

1. **Run debug script:**
   ```bash
   python debug_video_analysis.py
   ```

2. **Check console output:**
   - Look at terminal where Flask runs
   - Copy full error message

3. **Check FIXES_IMPLEMENTED.md:**
   - Technical details of all changes

4. **Check COMMANDS_GUIDE.md:**
   - All available commands

---

## Key Points to Remember

- ✅ Videos are now **KEPT** after processing (not deleted)
- ✅ Bidirectional matching is **ON** by default
- ✅ Error messages are **DETAILED** for easy debugging
- ✅ Template validation **CHECKS** for empty folders
- ✅ Use debug script to analyze unknown videos

---

Good luck! 🚀
