import sys
import os
sys.path.append(os.getcwd())

from src.core.metadata_parser import MetadataParser

def test_hasselblad_parsing():
    parser = MetadataParser()
    # Check if assets/1.json exists
    json_path = "d:/Projects/DataPrism/assets/1.json"
    if os.path.exists(json_path):
        entries = parser.parse_file(json_path)
        if entries:
            first = entries[0]
            print(f"File: {json_path}")
            print(f"C-Make: {first.camera_make}")
            print(f"C-Model: {first.camera_model}")
            print(f"L-Make: {first.lens_make}")
            print(f"L-Model: {first.lens_model}")
            
            if first.camera_make == "Hasselblad" and first.camera_model == "500C/M":
                print("✅ Camera make and model correctly split!")
            else:
                print(f"❌ Camera split failed. Got: C-Make={first.camera_make}, C-Model={first.camera_model}")
                
            if first.lens_make == "Carl Zeiss" and "Planar" in str(first.lens_model):
                print("✅ Lens make and model correctly split!")
            else:
                print(f"❌ Lens split failed. Got: L-Make={first.lens_make}, L-Model={first.lens_model}")
    else:
        print(f"File {json_path} not found.")

if __name__ == "__main__":
    test_hasselblad_parsing()
