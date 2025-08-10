from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils.file_manager import file_manager
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import random

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"



dyslexia_bp = Blueprint('dyslexia', __name__)

# Download NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class DyslexiaAI:
    def __init__(self):
        self.simple_words = self.load_simple_words()
        self.phonics_words = self.load_phonics_words()
    
    def load_simple_words(self):
        """Load simple word replacements"""
        return {
            'utilize': 'use', 'demonstrate': 'show', 'approximately': 'about',
            'consequently': 'so', 'furthermore': 'also', 'nevertheless': 'but',
            'subsequently': 'then', 'magnificent': 'great', 'enormous': 'huge',
            'diminish': 'reduce', 'acquire': 'get', 'commence': 'start',
            'terminate': 'end', 'assistance': 'help', 'sufficient': 'enough',
            'difficult': 'hard', 'important': 'key', 'understand': 'get',
            'remember': 'recall', 'different': 'other', 'because': 'since',
            'immediately': 'now', 'necessary': 'needed', 'opportunity': 'chance',
            'participate': 'join', 'communicate': 'talk', 'investigate': 'look into'
        }
    
    def load_phonics_words(self):
        """Load phonics word database with different difficulty levels"""
        return {
            'easy': [
                {'word': 'cat', 'sounds': ['c', 'a', 't'], 'phonemes': ['k', 'æ', 't']},
                {'word': 'dog', 'sounds': ['d', 'o', 'g'], 'phonemes': ['d', 'ɒ', 'g']},
                {'word': 'sun', 'sounds': ['s', 'u', 'n'], 'phonemes': ['s', 'ʌ', 'n']},
                {'word': 'hat', 'sounds': ['h', 'a', 't'], 'phonemes': ['h', 'æ', 't']},
                {'word': 'pen', 'sounds': ['p', 'e', 'n'], 'phonemes': ['p', 'e', 'n']},
                {'word': 'big', 'sounds': ['b', 'i', 'g'], 'phonemes': ['b', 'ɪ', 'g']},
                {'word': 'red', 'sounds': ['r', 'e', 'd'], 'phonemes': ['r', 'e', 'd']},
                {'word': 'top', 'sounds': ['t', 'o', 'p'], 'phonemes': ['t', 'ɒ', 'p']},
            ],
            'medium': [
                {'word': 'fish', 'sounds': ['f', 'i', 'sh'], 'phonemes': ['f', 'ɪ', 'ʃ']},
                {'word': 'ship', 'sounds': ['sh', 'i', 'p'], 'phonemes': ['ʃ', 'ɪ', 'p']},
                {'word': 'chair', 'sounds': ['ch', 'ai', 'r'], 'phonemes': ['tʃ', 'eə', 'r']},
                {'word': 'think', 'sounds': ['th', 'i', 'nk'], 'phonemes': ['θ', 'ɪ', 'ŋk']},
                {'word': 'phone', 'sounds': ['ph', 'o', 'ne'], 'phonemes': ['f', 'əʊ', 'n']},
                {'word': 'night', 'sounds': ['n', 'igh', 't'], 'phonemes': ['n', 'aɪ', 't']},
                {'word': 'light', 'sounds': ['l', 'igh', 't'], 'phonemes': ['l', 'aɪ', 't']},
                {'word': 'train', 'sounds': ['tr', 'ai', 'n'], 'phonemes': ['tr', 'eɪ', 'n']},
            ],
            'hard': [
                {'word': 'through', 'sounds': ['th', 'r', 'ough'], 'phonemes': ['θ', 'r', 'uː']},
                {'word': 'enough', 'sounds': ['e', 'n', 'ough'], 'phonemes': ['ɪ', 'n', 'ʌf']},
                {'word': 'daughter', 'sounds': ['d', 'augh', 'ter'], 'phonemes': ['d', 'ɔː', 'tə']},
                {'word': 'knight', 'sounds': ['kn', 'igh', 't'], 'phonemes': ['n', 'aɪ', 't']},
                {'word': 'psychology', 'sounds': ['ps', 'y', 'ch', 'o', 'lo', 'gy'], 'phonemes': ['s', 'aɪ', 'k', 'ɒ', 'lə', 'dʒi']},
                {'word': 'rhythm', 'sounds': ['rh', 'y', 'th', 'm'], 'phonemes': ['r', 'ɪ', 'ð', 'm']},
            ]
        }
    
    def simplify_text(self, text):
        """Enhanced text simplification for dyslexic readers using local AI"""
        if not text.strip():
            return text
        
        # Try using local AI model first
        try:
            from ai_helpers import AIHelpers
            from flask import current_app
            
            ai_helper = AIHelpers(current_app.config)
            ai_simplified = ai_helper.simplify_text(text)
            
            # Additional dyslexia-specific processing
            return self._post_process_for_dyslexia(ai_simplified)
        except Exception as e:
            print(f"AI simplification failed, using rule-based: {e}")
            # Fallback to existing rule-based method
            return self._rule_based_simplify(text)

    def _post_process_for_dyslexia(self, text):
        """Additional processing specific to dyslexia needs"""
        # Your existing logic here...
        sentences = sent_tokenize(text)
        # ... rest of your existing processing
        return text

    def _rule_based_simplify(self, text):
        """Your existing rule-based simplification logic"""
        # Move your existing simplification logic here
        sentences = sent_tokenize(text)
        simplified_sentences = []
        
        for sentence in sentences:
            # Remove complex punctuation
            sentence = re.sub(r'[;:]', '.', sentence)
            sentence = re.sub(r'["""]', '"', sentence)
            sentence = re.sub(r'['']', "'", sentence)
            
            # Split long sentences at conjunctions
            if len(sentence.split()) > 15:
                parts = re.split(r'\b(and|but|or|because|since|while|although|however|therefore)\b', sentence)
                for i, part in enumerate(parts):
                    part = part.strip()
                    if len(part) > 3 and not part.lower() in ['and', 'but', 'or', 'because', 'since', 'while', 'although', 'however', 'therefore']:
                        part = self.replace_complex_words(part)
                        if not part.endswith('.') and i == len(parts) - 1:
                            part += '.'
                        simplified_sentences.append(part)
            else:
                sentence = self.replace_complex_words(sentence)
                simplified_sentences.append(sentence)
        
        return ' '.join(simplified_sentences)
    
    def replace_complex_words(self, text):
        """Replace complex words with simpler alternatives"""
        words = text.split()
        simplified_words = []
        
        for word in words:
            # Extract punctuation
            punctuation = ''
            clean_word = word
            if word and not word[-1].isalnum():
                punctuation = word[-1]
                clean_word = word[:-1]
            
            # Check for replacement
            lower_word = clean_word.lower()
            if lower_word in self.simple_words:
                simplified_words.append(self.simple_words[lower_word] + punctuation)
            else:
                simplified_words.append(word)
        
        return ' '.join(simplified_words)
    
    def analyze_text(self, text):
        """Enhanced text analysis"""
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        
        # Filter out punctuation for word analysis
        actual_words = [word for word in words if word.isalnum()]
        
        avg_word_length = sum(len(word) for word in actual_words) / len(actual_words) if actual_words else 0
        avg_sentence_length = len(actual_words) / len(sentences) if sentences else 0
        
        # Count syllables (simplified)
        total_syllables = sum(self.count_syllables(word) for word in actual_words)
        avg_syllables = total_syllables / len(actual_words) if actual_words else 0
        
        # Determine difficulty
        difficulty = 'Easy'
        if avg_word_length > 6 or avg_sentence_length > 15 or avg_syllables > 2:
            difficulty = 'Hard'
        elif avg_word_length > 4 or avg_sentence_length > 10 or avg_syllables > 1.5:
            difficulty = 'Medium'
        
        # Find difficult words
        difficult_words = []
        for word in actual_words:
            if len(word) > 7 or self.count_syllables(word) > 3:
                difficult_words.append({
                    'word': word,
                    'syllables': self.count_syllables(word),
                    'length': len(word)
                })
        
        return {
            'word_count': len(actual_words),
            'sentence_count': len(sentences),
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_syllables': round(avg_syllables, 2),
            'difficulty': difficulty,
            'difficult_words': difficult_words[:10],  # Limit to 10 most difficult
            'readability_score': self.calculate_readability_score(avg_sentence_length, avg_syllables)
        }
    
    def count_syllables(self, word):
        """Count syllables in a word"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def calculate_readability_score(self, avg_sentence_length, avg_syllables):
        """Calculate a simplified readability score"""
        # Simplified Flesch Reading Ease formula
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        
        if score >= 90:
            return 'Very Easy'
        elif score >= 80:
            return 'Easy'
        elif score >= 70:
            return 'Fairly Easy'
        elif score >= 60:
            return 'Standard'
        elif score >= 50:
            return 'Fairly Difficult'
        elif score >= 30:
            return 'Difficult'
        else:
            return 'Very Difficult'
    
    def generate_phonics_questions(self, difficulty='easy', count=5):
        """Generate phonics questions based on difficulty"""
        words_pool = self.phonics_words.get(difficulty, self.phonics_words['easy'])
        selected_words = random.sample(words_pool, min(count, len(words_pool)))
        
        questions = []
        for word_data in selected_words:
            # Create multiple choice options
            correct_sounds = '-'.join(word_data['sounds'])
            
            # Generate wrong options
            wrong_options = []
            for _ in range(3):
                # Create plausible wrong answers
                wrong_sounds = word_data['sounds'].copy()
                if len(wrong_sounds) > 1:
                    # Swap some sounds
                    idx1, idx2 = random.sample(range(len(wrong_sounds)), 2)
                    wrong_sounds[idx1], wrong_sounds[idx2] = wrong_sounds[idx2], wrong_sounds[idx1]
                wrong_options.append('-'.join(wrong_sounds))
            
            options = [correct_sounds] + wrong_options
            random.shuffle(options)
            
            questions.append({
                'word': word_data['word'],
                'correct_sounds': correct_sounds,
                'options': options,
                'correct_index': options.index(correct_sounds),
                'phonemes': word_data.get('phonemes', [])
            })
        
        return questions

dyslexia_ai = DyslexiaAI()

@dyslexia_bp.route('/')
def main():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dyslexia/main.html')

@dyslexia_bp.route('/reader')
def reader():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dyslexia/reader.html')

@dyslexia_bp.route('/simplify', methods=['POST'])
def simplify_text():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({'success': False, 'message': 'No text provided'})
    
    try:
        simplified = dyslexia_ai.simplify_text(text)
        analysis = dyslexia_ai.analyze_text(text)
        
        # Save progress
        progress_data = {
            'user_id': session['user_id'],
            'activity': 'text_simplification',
            'original_text': text[:100] + '...' if len(text) > 100 else text,
            'difficulty': analysis['difficulty'],
            'word_count': analysis['word_count'],
            'readability_score': analysis['readability_score'],
            'timestamp': file_manager.get_timestamp()
        }
        
        fieldnames = ['user_id', 'activity', 'original_text', 'difficulty', 'word_count', 'readability_score', 'timestamp']
        file_manager.append_csv('data/dyslexia/progress.csv', progress_data, fieldnames)
        
        return jsonify({
            'success': True,
            'original': text,
            'simplified': simplified,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing text: {str(e)}'
        }), 500

@dyslexia_bp.route('/games')
def games():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dyslexia/games.html')

@dyslexia_bp.route('/games/phonics', methods=['POST'])
def phonics_game():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    difficulty = data.get('difficulty', 'easy')
    question_count = data.get('count', 5)
    
    try:
        questions = dyslexia_ai.generate_phonics_questions(difficulty, question_count)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'difficulty': difficulty,
            'total_questions': len(questions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating questions: {str(e)}'
        }), 500


@dyslexia_bp.route('/games/submit', methods=['POST'])
def submit_game():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    answers = data.get('answers', [])
    game_type = data.get('game_type', 'phonics')
    difficulty = data.get('difficulty', 'easy')
    questions = data.get('questions', []) # This will now be sent from the frontend
    
    if not answers or not questions:
        return jsonify({'success': False, 'message': 'Incomplete game data provided'})
    
    try:
        # Calculate score based on game type
        if game_type == 'phonics':
            correct_count = 0
            for i, answer_index in enumerate(answers):
                # Ensure the index and answer are valid
                if i < len(questions) and answer_index == questions[i].get('correct_index', -1):
                    correct_count += 1
            
            score = correct_count
            total_questions = len(questions)
            accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            
        elif game_type == 'word-building':
            correct_count = 0
            # The 'questions' list now contains the correct answers
            for i, answer in enumerate(answers):
                if i < len(questions) and answer.lower().strip() == questions[i].get('correct', ''):
                    correct_count += 1
            
            score = correct_count
            total_questions = len(questions)
            accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        else: # Default case
            score = 0
            total_questions = len(questions)
            accuracy = 0
        
        # Save game progress
        game_data = {
            'user_id': session['user_id'],
            'game_type': game_type,
            'difficulty': difficulty,
            'score': score,
            'total_questions': total_questions,
            'accuracy': round(accuracy, 2),
            'timestamp': file_manager.get_timestamp()
        }
        
        fieldnames = ['user_id', 'game_type', 'difficulty', 'score', 'total_questions', 'accuracy', 'timestamp']
        file_manager.append_csv('data/dyslexia/games.csv', game_data, fieldnames)
        
        return jsonify({
            'success': True,
            'score': score,
            'total': total_questions,
            'accuracy': round(accuracy, 2),
            'message': f'Great job! You got {score} out of {total_questions} correct!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing game results: {str(e)}'
        }), 500
@dyslexia_bp.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    """Handle text-to-speech requests"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({'success': False, 'message': 'No text provided'})
    
    # For now, return success - actual TTS is handled client-side
    # In production, you could integrate with services like Google TTS API
    return jsonify({
        'success': True,
        'message': 'Text ready for speech synthesis',
        'text': text
    })
