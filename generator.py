import os
import importlib
import hashlib
from datetime import datetime

# 1. THE HASHING ENGINE
def generate_sha256(content):
    """Calculates the cryptographic hash of the generated code."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def generate_files(ast, output_dir="build", manifest=None):
    print(f"🌍 Initializing Universal Plugin System in '{output_dir}/'...\n")
    
    if manifest:
        print(f"  🧠 [Generator] Applying MOSR manifest rules...")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Prepare our real-time ledger memory
    ledger_entries = []

    # ==========================================
    # 1. Group all blocks by their Language Engine
    # ==========================================
    engine_blocks = {}
    for global_node in ast:
        for local_node in global_node.get("children", []):
            rules = local_node.get("rules", {})
            engine = rules.get("engine")
            
            if not engine: continue
            
            engine_name = engine.lower()
            if engine_name not in engine_blocks:
                engine_blocks[engine_name] = []
                
            engine_blocks[engine_name].append(local_node)

    # ==========================================
    # 2. Dynamically load, execute, and LOG adapters
    # ==========================================
    for engine, blocks in engine_blocks.items():
        try:
            adapter_module = importlib.import_module(f"adapters.{engine}_adapter")
            output_files = adapter_module.build(blocks, manifest)
            
            # 3. Write files and stamp the Cryptographic Ledger
            if output_files:
                for filename, content in output_files.items():
                    filepath = os.path.join(output_dir, filename)
                    
                    # Write the physical file
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                        
                    # Calculate the hash
                    file_hash = generate_sha256(content)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Log the exact state
                    ledger_entries.append(f"[{timestamp}] ACTION: BUILD | FILE: {filename} | ENGINE: {engine.upper()} | SHA256: {file_hash}")
                    
                    print(f"     ✔️ Generated {filename} (Hash: {file_hash[:8]}...)")
                    
        except ModuleNotFoundError:
            print(f"❌ ERROR: No adapter found for Engine '{engine}'!")
        except TypeError as e:
            print(f"❌ ERROR: Adapter signature mismatch in '{engine}'. Details: {e}")

    # ==========================================
    # 4. Commit the Ledger to Disk
    # ==========================================
    if ledger_entries:
        ledger_path = os.path.join(output_dir, "poly.log")
        # We use "a" (append) so patches stack chronologically as Local Amendments
        with open(ledger_path, "a", encoding="utf-8") as log_file:
            for entry in ledger_entries:
                log_file.write(entry + "\n")
        print(f"\n  📜 [Ledger] Stamped {len(ledger_entries)} cryptographic entries to poly.log")