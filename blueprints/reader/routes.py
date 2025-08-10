from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from ai_helpers import AIHelpers
from models.progress import Progress, db
from datetime import datetime
import time

reader_bp = Blueprint('reader', __name__)

@reader_bp.route('/')
@login_required
def reader():
    return render_template('reader/reader.html', user=current_user)

@reader_bp.route('/simplify', methods=['POST'])
@login_required
def simplify_text():
    start_time = time.time()
    data = request.get_json()
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({
            'success': False,
            'message': 'No text provided'
        }), 400
    
    try:
        ai_helper = AIHelpers(current_app.config)
        
        # Simplify the text
        simplified_text = ai_helper.simplify_text(text)
        
        # Get annotations
        annotations = ai_helper.annotate_text(text)
        
        # Record progress
        processing_time = time.time() - start_time
        progress = Progress(
            user_id=current_user.id,
            activity_type='simplification',
            activity_name='Text Simplification',
            time_spent=int(processing_time),
            difficulty_level=annotations['reading_level']
        )
        db.session.add(progress)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'original': text,
            'simplified': simplified_text,
            'annotations': annotations,
            'processing_time': processing_time
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing text: {str(e)}'
        }), 500

@reader_bp.route('/annotate', methods=['POST'])
@login_required
def annotate_text():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({
            'success': False,
            'message': 'No text provided'
        }), 400
    
    try:
        ai_helper = AIHelpers(current_app.config)
        annotations = ai_helper.annotate_text(text)
        
        return jsonify({
            'success': True,
            'annotations': annotations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error annotating text: {str(e)}'
        }), 500

@reader_bp.route('/phonemes', methods=['POST'])
@login_required
def get_phonemes():
    data = request.get_json()
    word = data.get('word', '')
    
    if not word.strip():
        return jsonify({
            'success': False,
            'message': 'No word provided'
        }), 400
    
    try:
        ai_helper = AIHelpers(current_app.config)
        phonemes = ai_helper.generate_phoneme_breakdown(word)
        
        return jsonify({
            'success': True,
            'word': word,
            'phonemes': phonemes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating phonemes: {str(e)}'
        }), 500

@reader_bp.route('/reading-session', methods=['POST'])
@login_required
def record_reading_session():
    data = request.get_json()
    
    progress = Progress(
        user_id=current_user.id,
        activity_type='reading',
        activity_name=data.get('activity_name', 'Reading Session'),
        reading_speed=data.get('reading_speed'),
        accuracy=data.get('accuracy'),
        time_spent=data.get('time_spent'),
        difficulty_level=data.get('difficulty_level')
    )
    
    db.session.add(progress)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Reading session recorded'
    })
