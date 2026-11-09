"""
Database helper functions for storing and retrieving results.
Identical schema to the original StoS project for compatibility.
"""

import sqlite3
import json
from datetime import datetime
from app.config import Config
import os

def init_db():
    """Initialize database with schema"""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()
    
    # Create results table
    c.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            recognized_words TEXT,
            generated_sentence TEXT,
            processing_time REAL,
            detailed_results TEXT,
            video_path TEXT
        )
    ''')
    
    # Create batch jobs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS batch_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            total_videos INTEGER,
            completed_videos INTEGER,
            results_json TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_result(video_name, recognized_words, sentence, processing_time, detailed_results=None, video_path=None):
    """Save test result to database"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO test_results 
            (video_name, recognized_words, generated_sentence, processing_time, detailed_results, video_path, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_name,
            ','.join(recognized_words) if isinstance(recognized_words, list) else recognized_words,
            sentence,
            processing_time,
            json.dumps(detailed_results) if detailed_results else None,
            video_path,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        result_id = c.lastrowid
        conn.close()
        return result_id
    except Exception as e:
        print(f"Error saving result: {e}")
        return None

def get_all_results():
    """Get all test results"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM test_results ORDER BY timestamp DESC')
        results = [dict(row) for row in c.fetchall()]
        
        conn.close()
        return results
    except Exception as e:
        print(f"Error getting results: {e}")
        return []

def get_results_paginated(page=1, per_page=20):
    """Get results with pagination"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        offset = (page - 1) * per_page
        c.execute('SELECT * FROM test_results ORDER BY timestamp DESC LIMIT ? OFFSET ?', 
                 (per_page, offset))
        results = [dict(row) for row in c.fetchall()]
        
        # Get total count
        c.execute('SELECT COUNT(*) as count FROM test_results')
        total = c.fetchone()['count']
        
        conn.close()
        return results, total
    except Exception as e:
        print(f"Error getting paginated results: {e}")
        return [], 0

def get_statistics():
    """Get statistics from results"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) as total FROM test_results')
        total = c.fetchone()[0]
        
        c.execute('SELECT AVG(processing_time) as avg_time FROM test_results')
        avg_time = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_tests': total,
            'avg_processing_time': round(avg_time, 2)
        }
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {'total_tests': 0, 'avg_processing_time': 0}

def delete_result(result_id):
    """Delete a test result"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        c = conn.cursor()
        
        c.execute('DELETE FROM test_results WHERE id = ?', (result_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting result: {e}")
        return False

def clear_all_results():
    """Clear all results (for reset)"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        c = conn.cursor()
        
        c.execute('DELETE FROM test_results')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing results: {e}")
        return False
