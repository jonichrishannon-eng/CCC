def build(blocks, manifest=None):
    print("  -> Compiling CSS Stylesheets...")
    
    output = "/* 🎨 Auto-Generated CSS Engine */\n\n"
    
    # Check for OMNI Control Center theme injections
    if manifest and "Mode: Maximalist" in manifest:
        if manifest["Mode: Maximalist"].get("theme") == "dark":
            print("     [OMNI Override] Injecting System-Wide Dark Mode.")
            output += "body { background-color: #000000 !important; color: #00ffcc !important; }\n\n"

    for block in blocks:
        output += f"/* Source Block: `{block.get('id')} */\n"
        output += block.get("raw_code", "") + "\n\n"
        
    filename = "styles.css"
    if blocks and "rules" in blocks[0] and blocks[0]["rules"].get("filename"):
        filename = blocks[0]["rules"]["filename"]
    return {filename: output}