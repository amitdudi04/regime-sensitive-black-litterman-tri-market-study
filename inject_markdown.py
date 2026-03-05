import re
import os

md_path = "FINAL_PROJECT_IMPLEMENTATION.md"
with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

# Paths to the actual refactored codes we want to insert
files_to_inject = {
    "core/dual_market.py": "core/dual_market.py",
    "ui/desktop_gui.py": "ui/desktop_gui.py",
    "core/backtester.py": "core/backtester.py"
}

for module_name, filepath in files_to_inject.items():
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}, not found.")
        continue
        
    with open(filepath, "r", encoding="utf-8") as f:
        module_code = f.read()
    
    # regex pattern to find the exact block for the module
    # It looks for: # =================================\n# MODULE: ...\n# =================================\n ...code... until the next # ===... or end of tripple backticks
    pattern = rf"(# =+[\r\n]+# MODULE:\s*{module_name}[\r\n]+# =+[\r\n]+)(.*?)(?=(\n# =+[\r\n]+# MODULE:|\n```))"
    
    def replacer(match):
        header = match.group(1)
        return f"{header}\n{module_code}\n"
        
    new_content, count = re.subn(pattern, replacer, content, flags=re.DOTALL)
    if count > 0:
        print(f"Successfully injected {module_name}")
        content = new_content
    else:
        print(f"Could not find injection point for {module_name}")

with open(md_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Markdown injection complete.")
