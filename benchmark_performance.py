import os
import sys
import time
import subprocess
import json
import shutil
from pathlib import Path
import tempfile

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
    worker.read_exif(file_paths)
    return time.time() - start_time

def measure_write_v1_0(exiftool_path, tasks):
    """Simulate v1.0: Launching exiftool for every single file to write"""
    start_time = time.time()
    for t in tasks:
        file_path = t['file_path']
        exif_data = t['exif_data']
        cmd = [exiftool_path, "-overwrite_original", "-P"]
        for tag, val in exif_data.items():
            cmd.append(f"-{tag}={val}")
        cmd.append(file_path)
        subprocess.run(cmd, capture_output=True, creationflags=0x08000000)
    return time.time() - start_time

def measure_write_v1_1(worker, tasks):
    """Measure v1.1: Using Parallel Argfile writing"""
    start_time = time.time()
    results = {}
    done = False
    def on_write_finished(res):
        nonlocal results, done
        results = res
        done = True

    worker.write_finished.connect(on_write_finished)
    worker.batch_write_exif(tasks)
    
    # Wait for completion (since it's async in QThread)
    # In a script we might need a small loop if we don't have a Qt loop
    timeout = 60
    start_wait = time.time()
    while not done and time.time() - start_wait < timeout:
        time.sleep(0.1)
        
    return time.time() - start_time

def prepare_test_data(count=100):
    """Create unique copies of test images to avoid parallel collisions"""
    base_files = ["1.jpg", "test_data/1.jpg", "66.jpg", "67_L.jpg"]
    base_files = [str(Path(f).absolute()) for f in base_files if os.path.exists(f)]
    
    if not base_files:
        return None, []
        
    temp_dir = tempfile.mkdtemp(prefix="dp_bench_")
    bench_files = []
    for i in range(count):
        src = base_files[i % len(base_files)]
        dst = os.path.join(temp_dir, f"test_{i:03d}.jpg")
        shutil.copy2(src, dst)
        bench_files.append(dst)
    return temp_dir, bench_files

def run_benchmark():
    print("====================================================")
    print("DataPrism Performance Benchmark: v1.0 vs v1.1 PRO")
    print("====================================================")
    
    temp_dir, test_roll = prepare_test_data(100)
    if not test_roll:
        print("Error: No test images found. Please check paths.")
        return
        
    try:
        cfg = get_config()
        exiftool_path = cfg.get('exiftool_path', 'exiftool')
        worker = ExifToolWorker(exiftool_path)
        
        print(f"Simulating processing for 100 UNIQUE frames...")
        
        # --- READ PERFORMANCE ---
        print("\n[PART 1: READING]")
        print("Simulating v1.0 Reading...")
        read_v1_0 = measure_classic_v1_0(exiftool_path, test_roll)
        print(f"v1.0 Read Time: {read_v1_0:.2f}s")
        
        print("Simulating v1.1 Reading (Argfile + fast2)...")
        read_v1_1 = measure_argfile_v1_1(worker, test_roll)
        print(f"v1.1 Read Time: {read_v1_1:.2f}s")
        
        # --- WRITE PERFORMANCE ---
        print("\n[PART 2: WRITING]")
        write_tasks = [{"file_path": f, "exif_data": {"Artist": "DP Benchmark", "Copyright": "2026"}} for f in test_roll]
        
        print("Simulating v1.0 Writing...")
        write_v1_0 = measure_write_v1_0(exiftool_path, write_tasks)
        print(f"v1.0 Write Time: {write_v1_0:.2f}s")
        
        print("Simulating v1.1 Writing (Parallel Argfiles)...")
        write_v1_1 = measure_write_v1_1(worker, write_tasks)
        print(f"v1.1 Write Time: {write_v1_1:.2f}s")
        
        # --- Summary ---
        total_v1_0 = read_v1_0 + write_v1_0
        total_v1_1 = read_v1_1 + write_v1_1
        
        print("\n====================================================")
        print("FINAL COMPARISON (100 Photos)")
        print("====================================================")
        print(f"v1.0 Total Time: {total_v1_0:.2f}s")
        print(f"v1.1 Total Time: {total_v1_1:.2f}s")
        print(f"Speedup: {total_v1_0 / total_v1_1:.1f}x faster")
        print(f"Total Time Saved: {total_v1_0 - total_v1_1:.2f}s")
        print("====================================================")
        
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    run_benchmark()
