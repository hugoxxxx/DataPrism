import os
import subprocess
import sys
import shutil

def build():
    print("🚀 Starting DataPrism 1.0.0 Build Process (Optimized)...")
    
    # 1. Clean previous builds
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"🧹 Cleaning {folder}...")
            shutil.rmtree(folder)
            
    # 2. Detect PyInstaller Path
    pyinstaller_path = "pyinstaller" # Default
    scripts_dir = os.path.dirname(sys.executable)
    pyinstaller_exe = os.path.join(scripts_dir, "pyinstaller.exe")
    
    if os.path.exists(pyinstaller_exe):
        pyinstaller_path = pyinstaller_exe
        print(f"📍 Found local PyInstaller: {pyinstaller_path}")
    else:
        print(f"⚠️ Local PyInstaller not found at {pyinstaller_exe}, trying system 'pyinstaller'...")
    
    # 3. Size Optimization: Exclude unused large Qt modules
    excludes = [
        "PySide6.QtNetwork", "PySide6.QtSql", "PySide6.QtXml", "PySide6.QtTest",
        "PySide6.QtDBus", "PySide6.QtWebEngine", "PySide6.QtPdf", "PySide6.QtMultimedia",
        "PySide6.QtCharts", "PySide6.QtOpenGL", "PySide6.QtQml", "PySide6.QtQuick",
        "PySide6.Qt3D", "PySide6.QtBluetooth", "PySide6.QtPositioning", "PySide6.QtSensors",
        "PySide6.QtSerialPort", "PySide6.QtWebChannel", "PySide6.QtWebSockets",
        "PySide6.QtRemoteObjects", "PySide6.QtDesigner", "PySide6.QtHelp"
    ]
    
    # 4. PyInstaller Command
    cmd = [
        pyinstaller_path,
        "--onefile",
        "--noconsole",
        "--name=DataPrism",
        "--add-data=src/resources;src/resources",
        "--icon=assets/icon.ico" if os.path.exists("assets/icon.ico") else None,
        "--clean"
    ]
    
    # Add exclusions
    for mod in excludes:
        cmd.extend(["--exclude-module", mod])
        
    cmd.append("main.py")
    
    # Filter out None icons
    cmd = [c for c in cmd if c is not None]
    
    print(f"📦 Running Optimized Build: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Build Successful! Check the 'dist' folder for DataPrism.exe")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
