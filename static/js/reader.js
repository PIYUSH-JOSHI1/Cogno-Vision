class DyslexiaReader {
    constructor() {
        this.currentSettings = {
            fontSize: 16,
            lineSpacing: 1.5,
            contrastMode: 'normal',
            fontFamily: 'OpenDyslexic'
        };
        this.speechSynthesis = window.speechSynthesis;
        this.currentUtterance = null;
        this.isReading = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadUserSettings();
    }
    
    initializeElements() {
        // Settings elements
        this.settingsBtn = document.getElementById('settingsBtn');
        this.settingsPanel = document.getElementById('settingsPanel');
        this.fontSizeValue = document.getElementById('fontSizeValue');
        this.lineSpacingValue = document.getElementById('lineSpacingValue');
        this.contrastMode = document.getElementById('contrastMode');
        this.fontFamily = document.getElementById('fontFamily');
        this.readingRuler = document.getElementById('readingRuler');
        this.saveSettings = document.getElementById('saveSettings');
        
        // Action elements
        this.textInput = document.getElementById('textInput');
        this.simplifyBtn = document.getElementById('simplifyBtn');
        this.readAloudBtn = document.getElementById('readAloudBtn');
        this.annotateBtn = document.getElementById('annotateBtn');
        this.stopBtn = document.getElementById('stopBtn');
        
        // Display elements
        this.originalText = document.getElementById('originalText');
        this.simplifiedText = document.getElementById('simplifiedText');
        this.annotationsPanel = document.getElementById('annotationsPanel');
        this.annotationsContent = document.getElementById('annotationsContent');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.readingRulerOverlay = document.getElementById('readingRulerOverlay');
    }
    
    bindEvents() {
        // Settings events
        this.settingsBtn.addEventListener('click', () => this.toggleSettings());
        document.getElementById('fontSizeUp').addEventListener('click', () => this.adjustFontSize(2));
        document.getElementById('fontSizeDown').addEventListener('click', () => this.adjustFontSize(-2));
        document.getElementById('lineSpacingUp').addEventListener('click', () => this.adjustLineSpacing(0.1));
        document.getElementById('lineSpacingDown').addEventListener('click', () => this.adjustLineSpacing(-0.1));
        this.contrastMode.addEventListener('change', () => this.updateContrastMode());
        this.fontFamily.addEventListener('change', () => this.updateFontFamily());
        this.readingRuler.addEventListener('change', () => this.toggleReadingRuler());
        this.saveSettings.addEventListener('click', () => this.saveUserSettings());
        
        // Action events
        this.simplifyBtn.addEventListener('click', () => this.simplifyText());
        this.readAloudBtn.addEventListener('click', () => this.readAloud());
        this.annotateBtn.addEventListener('click', () => this.annotateText());
        this.stopBtn.addEventListener('click', () => this.stopReading());
        
        // Mouse tracking for reading ruler
        document.addEventListener('mousemove', (e) => this.updateReadingRuler(e));
    }
    
    loadUserSettings() {
        // Apply current user settings from template
        this.applyTextStyles();
    }
    
    toggleSettings() {
        this.settingsPanel.classList.toggle('hidden');
    }
    
    adjustFontSize(change) {
        this.currentSettings.fontSize = Math.max(12, Math.min(32, this.currentSettings.fontSize + change));
        this.fontSizeValue.textContent = this.currentSettings.fontSize + 'px';
        this.applyTextStyles();
    }
    
    adjustLineSpacing(change) {
        this.currentSettings.lineSpacing = Math.max(1.0, Math.min(3.0, this.currentSettings.lineSpacing + change));
        this.lineSpacingValue.textContent = this.currentSettings.lineSpacing.toFixed(1);
        this.applyTextStyles();
    }
    
    updateContrastMode() {
        this.currentSettings.contrastMode = this.contrastMode.value;
        this.applyTextStyles();
    }
    
    updateFontFamily() {
        this.currentSettings.fontFamily = this.fontFamily.value;
        this.applyTextStyles();
    }
    
    toggleReadingRuler() {
        if (this.readingRuler.checked) {
            this.readingRulerOverlay.classList.remove('hidden');
        } else {
            this.readingRulerOverlay.classList.add('hidden');
        }
    }
    
    updateReadingRuler(event) {
        if (this.readingRuler.checked) {
            const rect = this.originalText.getBoundingClientRect();
            if (event.clientX >= rect.left && event.clientX <= rect.right &&
                event.clientY >= rect.top && event.clientY <= rect.bottom) {
                this.readingRulerOverlay.style.top = (event.clientY - 20) + 'px';
                this.readingRulerOverlay.style.left = rect.left + 'px';
                this.readingRulerOverlay.style.width = rect.width + 'px';
            }
        }
    }
    
    applyTextStyles() {
        const textElements = document.querySelectorAll('.text-content');
        textElements.forEach(element => {
            element.style.fontSize = this.currentSettings.fontSize + 'px';
            element.style.lineHeight = this.currentSettings.lineSpacing;
            
            // Apply font family
            if (this.currentSettings.fontFamily === 'OpenDyslexic') {
                element.classList.add('dyslexic-font');
                element.classList.remove('lexend-font');
            } else if (this.currentSettings.fontFamily === 'Lexend') {
                element.classList.add('lexend-font');
                element.classList.remove('dyslexic-font');
            } else {
                element.classList.remove('dyslexic-font', 'lexend-font');
                element.style.fontFamily = this.currentSettings.fontFamily;
            }
            
            // Apply contrast mode
            if (this.currentSettings.contrastMode === 'high') {
                element.classList.add('high-contrast');
            } else {
                element.classList.remove('high-contrast');
            }
        });
    }
    
    async saveUserSettings() {
        try {
            const response = await fetch('/auth/update-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.currentSettings)
            });
            
            const result = await response.json();
            if (result.success) {
                this.showNotification('Settings saved successfully!', 'success');
            }
        } catch (error) {
            this.showNotification('Error saving settings', 'error');
        }
    }
    
    async simplifyText() {
        const text = this.textInput.value.trim();
        if (!text) {
            this.showNotification('Please enter some text first', 'warning');
            return;
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/reader/simplify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.originalText.innerHTML = `<p>${result.original}</p>`;
                this.simplifiedText.innerHTML = `<p>${result.simplified}</p>`;
                this.applyTextStyles();
                this.showNotification('Text simplified successfully!', 'success');
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error simplifying text', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async annotateText() {
        const text = this.textInput.value.trim();
        if (!text) {
            this.showNotification('Please enter some text first', 'warning');
            return;
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/reader/annotate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayAnnotations(result.annotations);
                this.annotationsPanel.classList.remove('hidden');
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error annotating text', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    displayAnnotations(annotations) {
        let html = `
            <div class="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                    <strong>Word Count:</strong> ${annotations.word_count}<br>
                    <strong>Reading Level:</strong> ${annotations.reading_level}
                </div>
            </div>
        `;
        
        if (Object.keys(annotations.annotations).length > 0) {
            html += '<h4 class="font-semibold mb-2">Difficult Words:</h4>';
            html += '<div class="grid md:grid-cols-2 gap-2">';
            
            for (const [word, info] of Object.entries(annotations.annotations)) {
                html += `
                    <div class="bg-white p-2 rounded border">
                        <strong>${word}</strong><br>
                        <small>Syllables: ${info.syllables} | Difficulty: ${info.difficulty}</small>
                    </div>
                `;
            }
            html += '</div>';
        }
        
        this.annotationsContent.innerHTML = html;
    }
    
    readAloud() {
        if (this.isReading) {
            this.stopReading();
            return;
        }
        
        const textToRead = this.simplifiedText.textContent.trim() || this.originalText.textContent.trim() || this.textInput.value.trim();
        
        if (!textToRead) {
            this.showNotification('No text to read', 'warning');
            return;
        }
        
        this.currentUtterance = new SpeechSynthesisUtterance(textToRead);
        this.currentUtterance.rate = 0.8; // Slower rate for dyslexic readers
        this.currentUtterance.pitch = 1.0;
        this.currentUtterance.volume = 1.0;
        
        this.currentUtterance.onstart = () => {
            this.isReading = true;
            this.readAloudBtn.classList.add('hidden');
            this.stopBtn.classList.remove('hidden');
        };
        
        this.currentUtterance.onend = () => {
            this.stopReading();
        };
        
        this.currentUtterance.onerror = () => {
            this.stopReading();
            this.showNotification('Error with text-to-speech', 'error');
        };
        
        this.speechSynthesis.speak(this.currentUtterance);
    }
    
    stopReading() {
        if (this.currentUtterance) {
            this.speechSynthesis.cancel();
        }
        this.isReading = false;
        this.readAloudBtn.classList.remove('hidden');
        this.stopBtn.classList.add('hidden');
    }
    
    showLoading(show) {
        if (show) {
            this.loadingIndicator.classList.remove('hidden');
        } else {
            this.loadingIndicator.classList.add('hidden');
        }
    }
    
    showNotification(message, type) {
        // Create a simple notification
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

// Initialize the reader when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new DyslexiaReader();
});
