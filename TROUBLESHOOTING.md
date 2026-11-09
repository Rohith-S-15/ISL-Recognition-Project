# Live Detection Troubleshooting Guide

## Status Messages

When you click "Start Camera", you should see these status messages:

1. **"Loading MediaPipe models..."** - Good, starting up
2. **"MediaPipe loaded - Ready"** - Success! Ready to detect
3. **"Processing frame..."** - Actively processing video
4. **"Hand detected!"** - Found a hand!
5. **"Detected: word XX%"** - Matched a sign!

## Check Browser Console (F12)

### Expected Console Output:
```
Initializing MediaPipe...
Loading: holistic.bin
MediaPipe initialized successfully
Processing frame...
Processing frame...
Hand detected!
Matching landmarks, length: 258
Detected: hello 87%
```

### If you see errors:

**"MediaPipe Holistic not loaded"**
- Check internet connection
- CDN might be blocked
- Try different browser

**"Cannot read property 'send' of undefined"**
- MediaPipe didn't load
- Refresh page
- Check console for earlier errors

**"No templates found"**
- Go to `/api/templates` in browser
- Should return: `{"count": 9, "templates": [...]}`
- If empty, record templates with `sign_studio.py`

## Visual Checks

### You should see:
- ✅ Your video feed
- ✅ Purple skeleton lines on your body
- ✅ Green lines on left hand (if visible)
- ✅ Red lines on right hand (if visible)
- ✅ Words appearing in "Detected Words" list
- ✅ Status showing "Processing frame..."

### You should NOT see:
- ❌ Black screen
- ❌ "Camera not found" error
- ❌ Red error messages
- ❌ Blank status

## Quick Test

1. Open browser DevTools (F12)
2. Go to Console tab
3. Type: `typeof Holistic`
4. Should return: `"function"`
5. If returns `"undefined"` - MediaPipe not loaded!

## Common Issues

### Issue: Status shows "Waiting to start..." forever
**Fix:** Click "Start Camera" button

### Issue: "Loading MediaPipe models..." but never completes
**Fix:** 
- Check internet connection
- Try different browser (Chrome recommended)
- Check if CDN is blocked by firewall

### Issue: Camera works but no skeleton lines
**Fix:**
- Make sure hands are visible
- Good lighting required
- Hands should be in frame
- Try moving closer to camera

### Issue: Shows "0 words detected"
**Fix:**
- Make sure templates exist (check bottom of page)
- Show clear hand signs
- Wait at least 1-2 seconds per sign
- Check console for "Detected: word XX%" messages

## Test Steps

1. **Test 1: Basic Load**
   - Open page
   - Check console: `typeof Holistic` should be "function"
   - Check templates list shows 9 templates

2. **Test 2: Camera**
   - Click "Start Camera"
   - Should see your video
   - Status: "MediaPipe loaded - Ready"

3. **Test 3: Detection**
   - Show hand to camera
   - Console should show: "Hand detected!"
   - If hands visible, should match templates
   - Words should appear in list

4. **Test 4: Sentence**
   - Detect 2-3 words
   - Stop showing hands
   - Wait 7 seconds
   - Should form sentence

## Still Not Working?

1. **Check Flask is running**: `python run_dashboard.py`
2. **Check templates exist**: Should see 9 templates listed
3. **Check browser console**: Look for errors
4. **Try different browser**: Chrome recommended
5. **Check internet**: MediaPipe loads from CDN
6. **Refresh page**: Clear any cached errors

## Success Indicators

You'll know it's working when:
- ✅ Status shows "Processing frame..."
- ✅ Console shows "Hand detected!"
- ✅ Words appear in list
- ✅ You see colored skeleton lines
- ✅ After 7 seconds, sentence forms
