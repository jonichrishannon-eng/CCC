import os
import sys
import json
import time
import platform
import ctypes
import argparse

# Updated imports to include extract_payloads
from parser import parse_mosr_manifest, build_ast, extract_payloads
from lexer import lex_poly_file       
from generator import generate_files  

def get_appdata_dir():
    if platform.system() == "Windows":
        base_dir = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        app_dir = os.path.join(base_dir, "OMNI_Engine")
    else:
        app_dir = os.path.join(os.path.expanduser("~"), ".omni_engine")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir, exist_ok=True)
    return app_dir

PROFILE_PATH = os.path.join(get_appdata_dir(), "omni_profile.json")

# ==========================================
# 1. THE ONE-TIME SYSTEM PROFILER
# ==========================================
def check_admin():
    """Returns True if the user has Admin rights, False if locked down."""
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def generate_system_profile(json_mode=False):
    """Runs only once per PC to map out the hardware and permissions."""
    if not json_mode:
        print("  ⚙️ [OMNI] First-time setup detected. Profiling host system...")
    
    profile = {
        "os": platform.system(),
        "arch": platform.machine(),
        "is_admin": check_admin(),
        "cores": os.cpu_count()
    }
    
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=4)
        
    if not json_mode:
        print(f"  ✔️ [OMNI] System profile locked: {profile['os']} | Admin: {profile['is_admin']}")
    return profile

def get_system_profile(json_mode=False):
    """Loads the saved profile, or generates a new one if missing."""
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    return generate_system_profile(json_mode)

# ==========================================
# 2. THE OMNI EXECUTION ROUTER
# ==========================================
def execute_poly_file(filepath, json_mode=False):
    if not json_mode:
        print(f"\n🚀 Launching OMNI Engine for: {filepath}")
    
    # 1. Load the Host Environment
    sys_profile = get_system_profile(json_mode)
    
    # 2. Read the Application Blueprint
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_code = f.read()
        
    app_manifest = parse_mosr_manifest(raw_code)
    
    # 3. The Collision Logic (Deciding how to build)
    if not json_mode:
        print("\n  🧠 [OMNI] Calculating optimal deployment strategy...")
        
    target_os = sys_profile["os"]
    
    if f"Target: {target_os}" in app_manifest:
        rules = app_manifest[f"Target: {target_os}"]
        if not json_mode:
            print(f"  -> Selected Blueprint: {target_os}")
            print(f"  -> Compiler Routed To: {rules.get('compiler', 'Default')}")
    else:
        if not json_mode:
            print(f"  -> No specific target for {target_os}. Falling back to Universal Build.")
        
    if not sys_profile["is_admin"] and "Privilege: User-Space" in app_manifest:
        if not json_mode:
            print("  -> ⚠️ Admin rights missing! Rerouting to User-Space bypass...")
        bypass_rules = app_manifest["Privilege: User-Space"]
        if not json_mode:
            print(f"  -> Forcing Linker: {bypass_rules.get('force_gnu_linker')}")

    if not json_mode:
        print("  🚀 [OMNI] Handoff initiated. Passing blueprint to compiler engine...")
    
    # 4. Trigger the Compiler Engine
    tokens = lex_poly_file(raw_code)
    ast = build_ast(tokens)
    
    # Extract the actual code and rules! 
    ast = extract_payloads(ast, raw_code)
    
    generate_files(ast, output_dir="build", manifest=app_manifest)
    
    if not json_mode:
        print("\n  ✅ [OMNI] Build complete. Workspace is ready.")
        
    # Return basic file tracking for the GUI JSON bridge
    return ["build/"]

# ==========================================
# 3. ARGUMENT PARSER & DATA BRIDGE
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="OMNI Engine - Multi-Language Compiler")
    parser.add_argument("command", help="Target .poly file to compile OR 'repair' to heal the system")
    parser.add_argument("--json", action="store_true", help="Output data in strict JSON format for GUI hooks")
    
    args = parser.parse_args()

    # Route 1: Trigger the self-healing immune system
    if args.command.lower() == "repair":
        from repair import verify_and_heal
        
        if args.json:
            import contextlib, io
            # Mute the repair.py outputs for the GUI bridge
            with contextlib.redirect_stdout(io.StringIO()):
                verify_and_heal()
            print(json.dumps({
                "status": "success", 
                "operation": "repair", 
                "timestamp": time.time()
            }))
        else:
            print("🔧 Initiating OMNI self-healing protocol...")
            verify_and_heal()
        return

    # Route 2: Establish the GUI Data Bridge for compiling
    bridge_data = {
        "status": "pending",
        "timestamp": time.time(),
        "blueprint": args.command,
        "files_generated": [],
        "errors": []
    }

    try:
        if args.json:
            import contextlib, io
            # THE GLOBAL SILENCER: Traps all emoji prints from lexer, parser, and generator
            with contextlib.redirect_stdout(io.StringIO()):
                generated_files = execute_poly_file(args.command, json_mode=True)
        else:
            # Run normally with all terminal UI enabled
            generated_files = execute_poly_file(args.command, json_mode=False)
        
        bridge_data["files_generated"] = generated_files 
        bridge_data["status"] = "success"

    except Exception as e:
        bridge_data["status"] = "failed"
        bridge_data["errors"].append(str(e))
        
        if not args.json:
            print(f"\n❌ [ERROR] {e}")

    # Final Output Gateway
    if args.json:
        # Print ONLY the strict JSON object to standard output
        print(json.dumps(bridge_data))

if __name__ == "__main__":
    main()