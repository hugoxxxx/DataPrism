import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.core.metadata_parser import MetadataParser

def test_gps_parsing_variants():
    test_json = {
        "pictures": [
            {
                "frame_number": 1,
                "camera": {"name": "Test Camera"},
                "location": "51.5074; -0.1278",  # Film Logbook coordinate style
                "notes": "Coordinate string test"
            },
            {
                "frame_number": 2,
                "camera": {"name": "Test Camera"},
                "location": "Paris, France",    # Human readable style
                "notes": "Human readable test"
            },
            {
                "frame_number": 3,
                "camera": {"name": "Test Camera"},
                "GPSLatitude": 35.6895,         # EXIF numeric style
                "GPSLongitude": 139.6917,
                "GPSLatitudeRef": "N",
                "GPSLongitudeRef": "E",
                "notes": "Standard EXIF style"
            }
        ]
    }
    
    with open("test_gps.json", "w") as f:
        json.dump(test_json, f)
        
    parser = MetadataParser()
    entries = parser.parse_file("test_gps.json")
    
    print(f"Parsed {len(entries)} entries.")
    for i, entry in enumerate(entries):
        print(f"Entry {i+1} ({entry.notes}):")
        print(f"  Location: {entry.location}")
        
    os.remove("test_gps.json")

if __name__ == "__main__":
    test_gps_parsing_variants()
