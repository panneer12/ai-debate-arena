/**
 * AI Debate Arena - WebSocket Manager
 * Handles real-time communication with backend
 */

class DebateWebSocket {
    constructor(baseUrl = null) {
        // Auto-detect WebSocket URL from current page
        if (!baseUrl) {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            this.baseUrl = `${protocol}//${host}`;
        } else {
            this.baseUrl = baseUrl;
        }
        this.ws = null;
        this.debateId = null;
        this.handlers = {
            connected: [],
            disconnected: [],
            error: [],
            message: [],
            argument: [],
            factCheck: [],
            challenge: [],
            synthesis: [],
            status: []
        };
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        this.isConnected = false;
        this.shouldReconnect = true;
    }

    /**
     * Connect to WebSocket server
     * @param {string} debateId - Debate session ID
     * @returns {Promise} Connection promise
     */
    connect(debateId) {
        return new Promise((resolve, reject) => {
            this.debateId = debateId;
            const wsUrl = `${this.baseUrl}/ws/debate/${debateId}`;

            console.log(`Connecting to WebSocket: ${wsUrl}`);

            try {
                this.ws = new WebSocket(wsUrl);

                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.trigger('connected', { debateId });
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    this.handleMessage(event);
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.trigger('error', error);
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.isConnected = false;
                    this.trigger('disconnected');

                    // Attempt to reconnect if not manually closed
                    if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.attemptReconnect();
                    }
                };
            } catch (error) {
                console.error('Failed to create WebSocket:', error);
                reject(error);
            }
        });
    }

    /**
     * Attempt to reconnect to WebSocket
     */
    attemptReconnect() {
        this.reconnectAttempts++;
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

        setTimeout(() => {
            if (this.debateId) {
                this.connect(this.debateId).catch(err => {
                    console.error('Reconnection failed:', err);
                });
            }
        }, this.reconnectDelay * this.reconnectAttempts);
    }

    /**
     * Handle incoming WebSocket message
     * @param {MessageEvent} event - WebSocket message event
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);

            // Trigger generic message handler
            this.trigger('message', data);

            // Trigger specific handlers based on message type
            if (data.type) {
                const eventType = data.type.toLowerCase();
                this.trigger(eventType, data);

                // Map specific message types to categories
                if (data.type === 'ARGUMENT' || data.type === 'REBUTTAL' || data.type === 'OPENING') {
                    this.trigger('argument', data);
                } else if (data.type === 'FACT_CHECK') {
                    this.trigger('factCheck', data);
                } else if (data.type === 'CHALLENGE' || data.type === 'QUESTION') {
                    this.trigger('challenge', data);
                } else if (data.type === 'SYNTHESIS') {
                    this.trigger('synthesis', data);
                }
            }

            // Handle status updates
            if (data.status) {
                this.trigger('status', data);
            }
        } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
        }
    }

    /**
     * Send message through WebSocket
     * @param {Object} data - Data to send
     * @returns {boolean} Success status
     */
    send(data) {
        if (!this.isConnected || !this.ws) {
            console.error('WebSocket not connected');
            return false;
        }

        try {
            this.ws.send(JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Failed to send WebSocket message:', error);
            return false;
        }
    }

    /**
     * Register event handler
     * @param {string} event - Event name
     * @param {Function} handler - Event handler function
     */
    on(event, handler) {
        if (!this.handlers[event]) {
            this.handlers[event] = [];
        }
        this.handlers[event].push(handler);
    }

    /**
     * Unregister event handler
     * @param {string} event - Event name
     * @param {Function} handler - Event handler function
     */
    off(event, handler) {
        if (!this.handlers[event]) return;

        const index = this.handlers[event].indexOf(handler);
        if (index > -1) {
            this.handlers[event].splice(index, 1);
        }
    }

    /**
     * Trigger event handlers
     * @param {string} event - Event name
     * @param {*} data - Event data
     */
    trigger(event, data) {
        const handlers = this.handlers[event] || [];
        handlers.forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error(`Error in ${event} handler:`, error);
            }
        });
    }

    /**
     * Close WebSocket connection
     */
    close() {
        this.shouldReconnect = false;
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        this.debateId = null;
    }

    /**
     * Get connection status
     * @returns {boolean} Connection status
     */
    getConnectionStatus() {
        return this.isConnected;
    }
}

/**
 * HTTP API Client for REST endpoints
 */
class DebateAPIClient {
    constructor(baseUrl = null) {
        // Auto-detect API URL from current page
        if (!baseUrl) {
            const protocol = window.location.protocol;
            const host = window.location.host;
            this.baseUrl = `${protocol}//${host}`;
        } else {
            this.baseUrl = baseUrl;
        }
    }

    /**
     * Start a new debate
     * @param {string} topic - Debate topic
     * @param {number} rounds - Number of rounds
     * @param {Array} agents - List of active agents
     * @returns {Promise} API response
     */
    async startDebate(topic, rounds, agents) {
        try {
            const response = await fetch(`${this.baseUrl}/api/debate/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic, rounds, agents })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.detail || `HTTP error! status: ${response.status}`;
                throw new Error(errorMessage);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to start debate:', error);
            throw error;
        }
    }

    /**
     * Stop ongoing debate
     * @param {string} debateId - Debate session ID
     * @returns {Promise} API response
     */
    async stopDebate(debateId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/debate/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ debate_id: debateId })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to stop debate:', error);
            throw error;
        }
    }

    /**
     * Get debate status
     * @param {string} debateId - Debate session ID
     * @returns {Promise} API response
     */
    async getDebateStatus(debateId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/debate/${debateId}/status`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get debate status:', error);
            throw error;
        }
    }

    /**
     * Get debate history
     * @param {string} debateId - Debate session ID
     * @returns {Promise} API response
     */
    async getDebateHistory(debateId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/debate/${debateId}/history`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get debate history:', error);
            throw error;
        }
    }

    /**
     * Export debate transcript
     * @param {string} debateId - Debate session ID
     * @param {string} format - Export format (json, txt, pdf)
     * @returns {Promise} API response
     */
    async exportDebate(debateId, format = 'txt') {
        try {
            const response = await fetch(`${this.baseUrl}/api/debate/${debateId}/export?format=${format}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.blob();
        } catch (error) {
            console.error('Failed to export debate:', error);
            throw error;
        }
    }

    /**
     * Health check
     * @returns {Promise} API response
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return response.ok;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }
}

// Create global instances
const debateWS = new DebateWebSocket();
const debateAPI = new DebateAPIClient();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DebateWebSocket, DebateAPIClient };
}
