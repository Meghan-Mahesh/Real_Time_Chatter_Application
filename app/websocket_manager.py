from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # key: token, value: WebSocket connection
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, token: str):
        await websocket.accept()
        self.active_connections[token] = websocket
        print(f"Client connected. Active connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        for token, ws in list(self.active_connections.items()):
            if ws == websocket:
                del self.active_connections[token]
                break
        print(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for ws in self.active_connections.values():
            await ws.send_text(message)
