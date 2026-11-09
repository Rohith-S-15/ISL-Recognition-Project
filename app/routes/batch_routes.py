"""
Routes for batch testing
"""

from flask import Blueprint, render_template, request, jsonify
import os
import time
from app.config import Config
from app.utils.inference_helper import process_video
from app.utils.db_helper import save_result

bp = Blueprint('batch', __name__, url_prefix='/batch')

@bp.route('/')
def batch_page():
    """Batch testing page"""
    test_folder = Config.TEST_VIDEOS_FOLDER
    videos = []
    
    if os.path.exists(test_folder):
        videos = sorted([f for f in os.listdir(test_folder) 
                        if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))])
    
    return render_template('batch.html', available_videos=videos)

@bp.route('/run', methods=['POST'])
def run_batch_test():
    """Run batch test on selected videos"""
    try:
        data = request.get_json()
        selected_videos = data.get('videos', [])
        
        if not selected_videos:
            return jsonify({'error': 'No videos selected'}), 400
        
        test_folder = Config.TEST_VIDEOS_FOLDER
        results = []
        total_time = 0
        
        for i, video_name in enumerate(selected_videos):
            video_path = os.path.join(test_folder, video_name)
            
            if not os.path.exists(video_path):
                results.append({
                    'video': video_name,
                    'success': False,
                    'error': 'Video not found'
                })
                continue
            
            try:
                # Process video
                words, sentence, processing_time, detailed_results = process_video(video_path)
                
                if words is None:
                    results.append({
                        'video': video_name,
                        'success': False,
                        'error': 'Error processing video'
                    })
                    continue
                
                # Save result
                result_id = save_result(
                    video_name=video_name,
                    recognized_words=words,
                    sentence=sentence,
                    processing_time=processing_time,
                    detailed_results=detailed_results,
                    video_path=video_path
                )
                
                total_time += processing_time
                
                results.append({
                    'video': video_name,
                    'success': True,
                    'result_id': result_id,
                    'recognized_words': words,
                    'sentence': sentence,
                    'processing_time': round(processing_time, 2),
                    'detailed_results': detailed_results
                })
            
            except Exception as e:
                results.append({
                    'video': video_name,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate statistics
        successful = len([r for r in results if r.get('success', False)])
        failed = len([r for r in results if not r.get('success', False)])
        
        response = {
            'success': True,
            'total_videos': len(selected_videos),
            'successful': successful,
            'failed': failed,
            'total_processing_time': round(total_time, 2),
            'results': results
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
