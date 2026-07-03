import sys
import os
import time
import subprocess

# Import your custom compiler engines
from lexer import lex_poly_file
from parser import build_ast, extract_payloads
from generator import generate_files

def print_banner():
    print("========================================")
    print(" 🚀 ANTI-GRAVITY 3.0 CLI 🚀 ")
    print("========================================\n")

# --- COMMAND 1: INIT ---
def init_project(name):
    print_banner()
    if os.path.exists(name):
        print(f"❌ ERROR: Folder '{name}' already exists.")
        return
        
    os.makedirs(name)
    
    # The default starter template for new projects
    starter_code = """// START GLOBAL 1
~1 /
  $ bool system_active = True
  
  `1 /
    /: Python | 1' \\
      def initialize_core():
          return "Core Online"
    /
  \\ 1`
\\ 1~"""
    
    filepath = os.path.join(name, f"main.poly")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(starter_code)
        
    print(f"✔️ Initialized new project in ./{name}")
    print(f"✔️ Created starter file: {filepath}")
    print("\nNext steps:")
    print(f"  cd {name}")
    print(f"  python ../poly.py build main.poly")

# --- COMMAND 2: BUILD ---
def build_project(filepath):
    print_banner()
    if not os.path.exists(filepath):
        print(f"❌ ERROR: Could not find '{filepath}'")
        return

    print(f"📄 Compiling: {filepath}...\n")
    start_time = time.time()

    with open(filepath, "r", encoding="utf-8") as file:
        file_content = file.read()

    tokens = lex_poly_file(file_content)
    if not tokens:
        print("❌ COMPILATION FAILED: Syntax Error")
        return

    empty_ast = build_ast(tokens)
    final_ast = extract_payloads(empty_ast, file_content)

    generate_files(final_ast, output_dir="build")

    end_time = time.time()
    compile_time = round((end_time - start_time) * 1000, 2)
    print("========================================")
    print(f"✅ BUILD SUCCESSFUL in {compile_time}ms")
    print("========================================")

# --- COMMAND 3: SERVE ---
def serve_project():
    print_banner()
    build_dir = "build"
    main_file = os.path.join(build_dir, "main.py")
    
    if not os.path.exists(main_file):
        print("❌ ERROR: No build found. Run the 'build' command first.")
        return
        
    print("🌐 Starting local development server...\n")
    try:
        # This tells Python to take over the terminal and run the FastAPI server
        subprocess.run([sys.executable, main_file])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")

# ==========================================
# THE CLI ROUTER
# ==========================================
if __name__ == "__main__":
    # If they type nothing, show the help menu
    if len(sys.argv) < 2:
        print_banner()
        print("Usage: python poly.py <command> [args]")
        print("\nCommands:")
        print("  init <name>    Create a new .poly project workspace")
        print("  build <file>   Compile a .poly file into the build/ directory")
        print("  serve          Start the local FastAPI backend server")
        sys.exit(1)

    # Grab the command the user typed
    command = sys.argv[1].lower()

    if command == "init":
        if len(sys.argv) < 3:
            print("⚠️ Usage: python poly.py init <project_name>")
        else:
            init_project(sys.argv[2])
            
    elif command == "build":
        if len(sys.argv) < 3:
            print("⚠️ Usage: python poly.py build <file.poly>")
        else:
            build_project(sys.argv[2])
            
    elif command == "serve":
        serve_project()
        
    else:
        print(f"❌ Unknown command: {command}")