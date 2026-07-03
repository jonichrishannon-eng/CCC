def build(blocks, manifest=None):
    output = "// ⚙️ Auto-Generated C++ Firmware\n#include <iostream>\n\nint main() {\n"
    
    for block in blocks:
        # Indent the C++ payload so it looks pretty inside the main() function
        raw_code = block.get("raw_code", "")
        indented_code = "\n".join([f"    {line}" for line in raw_code.split("\n")])
        output += indented_code + "\n"
        
    output += "\n    return 0;\n}\n"
    
    return {"firmware.cpp": output}