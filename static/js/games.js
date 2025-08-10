class PhonicGames {
    constructor() {
        this.currentGame = null;
        this.currentSession = null;
        this.gameAnswers = [];
        this.currentQuestionIndex = 0;
        
        this.initializeElements();
        this.bindEvents();
    }
    
    initializeElements() {
        this.gameModal = document.getElementById('gameModal');
        this.gameTitle = document.getElementById('gameTitle');
        this.gameContent = document.getElementById('gameContent');
        this.gameScore = document.getElementById('gameScore');
        this.submitGame = document.getElementById('submitGame');
        this.closeGameModal = document.getElementById('closeGameModal');
    }
    
    bindEvents() {
        this.closeGameModal.addEventListener('click', () => this.closeGame());
        this.submitGame.addEventListener('click', () => this.submitAnswers());
        
        // Close modal when clicking outside
        this.gameModal.addEventListener('click', (e) => {
            if (e.target === this.gameModal) {
                this.closeGame();
            }
        });
    }
    
    async startGame(gameId, difficulty = 'easy') {
    this.currentGame = { id: gameId, difficulty: difficulty };

    // We only have a backend route for the phonics game for now
    if (gameId === 'sound-match') {
        try {
            const response = await fetch('/dyslexia/games/phonics', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ difficulty: difficulty, count: 5 })
            });

            const result = await response.json();

            if (result.success) {
                this.currentSession = result; // Store the whole session data
                this.gameAnswers = [];
                this.currentQuestionIndex = 0;

                this.displayGame(result.questions);
                this.gameModal.style.display = 'block';
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error starting game', 'error');
        }
    } else if (gameId === 'word-builder') {
         // For now, word-builder uses hardcoded questions on the client
         const questions = [
            { sounds: ['c', 'a', 't'], correct: 'cat' },
            { sounds: ['d', 'o', 'g'], correct: 'dog' },
            { sounds: ['f', 'i', 'sh'], correct: 'fish' },
            { sounds: ['b', 'i', 'r', 'd'], correct: 'bird' },
            { sounds: ['tr', 'ee'], correct: 'tree' }
        ];
        this.currentSession = { questions: questions };
        this.displayGame(questions);
        this.gameModal.style.display = 'block';
    }
}
    displayGame(content) {
        this.gameTitle.textContent = this.currentGame.name;
        this.gameScore.textContent = `Score: 0 / ${this.currentGame.max_score}`;
        
        let html = '';
        
        switch (this.currentGame.id) {
            case 'sound-match':
                html = this.renderSoundMatchGame(content.questions);
                break;
            case 'syllable-count':
                html = this.renderSyllableCountGame(content.questions);
                break;
            case 'word-builder':
                html = this.renderWordBuilderGame(content.questions);
                break;
            case 'rhyme-time':
                html = this.renderRhymeTimeGame(content.questions);
                break;
        }
        
        this.gameContent.innerHTML = html;
        this.submitGame.classList.remove('hidden');
    }
    
    renderSoundMatchGame(questions) {
        let html = '<div class="space-y-6">';
        
        questions.forEach((question, index) => {
            html += `
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-lg font-semibold mb-3">
                        ${index + 1}. Listen to the word: <strong>"${question.sound}"</strong>
                    </h4>
                    <p class="mb-3 text-gray-600">Which shows the correct sounds?</p>
                    <div class="space-y-2">
            `;
            
            question.options.forEach((option, optionIndex) => {
                html += `
                    <label class="flex items-center p-2 bg-white rounded border hover:bg-blue-50 cursor-pointer">
                        <input type="radio" name="question_${index}" value="${optionIndex}" class="mr-3">
                        <span class="text-lg font-mono">${option}</span>
                    </label>
                `;
            });
            
            html += '</div></div>';
        });
        
        html += '</div>';
        return html;
    }
    
    renderSyllableCountGame(questions) {
        let html = '<div class="space-y-6">';
        
        questions.forEach((question, index) => {
            html += `
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-lg font-semibold mb-3">
                        ${index + 1}. How many syllables in: <strong>"${question.word}"</strong>
                    </h4>
                    <div class="flex space-x-4">
            `;
            
            for (let i = 1; i <= 4; i++) {
                html += `
                    <label class="flex items-center p-3 bg-white rounded border hover:bg-blue-50 cursor-pointer">
                        <input type="radio" name="question_${index}" value="${i}" class="mr-2">
                        <span class="text-lg font-bold">${i}</span>
                    </label>
                `;
            }
            
            html += '</div></div>';
        });
        
        html += '</div>';
        return html;
    }
    
    renderWordBuilderGame(questions) {
        let html = '<div class="space-y-6">';
        
        questions.forEach((question, index) => {
            html += `
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-lg font-semibold mb-3">
                        ${index + 1}. Build a word from these sounds:
                    </h4>
                    <div class="flex flex-wrap gap-2 mb-4">
            `;
            
            question.sounds.forEach(sound => {
                html += `<span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-mono text-lg">${sound}</span>`;
            });
            
            html += `
                    </div>
                    <input type="text" name="question_${index}" placeholder="Type the word here..." 
                           class="w-full p-3 border rounded-lg text-lg" autocomplete="off">
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }
    
    renderRhymeTimeGame(questions) {
        let html = '<div class="space-y-6">';
        
        questions.forEach((question, index) => {
            html += `
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-lg font-semibold mb-3">
                        ${index + 1}. Which word rhymes with: <strong>"${question.word}"</strong>
                    </h4>
                    <div class="grid grid-cols-3 gap-3">
            `;
            
            question.options.forEach((option, optionIndex) => {
                html += `
                    <label class="flex items-center justify-center p-3 bg-white rounded border hover:bg-blue-50 cursor-pointer">
                        <input type="radio" name="question_${index}" value="${optionIndex}" class="mr-2">
                        <span class="text-lg">${option}</span>
                    </label>
                `;
            });
            
            html += '</div></div>';
        });
        
        html += '</div>';
        return html;
    }
    
async submitAnswers() {
    this.collectAnswers();

    if (this.gameAnswers.length !== this.currentSession.questions.length) {
        this.showNotification('Please answer all questions', 'warning');
        return;
    }

    try {
        const response = await fetch('/dyslexia/games/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                answers: this.gameAnswers,
                game_type: this.currentGame.id === 'sound-match' ? 'phonics' : 'word-building',
                difficulty: this.currentGame.difficulty,
                questions: this.currentSession.questions // Send the questions back for scoring
            })
        });

        const result = await response.json();

        if (result.success) {
            this.displayResults(result);
        } else {
            this.showNotification(result.message, 'error');
        }
    } catch (error) {
        this.showNotification('Error submitting answers', 'error');
    }
}

collectAnswers() {
    this.gameAnswers = [];
    const form = this.gameContent;

    if (this.currentGame.id === 'word-builder') {
            // Handle text inputs for word builder
            const inputs = form.querySelectorAll('input[type="text"]');
            inputs.forEach(input => {
                this.gameAnswers.push(input.value.toLowerCase().trim());
            });
        } else {
            // Handle radio buttons for other games
            const questions = form.querySelectorAll('input[type="radio"]:checked');
            questions.forEach(input => {
                this.gameAnswers.push(parseInt(input.value));
            });
        }
    }
    
    displayResults(result) {
        const percentage = Math.round(result.percentage);
        let emoji = percentage >= 80 ? '🎉' : percentage >= 60 ? '👍' : '💪';
        
        this.gameContent.innerHTML = `
            <div class="text-center py-8">
                <div class="text-6xl mb-4">${emoji}</div>
                <h3 class="text-2xl font-bold mb-4">Game Complete!</h3>
                <div class="text-xl mb-4">
                    Score: <span class="font-bold text-dyslexia-blue">${result.score}</span> / ${result.max_score}
                </div>
                <div class="text-lg mb-4">
                    Accuracy: <span class="font-bold">${percentage}%</span>
                </div>
                <p class="text-gray-600 mb-6">${result.feedback}</p>
                <button onclick="location.reload()" 
                        class="bg-dyslexia-blue text-white px-6 py-3 rounded-lg text-lg hover:bg-blue-600">
                    Play Again
                </button>
            </div>
        `;
        
        this.submitGame.classList.add('hidden');
        this.gameScore.textContent = `Final Score: ${result.score} / ${result.max_score}`;
    }
    
    closeGame() {
        this.gameModal.classList.add('hidden');
        this.currentGame = null;
        this.currentSession = null;
        this.gameAnswers = [];
    }
    
    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 
            type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Global function to start games (called from template)
let gamesInstance;

function startGame(gameId) {
    if (!gamesInstance) {
        gamesInstance = new PhonicGames();
    }
    gamesInstance.startGame(gameId);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    gamesInstance = new PhonicGames();
});
