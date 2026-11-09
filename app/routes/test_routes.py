"""
Routes for single video testing
"""

from flask import Blueprint, render_template, request, jsonify
import os
import time
from werkzeug.utils import secure_filename
from app.config import Config, allowed_file
from app.utils.inference_helper import process_video
from app.utils.db_helper import save_result

bp = Blueprint('test', __name__, url_prefix='/test')

@bp.route('/')
def test_page():
    """Test video page"""
    return render_template('test.html')

@bp.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            # Process video
            words, sentence, processing_time, detailed_results = process_video(filepath)
            
            if words is None:
                # Clean up file
                os.remove(filepath)
                return jsonify({'error': 'Error processing video'}), 500
            
            # Save result to database (KEEP the file for viewing!)
            result_id = save_result(
                video_name=filename,
                recognized_words=words,
                sentence=sentence,
                processing_time=processing_time,
                detailed_results=detailed_results,
                video_path=filepath
            )
            
            # Prepare response
            response = {
                'success': True,
                'result_id': result_id,
                'recognized_words': words,
                'sentence': sentence,
                'processing_time': round(processing_time, 2),
                'detailed_results': detailed_results
            }
            
            return jsonify(response)
        
        except Exception as process_error:
            # Clean up on processing error
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'error': f'Error processing video: {str(process_error)}'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/load-test-folder', methods=['GET'])
def load_test_folder():
    """Load videos from test_videos folder"""
    try:
        test_folder = Config.TEST_VIDEOS_FOLDER
        
        if not os.path.exists(test_folder):
            return jsonify({'error': 'Test folder not found', 'videos': []}), 200
        
        videos = [f for f in os.listdir(test_folder) 
                  if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))]
        videos.sort()
        
        return jsonify({'videos': videos, 'folder': test_folder})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/process-test-video', methods=['POST'])
def process_test_video():
    """Process a video from test folder"""
    try:
        data = request.get_json()
        video_name = data.get('video_name')
        
        test_folder = Config.TEST_VIDEOS_FOLDER
        video_path = os.path.join(test_folder, video_name)
        
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video not found'}), 404
        
        # Process video
        words, sentence, processing_time, detailed_results = process_video(video_path)
        
        if words is None:
            return jsonify({'error': 'Error processing video'}), 500
        
        # Save result to database
        result_id = save_result(
            video_name=video_name,
            recognized_words=words,
            sentence=sentence,
            processing_time=processing_time,
            detailed_results=detailed_results,
            video_path=video_path
        )
        
        # Prepare response
        response = {
            'success': True,
            'result_id': result_id,
            'recognized_words': words,
            'sentence': sentence,
            'processing_time': round(processing_time, 2),
            'detailed_results': detailed_results
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
