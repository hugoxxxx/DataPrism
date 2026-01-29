import os
import sys
import time
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from src.core.exif_worker import ExifToolWorker
from src.core.config import get_config

def test_argfile_optimization():
    print("Starting Performance Optimization Test (v1.1 Argfile Pattern)...")
    
    cfg = get_config()
    exiftool_path = cfg.get('exiftool_path', 'exiftool')
    
    worker = ExifToolWorker(exiftool_path)
    
    # Use real file paths found in the project / 使用项目中发现的实际路径
    test_files = ["1.jpg", "test_data/1.jpg", "66.jpg", "67_L.jpg"]
    test_files = [str(Path(f).absolute()) for f in test_files if os.path.exists(f)]
    
    if not test_files:
        print("No test images found (1.jpg, test_data/1.jpg, etc.). Please ensure some images exist for testing.")
        return

    print(f"Testing Batch Read with {len(test_files)} files...")
    start_time = time.time()
    
    # Mocking the signal connection to avoid Qt event loop issues in a script
    read_results = {}
    def on_read_finished(results):
        nonlocal read_results
        read_results = results
        print(f"Batch Read logic finished. Results: {len(results)} files.")

    worker.read_finished.connect(on_read_finished)
    
    # Run the logic
    worker.read_exif(test_files)
    
    duration = time.time() - start_time
    print(f"Read operation logic duration: {duration:.4f}s")
    
    # Verify write
    print("\nTesting Batch Write (Argfile Mode)...")
    write_tasks = []
    for f in test_files:
        write_tasks.append({
            "file_path": f,
            "exif_data": {
                "Artist": "DataPrism v1.1 Tester",
                "Copyright": "ExifTool Argfile Test"
            }
        })
        
    start_time = time.time()
    
    def on_write_finished(results):
        print(f"Batch Write logic finished. {results.get('success', 0)}/{results.get('total', 0)} succeeded.")

    worker.write_finished.connect(on_write_finished)
    worker.batch_write_exif(write_tasks)
    
    duration = time.time() - start_time
    print(f"Write operation logic duration: {duration:.4f}s")
    
    print("\nVerification logic finished. Check logs for details.")

if __name__ == "__main__":
    test_argfile_optimization()
