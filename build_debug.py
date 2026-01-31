import os
import subprocess
import sys
import shutil

def build():
    print("[DEBUG BUILD] Starting build with --console for runtime error capture...")
    
    # 1. Clean
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            
    # 2. Command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console", # Enable console to see Traceback
        "--name=DataPrism",
        "--add-data", "src/resources;src/resources",
        "--icon", os.path.abspath("assets/icon.ico"),
        "--clean",
        "main.py"
    ]
    
    print(f"[RUN] {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    build()
