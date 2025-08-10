from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.progress import GameSession, Progress, db
from datetime import datetime
import json
import random

games_bp = Blueprint('games', __name__)

# Game definitions
GAMES_DATA = {
    'sound-match': {
        'id': 'sound-match',
        'name': 'Sound Match',
        'description': 'Match sounds to letters and letter combinations',
        'difficulty': 'Easy',
        'category': 'Phonics',
        'max_score': 100
    },
    'syllable-count': {
        'id': 'syllable-count',
        'name': 'Syllable Counter',
        'description': 'Count the syllables in different words',
        'difficulty': 'Medium',
        'category': 'Phonics',
        'max_score': 100
    },
    'word-builder': {
        'id': 'word-builder',
        'name': 'Word Builder',
        'description': 'Build words from individual sounds',
        'difficulty': 'Hard',
        'category': 'Spelling',
        'max_score': 150
    },
    'rhyme-time': {
        'id': 'rhyme-time',
        'name': 'Rhyme Time',
        'description': 'Find words that rhyme with the given word',
        'difficulty': 'Easy',
        'category': 'Phonics',
        'max_score': 100
    }
}

@games_bp.route('/')
@login_required
def games_list():
    return render_template('games/games.html', games=GAMES_DATA)

@games_bp.route('/list')
@login_required
def get_games_list():
    return jsonify({
        'success': True,
        'games': list(GAMES_DATA.values())
    })

@games_bp.route('/start/<game_id>', methods=['POST'])
@login_required
def start_game(game_id):
    if game_id not in GAMES_DATA:
        return jsonify({
            'success': False,
            'message': 'Game not found'
        }), 404
    
    game_info = GAMES_DATA[game_id]
    
    # Create new game session
    session = GameSession(
        user_id=current_user.id,
        game_id=game_id,
        game_name=game_info['name'],
        max_score=game_info['max_score']
    )
    
    db.session.add(session)
    db.session.commit()
    
    # Generate game content based on game type
    game_content = generate_game_content(game_id)
    
    return jsonify({
        'success': True,
        'session_id': session.id,
        'game': game_info,
        'content': game_content
    })

@games_bp.route('/submit', methods=['POST'])
@login_required
def submit_game():
    data = request.get_json()
    session_id = data.get('session_id')
    answers = data.get('answers', [])
    
    session = GameSession.query.get(session_id)
    if not session or session.user_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'Invalid session'
        }), 404
    
    # Calculate score based on answers
    score, feedback = calculate_game_score(session.game_id, answers)
    
    # Update session
    session.score = score
    session.status = 'completed'
    session.completed_at = datetime.utcnow()
    session.answers = json.dumps(answers)
    
    # Record progress
    progress = Progress(
        user_id=current_user.id,
        activity_type='game',
        activity_name=session.game_name,
        score=score,
        accuracy=(score / session.max_score) * 100,
        time_spent=int((session.completed_at - session.started_at).total_seconds()),
        difficulty_level=GAMES_DATA[session.game_id]['difficulty']
    )
    
    db.session.add(progress)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'score': score,
        'max_score': session.max_score,
        'feedback': feedback,
        'percentage': (score / session.max_score) * 100
    })

@games_bp.route('/game/<game_id>')
@login_required
def play_game(game_id):
    if game_id not in GAMES_DATA:
        return "Game not found", 404
    
    game_info = GAMES_DATA[game_id]
    return render_template('games/play.html', game=game_info)

def generate_game_content(game_id):
    """Generate content for different game types"""
    
    if game_id == 'sound-match':
        sounds = [
            {'sound': 'cat', 'options': ['c-a-t', 'k-a-t', 's-a-t'], 'correct': 0},
            {'sound': 'dog', 'options': ['d-o-g', 't-o-g', 'd-a-g'], 'correct': 0},
            {'sound': 'fish', 'options': ['f-i-s-h', 'p-i-s-h', 'f-i-t-h'], 'correct': 0},
            {'sound': 'bird', 'options': ['b-i-r-d', 'p-i-r-d', 'b-u-r-d'], 'correct': 0},
            {'sound': 'tree', 'options': ['t-r-e-e', 't-r-i-e', 'd-r-e-e'], 'correct': 0}
        ]
        return {'questions': sounds}
    
    elif game_id == 'syllable-count':
        words = [
            {'word': 'cat', 'syllables': 1},
            {'word': 'elephant', 'syllables': 3},
            {'word': 'butterfly', 'syllables': 3},
            {'word': 'dog', 'syllables': 1},
            {'word': 'computer', 'syllables': 3}
        ]
        return {'questions': words}
    
    elif game_id == 'word-builder':
        challenges = [
            {'sounds': ['c', 'a', 't'], 'word': 'cat'},
            {'sounds': ['d', 'o', 'g'], 'word': 'dog'},
            {'sounds': ['f', 'i', 'sh'], 'word': 'fish'},
            {'sounds': ['b', 'i', 'r', 'd'], 'word': 'bird'},
            {'sounds': ['tr', 'ee'], 'word': 'tree'}
        ]
        return {'questions': challenges}
    
    elif game_id == 'rhyme-time':
        rhymes = [
            {'word': 'cat', 'options': ['bat', 'dog', 'car'], 'correct': 0},
            {'word': 'tree', 'options': ['car', 'bee', 'dog'], 'correct': 1},
            {'word': 'sun', 'options': ['moon', 'fun', 'star'], 'correct': 1},
            {'word': 'book', 'options': ['look', 'pen', 'car'], 'correct': 0},
            {'word': 'fish', 'options': ['cat', 'wish', 'dog'], 'correct': 1}
        ]
        return {'questions': rhymes}
    
    return {'questions': []}

def calculate_game_score(game_id, answers):
    """Calculate score and provide feedback for game answers"""
    
    if game_id == 'sound-match':
        correct_answers = [0, 0, 0, 0, 0]  # All first options are correct
        score = sum(1 for i, answer in enumerate(answers) if answer == correct_answers[i]) * 20
        feedback = f"You got {score//20} out of 5 correct!"
    
    elif game_id == 'syllable-count':
        correct_answers = [1, 3, 3, 1, 3]
        score = sum(1 for i, answer in enumerate(answers) if answer == correct_answers[i]) * 20
        feedback = f"You counted syllables correctly {score//20} out of 5 times!"
    
    elif game_id == 'word-builder':
        # More complex scoring for word building
        score = len(answers) * 30  # 30 points per completed word
        feedback = f"You built {len(answers)} words correctly!"
    
    elif game_id == 'rhyme-time':
        correct_answers = [0, 1, 1, 0, 1]
        score = sum(1 for i, answer in enumerate(answers) if answer == correct_answers[i]) * 20
        feedback = f"You found {score//20} out of 5 rhymes!"
    
    else:
        score = 0
        feedback = "Game completed!"
    
    return score, feedback
