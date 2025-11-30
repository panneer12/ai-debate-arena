/**
 * AI Debate Arena - Utility Functions
 */

// Utility object
const Utils = {
    /**
     * Format timestamp to readable string
     * @param {Date} date - Date object
     * @returns {string} Formatted time string
     */
    formatTime(date) {
        if (!(date instanceof Date)) {
            date = new Date(date);
        }
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = date.getSeconds().toString().padStart(2, '0');
        return `${hours}:${minutes}:${seconds}`;
    },

    /**
     * Generate unique ID
     * @returns {string} Unique identifier
     */
    generateId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    },

    /**
     * Debounce function execution
     * @param {Function} func - Function to debounce
     * @param {number} wait - Milliseconds to wait
     * @returns {Function} Debounced function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function execution
     * @param {Function} func - Function to throttle
     * @param {number} limit - Milliseconds between calls
     * @returns {Function} Throttled function
     */
    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Sanitize HTML to prevent XSS
     * @param {string} html - HTML string to sanitize
     * @returns {string} Sanitized HTML
     */
    sanitizeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    },

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHTML(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    },

    /**
     * Create toast notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, info)
     * @param {number} duration - Display duration in ms
     */
    showToast(message, type = 'info', duration = 3000) {
        // Create toast container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = {
            success: '✅',
            error: '❌',
            info: 'ℹ️'
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${this.escapeHTML(message)}</span>
            <button class="toast-close">&times;</button>
        `;

        // Add to container
        container.appendChild(toast);

        // Close button handler
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.removeToast(toast);
        });

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.removeToast(toast);
            }, duration);
        }
    },

    /**
     * Remove toast notification
     * @param {HTMLElement} toast - Toast element to remove
     */
    removeToast(toast) {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300);
    },

    /**
     * Show error dialog for long error messages
     * @param {string} title - Dialog title
     * @param {string} message - Error message
     */
    showErrorDialog(title, message) {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.style.display = 'flex';

        // Create dialog
        const dialog = document.createElement('div');
        dialog.className = 'error-dialog';
        dialog.innerHTML = `
            <div class="error-dialog-header">
                <h3>❌ ${this.escapeHtml(title)}</h3>
                <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            <div class="error-dialog-content">
                <p>${this.escapeHtml(message)}</p>
            </div>
            <div class="error-dialog-footer">
                <button class="btn-primary" onclick="this.closest('.modal-overlay').remove()">OK</button>
            </div>
        `;

        overlay.appendChild(dialog);
        document.body.appendChild(overlay);

        // Close on overlay click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
            }
        });

        // Close on Escape key
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                overlay.remove();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    },

    /**
     * Copy text to clipboard
     * @param {string} text - Text to copy
     * @returns {Promise<boolean>} Success status
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copied to clipboard', 'success');
            return true;
        } catch (err) {
            console.error('Failed to copy:', err);
            this.showToast('Failed to copy', 'error');
            return false;
        }
    },

    /**
     * Download text as file
     * @param {string} content - File content
     * @param {string} filename - File name
     * @param {string} mimeType - MIME type
     */
    downloadFile(content, filename, mimeType = 'text/plain') {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    },

    /**
     * Get agent display name
     * @param {string} agentId - Agent identifier
     * @returns {string} Display name
     */
    getAgentDisplayName(agentId) {
        if (!agentId) {
            return 'Unknown Agent';
        }
        const names = {
            moderator: '🎯 Moderator',
            conservative: '🔴 Conservative',
            progressive: '🔵 Progressive',
            factchecker: '✅ Fact Checker',
            devilsadvocate: '😈 Devil\'s Advocate',
            synthesizer: '🧠 Synthesizer',
            libertarian: '🟡 Libertarian',
            international: '🌍 International'
        };
        return names[agentId.toLowerCase()] || agentId;
    },

    /**
     * Get agent color class
     * @param {string} agentId - Agent identifier
     * @returns {string} CSS class name
     */
    getAgentColorClass(agentId) {
        if (!agentId) {
            return 'message-default';
        }
        const classes = {
            moderator: 'message-moderator',
            conservative: 'message-conservative',
            progressive: 'message-progressive',
            factchecker: 'message-factchecker',
            devilsadvocate: 'message-devilsadvocate',
            synthesizer: 'message-synthesizer'
        };
        return classes[agentId.toLowerCase()] || 'message-default';
    },

    /**
     * Get message type display info
     * @param {string} messageType - Message type
     * @returns {object} Display info
     */
    getMessageTypeInfo(messageType) {
        const types = {
            ARGUMENT: { label: 'Argument', class: 'type-argument' },
            FACT_CHECK: { label: 'Fact Check', class: 'type-fact-check' },
            CHALLENGE: { label: 'Challenge', class: 'type-challenge' },
            SYNTHESIS: { label: 'Synthesis', class: 'type-synthesis' },
            ERROR: { label: 'Error', class: 'type-error' },
            OPENING: { label: 'Opening', class: 'type-argument' },
            REBUTTAL: { label: 'Rebuttal', class: 'type-argument' },
            QUESTION: { label: 'Question', class: 'type-challenge' },
            ANSWER: { label: 'Answer', class: 'type-argument' }
        };
        return types[messageType] || { label: messageType, class: '' };
    },

    /**
     * Parse markdown-like formatting to HTML
     * @param {string} text - Text with markdown
     * @param {boolean} wrapWords - If true, wrap words in spans for highlighting
     * @returns {string} HTML string
     */
    parseMarkdown(text, wrapWords = false) {
        // Simple markdown parsing for bold and italic
        text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Convert line breaks to paragraphs
        const paragraphs = text.split('\n\n');
        let html = paragraphs.map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('');

        // If word wrapping is enabled, wrap each word in a span
        if (wrapWords) {
            html = this.wrapWordsInHTML(html);
        }

        return html;
    },

    /**
     * Wrap words in HTML with span elements for highlighting
     * @param {string} html - HTML string
     * @returns {string} HTML with words wrapped in spans
     */
    wrapWordsInHTML(html) {
        let charIndex = 0;

        // Process HTML while preserving tags
        return html.replace(/>([^<]+)</g, (match, textContent) => {
            // Split text into words and non-words (spaces, punctuation)
            const parts = textContent.split(/(\s+)/);
            const wrapped = parts.map(part => {
                if (part.trim().length === 0) {
                    // Whitespace - don't wrap
                    charIndex += part.length;
                    return part;
                }

                // Word - wrap in span with char position
                const start = charIndex;
                const end = start + part.length;
                charIndex = end;

                return `<span class="word" data-char-start="${start}" data-char-end="${end}">${part}</span>`;
            });

            return `>${wrapped.join('')}<`;
        });
    },

    /**
     * Truncate text to specified length
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated text
     */
    truncate(text, maxLength = 100) {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength - 3) + '...';
    },

    /**
     * Check if element is in viewport
     * @param {HTMLElement} element - Element to check
     * @returns {boolean} True if in viewport
     */
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },

    /**
     * Scroll element into view smoothly
     * @param {HTMLElement} element - Element to scroll to
     * @param {string} position - Scroll position (start, center, end)
     */
    scrollToElement(element, position = 'end') {
        element.scrollIntoView({
            behavior: 'smooth',
            block: position,
            inline: 'nearest'
        });
    },

    /**
     * Add CSS class with animation
     * @param {HTMLElement} element - Target element
     * @param {string} className - CSS class to add
     */
    addClassAnimated(element, className) {
        element.classList.add(className);
    },

    /**
     * Remove CSS class with animation
     * @param {HTMLElement} element - Target element
     * @param {string} className - CSS class to remove
     */
    removeClassAnimated(element, className) {
        element.classList.remove(className);
    },

    /**
     * Wait for specified milliseconds
     * @param {number} ms - Milliseconds to wait
     * @returns {Promise} Promise that resolves after delay
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    /**
     * Format number with commas
     * @param {number} num - Number to format
     * @returns {string} Formatted number
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    /**
     * Get random item from array
     * @param {Array} array - Source array
     * @returns {*} Random item
     */
    randomItem(array) {
        return array[Math.floor(Math.random() * array.length)];
    },

    /**
     * Shuffle array
     * @param {Array} array - Array to shuffle
     * @returns {Array} Shuffled array
     */
    shuffle(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    },

    /**
     * Check if string is valid JSON
     * @param {string} str - String to check
     * @returns {boolean} True if valid JSON
     */
    isValidJSON(str) {
        try {
            JSON.parse(str);
            return true;
        } catch (e) {
            return false;
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
}
