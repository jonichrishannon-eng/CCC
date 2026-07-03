from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 THE CENTRAL NERVOUS SYSTEM
STATE_STORE = {
    'reactor_temp': 500,
}
active_clients = []

# ⚡ V2.0 WEBSOCKET PIPELINE
@app.websocket("/ws/state")
async def websocket_state(websocket: WebSocket):
    await websocket.accept()
    active_clients.append(websocket)
    
    await websocket.send_json({"type": "init", "state": STATE_STORE})
    
    try:
        while True:
            data = await websocket.receive_json()
            if "key" in data and "value" in data:
                STATE_STORE[data["key"]] = data["value"]
                print(f"⚡ WEBSOCKET SYNC: {data['key']} is now {data['value']}")
                
                for client in active_clients:
                    await client.send_json({"type": "update", "key": data["key"], "value": data["value"]})
    except WebSocketDisconnect:
        active_clients.remove(websocket)

# 📡 V1.0 BACKWARD COMPATIBILITY
@app.post("/api/state/{key}")
async def update_state_http(key: str, payload: dict):
    if key in STATE_STORE:
        STATE_STORE[key] = payload.get("value")
        for client in active_clients:
            await client.send_json({"type": "update", "key": key, "value": STATE_STORE[key]})
        return {"status": "success", "state": STATE_STORE}
    return {"status": "error", "reason": "Not found"}

# ⚙️ INJECTED RAW LOGIC
# --- Source Block `0 ---
def get_status():
          return "System Online"



@app.get('/api/func/get_status')
def api_get_status():
    result = get_status()
    return {'status': 'success', 'function': 'get_status', 'result': result}

# --- FRONTEND ROUTING ---
@app.get("/")
async def serve_ui():
    return FileResponse("build/index.html")

@app.get("/{filename}")
async def serve_assets(filename: str):
    file_path = f"build/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

if __name__ == "__main__":
    print("🚀 Anti-Gravity Server running on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
