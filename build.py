import os
import subprocess
import sys
import shutil

def build():
    print("[BUILD] Starting DataPrism 1.1.0 Optimized Build Process...")
    
    # 1. Clean previous builds
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"[CLEAN] Cleaning {folder}...")
            shutil.rmtree(folder)
            
    # 2. PyInstaller Path Detection
    current_python_dir = os.path.dirname(sys.executable)
    pyinstaller_path = os.path.join(current_python_dir, "Scripts", "pyinstaller.exe")
    if not os.path.exists(pyinstaller_path):
        pyinstaller_path = os.path.join(current_python_dir, "pyinstaller.exe")
    
    # 3. Size Optimization: Exclude unused large Qt modules
    # These were likely excluded in v1.0.0 to Achieve the 40MB size.
    excludes = [
        "PySide6.QtNetwork", "PySide6.QtSql", "PySide6.QtXml", "PySide6.QtTest",
        "PySide6.QtDBus", "PySide6.QtWebEngine", "PySide6.QtPdf", "PySide6.QtMultimedia",
        "PySide6.QtCharts", "PySide6.QtOpenGL", "PySide6.QtQml", "PySide6.QtQuick",
        "PySide6.Qt3D", "PySide6.QtBluetooth", "PySide6.QtPositioning", "PySide6.QtSensors",
        "PySide6.QtSerialPort", "PySide6.QtWebChannel", "PySide6.QtWebSockets",
        "PySide6.QtRemoteObjects", "PySide6.QtDesigner", "PySide6.QtHelp"
    ]
    
    # 4. Command Construction
    cmd = [
        pyinstaller_path,
        "--onefile",
        "--noconsole",
        "--name=DataPrism",
        "--add-data=src/resources;src/resources",
        f"--icon={os.path.abspath('assets/icon.ico')}",
        "--clean"
    ]
    
    for mod in excludes:
        cmd.extend(["--exclude-module", mod])
        
    cmd.append("main.py")
    
    # 5. UPX Optimization (Optional, if exists in root)
    if os.path.exists("upx.exe"):
        cmd.append("--upx-dir=.")
        
    print(f"[RUN] {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n[SUCCESS] Build Successful! Check dist/DataPrism.exe")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
