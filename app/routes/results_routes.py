"""
Routes for results and history
"""

from flask import Blueprint, render_template, request, jsonify, send_file
from app.utils.db_helper import get_all_results, get_results_paginated, delete_result, clear_all_results, get_statistics
import os

bp = Blueprint('results', __name__, url_prefix='/results')

@bp.route('/')
def results_page():
    """Results history page"""
    return render_template('results.html')

@bp.route('/api/all')
def api_all_results():
    """Get all results (API)"""
    try:
        results = get_all_results()
        stats = get_statistics()
        
        return jsonify({
            'success': True,
            'results': results,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/paginated')
def api_paginated_results():
    """Get paginated results"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        results, total = get_results_paginated(page, per_page)
        stats = get_statistics()
        
        return jsonify({
            'success': True,
            'results': results,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/delete/<int:result_id>', methods=['POST'])
def api_delete_result(result_id):
    """Delete a result"""
    try:
        success = delete_result(result_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/clear', methods=['POST'])
def api_clear_results():
    """Clear all results"""
    try:
        success = clear_all_results()
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/stats')
def api_get_stats():
    """Get statistics"""
    try:
        stats = get_statistics()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/video/<int:result_id>')
def api_get_video(result_id):
    """Get video file for a result"""
    try:
        results = get_all_results()
        result = next((r for r in results if r['id'] == result_id), None)
        
        if not result:
            return jsonify({'success': False, 'error': 'Result not found'}), 404
        
        video_path = result.get('video_path')
        if not video_path or not os.path.exists(video_path):
            return jsonify({'success': False, 'error': 'Video file not found'}), 404
        
        return send_file(video_path, mimetype='video/mp4')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

