# AI Debate Arena - Web UI

Modern, voice-enabled web interface for the AI Debate Arena.

## Features

- 🎨 **Modern Dark Theme** - Professional GitHub-inspired design
- 🎙️ **Voice Playback** - Text-to-Speech for agent arguments using Web Speech API
- 📊 **Live Insights** - Real-time fact checks, challenges, and statistics
- 🔄 **Real-time Updates** - WebSocket support for live debate streaming
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 💾 **Export Functionality** - Download debate transcripts
- ⚙️ **Customizable** - Adjustable voice speed, agent selection

## Quick Start

### Running Locally

1. **Open in Browser**
   ```bash
   # Simply open index.html in your web browser
   # Or use a local server:

   # Python 3
   cd demo/ui
   python -m http.server 8080

   # Or Node.js
   npx http-server -p 8080
   ```

2. **Access the UI**
   ```
   http://localhost:8080
   ```

### Using Mock Data

The UI is configured to use mock data by default for testing without a backend:

1. Enter a debate topic (or click a quick topic chip)
2. Select number of rounds (1-5)
3. Choose active agents (at least 2)
4. Click "Start Debate"

Mock messages will appear every 3 seconds, demonstrating the full UI functionality.

### Connecting to Backend

When the backend is ready:

1. Edit `js/app.js` and set `useMockData = false`
2. Update the WebSocket URL in `js/websocket.js` if needed
3. Ensure the backend is running
4. Start a debate - it will connect to the real backend

## File Structure

```
demo/ui/
├── index.html              # Main HTML file
├── styles/
│   ├── main.css           # Core styles (layout, theme)
│   ├── components.css     # Component-specific styles
│   └── animations.css     # Animation keyframes
├── js/
│   ├── app.js            # Main application logic
│   ├── debate.js         # Debate state management
│   ├── voice.js          # Voice/TTS functionality
│   ├── websocket.js      # WebSocket & API client
│   └── utils.js          # Utility functions
└── assets/
    └── icons/            # Agent icons (optional)
```

## UI Components

### Control Panel (Left Sidebar)
- Topic input
- Round selection
- Agent selection (checkboxes)
- Voice settings
- Quick topic chips
- Control buttons (Start/Stop/Clear)

### Debate Feed (Center)
- Real-time message display
- Message cards with agent avatars
- Voice playback controls
- Round indicator

### Insights Panel (Right Sidebar)
- Debate statistics
- Fact check list
- Challenge list
- Fallacy detection list

### Synthesis Modal
- Common ground analysis
- Key arguments summary
- Main insights
- Export functionality

## Voice Features

The UI uses the **Web Speech API** for text-to-speech:

- Different voices for different agents
- Adjustable speed (0.5x - 2.0x)
- Play/Pause/Skip controls
- Visual indicators for speaking agent
- Automatic queue management

### Supported Browsers
- Chrome/Edge (Best support)
- Safari (Good support)
- Firefox (Limited voice selection)

## Customization

### Changing Colors

Edit `styles/main.css`:
```css
:root {
    --accent-blue: #58a6ff;      /* Primary accent */
    --accent-green: #3fb950;     /* Success/positive */
    --accent-yellow: #d29922;    /* Warning */
    --accent-red: #f85149;       /* Error/negative */
}
```

### Adding New Agent Types

1. Add agent to `js/utils.js`:
```javascript
getAgentDisplayName(agentId) {
    const names = {
        // ... existing agents
        newagent: '🎨 New Agent'
    };
}
```

2. Add color class to `styles/components.css`:
```css
.message-card.message-newagent::before {
    background: var(--accent-custom);
}
```

### Adjusting Animation Speed

Edit `styles/animations.css` to change animation durations.

## Testing

### Manual Testing Checklist

- [ ] UI loads without errors
- [ ] Topic input works
- [ ] Agent checkboxes can be toggled
- [ ] Start debate button triggers mock debate
- [ ] Messages appear in feed
- [ ] Voice playback works (if enabled)
- [ ] Voice controls (pause/resume/skip) work
- [ ] Stats update correctly
- [ ] Fact checks appear in sidebar
- [ ] Challenges appear in sidebar
- [ ] Synthesis modal appears at end
- [ ] Export transcript downloads file
- [ ] Clear button resets UI
- [ ] Responsive design on mobile

### Browser Console

Open browser DevTools (F12) to see:
- Initialization logs
- Message reception
- Voice synthesis status
- Any errors

## API Integration

### REST Endpoints (When backend ready)

```javascript
// Start debate
POST /api/debate/start
{
    "topic": "string",
    "rounds": number,
    "agents": ["agent1", "agent2", ...]
}

// Stop debate
POST /api/debate/stop
{
    "debate_id": "string"
}

// Get status
GET /api/debate/{debate_id}/status

// Get history
GET /api/debate/{debate_id}/history

// Export
GET /api/debate/{debate_id}/export?format=txt
```

### WebSocket Events

```javascript
// Connect
WS /ws/debate/{debate_id}

// Receive messages
{
    "type": "ARGUMENT" | "FACT_CHECK" | "CHALLENGE" | "SYNTHESIS",
    "from_agent": "agent_id",
    "content": "message content",
    "timestamp": "ISO-8601"
}
```

## Performance

- Lightweight vanilla JavaScript (no frameworks)
- CSS animations (GPU-accelerated)
- Efficient message rendering
- Scroll optimization
- Debounced event handlers

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## Troubleshooting

### Voice not working
- Check browser supports Web Speech API
- Ensure "Enable Voice" is checked
- Try different browser (Chrome recommended)
- Check browser console for errors

### WebSocket connection fails
- Verify backend is running
- Check WebSocket URL in `js/websocket.js`
- Look for CORS issues in console
- Check firewall/network settings

### Messages not appearing
- Check browser console for errors
- Verify mock data is enabled or backend is connected
- Check debate is actually started (button disabled)

## Future Enhancements

- [ ] Agent avatar images/icons
- [ ] Message reactions/voting
- [ ] Debate replay controls
- [ ] Multi-language support
- [ ] Dark/light theme toggle
- [ ] Accessibility improvements (ARIA)
- [ ] PWA support (offline mode)
- [ ] Chat-style message input
- [ ] Video recording of debates

## License

Part of the AI Debate Arena project.

---

**Built with ❤️ for the Kaggle AI Agents Capstone**
