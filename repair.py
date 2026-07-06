import os
import hashlib
from datetime import datetime
from google import genai  # <-- The new modern SDK

def generate_sha256(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def clean_ai_response(text):
    """Strips Markdown formatting fences (like ```html) from the AI output."""
    if text.strip().startswith("```"):
        lines = text.strip().split("\n")
        # Drop the first line (```lang) and the last line (```)
        return "\n".join(lines[1:-1]).strip()
    return text.strip()

def scan_ledger(output_dir="build"):
    output_dir = os.path.join(os.getcwd(), output_dir)
    ledger_path = os.path.join(output_dir, "poly.log")
    if not os.path.exists(ledger_path):
        print("❌ [Repair] No poly.log found. Cannot verify integrity.")
        return None

    print(f"🔍 [Repair] Scanning Cryptographic Ledger in '{output_dir}/'...\n")
    expected_hashes = {}
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        if "ACTION:" in line: 
            parts = line.split(" | ")
            filename = parts[1].replace("FILE: ", "").strip()
            file_hash = parts[3].replace("SHA256: ", "").strip()
            expected_hashes[filename] = file_hash

    return expected_hashes

def verify_and_heal(output_dir="build"):
    output_dir = os.path.join(os.getcwd(), output_dir)
    expected_hashes = scan_ledger(output_dir)
    if not expected_hashes: return
    
    collisions_found = []
    
    for filename, expected_hash in expected_hashes.items():
        filepath = os.path.join(output_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"  ❌ MISSING: {filename}")
            collisions_found.append({"file": filename, "hash": expected_hash, "filepath": filepath})
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            current_content = f.read()
            
        current_hash = generate_sha256(current_content)
        
        if current_hash == expected_hash:
            print(f"  ✔️ VERIFIED: {filename}")
        else:
            print(f"  ⚠️ COLLISION DETECTED: {filename} has been tampered with or broken!")
            collisions_found.append({"file": filename, "hash": expected_hash, "filepath": filepath})

    if collisions_found:
        print("\n🚨 [Immune System] Architecture compromised. Initiating Bypass Protocol...")
        for collision in collisions_found:
            trigger_bypass(collision)
    else:
        print("\n✅ [Immune System] All files mathematically verified. Architecture is stable.")

def get_appdata_dir():
    import platform
    if platform.system() == "Windows":
        base_dir = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        app_dir = os.path.join(base_dir, "OMNI_Engine")
    else:
        app_dir = os.path.join(os.path.expanduser("~"), ".omni_engine")
    return app_dir

def trigger_bypass(collision):
    """The Two-Layer Survival Mechanism."""
    import json # Added here just in case it isn't at the top of the file
    
    filename = collision['file']
    filepath = collision['filepath']
    
    print(f"\n  🛠️ Attempting to heal: {filename} (Target Hash: {collision['hash'][:8]}...)")
    
    # ==========================================
    # LAYER 1: OMNIMod Community Marketplace
    # ==========================================
    print("     -> [Layer 1] Querying free & open OMNIMod Community Marketplace...")
    local_marketplace_file = os.path.join(os.getcwd(), "marketplace.json")
    global_marketplace_file = os.path.join(get_appdata_dir(), "marketplace.json")
    marketplace_file = local_marketplace_file if os.path.exists(local_marketplace_file) else global_marketplace_file
    print(f"     -> [Info] Using marketplace at: {marketplace_file}")
    
    if os.path.exists(marketplace_file):
        with open(marketplace_file, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
            
        if filename in marketplace:
            mod = marketplace[filename]
            print(f"     -> 📦 Found Community Patch by {mod['author']}: {mod['description']}")
            
            fixed_code = mod['code']
            
            # 1. Hot-Swap the physical file with the community fix
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fixed_code)
                
            # 2. Stamp the amendment into the ledger
            new_hash = generate_sha256(fixed_code)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ledger_entry = f"[{timestamp}] ACTION: HEAL | FILE: {filename} | ENGINE: OMNIMOD_MARKETPLACE | SHA256: {new_hash}\n"
            
            output_dir = os.path.dirname(filepath)
            with open(os.path.join(output_dir, "poly.log"), "a", encoding="utf-8") as f:
                f.write(ledger_entry)
                
            print(f"     -> 🟢 SUCCESS: File repaired via Community Patch. New hash: {new_hash[:8]}...")
            return # EXIT HERE! We don't need the AI!

    print("     -> ❌ No community patch found for this collision.")
    
    # ==========================================
    # LAYER 2: AI Synthesizer (Gemini)
    # ==========================================
    print("     -> [Layer 2] Awakening AI Synthesizer (Gemini API)...")
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("     -> 🛑 ERROR: No GEMINI_API_KEY found in environment variables. Synthesis aborted.")
        return
        
    client = genai.Client()
    
    with open(filepath, "r", encoding="utf-8") as f:
        corrupted_code = f.read()

    prompt = f"""
    You are the OMNI Engine Auto-Repair Module.
    The following file ({filename}) has failed cryptographic verification due to a syntax error or tampering.
    
    Analyze the corrupted code below, fix any syntactical errors, and return ONLY the completely corrected raw code.
    Do not add explanations, comments, or pleasantries. Return only the code that should be saved to the file.
    
    CORRUPTED CODE:
    {corrupted_code}
    """
    
    print("     -> 🧠 Analyzing syntax damage and generating patch...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        fixed_code = clean_ai_response(response.text)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(fixed_code)
            
        new_hash = generate_sha256(fixed_code)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ledger_entry = f"[{timestamp}] ACTION: HEAL | FILE: {filename} | ENGINE: AI_SYNTHESIZER | SHA256: {new_hash}\n"
        
        output_dir = os.path.dirname(filepath)
        with open(os.path.join(output_dir, "poly.log"), "a", encoding="utf-8") as f:
            f.write(ledger_entry)
            
        print(f"     -> 🟢 SUCCESS: File repaired via AI Synthesis. New hash: {new_hash[:8]}...")
        
    except Exception as e:
        print(f"     -> 🔴 AI Synthesis failed: {e}")

if __name__ == "__main__":
    verify_and_heal()