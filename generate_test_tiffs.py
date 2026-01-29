import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QColor

def generate_noise_tiff(app, path, width, height):
    print(f"Generating {path} ({width}x{height})...")
    
    image = QImage(width, height, QImage.Format_RGB32)
    image.fill(QColor("#1a1a1a"))
    
    if image.save(path, "TIFF"):
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"Successfully saved {path} ({size_mb:.2f} MB)")
    else:
        print(f"Failed to save {path}")

if __name__ == "__main__":
    test_dir = "test_large_tiff"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        
    app = QApplication(sys.argv)
    
    # We already have the 200MB one, but let's redo a HUGE one
    generate_noise_tiff(app, os.path.join(test_dir, "test_500mb.tiff"), 12000, 12000)
    
    app.quit()
