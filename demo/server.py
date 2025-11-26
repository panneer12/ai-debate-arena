"""
FastAPI Server for AI Debate Arena.
Serves the Web UI and handles WebSocket connections.
"""
import logging
import asyncio
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from demo.debate_manager import DebateManager

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

# Global Debate Manager
debate_manager: Optional[DebateManager] = None

# -- Data Models --
class StartDebateRequest(BaseModel):
    topic: str
    rounds: int = 2
    agents: List[str]

class StopDebateRequest(BaseModel):
    debate_id: Optional[str] = None

# -- Connection Manager --
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")

manager = ConnectionManager()

# -- Lifespan --
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Server starting up...")
    global debate_manager
    logger.info("📦 Creating DebateManager...")
    debate_manager = DebateManager(broadcast_func=manager.broadcast)
    logger.info("🤖 Initializing agents (this may take 30 seconds)...")
    await debate_manager.initialize_agents()
    logger.info("✅ Server ready! All agents initialized.")
    yield
    # Shutdown
    logger.info("🛑 Server shutting down...")
    if debate_manager and debate_manager.is_running:
        await debate_manager.stop_debate()

# -- App --
app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- API Endpoints --

@app.post("/api/debate/start")
async def start_debate(request: StartDebateRequest):
    if debate_manager.is_running:
        raise HTTPException(status_code=400, detail="Debate already running")

    # Generate debate ID upfront
    from datetime import datetime
    debate_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Run in background
    asyncio.create_task(
        debate_manager.start_debate(
            topic=request.topic,
            rounds=request.rounds,
            active_agents=request.agents,
            debate_id=debate_id  # Pass the ID we generated
        )
    )
    return {"status": "started", "topic": request.topic, "debate_id": debate_id}

@app.post("/api/debate/stop")
async def stop_debate(request: StopDebateRequest):
    if not debate_manager.is_running:
        return {"status": "already_stopped"}
        
    await debate_manager.stop_debate()
    return {"status": "stopping"}

@app.get("/api/debate/{debate_id}/status")
async def get_status(debate_id: str):
    return {
        "is_running": debate_manager.is_running,
        "debate_id": debate_manager.debate_id
    }

@app.get("/api/debate/{debate_id}/history")
async def get_history(debate_id: str):
    """Get the full debate history."""
    if not debate_manager.memory:
        raise HTTPException(status_code=404, detail="No active debate")

    history = debate_manager.memory.get_full_history()
    return {
        "debate_id": debate_id,
        "messages": [msg.to_dict() for msg in history]
    }

@app.get("/api/debate/{debate_id}/export")
async def export_debate(debate_id: str, format: str = "txt"):
    """Export debate transcript."""
    from fastapi.responses import PlainTextResponse, JSONResponse

    if not debate_manager.memory:
        raise HTTPException(status_code=404, detail="No active debate")

    history = debate_manager.memory.get_full_history()

    if format == "json":
        return JSONResponse({
            "debate_id": debate_id,
            "messages": [msg.to_dict() for msg in history]
        })
    elif format == "txt":
        # Create text transcript
        lines = []
        lines.append(f"AI Debate Arena - Transcript")
        lines.append(f"Debate ID: {debate_id}")
        lines.append(f"=" * 80)
        lines.append("")

        for msg in history:
            lines.append(f"[{msg.from_agent}] ({msg.type})")
            lines.append(msg.content)
            lines.append("-" * 80)
            lines.append("")

        transcript = "\n".join(lines)
        return PlainTextResponse(transcript, media_type="text/plain")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# -- WebSocket --

@app.websocket("/ws/debate/{debate_id}")
async def websocket_endpoint(websocket: WebSocket, debate_id: str):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client commands (if any)
            data = await websocket.receive_text()
            # Currently we don't handle client-to-server messages, but we could
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# -- Static Files --
# Mount the 'demo/ui' directory to serve HTML/JS/CSS
app.mount("/", StaticFiles(directory="demo/ui", html=True), name="ui")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
