import json
import re

# =====================================================================
# 1. THE TREE BUILDER (AST GENERATION)
# =====================================================================
def build_ast(tokens):
    print("🌲 Building the Abstract Syntax Tree...\n")
    
    ast = []      # The final tree we will return
    stack = []    # Temporary memory to keep track of what's currently "open"
    
    for token in tokens:
        # IF WE HIT A GLOBAL START BOUNDARY (~1 /)
        if token["type"] == "GLOBAL_START":
            node = {
                "type": "GlobalScope", 
                "id": token["id"], 
                "children": [],    
                "start_pos": token["position"],
                "end_pos": None
            }
            
            if not stack:
                ast.append(node)
            else:
                stack[-1]["children"].append(node)
                
            stack.append(node) 

        # IF WE HIT A LOCAL START BOUNDARY (`1 /)
        elif token["type"] == "LOCAL_START":
            node = {
                "type": "LocalScope", 
                "id": token["id"],
                "header": None,    
                "raw_code": None,  
                "start_pos": token["position"],
                "end_pos": None
            }
            
            if stack:
                stack[-1]["children"].append(node)
            else:
                print(f"⚠️ SYNTAX ERROR: Local Block {token['id']} found outside a Global Block!")
                
            stack.append(node)

        # IF WE HIT ANY END BOUNDARY (\ 1` or \ 1~)
        elif token["type"] in ["GLOBAL_END", "LOCAL_END"]:
            if stack:
                finished_node = stack.pop()
                finished_node["end_pos"] = token["position"]
    
    return ast

def parse_compute_header(header_string):
    # If the block has no header, return empty rules
    if not header_string:
        return {}

    # The blueprint for our execution rules
    rules = {
        "engine": None,    # e.g., Python, HTML
        "priority": None,  # BACKEND or FRONTEND
        "condition": None, # e.g., logged_in == False
        "amendment": None, # e.g., h1=Header
        "loop": None,      # e.g., task in task_list
        "filename": None   # e.g., server.py
    }

    # Split the string by your pipe | symbol and clean up spaces
    chunks = [chunk.strip() for chunk in header_string.split("|")]

    for chunk in chunks:
        if not chunk: continue
        
        # 1. Condition (Uses your ? symbol)
        if chunk.startswith("?"):
            rules["condition"] = chunk[1:].strip()
            
        # 2. Amendment (Uses your ! symbol)
        elif chunk.startswith("!"):
            rules["amendment"] = chunk[1:].strip()
            
        # 3. Iterate / Loop (Uses your @ symbol)
        elif chunk.startswith("@"):
            rules["loop"] = chunk[1:].strip()
            
        # 4. Priority Backend (Uses your ' symbol)
        elif "'" in chunk:
            rules["priority"] = "BACKEND"
            
        # 5. Priority Frontend (Uses your " symbol)
        elif '"' in chunk:
            rules["priority"] = "FRONTEND"
            
        # 6. Filename (Contains a dot, e.g., server.py)
        elif "." in chunk and not chunk.startswith("!") and not chunk.startswith("?") and not chunk.startswith("@"):
            rules["filename"] = chunk

        # 7. Engine (If it has no special symbols, it must be the language name)
        else:
            rules["engine"] = chunk

    return rules

# =====================================================================
# 2. THE PAYLOAD EXTRACTOR (LOGIC & CODE SEPARATION)
# =====================================================================
def extract_global_state(global_block_text):
    # Regex to find: $ [type] [name] = [value]
    state_vars = {}
    matches = re.finditer(r"\$\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)\s*=\s*(.+)", global_block_text)
    
    for match in matches:
        var_type = match.group(1).strip()
        var_name = match.group(2).strip()
        var_value = match.group(3).strip()
        
        state_vars[var_name] = {
            "type": var_type,
            "initial_value": var_value
        }
    
    return state_vars

def extract_payloads(ast, file_content):
    print("🧠 Extracting Compute Headers and Raw Code...\n")
    
    for global_node in ast:
        # NEW: Slice the entire Global Block text to hunt for state variables
        global_block_text = file_content[global_node["start_pos"] : global_node["end_pos"]]
        global_node["state"] = extract_global_state(global_block_text)
        for local_node in global_node["children"]:
            # NEW: Attach the global state to every local block so adapters can see it!
            local_node["global_state"] = global_node["state"]
            
            # Slice the exact text of this Local block from the raw file
            raw_block = file_content[local_node["start_pos"] : local_node["end_pos"]]
            
            # Extract the Compute Header (/: ... \)
            header_match = re.search(r"/:([\s\S]*?)\\", raw_block)
            
            if header_match:
                # Save the raw header string
                raw_header = header_match.group(1).strip()
                local_node["header"] = raw_header
                
                # NEW: Decode the rules using your custom symbols!
                local_node["rules"] = parse_compute_header(raw_header)
                
                # Extract the Raw Payload (everything after the header)
                header_end_index = header_match.end()
                raw_code = raw_block[header_end_index:]
                
                # Clean up the raw code
                raw_code = raw_code.strip()
                if raw_code.endswith('/'):
                    raw_code = raw_code[:-1].strip()
                local_node["raw_code"] = raw_code
                
    # Print the finalized Tree structure beautifully to the terminal
    print(json.dumps(ast, indent=4))
    
    return ast

# =====================================================================
# 3. COMPILER EXECUTION / TESTING
# =====================================================================
if __name__ == "__main__":
    
    # The dummy file content
    dummy_poly_code = r"""
    // START GLOBAL 1
    ~1 /
      
      ; Python & HTML & CSS
      $ bool logged_in = True
      
      // START LOCAL 1
      `1 /
        /: Python | 1' | ? logged_in == False \
          def secure_system():
              return "Access Denied"
        /
      \ 1`

    \ 1~
    """

    # The exact tokens passed from lexer.py (hardcoded for testing)
    mock_lexer_tokens = [
        {"type": "GLOBAL_START", "id": "1", "position": 27},
        {"type": "LOCAL_START", "id": "1", "position": 142},
        {"type": "LOCAL_END", "id": "1", "position": 260},
        {"type": "GLOBAL_END", "id": "1", "position": 273}
    ]
    
    # Run Phase 1: Build the empty folders
    syntax_tree = build_ast(mock_lexer_tokens)
    
    # Run Phase 2: Fill the folders with Logic and Code
    populated_tree = extract_payloads(syntax_tree, dummy_poly_code)

def parse_mosr_manifest(raw_code):
    """
    Extracts the routing rules and environment constraints from the MOSR block.
    """
    print("  🧠 [MOSR] Decoding Master Operating System Record...")
    manifest = {}
    
    # Split the raw text by the bracketed headers, e.g., [Target: Windows]
    # This separates the string into headers and their following content.
    sections = re.split(r'\[(.*?)\]', raw_code)
    
    # sections[0] is usually empty or contains the '/: MOSR' header text.
    # We loop through in pairs: i is the header, i+1 is the properties.
    for i in range(1, len(sections), 2):
        category = sections[i].strip()  # e.g., 'Target: Windows' or 'Mode: Minimalist'
        properties = sections[i+1].strip()
        
        manifest[category] = {}
        
        # Extract the key-value rules within this section
        for line in properties.split('\n'):
            line = line.strip()
            # Ignore empty lines and comments
            if ':' in line and not line.startswith('//') and not line.startswith(';'):
                key, value = line.split(':', 1)
                manifest[category][key.strip()] = value.strip()
                
    return manifest