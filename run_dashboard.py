"""
ISL Similarity Studio - Dashboard Launcher
===========================================
Run this file to start the Flask web dashboard.

Usage:
    python run_dashboard.py

Then open your browser to:
    http://localhost:5000
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import create_app

if __name__ == '__main__':
    print("=" * 60)
    print("  ISL Similarity Studio - Web Dashboard")
    print("=" * 60)
    print()
    print("  Starting Flask server...")
    print("  Open your browser to: http://localhost:5000")
    print()
    print("  Press Ctrl+C to stop the server.")
    print("=" * 60)
    print()

    app = create_app()

    # Start inference thread BEFORE Flask server
    try:
        from app.routes import live_routes
        live_routes.start_inference_thread()
        print("[MAIN] Inference thread started successfully")
    except Exception as e:
        print(f'[MAIN] WARNING: Could not start live inference: {e}')
        import traceback
        traceback.print_exc()

    # Disable debug mode to prevent camera conflicts from reloader
    app.run(debug=False, host='0.0.0.0', port=5000)
