#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Create necessary directories
mkdir -p data/users data/progress data/dyslexia data/dyscalculia data/dysgraphia data/dyspraxia data/ai_models static/uploads static/user_data

# Start the application
gunicorn --bind 0.0.0.0:$PORT wsgi:app
