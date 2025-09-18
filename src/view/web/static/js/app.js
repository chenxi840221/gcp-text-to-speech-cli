// Text-to-Speech Application JavaScript

class TTSApp {
    constructor() {
        this.apiBaseUrl = '/api/v1/tts';
        this.voices = {};
        this.currentLanguage = 'en-US';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadVoices();
        this.updateCharacterCount();
    }

    bindEvents() {
        // Input type toggle
        document.querySelectorAll('input[name="inputType"]').forEach(radio => {
            radio.addEventListener('change', this.toggleInputType.bind(this));
        });

        // Character counter
        document.getElementById('textContent').addEventListener('input', this.updateCharacterCount.bind(this));

        // Language change
        document.getElementById('languageSelect').addEventListener('change', this.onLanguageChange.bind(this));

        // Range sliders
        document.getElementById('speakingRate').addEventListener('input', this.updateRateDisplay.bind(this));
        document.getElementById('pitch').addEventListener('input', this.updatePitchDisplay.bind(this));

        // Generate button
        document.getElementById('generateBtn').addEventListener('click', this.generateSpeech.bind(this));

        // Example buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', this.loadExample.bind(this));
        });
    }

    toggleInputType() {
        const inputType = document.querySelector('input[name="inputType"]:checked').value;
        const textSection = document.getElementById('textInputSection');
        const ssmlSection = document.getElementById('ssmlInputSection');

        if (inputType === 'text') {
            textSection.style.display = 'block';
            ssmlSection.style.display = 'none';
        } else {
            textSection.style.display = 'none';
            ssmlSection.style.display = 'block';
        }
    }

    updateCharacterCount() {
        const textContent = document.getElementById('textContent');
        const charCount = document.getElementById('charCount');
        const count = textContent.value.length;

        charCount.textContent = count;
        charCount.style.color = count > 4500 ? '#f44336' : '#1976d2';
    }

    updateRateDisplay() {
        const rate = document.getElementById('speakingRate').value;
        document.getElementById('rateValue').textContent = rate;
    }

    updatePitchDisplay() {
        const pitch = document.getElementById('pitch').value;
        document.getElementById('pitchValue').textContent = pitch;
    }

    async loadVoices() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/voices?language_code=${this.currentLanguage}`);
            const data = await response.json();

            if (data.success) {
                this.voices[this.currentLanguage] = data.data.voices;
                this.populateVoiceSelect();
            } else {
                console.error('Failed to load voices:', data.error);
                this.showAlert('Failed to load voices', 'danger');
            }
        } catch (error) {
            console.error('Error loading voices:', error);
            this.showAlert('Error loading voices', 'danger');
        }
    }

    populateVoiceSelect() {
        const select = document.getElementById('voiceSelect');
        select.innerHTML = '<option value="">Select a voice...</option>';

        const voices = this.voices[this.currentLanguage];
        if (!voices) return;

        // Group voices by type
        const categories = ['neural2', 'wavenet', 'standard', 'news', 'studio'];

        categories.forEach(category => {
            const categoryVoices = voices[category] || [];
            if (categoryVoices.length > 0) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = this.formatCategoryName(category);

                categoryVoices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.name;
                    option.textContent = `${voice.name} (${voice.ssml_gender})`;
                    option.dataset.type = category;
                    optgroup.appendChild(option);
                });

                select.appendChild(optgroup);
            }
        });
    }

    formatCategoryName(category) {
        const names = {
            'neural2': 'Neural2 (Premium)',
            'wavenet': 'WaveNet (High Quality)',
            'standard': 'Standard',
            'news': 'News (Broadcast Style)',
            'studio': 'Studio (Ultra Premium)'
        };
        return names[category] || category;
    }

    onLanguageChange() {
        this.currentLanguage = document.getElementById('languageSelect').value;
        if (!this.voices[this.currentLanguage]) {
            this.loadVoices();
        } else {
            this.populateVoiceSelect();
        }
    }

    loadExample(event) {
        const btn = event.target;
        const exampleText = btn.dataset.text;
        const exampleSSML = btn.dataset.ssml;

        if (exampleText) {
            document.getElementById('textInput').checked = true;
            document.getElementById('textContent').value = exampleText;
            this.toggleInputType();
            this.updateCharacterCount();
        } else if (exampleSSML) {
            document.getElementById('ssmlInput').checked = true;
            document.getElementById('ssmlContent').value = exampleSSML;
            this.toggleInputType();
        }
    }

    async generateSpeech() {
        const inputType = document.querySelector('input[name="inputType"]:checked').value;
        const text = document.getElementById('textContent').value.trim();
        const ssml = document.getElementById('ssmlContent').value.trim();

        if (inputType === 'text' && !text) {
            this.showAlert('Please enter some text to convert to speech', 'warning');
            return;
        }

        if (inputType === 'ssml' && !ssml) {
            this.showAlert('Please enter SSML content to convert to speech', 'warning');
            return;
        }

        const requestData = {
            language_code: document.getElementById('languageSelect').value,
            voice_name: document.getElementById('voiceSelect').value || null,
            ssml_gender: document.getElementById('genderSelect').value,
            audio_encoding: document.getElementById('encodingSelect').value,
            speaking_rate: parseFloat(document.getElementById('speakingRate').value),
            pitch: parseFloat(document.getElementById('pitch').value),
            user_id: this.generateUserId()
        };

        if (inputType === 'text') {
            requestData.text = text;
        } else {
            requestData.ssml = ssml;
        }

        this.showLoading(true);

        try {
            const endpoint = inputType === 'text' ? '/synthesize' : '/synthesize-ssml';
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (data.success) {
                this.displayAudioResult(data.data);
                this.showAlert('Speech generated successfully!', 'success');
            } else {
                this.showAlert(`Error: ${data.error.message}`, 'danger');
            }
        } catch (error) {
            console.error('Error generating speech:', error);
            this.showAlert('Failed to generate speech. Please try again.', 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    displayAudioResult(data) {
        const audioResult = document.getElementById('audioResult');
        const noAudio = document.getElementById('noAudio');
        const audioPlayer = document.getElementById('audioPlayer');
        const downloadLink = document.getElementById('downloadLink');
        const metadata = document.getElementById('audioMetadata');

        // Show audio section
        audioResult.style.display = 'block';
        noAudio.style.display = 'none';

        // Set audio source
        audioPlayer.src = data.audio_url;

        // Set download link
        downloadLink.href = data.audio_url;
        const extension = data.metadata.audio_encoding.toLowerCase().replace('_', '.');
        downloadLink.download = `tts_audio_${data.request_id}.${extension}`;

        // Display metadata
        metadata.innerHTML = `
            <strong>Duration:</strong> ${data.duration_seconds.toFixed(2)}s |
            <strong>Characters:</strong> ${data.character_count} |
            <strong>Processing Time:</strong> ${data.processing_time_ms}ms<br>
            <strong>Voice:</strong> ${data.metadata.voice_name || 'Default'} |
            <strong>Language:</strong> ${data.metadata.language_code} |
            <strong>Format:</strong> ${data.metadata.audio_encoding}
        `;

        // Add animation
        audioResult.classList.add('fade-in');
    }

    showLoading(show) {
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        const generateBtn = document.getElementById('generateBtn');

        if (show) {
            modal.show();
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
        } else {
            modal.hide();
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Speech';
        }
    }

    showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show slide-in`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at top of main content
        const container = document.querySelector('.container');
        container.insertBefore(alert, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    generateUserId() {
        // Generate a simple user ID for demo purposes
        let userId = localStorage.getItem('tts_user_id');
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('tts_user_id', userId);
        }
        return userId;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TTSApp();
});

// Service Worker registration for offline capability (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}