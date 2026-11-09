""" Flask app initialization for ISL Similarity App """

import os
import cv2
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.utils.db_helper import init_db

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # Load config
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Initialize database
    init_db()

    # Register blueprints
    from app.routes import test_routes, batch_routes, results_routes, live_routes

    # live_routes registers '/' for the live detection page
    app.register_blueprint(live_routes.bp)
    app.register_blueprint(test_routes.bp)
    app.register_blueprint(batch_routes.bp)
    app.register_blueprint(results_routes.bp)

    # NOTE: Camera is NOT tested here to avoid holding the device.
    # The camera_thread in live_routes handles all camera access.
    print('[APP] Flask app created successfully')

    return app