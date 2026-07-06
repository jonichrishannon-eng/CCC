import os
import json
import platform
import ctypes

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

def generate_system_profile():
    """Runs only once per PC to map out the hardware and permissions."""
    print("  ⚙️ [OMNI] First-time setup detected. Profiling host system...")
    
    profile = {
        "os": platform.system(),
        "arch": platform.machine(),
        "is_admin": check_admin(),
        "cores": os.cpu_count()
    }
    
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=4)
        
    print(f"  ✔️ [OMNI] System profile locked: {profile['os']} | Admin: {profile['is_admin']}")
    return profile

def get_system_profile():
    """Loads the saved profile, or generates a new one if missing."""
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    return generate_system_profile()

# ==========================================
# 2. THE OMNI EXECUTION ROUTER
# ==========================================
def execute_poly_file(filepath):
    print(f"\n🚀 Launching OMNI Engine for: {filepath}")
    
    # 1. Load the Host Environment
    sys_profile = get_system_profile()
    
    # 2. Read the Application Blueprint
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_code = f.read()
        
    app_manifest = parse_mosr_manifest(raw_code)
    
    # 3. The Collision Logic (Deciding how to build)
    print("\n  🧠 [OMNI] Calculating optimal deployment strategy...")
    target_os = sys_profile["os"]
    
    if f"Target: {target_os}" in app_manifest:
        rules = app_manifest[f"Target: {target_os}"]
        print(f"  -> Selected Blueprint: {target_os}")
        print(f"  -> Compiler Routed To: {rules.get('compiler', 'Default')}")
    else:
        print(f"  -> No specific target for {target_os}. Falling back to Universal Build.")
        
    if not sys_profile["is_admin"] and "Privilege: User-Space" in app_manifest:
        print("  -> ⚠️ Admin rights missing! Rerouting to User-Space bypass...")
        bypass_rules = app_manifest["Privilege: User-Space"]
        print(f"  -> Forcing Linker: {bypass_rules.get('force_gnu_linker')}")

    print("  🚀 [OMNI] Handoff initiated. Passing blueprint to compiler engine...")
    
    # 4. Trigger the Compiler Engine
    tokens = lex_poly_file(raw_code)
    ast = build_ast(tokens)
    
# ---> THE MISSING LINK: Extract the actual code and rules! <---
    ast = extract_payloads(ast, raw_code)
    
    generate_files(ast, output_dir="build", manifest=app_manifest)
    
    print("\n  ✅ [OMNI] Build complete. Workspace is ready.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: omni <file.poly> OR omni repair")
    elif sys.argv[1] == "repair":
        from repair import verify_and_heal
        verify_and_heal()
    else:
        execute_poly_file(sys.argv[1])