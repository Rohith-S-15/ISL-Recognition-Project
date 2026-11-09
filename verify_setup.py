"""
Quick Test Script - Verify ISL Similarity App Setup
Run this to ensure everything is configured correctly
"""

import os
import sys

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def check_item(condition, success_msg, error_msg):
    if condition:
        print(f"  [OK] {success_msg}")
        return True
    else:
        print(f"  [ERROR] {error_msg}")
        return False

def main():
    print_header("ISL SIMILARITY APP - SETUP VERIFICATION")
    
    all_good = True
    
    # Check Python version
    print("\n1. Checking Python...")
    py_version = sys.version_info
    all_good &= check_item(
        py_version.major >= 3 and py_version.minor >= 8,
        f"Python {py_version.major}.{py_version.minor}.{py_version.micro}",
        f"Python version too old: {py_version.major}.{py_version.minor} (need 3.8+)"
    )
    
    # Check required packages
    print("\n2. Checking installed packages...")
    packages = ['flask', 'cv2', 'mediapipe', 'numpy', 'scipy', 'customtkinter']
    for pkg in packages:
        try:
            __import__(pkg)
            all_good &= check_item(True, f"{pkg} is installed", "")
        except ImportError:
            all_good &= check_item(False, "", f"{pkg} NOT installed - run: pip install -r requirements.txt")
    
    # Check project structure
    print("\n3. Checking project structure...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    dirs_to_check = [
        ('Sign_Templates', 'Templates directory'),
        ('app', 'Flask app directory'),
        ('database', 'Database directory'),
        ('uploads', 'Uploads directory'),
        ('src', 'Engine source directory'),
        ('app/templates', 'HTML templates directory'),
        ('app/routes', 'Routes directory'),
        ('app/static', 'Static files directory'),
    ]
    
    for dir_name, desc in dirs_to_check:
        dir_path = os.path.join(base_dir, dir_name)
        all_good &= check_item(
            os.path.exists(dir_path),
            f"{desc} exists",
            f"{desc} NOT FOUND: {dir_path}"
        )
    
    # Check key files
    print("\n4. Checking key files...")
    files_to_check = [
        ('run_dashboard.py', 'Dashboard launcher'),
        ('sign_studio.py', 'Desktop app'),
        ('requirements.txt', 'Dependencies'),
        ('src/similarity_engine.py', 'Similarity engine'),
        ('app/app.py', 'Flask app'),
        ('app/config.py', 'Configuration'),
    ]
    
    for file_name, desc in files_to_check:
        file_path = os.path.join(base_dir, file_name)
        all_good &= check_item(
            os.path.exists(file_path),
            f"{desc} found",
            f"{desc} NOT FOUND: {file_path}"
        )
    
    # Check templates
    print("\n5. Checking templates...")
    templates_dir = os.path.join(base_dir, 'Sign_Templates')
    if os.path.exists(templates_dir):
        npy_files = [f for f in os.listdir(templates_dir) if f.endswith('.npy')]
        all_good &= check_item(
            len(npy_files) > 0,
            f"{len(npy_files)} templates found: {', '.join([f.replace('.npy', '') for f in npy_files[:5]])}{'...' if len(npy_files) > 5 else ''}",
            "No templates found - Use sign_studio.py to record templates"
        )
    
    # Check uploads folder writable
    print("\n6. Checking file permissions...")
    uploads_dir = os.path.join(base_dir, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    try:
        test_file = os.path.join(uploads_dir, '.test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        all_good &= check_item(True, "Uploads folder is writable", "")
    except:
        all_good &= check_item(False, "", "Cannot write to uploads folder - check permissions")
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    if all_good:
        print("\n  [SUCCESS] All checks passed! Ready to run:")
        print("\n  Command 1: python run_dashboard.py")
        print("  -> Starts web dashboard on http://localhost:5000")
        print("\n  Command 2: python sign_studio.py")
        print("  -> Starts desktop app for recording templates")
        print("\n  Command 3: python debug_video_analysis.py")
        print("  -> Analyzes test videos for troubleshooting")
    else:
        print("\n  [WARNING] Some checks failed. Please fix the issues above.")
        print("\n  Common fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Record templates: python sign_studio.py")
        print("  3. Check folder permissions")
    
    print(f"\n{'='*60}\n")
    return all_good

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
