"""
Main routes for home dashboard
"""

from flask import Blueprint, render_template, jsonify
from app.utils.db_helper import get_all_results, get_statistics
from app.config import Config
import os

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/home')
def home():
    """Home dashboard page"""
    # Get stats
    stats = get_statistics()
    
    # Get recent results (last 5)
    all_results = get_all_results()
    recent_results = all_results[:5]
    
    # Get engine info
    engine_info = {
        'method': 'Cosine Similarity',
        'templates': 0,
        'template_names': []
    }
    
    # Count templates
    if os.path.exists(Config.SIGN_TEMPLATES_DIR):
        npy_files = [f for f in os.listdir(Config.SIGN_TEMPLATES_DIR) if f.endswith('.npy')]
        engine_info['templates'] = len(npy_files)
        engine_info['template_names'] = [f.replace('.npy', '') for f in sorted(npy_files)]
    
    return render_template('index.html',
                         stats=stats,
                         recent_results=recent_results,
                         engine_info=engine_info)

@bp.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    stats = get_statistics()
    return jsonify(stats)
