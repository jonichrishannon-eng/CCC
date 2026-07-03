from parser import parse_mosr_manifest

mock_mosr_block = """
/: MOSR | OMNI-Manifest \
  [Target: Windows]
    compiler: MSVC
    fallback: GNU-user-space
    ui_engine: WebView2
    
  [Target: Android]
    compiler: NDK
    ui_engine: Native-APK-Wrapper
    
  [Privilege: User-Space]
    force_gnu_linker: True
    bypass_registry: True
"""

# Run the decoder
omni_rules = parse_mosr_manifest(mock_mosr_block)

# Print the resulting Python Dictionary
print("\n=== EXTRACTED OMNI RULES ===")
for category, rules in omni_rules.items():
    print(f"\n[{category}]")
    for key, val in rules.items():
        print(f"  -> {key}: {val}")