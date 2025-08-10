#!/bin/bash
# Build script for Render deployment

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)"

echo "Creating data directories..."
mkdir -p data/{users,progress,dyslexia,dyscalculia,dysgraphia,dyspraxia,ai_models}
mkdir -p static/{uploads,user_data}

echo "Build completed successfully!"
