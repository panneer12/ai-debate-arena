/**
 * AI Debate Arena - Debate Manager
 * Manages debate state and UI updates
 */

class DebateManager {
    constructor() {
        this.debateId = null;
        this.isActive = false;
        this.topic = '';
        this.rounds = 0;
        this.currentRound = 0;
        this.messages = [];
        this.stats = {
            messages: 0,
            factChecks: 0,
            challenges: 0,
            arguments: 0
        };
        this.synthesis = null;

        // DOM element references
        this.messageContainer = null;
        this.initializeElements();
    }

    /**
     * Initialize DOM element references
     */
    initializeElements() {
        this.messageContainer = document.getElementById('messageContainer');
        this.statMessages = document.getElementById('statMessages');
        this.statFactChecks = document.getElementById('statFactChecks');
        this.statChallenges = document.getElementById('statChallenges');
        this.statArguments = document.getElementById('statArguments');
        this.factCheckList = document.getElementById('factCheckList');
        this.challengeList = document.getElementById('challengeList');
        this.fallacyList = document.getElementById('fallacyList');
        this.currentRoundDisplay = document.getElementById('currentRound');
        this.totalRoundsDisplay = document.getElementById('totalRounds');
    }

    /**
     * Start a new debate
     * @param {string} topic - Debate topic
     * @param {number} rounds - Number of rounds
     * @param {Array} agents - Active agents
     */
    async startDebate(topic, rounds, agents) {
        try {
            // Clear previous state
            this.clearDebate();

            // Set debate parameters
            this.topic = topic;
            this.rounds = rounds;
            this.isActive = true;

            // Update UI
            this.updateRoundDisplay(0, rounds);
            this.clearMessages();

            // Show loading state
            this.showLoadingMessage();

            // Call backend API
            console.log('Starting debate:', { topic, rounds, agents });
            const response = await debateAPI.startDebate(topic, rounds, agents);

            if (response && response.status === 'started') {
                // The backend doesn't return the ID in the start response immediately?
                // Wait, server.py says: return {"status": "started", "topic": request.topic}
                // It runs in background.
                // We need the debate ID to connect via WebSocket.
                // But server.py start_debate doesn't return debate_id!

                // Let's check server.py again.
                // It creates a task. debate_manager.debate_id is set inside start_debate.
                // But we need it HERE to connect.

                // I need to update server.py to return the debate_id.
                // But for now, let's assume I'll fix server.py.

                this.debateId = response.debate_id;
                this.currentRound = 1;
                this.updateRoundDisplay(1, rounds);
                return this.debateId;
            } else {
                throw new Error('Failed to start debate');
            }
        } catch (error) {
            console.error('Failed to start debate:', error);
            Utils.showToast(error.message || 'Failed to start debate', 'error');
            throw error;
        }
    }

    /**
     * Stop ongoing debate
     */
    async stopDebate() {
        if (!this.isActive || !this.debateId) {
            return;
        }

        try {
            console.log('Stopping debate:', this.debateId);

            // Stop voice
            if (typeof voiceManager !== 'undefined') {
                voiceManager.stop();
            }

            // Mark as inactive
            this.isActive = false;

            // Update UI
            Utils.showToast('Debate stopped', 'info');
        } catch (error) {
            console.error('Failed to stop debate:', error);
            Utils.showToast('Failed to stop debate', 'error');
        }
    }

    /**
     * Clear debate state
     */
    clearDebate() {
        this.debateId = null;
        this.isActive = false;
        this.topic = '';
        this.rounds = 0;
        this.currentRound = 0;
        this.messages = [];
        this.stats = {
            messages: 0,
            factChecks: 0,
            challenges: 0,
            arguments: 0
        };
        this.synthesis = null;

        // Clear UI
        this.clearMessages();
        this.clearInsights();
        this.updateStats();
        this.updateRoundDisplay(0, 0);
    }

    /**
     * Add message to debate
     * @param {Object} message - Message object
     */
    addMessage(message) {
        this.messages.push(message);
        this.stats.messages++;

        // Update stats based on message type
        if (message.type === 'FACT_CHECK') {
            this.stats.factChecks++;
            this.addFactCheck(message);
        } else if (message.type === 'CHALLENGE' || message.type === 'QUESTION') {
            this.stats.challenges++;
            this.addChallenge(message);
        } else if (message.type === 'ARGUMENT' || message.type === 'REBUTTAL') {
            this.stats.arguments++;
        }

        // Render message in UI
        this.renderMessage(message);

        // Update stats display
        this.updateStats();

        // Speak message if voice enabled
        if (typeof voiceManager !== 'undefined' && voiceManager.enabled) {
            voiceManager.speak(message.content, message.from_agent, null, message.id);
        }
    }

    /**
     * Render message in UI
     * @param {Object} message - Message object
     */
    renderMessage(message) {
        // Remove placeholder if exists
        const placeholder = this.messageContainer.querySelector('.message-placeholder');
        if (placeholder) {
            placeholder.remove();
        }

        // Create message card
        const messageCard = this.createMessageCard(message);

        // Add to container
        this.messageContainer.appendChild(messageCard);

        // Scroll to bottom
        Utils.scrollToElement(messageCard, 'end');
    }

    /**
     * Create message card element
     * @param {Object} message - Message object
     * @returns {HTMLElement} Message card element
     */
    createMessageCard(message) {
        const card = document.createElement('div');
        card.className = `message-card ${Utils.getAgentColorClass(message.from_agent)}`;
        card.setAttribute('data-message-id', message.id || Utils.generateId());

        // Store original content for word highlighting
        card.setAttribute('data-content', message.content);

        const typeInfo = Utils.getMessageTypeInfo(message.type);
        const timestamp = Utils.formatTime(message.timestamp || new Date());

        card.innerHTML = `
            <div class="message-header">
                <div class="message-header-left">
                    <div class="agent-avatar">${this.getAgentEmoji(message.from_agent)}</div>
                    <span class="agent-name-display">${Utils.getAgentDisplayName(message.from_agent)}</span>
                    <span class="message-type-badge ${typeInfo.class}">${typeInfo.label}</span>
                    <span class="timestamp">${timestamp}</span>
                </div>
                <div class="message-header-right message-actions">
                    <button onclick="debateManager.speakMessage('${message.id || ''}')" title="Speak">🔊</button>
                    <button onclick="debateManager.copyMessage('${message.id || ''}')" title="Copy">📋</button>
                </div>
            </div>
            <div class="message-content">
                ${Utils.parseMarkdown(message.content, true)}
            </div>
        `;

        return card;
    }

    /**
     * Get emoji for agent
     * @param {string} agent - Agent identifier
     * @returns {string} Emoji
     */
    getAgentEmoji(agent) {
        const emojis = {
            moderator: '🎯',
            conservative: '🔴',
            progressive: '🔵',
            factchecker: '✅',
            devilsadvocate: '😈',
            synthesizer: '🧠',
            libertarian: '🟡',
            international: '🌍'
        };
        return emojis[agent.toLowerCase()] || '🤖';
    }

    /**
     * Add fact check to insights panel
     * @param {Object} factCheck - Fact check object
     */
    addFactCheck(factCheck) {
        // Remove empty state
        const emptyState = this.factCheckList.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }

        const item = document.createElement('div');
        item.className = `fact-check-item verdict-${factCheck.verdict?.toLowerCase() || 'unknown'}`;

        const verdictIcon = this.getVerdictIcon(factCheck.verdict);
        const verdictClass = `verdict-${factCheck.verdict?.toLowerCase() || 'unknown'}`;

        item.innerHTML = `
            <div class="fact-check-claim">"${Utils.truncate(factCheck.claim || factCheck.content, 80)}"</div>
            <div class="fact-check-verdict ${verdictClass}">
                <span class="verdict-icon">${verdictIcon}</span>
                <span>${factCheck.verdict || 'CHECKING'}</span>
            </div>
        `;

        this.factCheckList.appendChild(item);
    }

    /**
     * Get verdict icon
     * @param {string} verdict - Verdict string
     * @returns {string} Icon emoji
     */
    getVerdictIcon(verdict) {
        const icons = {
            TRUE: '✅',
            FALSE: '❌',
            'MOSTLY_TRUE': '⚠️',
            'MOSTLY_FALSE': '⚠️',
            UNVERIFIED: '❓'
        };
        return icons[verdict] || '❓';
    }

    /**
     * Add challenge to insights panel
     * @param {Object} challenge - Challenge object
     */
    addChallenge(challenge) {
        // Remove empty state
        const emptyState = this.challengeList.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }

        const item = document.createElement('div');
        item.className = 'challenge-item';

        item.innerHTML = `
            <div class="challenge-text">${Utils.truncate(challenge.content, 100)}</div>
        `;

        this.challengeList.appendChild(item);
    }

    /**
     * Update stats display
     */
    updateStats() {
        if (this.statMessages) this.statMessages.textContent = this.stats.messages;
        if (this.statFactChecks) this.statFactChecks.textContent = this.stats.factChecks;
        if (this.statChallenges) this.statChallenges.textContent = this.stats.challenges;
        if (this.statArguments) this.statArguments.textContent = this.stats.arguments;
    }

    /**
     * Update round display
     * @param {number} current - Current round
     * @param {number} total - Total rounds
     */
    updateRoundDisplay(current, total) {
        if (this.currentRoundDisplay) this.currentRoundDisplay.textContent = current;
        if (this.totalRoundsDisplay) this.totalRoundsDisplay.textContent = total;
    }

    /**
     * Clear all messages
     */
    clearMessages() {
        if (this.messageContainer) {
            this.messageContainer.innerHTML = `
                <div class="message-placeholder">
                    <div class="placeholder-icon">🎙️</div>
                    <h3>No Active Debate</h3>
                    <p>Configure your debate settings and click "Start Debate" to begin</p>
                    <p class="placeholder-hint">Try one of the quick topics or enter your own controversial question</p>
                </div>
            `;
        }
    }

    /**
     * Clear insights panels
     */
    clearInsights() {
        if (this.factCheckList) {
            this.factCheckList.innerHTML = '<p class="empty-state">No fact checks yet</p>';
        }
        if (this.challengeList) {
            this.challengeList.innerHTML = '<p class="empty-state">No challenges yet</p>';
        }
        if (this.fallacyList) {
            this.fallacyList.innerHTML = '<p class="empty-state">No fallacies detected</p>';
        }
    }

    /**
     * Show loading message
     */
    showLoadingMessage() {
        this.messageContainer.innerHTML = `
            <div class="message-placeholder">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <h3>Starting Debate...</h3>
                <p>Initializing agents and preparing arguments</p>
            </div>
        `;
    }

    /**
     * Show synthesis results
     * @param {Object} synthesis - Synthesis data
     */
    showSynthesis(synthesis) {
        this.synthesis = synthesis;

        // Update modal content
        const commonGroundDisplay = document.getElementById('commonGroundDisplay');
        const keyArgumentsDisplay = document.getElementById('keyArgumentsDisplay');
        const insightsDisplay = document.getElementById('insightsDisplay');

        if (commonGroundDisplay) {
            commonGroundDisplay.innerHTML = Utils.parseMarkdown(synthesis.commonGround || 'No common ground identified.');
        }

        if (keyArgumentsDisplay) {
            const args = synthesis.keyArguments || [];
            keyArgumentsDisplay.innerHTML = args.length > 0
                ? `<ul>${args.map(arg => `<li>${arg}</li>`).join('')}</ul>`
                : '<p>No key arguments identified.</p>';
        }

        if (insightsDisplay) {
            insightsDisplay.innerHTML = Utils.parseMarkdown(synthesis.insights || 'No insights available.');
        }

        // Show modal
        this.showModal();
    }

    /**
     * Show synthesis modal
     */
    showModal() {
        const modal = document.getElementById('synthesisModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    /**
     * Hide synthesis modal
     */
    hideModal() {
        const modal = document.getElementById('synthesisModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    /**
     * Speak specific message
     * @param {string} messageId - Message ID
     */
    speakMessage(messageId) {
        const message = this.messages.find(m => m.id === messageId);
        if (message && typeof voiceManager !== 'undefined') {
            voiceManager.speak(message.content, message.from_agent);
        }
    }

    /**
     * Copy message content
     * @param {string} messageId - Message ID
     */
    copyMessage(messageId) {
        const message = this.messages.find(m => m.id === messageId);
        if (message) {
            Utils.copyToClipboard(message.content);
        }
    }

    /**
     * Export debate transcript
     */
    async exportTranscript() {
        const transcript = this.generateTranscript();
        const filename = `debate_${this.topic.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${Date.now()}.txt`;
        Utils.downloadFile(transcript, filename, 'text/plain');
        Utils.showToast('Transcript exported', 'success');
    }

    /**
     * Generate text transcript
     * @returns {string} Transcript text
     */
    generateTranscript() {
        let transcript = `AI DEBATE ARENA - TRANSCRIPT\n`;
        transcript += `================================\n\n`;
        transcript += `Topic: ${this.topic}\n`;
        transcript += `Rounds: ${this.rounds}\n`;
        transcript += `Date: ${new Date().toLocaleString()}\n\n`;
        transcript += `================================\n\n`;

        this.messages.forEach((msg, index) => {
            transcript += `[${index + 1}] ${Utils.getAgentDisplayName(msg.from_agent)}\n`;
            transcript += `Type: ${msg.type}\n`;
            transcript += `Time: ${Utils.formatTime(msg.timestamp || new Date())}\n\n`;
            transcript += `${msg.content}\n\n`;
            transcript += `--------------------------------\n\n`;
        });

        return transcript;
    }
}

// Create global debate manager instance
const debateManager = new DebateManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DebateManager;
}
