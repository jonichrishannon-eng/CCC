def build(blocks, manifest=None):
    print("      -> Injecting HTML UI & Magic DOM WebSocket Engine...")
    
    output = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anti-Gravity V2.0</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
"""
    
    for block in blocks:
        raw_code = block.get("raw_code", "")
        indented_code = "\n".join([f"    {line}" for line in raw_code.split("\n")])
        output += f"    \n"
        output += indented_code + "\n\n"
        
    # ⚡ THE V2.0 MAGIC DOM ENGINE ⚡
    output += """
<script>
    // Automatically connect to the Python Brain
    const ws = new WebSocket('ws://' + window.location.host + '/ws/state');

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        // When Python broadcasts an update, change the HTML instantly!
        if (data.type === 'init') {
            for (const [key, value] of Object.entries(data.state)) {
                updateMagicDOM(key, value);
            }
        } else if (data.type === 'update') {
            updateMagicDOM(data.key, data.value);
        }
    };

    function updateMagicDOM(key, value) {
        // Find any HTML element with data-poly-bind="variable_name"
        const elements = document.querySelectorAll(`[data-poly-bind="${key}"]`);
        elements.forEach(el => {
            el.innerText = value; // Inject the new value right into the webpage
        });
    }
    
    // A simple function you can use in HTML buttons to change state
    window.polyState = function(key, value) {
        ws.send(JSON.stringify({key: key, value: value}));
    };
</script>
</body>
</html>"""
    
    return {"index.html": output}