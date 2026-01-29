import os
import sys
import time
import subprocess
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from src.core.exif_worker import ExifToolWorker
from src.core.config import get_config

def measure_classic_v1_0(exiftool_path, file_paths):
    """Simulate v1.0: Launching exiftool for every single file"""
    start_time = time.time()
    results = {}
    for f in file_paths:
        cmd = [exiftool_path, "-json", f]
        result = subprocess.run(cmd, capture_output=True, creationflags=0x08000000) # CREATE_NO_WINDOW
        if result.returncode == 0:
            results[f] = json.loads(result.stdout)[0]
    return time.time() - start_time

def measure_argfile_v1_1(worker, file_paths):
    """Measure v1.1: Using the new Argfile batching"""
    start_time = time.time()
    # Manual call to avoid Qt thread issues in basic script
    worker.read_exif(file_paths)
    return time.time() - start_time

def run_benchmark():
    print("====================================================")
    print("DataPrism Performance Benchmark: v1.0 vs v1.1")
    print("====================================================")
    
    cfg = get_config()
    exiftool_path = cfg.get('exiftool_path', 'exiftool')
    worker = ExifToolWorker(exiftool_path)
    
    # 1. Prepare a "Virtual Roll" of 36 frames (by duplicating existing test files)
    base_files = ["1.jpg", "test_data/1.jpg", "66.jpg", "67_L.jpg"]
    base_files = [str(Path(f).absolute()) for f in base_files if os.path.exists(f)]
    
    if not base_files:
        print("Error: No test images found. Please check paths.")
        return
        
    # Duplicate until we have 36 files to simulate a real-world roll
    test_roll = (base_files * 10)[:36]
    print(f"Simulating processing for 1 roll ({len(test_roll)} frames)...")
    
    # --- V1.0 Test ---
    print("\n[V1.0 Strategy: Loop-based subprocesses]")
    print("Processing...")
    v1_0_time = measure_classic_v1_0(exiftool_path, test_roll)
    print(f"v1.0 Time: {v1_0_time:.2f} seconds")
    
    # --- V1.1 Test ---
    print("\n[V1.1 Strategy: Argfile Batching]")
    print("Processing...")
    v1_1_time = measure_argfile_v1_1(worker, test_roll)
    print(f"v1.1 Time: {v1_1_time:.2f} seconds")
    
    # --- Results ---
    improvement = ((v1_0_time - v1_1_time) / v1_0_time) * 100
    speedup = v1_0_time / v1_1_time
    
    print("\n====================================================")
    print("FINAL RESULT")
    print("====================================================")
    print(f"Speedup Factor: {speedup:.1f}x faster")
    print(f"Time Saved: {v1_0_time - v1_1_time:.2f}s ({improvement:.1f}%)")
    print("====================================================")

if __name__ == "__main__":
    run_benchmark()
