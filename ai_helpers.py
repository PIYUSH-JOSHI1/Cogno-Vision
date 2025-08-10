import requests
import json
import re
from typing import Dict, List
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class AIHelpers:
    def __init__(self, config=None):
        self.config = config or {}
        self.pipeline = None
        self._initialize_pipeline()
        
        
    def _initialize_pipeline(self):
        """Initialize local transformers pipeline"""
        try:
            if self.config.get('USE_LOCAL_MODELS', True):
                # Disable TensorFlow to avoid conflicts
                import os
                os.environ['USE_TF'] = 'false'
                os.environ['USE_TORCH'] = 'true'
                
                from transformers import pipeline
                
                model_name = self.config.get('AI_MODEL_NAME', 'google/flan-t5-small')
                cache_dir = self.config.get('MODEL_CACHE_DIR', './data/ai_models')
                
                # Ensure cache directory exists
                os.makedirs(cache_dir, exist_ok=True)
                
                print(f"Initializing local AI model: {model_name}")
                
                # Set environment variable for cache directory
                os.environ['TRANSFORMERS_CACHE'] = cache_dir
                
                self.pipeline = pipeline(
                    "text2text-generation",
                    model=model_name,
                    framework="pt"  # Force PyTorch
                )
                print("Local AI model initialized successfully!")
            else:
                self.pipeline = None
                print("Local models disabled, using rule-based fallback")
        except Exception as e:
            print(f"Error initializing local pipeline: {e}")
            self.pipeline = None
            self.pipeline = None
            
    def simplify_text(self, text: str) -> str:
        """
        Simplify text using local transformers model or rule-based approach
        """
        try:
            # Try local model first if available
            if self.config.get('USE_LOCAL_MODELS', True):
                return self._simplify_with_local_model(text)
            else:
                # Fallback to rule-based simplification
                return self._simplify_rule_based(text)
        except Exception as e:
            print(f"Error in text simplification: {e}")
            return self._simplify_rule_based(text)
    
    def _simplify_with_local_model(self, text: str) -> str:
        """Use local T5 model for text simplification"""
        try:
            if self.pipeline:
                prompt = f"simplify: {text}"
                result = self.pipeline(
                    prompt,
                    max_length=min(len(text.split()) * 2, 512),
                    do_sample=True,
                    temperature=0.7,
                    num_return_sequences=1
                )
                if result and len(result) > 0:
                    return result[0]['generated_text']
            return self._simplify_rule_based(text)
        except Exception as e:
            print(f"Error with local model: {e}")
            return self._simplify_rule_based(text)
    
    def _simplify_with_huggingface(self, text: str) -> str:
        """Use HuggingFace T5 model for text simplification"""
        headers = {
            "Authorization": f"Bearer {self.config.get('HUGGINGFACE_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": f"simplify: {text}",
            "parameters": {
                "max_length": len(text.split()) * 2,
                "temperature": 0.7
            }
        }
        
        response = requests.post(
            self.config.get('HUGGINGFACE_API_URL'),
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', text)
        
        return self._simplify_rule_based(text)
    
    def _simplify_with_local_model(self, text: str) -> str:
        """Use local T5 model for text simplification"""
        try:
            if self.pipeline:
                prompt = f"simplify: {text}"
                result = self.pipeline(prompt, max_length=len(text.split()) * 2, temperature=0.7)
                return result[0]['generated_text']
            else:
                return self._simplify_rule_based(text)
        except Exception as e:
            print(f"Error with local model: {e}")
            return self._simplify_rule_based(text)
    
    def _simplify_rule_based(self, text: str) -> str:
        """Rule-based text simplification for dyslexic readers"""
        # Split into sentences
        sentences = sent_tokenize(text)
        simplified_sentences = []
        
        for sentence in sentences:
            # Remove complex punctuation
            sentence = re.sub(r'[;:]', '.', sentence)
            
            # Split long sentences at conjunctions
            parts = re.split(r'\b(and|but|or|because|since|while|although)\b', sentence)
            
            for part in parts:
                part = part.strip()
                if len(part) > 3:  # Ignore conjunctions and short parts
                    # Simplify vocabulary
                    part = self._replace_complex_words(part)
                    simplified_sentences.append(part)
        
        return '. '.join(simplified_sentences)
    
    def _replace_complex_words(self, text: str) -> str:
        """Replace complex words with simpler alternatives"""
        replacements = {
            'utilize': 'use',
            'demonstrate': 'show',
            'approximately': 'about',
            'consequently': 'so',
            'furthermore': 'also',
            'nevertheless': 'but',
            'subsequently': 'then',
            'magnificent': 'great',
            'enormous': 'huge',
            'diminish': 'reduce',
            'acquire': 'get',
            'commence': 'start',
            'terminate': 'end'
        }
        
        for complex_word, simple_word in replacements.items():
            text = re.sub(r'\b' + complex_word + r'\b', simple_word, text, flags=re.IGNORECASE)
        
        return text
    
    def annotate_text(self, text: str) -> Dict:
        """Add helpful annotations for dyslexic readers"""
        words = word_tokenize(text)
        annotations = {}
        
        # Identify difficult words (longer than 7 characters)
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if len(clean_word) > 7:
                annotations[word] = {
                    'syllables': self._count_syllables(clean_word),
                    'difficulty': 'hard' if len(clean_word) > 10 else 'medium'
                }
        
        return {
            'text': text,
            'annotations': annotations,
            'word_count': len(words),
            'reading_level': self._estimate_reading_level(text)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word"""
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
    
    def _estimate_reading_level(self, text: str) -> str:
        """Estimate reading difficulty level"""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        if avg_sentence_length < 10 and avg_word_length < 5:
            return 'Easy'
        elif avg_sentence_length < 15 and avg_word_length < 6:
            return 'Medium'
        else:
            return 'Hard'
    
    def generate_phoneme_breakdown(self, word: str) -> List[str]:
        """Generate phoneme breakdown for a word (simplified)"""
        # This is a simplified phoneme breakdown
        # In production, you'd use a proper phonemizer library
        phoneme_patterns = {
            'ch': ['ch'],
            'sh': ['sh'],
            'th': ['th'],
            'ph': ['f'],
            'ck': ['k'],
            'ng': ['ng']
        }
        
        word = word.lower()
        phonemes = []
        i = 0
        
        while i < len(word):
            # Check for two-letter combinations first
            if i < len(word) - 1:
                two_char = word[i:i+2]
                if two_char in phoneme_patterns:
                    phonemes.extend(phoneme_patterns[two_char])
                    i += 2
                    continue
            
            # Single character
            char = word[i]
            if char.isalpha():
                phonemes.append(char)
            i += 1
        
        return phonemes
