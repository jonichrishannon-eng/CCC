import re
import textwrap

def build(blocks, manifest=None):
    print("      -> Forging Python State Broker (FastAPI)...")

    # 1. Initialize State Store from the AST
    initial_state = {}
    if blocks and "global_state" in blocks[0]:
        initial_state = blocks[0]["global_state"]

    state_dict_str = "{\n"
    for key, data in initial_state.items():
        val = data['initial_value']
        if val in ["True", "False"] or val.isdigit():
            state_dict_str += f"    '{key}': {val},\n"
        else:
            state_dict_str += f"    '{key}': '{val}',\n"
    state_dict_str += "}"

    raw_python_code = ""
    functions_to_bridge = []

    for block in blocks:
        # THE FIX: Strip dangling spaces, then calculate the perfect left wall
        raw_code = block.get("raw_code", "").rstrip()
        code = textwrap.dedent(raw_code).strip("\n")
        
        raw_python_code += f"# --- Source Block `{block.get('id', 'X')} ---\n{code}\n\n"
        
        matches = re.finditer(r"def\s+([a-zA-Z0-9_]+)\s*\(", code)
        for match in matches:
            functions_to_bridge.append({
                "name": match.group(1),
                "condition": block.get("rules", {}).get("condition")
            })

    # 3. Assemble the FastAPI Server
    fastapi_server = f"""from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
STATE_STORE = {state_dict_str}
active_clients = []

# ⚡ V2.0 WEBSOCKET PIPELINE
@app.websocket("/ws/state")
async def websocket_state(websocket: WebSocket):
    await websocket.accept()
    active_clients.append(websocket)
    
    await websocket.send_json({{"type": "init", "state": STATE_STORE}})
    
    try:
        while True:
            data = await websocket.receive_json()
            if "key" in data and "value" in data:
                STATE_STORE[data["key"]] = data["value"]
                print(f"⚡ WEBSOCKET SYNC: {{data['key']}} is now {{data['value']}}")
                
                for client in active_clients:
                    await client.send_json({{"type": "update", "key": data["key"], "value": data["value"]}})
    except WebSocketDisconnect:
        active_clients.remove(websocket)

# 📡 V1.0 BACKWARD COMPATIBILITY
@app.post("/api/state/{{key}}")
async def update_state_http(key: str, payload: dict):
    if key in STATE_STORE:
        STATE_STORE[key] = payload.get("value")
        for client in active_clients:
            await client.send_json({{"type": "update", "key": key, "value": STATE_STORE[key]}})
        return {{"status": "success", "state": STATE_STORE}}
    return {{"status": "error", "reason": "Not found"}}

# ⚙️ INJECTED RAW LOGIC
{raw_python_code}
"""
    
    for func in functions_to_bridge:
        name = func["name"]
        cond = func["condition"]
        
        fastapi_server += f"\n@app.get('/api/func/{name}')\n"
        fastapi_server += f"def api_{name}():\n"
        
        if cond:
            safe_cond = cond
            for key in initial_state.keys():
                safe_cond = safe_cond.replace(key, f"STATE_STORE['{key}']")

            fastapi_server += f"    # 3C Security Gate\n"
            fastapi_server += f"    if not ({safe_cond}):\n"
            fastapi_server += f"        return {{'status': 'blocked', 'reason': 'Failed condition: {cond}'}}\n"
            
        fastapi_server += f"    result = {name}()\n"
        fastapi_server += f"    return {{'status': 'success', 'function': '{name}', 'result': result}}\n"

    # 🛡️ BULLETPROOF STATIC ROUTING
    fastapi_server += """
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
"""

    filename = "main.py"
    if blocks and "rules" in blocks[0] and blocks[0]["rules"].get("filename"):
        filename = blocks[0]["rules"]["filename"]
    return {filename: fastapi_server}