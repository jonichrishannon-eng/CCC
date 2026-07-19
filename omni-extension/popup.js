document.getElementById('compile-btn').addEventListener('click', async () => {
    const outputBox = document.getElementById('output');
    const targetFile = document.getElementById('target-file').value;
    
    outputBox.style.color = "#8b949e";
    outputBox.innerText = `Sending blueprint '${targetFile}' to local bridge...`;

    try {
        // We will build a local server on port 8000 to listen for this
        const response = await fetch('http://localhost:8000/compile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file: targetFile })
        });

        if (!response.ok) throw new Error("Bridge connection failed.");

        const jsonResponse = await response.json();
        
        // Render the raw JSON output beautifully in the extension
        outputBox.style.color = "#3fb950";
        outputBox.innerText = JSON.stringify(jsonResponse, null, 2);

    } catch (error) {
        outputBox.style.color = "#f85149";
        outputBox.innerText = "❌ ERROR: Could not connect to local bridge. Is the middleware running?\n\n" + error.message;
    }
});