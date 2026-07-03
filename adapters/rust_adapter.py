import os

def build(blocks, manifest=None):
    print("  -> Forging Pure-TCP Rust Engine (Zero Dependencies)...")
    
    os.makedirs("build/src", exist_ok=True)
    
    # 1. Check OMNI Manifest for corporate/admin bypass rules
    linker_override = ""
    if manifest and "Privilege: User-Space" in manifest:
        if manifest["Privilege: User-Space"].get("force_gnu_linker") == "True":
            print("     [OMNI Override] Locked environment detected. Forcing GNU toolchain.")
            linker_override = "--target x86_64-pc-windows-gnu"
            
    # You would append this linker_override to the subprocess build command later!

    # 2. Look at this Cargo.toml. ZERO dependencies.
    cargo_toml = """[package]
name = "poly_compute"
version = "0.1.0"
edition = "2021"

[dependencies]
"""

    # 2. We use Rust's built-in std::net to manually write the HTTP protocol!
    rust_code = """// 🦀 Auto-Generated Rust Compute Node (Raw TCP)
use std::io::Write;
use std::net::TcpStream;

// The invisible raw-TCP bridge to the Magic DOM
fn poly_state(key: &str, value: &str) {
    if let Ok(mut stream) = TcpStream::connect("127.0.0.1:8000") {
        // Manually format the JSON body
        let body = format!("{{\\"value\\": \\"{}\\"}}", value);
        
        // Manually construct the raw HTTP POST request string
        let request = format!(
            "POST /api/state/{} HTTP/1.1\\r\\n\\
             Host: 127.0.0.1:8000\\r\\n\\
             Content-Type: application/json\\r\\n\\
             Content-Length: {}\\r\\n\\
             Connection: close\\r\\n\\
             \\r\\n\\
             {}",
            key, body.len(), body
        );
        
        // Blast it through the TCP pipe
        let _ = stream.write_all(request.as_bytes());
    }
}

fn main() {
    println!("🦀 Rust Pure-TCP Node Online. Initiating matrix...");
"""

    for block in blocks:
        raw_code = block.get("raw_code", "")
        indented_code = "\n".join([f"    {line}" for line in raw_code.split("\n")])
        rust_code += indented_code + "\n\n"

    rust_code += "}\n"
    
    return {
        "Cargo.toml": cargo_toml,
        "src/main.rs": rust_code
    }