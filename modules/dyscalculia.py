from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils.file_manager import file_manager
import random
import math

dyscalculia_bp = Blueprint('dyscalculia', __name__)

class DyscalculiaAI:
    def __init__(self):
        self.difficulty_levels = {
            'easy': {'range': (1, 10), 'operations': ['+', '-']},
            'medium': {'range': (1, 50), 'operations': ['+', '-', '*']},
            'hard': {'range': (1, 100), 'operations': ['+', '-', '*', '/']}
        }
    
    def generate_math_problem(self, difficulty='easy', operation=None):
        """Generate math problems based on difficulty"""
        level = self.difficulty_levels[difficulty]
        min_val, max_val = level['range']
        ops = level['operations']
        
        if operation and operation in ops:
            op = operation
        else:
            op = random.choice(ops)
        
        a = random.randint(min_val, max_val)
        b = random.randint(min_val, max_val)
        
        if op == '+':
            answer = a + b
            problem = f"{a} + {b}"
        elif op == '-':
            if a < b:
                a, b = b, a  # Ensure positive result
            answer = a - b
            problem = f"{a} - {b}"
        elif op == '*':
            answer = a * b
            problem = f"{a} × {b}"
        elif op == '/':
            # Ensure clean division
            answer = random.randint(1, 12)
            a = answer * b
            problem = f"{a} ÷ {b}"
        
        return {
            'problem': problem,
            'answer': answer,
            'operation': op,
            'difficulty': difficulty
        }
    
    def generate_number_sequence(self, start=1, step=1, length=5):
        """Generate number sequences for pattern recognition"""
        sequence = []
        current = start
        for _ in range(length):
            sequence.append(current)
            current += step
        
        return {
            'sequence': sequence[:-1],  # Hide last number
            'missing': sequence[-1],
            'pattern': f"Add {step}"
        }
    
    def generate_visual_math(self, difficulty='easy'):
        """Generate visual math problems with objects"""
        objects = ['🍎', '🐕', '⭐', '🚗', '🏠', '🌸', '📚', '⚽']
        obj = random.choice(objects)
        
        if difficulty == 'easy':
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            operation = random.choice(['+', '-'])
        else:
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            operation = random.choice(['+', '-', '*'])
        
        if operation == '+':
            answer = a + b
            visual = f"{obj * a} + {obj * b} = ?"
        elif operation == '-':
            if a < b:
                a, b = b, a
            answer = a - b
            visual = f"{obj * a} - {obj * b} = ?"
        elif operation == '*':
            answer = a * b
            visual = f"{a} groups of {obj * b} = ?"
        
        return {
            'visual': visual,
            'answer': answer,
            'objects_count': {'a': a, 'b': b},
            'operation': operation
        }

dyscalculia_ai = DyscalculiaAI()

@dyscalculia_bp.route('/')
def main():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dyscalculia/main.html')

@dyscalculia_bp.route('/practice')
def practice():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dyscalculia/practice.html')

@dyscalculia_bp.route('/generate-problem', methods=['POST'])
def generate_problem():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    difficulty = data.get('difficulty', 'easy')
    problem_type = data.get('type', 'arithmetic')
    
    if problem_type == 'arithmetic':
        problem = dyscalculia_ai.generate_math_problem(difficulty)
    elif problem_type == 'sequence':
        problem = dyscalculia_ai.generate_number_sequence()
    elif problem_type == 'visual':
        problem = dyscalculia_ai.generate_visual_math(difficulty)
    
    return jsonify({'success': True, 'problem': problem})

@dyscalculia_bp.route('/check-answer', methods=['POST'])
def check_answer():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    user_answer = data.get('answer')
    correct_answer = data.get('correct_answer')
    problem_type = data.get('problem_type', 'arithmetic')
    difficulty = data.get('difficulty', 'easy')
    
    is_correct = str(user_answer) == str(correct_answer)
    
    # Save progress
    progress_data = {
        'user_id': session['user_id'],
        'problem_type': problem_type,
        'difficulty': difficulty,
        'correct': is_correct,
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'timestamp': file_manager.get_timestamp()
    }
    
    fieldnames = ['user_id', 'problem_type', 'difficulty', 'correct', 'user_answer', 'correct_answer', 'timestamp']
    file_manager.append_csv('data/dyscalculia/progress.csv', progress_data, fieldnames)
    
    return jsonify({
        'success': True,
        'correct': is_correct,
        'message': 'Correct! Well done!' if is_correct else f'Not quite. The answer is {correct_answer}'
    })

@dyscalculia_bp.route('/games')
def games():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dyscalculia/games.html')

@dyscalculia_bp.route('/number-line')
def number_line():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dyscalculia/number_line.html')
