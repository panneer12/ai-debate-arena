/**
 * AI Debate Arena - Voice Manager
 * Handles Text-to-Speech functionality using Web Speech API
 */

class VoiceManager {
    constructor() {
        this.synth = window.speechSynthesis;
        this.voices = {};
        this.enabled = true;
        this.speed = 1.0;
        this.volume = 1.0;
        this.pitch = 1.0;
        this.queue = [];
        this.isSpeaking = false;
        this.currentUtterance = null;
        this.isPaused = false;
        this.currentMessageCard = null;
        this.currentHighlightedWord = null;

        // Initialize voices
        this.init();

        // Handle voices changed event (some browsers load voices async)
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = () => this.init();
        }
    }

    /**
     * Initialize voice system and assign voices to agents
     */
    init() {
        const availableVoices = this.synth.getVoices();

        if (availableVoices.length === 0) {
            console.warn('No voices available yet');
            return;
        }

        console.log(`Loaded ${availableVoices.length} voices`);

        // Assign specific voices to different agents for variety
        this.voices = {
            moderator: this.findBestVoice(availableVoices, ['Google US English', 'Microsoft David', 'Alex'], 'en-US'),
            conservative: this.findBestVoice(availableVoices, ['Google UK English Male', 'Microsoft George', 'Daniel'], 'en-GB'),
            progressive: this.findBestVoice(availableVoices, ['Google US English', 'Microsoft Zira', 'Samantha'], 'en-US'),
            factchecker: this.findBestVoice(availableVoices, ['Google UK English Female', 'Microsoft Hazel', 'Karen'], 'en-GB'),
            devilsadvocate: this.findBestVoice(availableVoices, ['Google UK English Male', 'Microsoft Ravi', 'Oliver'], 'en-GB'),
            synthesizer: this.findBestVoice(availableVoices, ['Google US English', 'Microsoft Mark', 'Fred'], 'en-US')
        };

        // Fallback to default voice if specific ones not found
        const defaultVoice = availableVoices.find(v => v.lang.startsWith('en')) || availableVoices[0];
        Object.keys(this.voices).forEach(agent => {
            if (!this.voices[agent]) {
                this.voices[agent] = defaultVoice;
            }
        });
    }

    /**
     * Find best matching voice from available voices
     * @param {Array} voices - Available voices
     * @param {Array} preferredNames - Preferred voice names
     * @param {string} lang - Preferred language
     * @returns {Object} Best matching voice
     */
    findBestVoice(voices, preferredNames, lang) {
        // Try to find exact match
        for (const name of preferredNames) {
            const voice = voices.find(v => v.name.includes(name) && v.lang.startsWith(lang));
            if (voice) return voice;
        }

        // Fallback to any voice with matching language
        return voices.find(v => v.lang.startsWith(lang)) || voices[0];
    }

    /**
     * Speak text with specified agent's voice
     * @param {string} text - Text to speak
     * @param {string} agent - Agent identifier
     * @param {Function} onEnd - Callback when speaking ends
     * @param {string} messageId - Optional message ID for word highlighting
     * @returns {Promise} Promise that resolves when speaking starts
     */
    speak(text, agent = 'moderator', onEnd = null, messageId = null) {
        return new Promise((resolve, reject) => {
            if (!this.enabled) {
                resolve();
                return;
            }

            // Add to queue
            this.queue.push({ text, agent, onEnd, resolve, reject, messageId });

            // Start processing queue if not already speaking
            if (!this.isSpeaking) {
                this.processQueue();
            }
        });
    }

    /**
     * Process speech queue
     */
    async processQueue() {
        if (this.queue.length === 0) {
            this.isSpeaking = false;
            this.currentMessageCard = null;
            this.updateUI('No one speaking', false);
            return;
        }

        this.isSpeaking = true;
        const { text, agent, onEnd, resolve, reject, messageId } = this.queue.shift();

        // Find message card if messageId provided
        if (messageId) {
            this.currentMessageCard = document.querySelector(`[data-message-id="${messageId}"]`);
            if (this.currentMessageCard) {
                this.currentMessageCard.classList.add('speaking');
            }
        }

        try {
            await this.speakNow(text, agent, () => {
                // Cleanup highlighting
                this.clearHighlighting();

                if (onEnd) onEnd();
                resolve();
                // Process next in queue
                this.processQueue();
            });
        } catch (error) {
            console.error('Speech error:', error);
            this.clearHighlighting();
            reject(error);
            this.processQueue();
        }
    }

    /**
     * Speak text immediately
     * @param {string} text - Text to speak
     * @param {string} agent - Agent identifier
     * @param {Function} onEnd - Callback when done
     */
    speakNow(text, agent, onEnd) {
        return new Promise((resolve, reject) => {
            // Cancel any ongoing speech
            this.synth.cancel();

            // Create utterance
            const utterance = new SpeechSynthesisUtterance(text);

            // Set voice
            const voice = this.voices[agent.toLowerCase()] || this.voices.moderator;
            if (voice) {
                utterance.voice = voice;
                utterance.lang = voice.lang;
            }

            // Set parameters
            utterance.rate = this.speed;
            utterance.pitch = this.pitch;
            utterance.volume = this.volume;

            // Event handlers
            utterance.onstart = () => {
                this.currentUtterance = utterance;
                this.updateUI(Utils.getAgentDisplayName(agent), true);
                resolve();
            };

            utterance.onend = () => {
                this.currentUtterance = null;
                this.updateUI('No one speaking', false);
                if (onEnd) onEnd();
            };

            utterance.onerror = (event) => {
                console.error('Speech error:', event);
                this.currentUtterance = null;
                reject(event);
            };

            utterance.onpause = () => {
                this.isPaused = true;
            };

            utterance.onresume = () => {
                this.isPaused = false;
            };

            // Word boundary event for highlighting
            utterance.onboundary = (event) => {
                if (event.name === 'word' && this.currentMessageCard) {
                    this.highlightWordAtCharIndex(event.charIndex);
                }
            };

            // Speak
            this.synth.speak(utterance);
        });
    }

    /**
     * Pause current speech
     */
    pause() {
        if (this.isSpeaking && !this.isPaused) {
            this.synth.pause();
            this.isPaused = true;
            return true;
        }
        return false;
    }

    /**
     * Resume paused speech
     */
    resume() {
        if (this.isSpeaking && this.isPaused) {
            this.synth.resume();
            this.isPaused = false;
            return true;
        }
        return false;
    }

    /**
     * Stop current speech and clear queue
     */
    stop() {
        this.synth.cancel();
        this.queue = [];
        this.isSpeaking = false;
        this.isPaused = false;
        this.currentUtterance = null;
        this.updateUI('No one speaking', false);
    }

    /**
     * Skip current speech and move to next
     */
    skip() {
        this.synth.cancel();
        if (this.queue.length > 0) {
            this.processQueue();
        } else {
            this.isSpeaking = false;
            this.updateUI('No one speaking', false);
        }
    }

    /**
     * Set speech rate
     * @param {number} rate - Speech rate (0.5 to 2.0)
     */
    setSpeed(rate) {
        this.speed = Math.max(0.5, Math.min(2.0, rate));
    }

    /**
     * Set volume
     * @param {number} volume - Volume level (0.0 to 1.0)
     */
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
    }

    /**
     * Enable or disable voice
     * @param {boolean} enabled - Enable state
     */
    setEnabled(enabled) {
        this.enabled = enabled;
        if (!enabled) {
            this.stop();
        }
    }

    /**
     * Get current speaking status
     * @returns {boolean} True if speaking
     */
    getSpeakingStatus() {
        return this.isSpeaking;
    }

    /**
     * Get queue length
     * @returns {number} Number of items in queue
     */
    getQueueLength() {
        return this.queue.length;
    }

    /**
     * Update UI to reflect current speech status
     * @param {string} agentName - Name of speaking agent
     * @param {boolean} isActive - Whether actively speaking
     */
    updateUI(agentName, isActive) {
        const speakingElement = document.getElementById('speakingAgent');
        const nowSpeaking = document.getElementById('nowSpeaking');
        const speakingIcon = document.querySelector('.speaking-icon');

        if (speakingElement) {
            speakingElement.textContent = agentName;
        }

        if (nowSpeaking) {
            if (isActive) {
                nowSpeaking.classList.add('active');
            } else {
                nowSpeaking.classList.remove('active');
            }
        }

        if (speakingIcon) {
            speakingIcon.textContent = isActive ? '🔊' : '🔇';
        }

        // Update voice control buttons
        const pauseBtn = document.getElementById('pauseVoice');
        const resumeBtn = document.getElementById('resumeVoice');
        const skipBtn = document.getElementById('skipVoice');

        if (pauseBtn) pauseBtn.disabled = !isActive || this.isPaused;
        if (resumeBtn) resumeBtn.disabled = !isActive || !this.isPaused;
        if (skipBtn) skipBtn.disabled = !isActive;
    }

    /**
     * Get list of available voices
     * @returns {Array} Available voices
     */
    getAvailableVoices() {
        return this.synth.getVoices();
    }

    /**
     * Test voice with sample text
     * @param {string} agent - Agent to test
     */
    testVoice(agent = 'moderator') {
        const testTexts = {
            moderator: 'I will moderate this debate fairly and ensure all voices are heard.',
            conservative: 'Individual liberty and free markets are the foundation of prosperity.',
            progressive: 'We must work together to create a more equitable society for all.',
            factchecker: 'I will verify all claims with authoritative sources and evidence.',
            devilsadvocate: 'Let me challenge that assumption from a different perspective.',
            synthesizer: 'After analyzing all arguments, here is a balanced synthesis.'
        };

        const text = testTexts[agent] || 'Testing voice synthesis.';
        this.speak(text, agent);
    }

    /**
     * Highlight word at specific character index
     * @param {number} charIndex - Character index in the original text
     */
    highlightWordAtCharIndex(charIndex) {
        if (!this.currentMessageCard) return;

        // Remove previous highlighting
        if (this.currentHighlightedWord) {
            this.currentHighlightedWord.classList.remove('speaking');
        }

        // Find word span at this character index
        const messageContent = this.currentMessageCard.querySelector('.message-content');
        if (!messageContent) return;

        const words = messageContent.querySelectorAll('.word');
        for (const word of words) {
            const start = parseInt(word.getAttribute('data-char-start'));
            const end = parseInt(word.getAttribute('data-char-end'));

            if (charIndex >= start && charIndex < end) {
                word.classList.add('speaking');
                this.currentHighlightedWord = word;

                // Scroll word into view if needed
                word.scrollIntoView({
                    behavior: 'smooth',
                    block: 'nearest',
                    inline: 'nearest'
                });

                break;
            }
        }
    }

    /**
     * Clear all word highlighting
     */
    clearHighlighting() {
        if (this.currentHighlightedWord) {
            this.currentHighlightedWord.classList.remove('speaking');
            this.currentHighlightedWord = null;
        }

        if (this.currentMessageCard) {
            this.currentMessageCard.classList.remove('speaking');

            // Clear all word highlights in message
            const words = this.currentMessageCard.querySelectorAll('.word.speaking');
            words.forEach(word => word.classList.remove('speaking'));

            this.currentMessageCard = null;
        }
    }
}

// Create global voice manager instance
const voiceManager = new VoiceManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceManager;
}
