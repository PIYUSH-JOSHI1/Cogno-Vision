from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils.file_manager import file_manager
import re
import random

dysgraphia_bp = Blueprint('dysgraphia', __name__)

class DysgraphiaAI:
    def __init__(self):
        self.common_mistakes = {
            'b': 'd', 'd': 'b', 'p': 'q', 'q': 'p',
            'was': 'saw', 'saw': 'was', 'on': 'no', 'no': 'on'
        }
        self.writing_prompts = {
            'general': {
                'easy': [
                    "Write about your favorite day of the week and why you like it.",
                    "Describe what you did yesterday from morning to night.",
                    "Write about your favorite food and why you enjoy it.",
                    "Tell about a time when you helped someone.",
                    "Describe your bedroom and what makes it special."
                ],
                'medium': [
                    "Write about a challenge you overcame and how it made you feel.",
                    "Describe a place you would like to visit and explain why.",
                    "Write about a skill you would like to learn and your plan to learn it.",
                    "Tell about a time when you had to make a difficult decision.",
                    "Describe how you think the world will be different in 10 years."
                ],
                'hard': [
                    "Write about a social issue that concerns you and propose a solution.",
                    "Describe how technology has changed the way people communicate.",
                    "Write about the importance of preserving the environment for future generations.",
                    "Discuss the role of education in personal development.",
                    "Analyze the impact of social media on modern relationships."
                ]
            },
            'personal': {
                'easy': [
                    "Write about your family and what makes them special.",
                    "Describe your best friend and why you like them.",
                    "Tell about your favorite hobby or activity.",
                    "Write about a happy memory from your childhood.",
                    "Describe what you want to be when you grow up."
                ],
                'medium': [
                    "Write about a person who has influenced your life positively.",
                    "Describe a goal you have and your plan to achieve it.",
                    "Tell about a time when you learned something important about yourself.",
                    "Write about a tradition in your family that you value.",
                    "Describe how you handle stress or difficult situations."
                ],
                'hard': [
                    "Reflect on how your values and beliefs have shaped who you are today.",
                    "Write about a life lesson you learned through a difficult experience.",
                    "Describe how you have grown as a person over the past year.",
                    "Analyze your strengths and areas for improvement.",
                    "Write about your vision for your future and the steps to get there."
                ]
            },
            'creative': {
                'easy': [
                    "Write a story about a magical pet that can talk.",
                    "Describe a day when everything went perfectly.",
                    "Create a story about finding a treasure map.",
                    "Write about a world where animals can drive cars.",
                    "Tell a story about a superhero who helps with everyday problems."
                ],
                'medium': [
                    "Write a story about time travel to any period in history.",
                    "Create a tale about a character who can read minds.",
                    "Write about a world where colors have disappeared.",
                    "Tell a story about a mysterious door that appears in your room.",
                    "Create a story about living in a city in the clouds."
                ],
                'hard': [
                    "Write a complex story with multiple characters and plot twists.",
                    "Create a science fiction story about colonizing another planet.",
                    "Write a mystery story where the reader must solve the puzzle.",
                    "Tell a story that explores themes of identity and belonging.",
                    "Create a dystopian story about a society with unusual rules."
                ]
            },
            'descriptive': {
                'easy': [
                    "Describe your favorite season and what you like about it.",
                    "Write about the sounds, smells, and sights of your neighborhood.",
                    "Describe a delicious meal in detail.",
                    "Write about the feeling of your favorite weather.",
                    "Describe a place where you feel completely relaxed."
                ],
                'medium': [
                    "Describe a bustling marketplace using all five senses.",
                    "Write about the atmosphere of a library or bookstore.",
                    "Describe the experience of watching a sunrise or sunset.",
                    "Write about the feeling of accomplishing something difficult.",
                    "Describe a storm from the perspective of someone watching it."
                ],
                'hard': [
                    "Describe an abstract concept like 'freedom' or 'happiness' in concrete terms.",
                    "Write about a complex emotion using sensory details.",
                    "Describe a historical event as if you were witnessing it.",
                    "Write about the passage of time in a specific location.",
                    "Describe the atmosphere of a significant cultural event."
                ]
            }
        }
        
        self.games = {
            'letter_sorting': {
                'name': 'Letter Sorting',
                'description': 'Sort letters into correct and reversed groups',
                'difficulty_levels': ['easy', 'medium', 'hard']
            },
            'word_scramble': {
                'name': 'Word Scramble',
                'description': 'Unscramble letters to form words',
                'difficulty_levels': ['easy', 'medium', 'hard']
            }
        }
    
    def analyze_handwriting(self, text):
        """Analyze text for common dysgraphia patterns"""
        issues = []
        
        # Check for letter reversals
        for correct, incorrect in self.common_mistakes.items():
            if incorrect in text.lower():
                issues.append(f"Possible letter reversal: '{incorrect}' might be '{correct}'")
        
        # Check for spacing issues
        if '  ' in text:
            issues.append("Multiple spaces detected - work on consistent spacing")
        
        # Check for capitalization
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence[0].isupper():
                issues.append("Remember to capitalize the first letter of sentences")
        
        # Check sentence structure
        if len(text.split('.')) == 1 and len(text.split()) > 10:
            issues.append("Try breaking long thoughts into shorter sentences")
        
        return {
            'issues': issues,
            'word_count': len(text.split()),
            'sentence_count': len([s for s in text.split('.') if s.strip()]),
            'suggestions': self.get_suggestions(issues)
        }
    
    def get_suggestions(self, issues):
        """Provide suggestions based on identified issues"""
        suggestions = []
        
        if any('reversal' in issue for issue in issues):
            suggestions.append("Practice letter formation exercises")
        
        if any('spacing' in issue for issue in issues):
            suggestions.append("Use finger spaces between words")
        
        if any('capitalize' in issue for issue in issues):
            suggestions.append("Remember: Capital letter at start of sentences")
        
        if any('sentences' in issue for issue in issues):
            suggestions.append("Use periods to end complete thoughts")
        
        return suggestions
    
    def generate_letter_practice(self, letter):
        """Generate letter formation practice"""
        letter = letter.lower()
        
        formation_guides = {
            'a': "Start at the top, curve down and around, then add a line",
            'b': "Start with a line down, then add two bumps",
            'c': "Start at the top and curve around like a circle, but don't close it",
            'd': "Start with a curve, then add a line up and down",
            'e': "Start in the middle, curve around and add a line across",
            'f': "Start with a line down, then add two lines across",
            'g': "Like 'c' but add a tail that goes down",
            'h': "Line down, then add a hump",
            'i': "Line down, then add a dot on top",
            'j': "Line down with a curve, then add a dot",
            'k': "Line down, then add two diagonal lines",
            'l': "Just a line down",
            'm': "Line down, then add two humps",
            'n': "Line down, then add one hump",
            'o': "Make a circle",
            'p': "Line down, then add a bump at the top",
            'q': "Make a circle, then add a line down",
            'r': "Line down, then add a small curve at the top",
            's': "Curve like a snake",
            't': "Line down, then add a line across the top",
            'u': "Curve down and up, then add a line",
            'v': "Two diagonal lines that meet at the bottom",
            'w': "Like 'v' but do it twice",
            'x': "Two diagonal lines that cross",
            'y': "Two diagonal lines, one continues down",
            'z': "Line across, diagonal down, line across"
        }
        
        return {
            'letter': letter,
            'guide': formation_guides.get(letter, "Practice this letter carefully"),
            'practice_words': self.get_practice_words(letter)
        }
    
    def get_practice_words(self, letter):
        """Get practice words for a specific letter"""
        word_lists = {
            'a': ['cat', 'hat', 'bat', 'mat', 'rat'],
            'b': ['ball', 'book', 'bird', 'boat', 'bear'],
            'c': ['car', 'cat', 'cup', 'cake', 'coat'],
            'd': ['dog', 'duck', 'door', 'doll', 'desk'],
            'e': ['egg', 'elephant', 'eye', 'ear', 'eat'],
            'f': ['fish', 'frog', 'fire', 'flag', 'foot'],
            'g': ['goat', 'girl', 'game', 'gate', 'gift'],
            'h': ['hat', 'house', 'horse', 'hand', 'heart'],
            'i': ['ice', 'ink', 'insect', 'island', 'igloo'],
            'j': ['jump', 'jar', 'juice', 'jacket', 'jewel'],
            'k': ['kite', 'key', 'king', 'kitchen', 'knee'],
            'l': ['lion', 'lamp', 'leaf', 'lock', 'love'],
            'm': ['moon', 'mouse', 'milk', 'money', 'music'],
            'n': ['nose', 'nest', 'night', 'number', 'name'],
            'o': ['owl', 'ocean', 'orange', 'open', 'over'],
            'p': ['pig', 'pen', 'paper', 'pizza', 'park'],
            'q': ['queen', 'quiet', 'quick', 'question', 'quilt'],
            'r': ['rabbit', 'rain', 'red', 'rock', 'run'],
            's': ['sun', 'snake', 'star', 'smile', 'song'],
            't': ['tree', 'table', 'tiger', 'toy', 'time'],
            'u': ['umbrella', 'under', 'up', 'use', 'uncle'],
            'v': ['van', 'violin', 'voice', 'very', 'visit'],
            'w': ['water', 'window', 'wind', 'word', 'work'],
            'x': ['box', 'fox', 'six', 'mix', 'wax'],
            'y': ['yellow', 'yes', 'yard', 'year', 'young'],
            'z': ['zoo', 'zero', 'zip', 'zone', 'zebra']
        }
        
        return word_lists.get(letter, ['practice', 'writing', 'letters'])

dysgraphia_ai = DysgraphiaAI()

@dysgraphia_bp.route('/')
def main():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dysgraphia/main.html')

@dysgraphia_bp.route('/writing-practice')
def writing_practice():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dysgraphia/writing_practice.html')

@dysgraphia_bp.route('/writing-prompts')
def writing_prompts():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dysgraphia/writing_prompts.html')

@dysgraphia_bp.route('/letter-practice')
def letter_practice():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dysgraphia/letter_practice.html')

@dysgraphia_bp.route('/analyze-writing', methods=['POST'])
def analyze_writing():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({'success': False, 'message': 'No text provided'})
    
    analysis = dysgraphia_ai.analyze_handwriting(text)
    
    # Save progress
    progress_data = {
        'user_id': session['user_id'],
        'activity': 'writing_analysis',
        'text_sample': text[:100] + '...' if len(text) > 100 else text,
        'word_count': analysis['word_count'],
        'issues_count': len(analysis['issues']),
        'timestamp': file_manager.get_timestamp()
    }
    
    fieldnames = ['user_id', 'activity', 'text_sample', 'word_count', 'issues_count', 'timestamp']
    file_manager.append_csv('data/dysgraphia/progress.csv', progress_data, fieldnames)
    
    return jsonify({
        'success': True,
        'analysis': analysis
    })

@dysgraphia_bp.route('/save-writing', methods=['POST'])
def save_writing():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    
    writing_data = {
        'user_id': session['user_id'],
        'prompt': data.get('prompt', ''),
        'text_sample': data.get('text', '')[:200] + '...' if len(data.get('text', '')) > 200 else data.get('text', ''),
        'word_count': data.get('word_count', 0),
        'time_spent': data.get('time_spent', ''),
        'category': data.get('category', 'general'),
        'difficulty': data.get('difficulty', 'easy'),
        'timestamp': file_manager.get_timestamp()
    }
    
    fieldnames = ['user_id', 'prompt', 'text_sample', 'word_count', 'time_spent', 'category', 'difficulty', 'timestamp']
    file_manager.append_csv('data/dysgraphia/writings.csv', writing_data, fieldnames)
    
    return jsonify({'success': True, 'message': 'Writing saved successfully'})

@dysgraphia_bp.route('/writing-history')
def writing_history():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    writings = file_manager.read_csv('data/dysgraphia/writings.csv')
    user_writings = [w for w in writings if w['user_id'] == session['user_id']]
    
    # Sort by timestamp, most recent first
    user_writings.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return jsonify({
        'success': True,
        'history': user_writings[:10]  # Return last 10 writings
    })

@dysgraphia_bp.route('/get-letter-practice', methods=['POST'])
def get_letter_practice():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    letter = data.get('letter', 'a')
    
    practice_data = dysgraphia_ai.generate_letter_practice(letter)
    
    return jsonify({
        'success': True,
        'practice': practice_data
    })

@dysgraphia_bp.route('/get-writing-prompt', methods=['POST'])
def get_writing_prompt():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    category = data.get('category', 'general')
    difficulty = data.get('difficulty', 'easy')
    
    prompts = dysgraphia_ai.writing_prompts.get(category, {}).get(difficulty, [])
    if not prompts:
        prompts = dysgraphia_ai.writing_prompts['general']['easy']
    
    prompt = random.choice(prompts)
    
    return jsonify({
        'success': True,
        'prompt': prompt
    })

@dysgraphia_bp.route('/games')
def games():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dysgraphia/games.html', games=dysgraphia_ai.games)
