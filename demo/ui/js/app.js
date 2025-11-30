/**
 * AI Debate Arena - Main Application
 * Initializes and coordinates all UI components
 */

class DebateApp {
    constructor() {
        this.useMockData = false; // Backend is ready!
        this.mockInterval = null;
        this.currentTheme = 'dark'; // Default theme
        this.initializeTheme();
        this.initializeEventListeners();
        this.setupVoiceControls();
        this.setupModalHandlers();
        this.loadPreferences();
    }

    /**
     * Initialize theme from localStorage or default
     */
    initializeTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        this.setTheme(savedTheme, false);
    }

    /**
     * Set theme (light or dark)
     * @param {string} theme - Theme name ('light' or 'dark')
     * @param {boolean} save - Whether to save to localStorage
     */
    setTheme(theme, save = true) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);

        // Update theme toggle icon
        const themeIcon = document.querySelector('.theme-icon');
        if (themeIcon) {
            themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
        }

        // Save to localStorage
        if (save) {
            localStorage.setItem('theme', theme);
        }
    }

    /**
     * Toggle between light and dark theme
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        Utils.showToast(`Switched to ${newTheme} mode`, 'info', 2000);
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Theme toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Start debate button
        const startBtn = document.getElementById('startDebate');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.handleStartDebate());
        }

        // Stop debate button
        const stopBtn = document.getElementById('stopDebate');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.handleStopDebate());
        }

        // Clear debate button
        const clearBtn = document.getElementById('clearDebate');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.handleClearDebate());
        }

        // Quick topic chips
        const topicChips = document.querySelectorAll('.topic-chip');
        topicChips.forEach(chip => {
            chip.addEventListener('click', (e) => {
                const topic = e.target.getAttribute('data-topic');
                document.getElementById('topicInput').value = topic;
            });
        });

        // Export debate button
        const exportBtn = document.getElementById('exportDebate');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => debateManager.exportTranscript());
        }

        // WebSocket event handlers
        this.setupWebSocketHandlers();
    }

    /**
     * Setup WebSocket event handlers
     */
    setupWebSocketHandlers() {
        // Handle incoming messages
        debateWS.on('message', (data) => {
            console.log('WebSocket message:', data);

            // Add message to debate manager
            if (data.type && data.content) {
                debateManager.addMessage(data);
            }
        });

        // Handle status updates
        debateWS.on('status', (data) => {
            console.log('Status update:', data);

            if (data.status === 'running') {
                this.updateStatus('running', 'Debate Running');
                debateManager.isActive = true;
            } else if (data.status === 'stopped') {
                this.updateStatus('ready', 'Ready');
                debateManager.isActive = false;
                this.setDebateControlsState(false);
            } else if (data.status === 'synthesizing') {
                this.updateStatus('running', 'Synthesizing Results...');
            }
        });

        // Handle synthesis results
        debateWS.on('synthesis', (data) => {
            console.log('Synthesis:', data);

            // Format synthesis data for display
            const synthesis = {
                commonGround: data.common_ground?.summary || 'No common ground identified.',
                keyArguments: data.synthesis?.key_arguments || [],
                insights: data.synthesis?.summary || 'No insights available.'
            };

            // Add synthesis message to conversation feed
            const synthesisMessage = {
                type: 'SYNTHESIS',
                from_agent: 'Synthesizer',
                content: `## Common Ground\n${synthesis.commonGround}\n\n## Key Arguments\n${synthesis.keyArguments.join(', ')}\n\n## Final Synthesis\n${synthesis.insights}`,
                timestamp: new Date().toISOString()
            };
            debateManager.addMessage(synthesisMessage);

            // Also show modal popup
            debateManager.showSynthesis(synthesis);
        });

        // Handle round start
        debateWS.on('round_start', (data) => {
            console.log('Round start:', data);
            if (data.round) {
                debateManager.currentRound = data.round;
                debateManager.updateRoundDisplay(data.round, debateManager.rounds);
            }
        });

        // Handle connection
        debateWS.on('connected', () => {
            console.log('WebSocket connected');
            Utils.showToast('Connected to debate server', 'success', 2000);
        });

        // Handle disconnection
        debateWS.on('disconnected', () => {
            console.log('WebSocket disconnected');
            Utils.showToast('Disconnected from server', 'warning');
        });

        // Handle errors
        debateWS.on('error', (error) => {
            console.error('WebSocket error:', error);
            Utils.showToast('Connection error', 'error');
        });
    }

    /**
     * Setup voice control event listeners
     */
    setupVoiceControls() {
        // Enable voice checkbox
        const enableVoiceCheckbox = document.getElementById('enableVoice');
        if (enableVoiceCheckbox) {
            enableVoiceCheckbox.addEventListener('change', (e) => {
                voiceManager.setEnabled(e.target.checked);
                this.savePreferences();
            });
        }

        // Voice speed slider
        const voiceSpeedSlider = document.getElementById('voiceSpeed');
        const speedValue = document.getElementById('speedValue');
        if (voiceSpeedSlider && speedValue) {
            voiceSpeedSlider.addEventListener('input', (e) => {
                const speed = parseFloat(e.target.value);
                voiceManager.setSpeed(speed);
                speedValue.textContent = `${speed.toFixed(1)}x`;
                this.savePreferences();
            });
        }

        // Voice control buttons
        const pauseBtn = document.getElementById('pauseVoice');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                voiceManager.pause();
                this.updateVoiceButtons();
            });
        }

        const resumeBtn = document.getElementById('resumeVoice');
        if (resumeBtn) {
            resumeBtn.addEventListener('click', () => {
                voiceManager.resume();
                this.updateVoiceButtons();
            });
        }

        const skipBtn = document.getElementById('skipVoice');
        if (skipBtn) {
            skipBtn.addEventListener('click', () => {
                voiceManager.skip();
            });
        }
    }

    /**
     * Setup modal event handlers
     */
    setupModalHandlers() {
        const modal = document.getElementById('synthesisModal');
        const closeBtn = document.getElementById('closeSynthesis');
        const closeModalBtn = document.getElementById('closeModalBtn');
        const overlay = document.getElementById('modalOverlay');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => debateManager.hideModal());
        }

        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => debateManager.hideModal());
        }

        if (overlay) {
            overlay.addEventListener('click', () => debateManager.hideModal());
        }

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
                debateManager.hideModal();
            }
        });
    }

    /**
     * Handle start debate button click
     */
    async handleStartDebate() {
        const topicInput = document.getElementById('topicInput');
        const roundsInput = document.getElementById('roundsInput');

        // Validate inputs
        const topic = topicInput.value.trim();
        if (!topic) {
            Utils.showToast('Please enter a debate topic', 'error');
            topicInput.focus();
            return;
        }

        const rounds = parseInt(roundsInput.value);
        if (!rounds || rounds < 1 || rounds > 5) {
            Utils.showToast('Please select 1-5 rounds', 'error');
            roundsInput.focus();
            return;
        }

        // Get selected agents
        const agentCheckboxes = document.querySelectorAll('.agent-checkbox input[type="checkbox"]:checked');
        const agents = Array.from(agentCheckboxes).map(cb => cb.value);

        if (agents.length < 2) {
            Utils.showToast('Please select at least 2 agents', 'error');
            return;
        }

        try {
            // Update button states
            this.setDebateControlsState(true);

            // Start debate
            await debateManager.startDebate(topic, rounds, agents);

            Utils.showToast(`Debate started: ${topic}`, 'success');

            // Update status
            this.updateStatus('running', 'Debate Running');

            // Start mock data if enabled
            if (this.useMockData) {
                this.startMockDebate(topic, rounds, agents);
            } else {
                // Connect to WebSocket
                await debateWS.connect(debateManager.debateId);
            }
        } catch (error) {
            console.error('Failed to start debate:', error);

            // Reset UI state
            debateManager.isActive = false;
            debateManager.clearMessages();
            this.setDebateControlsState(false);
            this.updateStatus('ready', 'Ready');

            // Show error in dialog if message is long, otherwise use toast
            const errorMessage = error.message || 'Failed to start debate';
            if (errorMessage.length > 100) {
                Utils.showErrorDialog('Failed to Start Debate', errorMessage);
            } else {
                Utils.showToast(errorMessage, 'error', 5000);
            }
        }
    }

    /**
     * Handle stop debate button click
     */
    async handleStopDebate() {
        try {
            await debateManager.stopDebate();
            this.setDebateControlsState(false);
            this.updateStatus('ready', 'Ready');
            this.stopMockDebate();
        } catch (error) {
            console.error('Failed to stop debate:', error);
            Utils.showToast('Failed to stop debate', 'error');
        }
    }

    /**
     * Handle clear debate button click
     */
    handleClearDebate() {
        if (debateManager.isActive) {
            Utils.showToast('Please stop the debate first', 'error');
            return;
        }

        debateManager.clearDebate();
        Utils.showToast('Debate cleared', 'info');
    }

    /**
     * Set debate control button states
     * @param {boolean} debateActive - Whether debate is active
     */
    setDebateControlsState(debateActive) {
        const startBtn = document.getElementById('startDebate');
        const stopBtn = document.getElementById('stopDebate');
        const topicInput = document.getElementById('topicInput');
        const roundsInput = document.getElementById('roundsInput');

        if (startBtn) {
            startBtn.disabled = debateActive;
            // Keep primary class but it will be faded when disabled
        }

        if (stopBtn) {
            stopBtn.disabled = !debateActive;
            // Change to danger (red) when active, secondary when inactive
            if (debateActive) {
                stopBtn.classList.remove('btn-secondary');
                stopBtn.classList.add('btn-danger');
            } else {
                stopBtn.classList.remove('btn-danger');
                stopBtn.classList.add('btn-secondary');
            }
        }

        if (topicInput) topicInput.disabled = debateActive;
        if (roundsInput) roundsInput.disabled = debateActive;

        // Disable agent checkboxes during debate
        const agentCheckboxes = document.querySelectorAll('.agent-checkbox input[type="checkbox"]:not([disabled])');
        agentCheckboxes.forEach(cb => {
            cb.disabled = debateActive;
        });
    }

    /**
     * Update status indicator
     * @param {string} status - Status type (ready, running, error)
     * @param {string} text - Status text
     */
    updateStatus(status, text) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');

        if (statusDot) {
            statusDot.className = `status-dot status-${status}`;
        }

        if (statusText) {
            statusText.textContent = text;
        }
    }

    /**
     * Update voice control button states
     */
    updateVoiceButtons() {
        const pauseBtn = document.getElementById('pauseVoice');
        const resumeBtn = document.getElementById('resumeVoice');
        const skipBtn = document.getElementById('skipVoice');

        const isSpeaking = voiceManager.getSpeakingStatus();
        const isPaused = voiceManager.isPaused;

        if (pauseBtn) pauseBtn.disabled = !isSpeaking || isPaused;
        if (resumeBtn) resumeBtn.disabled = !isSpeaking || !isPaused;
        if (skipBtn) skipBtn.disabled = !isSpeaking;
    }

    /**
     * Save user preferences to localStorage
     */
    savePreferences() {
        const prefs = {
            voiceEnabled: document.getElementById('enableVoice')?.checked || true,
            voiceSpeed: parseFloat(document.getElementById('voiceSpeed')?.value || 1.0)
        };

        localStorage.setItem('debatePreferences', JSON.stringify(prefs));
    }

    /**
     * Load user preferences from localStorage
     */
    loadPreferences() {
        try {
            const saved = localStorage.getItem('debatePreferences');
            if (saved) {
                const prefs = JSON.parse(saved);

                const enableVoice = document.getElementById('enableVoice');
                if (enableVoice && prefs.voiceEnabled !== undefined) {
                    enableVoice.checked = prefs.voiceEnabled;
                    voiceManager.setEnabled(prefs.voiceEnabled);
                }

                const voiceSpeed = document.getElementById('voiceSpeed');
                const speedValue = document.getElementById('speedValue');
                if (voiceSpeed && prefs.voiceSpeed) {
                    voiceSpeed.value = prefs.voiceSpeed;
                    speedValue.textContent = `${prefs.voiceSpeed.toFixed(1)}x`;
                    voiceManager.setSpeed(prefs.voiceSpeed);
                }
            }
        } catch (error) {
            console.error('Failed to load preferences:', error);
        }
    }

    /**
     * Start mock debate data (for testing without backend)
     * @param {string} topic - Debate topic
     * @param {number} rounds - Number of rounds
     * @param {Array} agents - Active agents
     */
    startMockDebate(topic, rounds, agents) {
        const mockMessages = this.generateMockMessages(topic, agents);
        let messageIndex = 0;

        // Send messages at intervals
        this.mockInterval = setInterval(() => {
            if (messageIndex < mockMessages.length && debateManager.isActive) {
                debateManager.addMessage(mockMessages[messageIndex]);
                messageIndex++;

                // Update round
                const round = Math.floor(messageIndex / agents.length) + 1;
                debateManager.currentRound = Math.min(round, rounds);
                debateManager.updateRoundDisplay(debateManager.currentRound, rounds);
            } else {
                // Debate complete - show synthesis
                this.stopMockDebate();
                if (debateManager.isActive) {
                    this.showMockSynthesis(topic);
                }
            }
        }, 3000); // Message every 3 seconds
    }

    /**
     * Stop mock debate
     */
    stopMockDebate() {
        if (this.mockInterval) {
            clearInterval(this.mockInterval);
            this.mockInterval = null;
        }
    }

    /**
     * Generate mock debate messages
     * @param {string} topic - Debate topic
     * @param {Array} agents - Active agents
     * @returns {Array} Mock messages
     */
    generateMockMessages(topic, agents) {
        const messages = [];
        const messageTemplates = {
            moderator: `Welcome to today's debate on: "${topic}". Let's ensure a respectful and fact-based discussion.`,
            conservative: `From a conservative perspective, we must consider traditional values and proven solutions when addressing ${topic}.`,
            progressive: `Progressive values demand that we examine ${topic} through the lens of social justice and equality for all.`,
            factchecker: `I've verified the recent claims about ${topic}. Based on authoritative sources, the evidence shows...`,
            devilsadvocate: `Let me challenge both sides here - what if we're approaching ${topic} from entirely the wrong angle?`,
            synthesizer: `After analyzing all arguments, I can identify several key points of agreement and important nuances in this ${topic} debate.`
        };

        // Opening statements
        agents.forEach(agent => {
            if (messageTemplates[agent]) {
                messages.push({
                    id: Utils.generateId(),
                    type: 'OPENING',
                    from_agent: agent,
                    content: messageTemplates[agent],
                    timestamp: new Date()
                });
            }
        });

        // Arguments
        if (agents.includes('conservative')) {
            messages.push({
                id: Utils.generateId(),
                type: 'ARGUMENT',
                from_agent: 'conservative',
                content: `Individual liberty and free-market solutions have historically proven effective. We should apply these principles to ${topic}.`,
                timestamp: new Date()
            });
        }

        if (agents.includes('progressive')) {
            messages.push({
                id: Utils.generateId(),
                type: 'ARGUMENT',
                from_agent: 'progressive',
                content: `Studies show that collective action and systemic reforms are necessary. The evidence for ${topic} clearly demonstrates this.`,
                timestamp: new Date()
            });
        }

        // Fact check
        if (agents.includes('factchecker')) {
            messages.push({
                id: Utils.generateId(),
                type: 'FACT_CHECK',
                from_agent: 'factchecker',
                content: 'Recent statistical claims have been verified against peer-reviewed sources.',
                claim: 'Statistical claim about the topic',
                verdict: 'TRUE',
                timestamp: new Date()
            });
        }

        // Challenge
        if (agents.includes('devilsadvocate')) {
            messages.push({
                id: Utils.generateId(),
                type: 'CHALLENGE',
                from_agent: 'devilsadvocate',
                content: 'Both arguments assume certain premises. What if those foundational assumptions are incorrect?',
                timestamp: new Date()
            });
        }

        return messages;
    }

    /**
     * Show mock synthesis results
     * @param {string} topic - Debate topic
     */
    showMockSynthesis(topic) {
        const synthesis = {
            commonGround: `Despite different approaches, both perspectives agree that ${topic} requires thoughtful consideration and evidence-based solutions. Key areas of agreement include the importance of individual rights balanced with collective welfare.`,
            keyArguments: [
                'Individual liberty and personal responsibility (Conservative perspective)',
                'Systemic reform and collective action (Progressive perspective)',
                'Evidence-based policy informed by research (Fact Checker contribution)',
                'Critical examination of underlying assumptions (Devil\'s Advocate insight)'
            ],
            insights: `This debate reveals that **${topic}** is not a simple binary choice but a complex issue requiring nuanced understanding. The strongest path forward likely involves elements from multiple perspectives, adapted to specific contexts and informed by rigorous evidence.`
        };

        debateManager.showSynthesis(synthesis);

        // Stop debate
        setTimeout(() => {
            this.handleStopDebate();
        }, 1000);
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Debate Arena - Initializing...');

    // Create app instance
    window.debateApp = new DebateApp();

    // Show welcome message
    Utils.showToast('Welcome to AI Debate Arena', 'info', 5000);

    console.log('AI Debate Arena - Ready!');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (voiceManager) {
        if (document.hidden) {
            // Pause voice when tab is hidden
            voiceManager.pause();
        } else {
            // Resume voice when tab becomes visible again
            voiceManager.resume();
        }
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (voiceManager) {
        voiceManager.stop();
    }
    if (debateWS) {
        debateWS.close();
    }
});
