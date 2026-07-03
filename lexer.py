import re

def lex_poly_file(file_content):
    print("🚀 Firing up the .poly Lexer Engine...\n")
    
    # 1. DEFINE THE REGULAR EXPRESSIONS
    global_start_pattern = r"~(\d+)\s*/"
    global_end_pattern = r"\\\s*(\d+)~"
    
    # NEW: Local Scope Patterns (using the backtick `)
    local_start_pattern = r"`(\d+)\s*/"
    local_end_pattern = r"\\\s*(\d+)`"
    
    # 2. SCAN THE FILE FOR MATCHES
    tokens = []
    
    for match in re.finditer(global_start_pattern, file_content):
        tokens.append({"type": "GLOBAL_START", "id": match.group(1), "position": match.start()})
        
    for match in re.finditer(global_end_pattern, file_content):
        tokens.append({"type": "GLOBAL_END", "id": match.group(1), "position": match.start()})

    for match in re.finditer(local_start_pattern, file_content):
        tokens.append({"type": "LOCAL_START", "id": match.group(1), "position": match.start()})
        
    for match in re.finditer(local_end_pattern, file_content):
        tokens.append({"type": "LOCAL_END", "id": match.group(1), "position": match.start()})
        
    # 3. CHRONOLOGICAL SORT (The secret to reading top-to-bottom)
    tokens.sort(key=lambda x: x["position"])
    
    # 4. PRINT THE RESULTS WITH INDENTATION
    for t in tokens:
        # Add visual indentation for Local blocks to prove we understand the nesting
        indent = "    " if "LOCAL" in t["type"] else ""
        print(f"{indent}✔️ TOKEN FOUND: [{t['type']}] Scope {t['id']} at index {t['position']}")

    print("\nLexer Scan Complete.")
    return tokens


# --- TESTING THE LEXER ---
if __name__ == "__main__":
    
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
    
    extracted_tokens = lex_poly_file(dummy_poly_code)