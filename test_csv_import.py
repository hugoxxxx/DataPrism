#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for CSV import functionality
CSV 导入功能测试脚本
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.csv_parser import CSVParser
from src.core.csv_converter import CSVConverter

def test_csv_parser():
    """Test CSV parser"""
    print("=" * 60)
    print("Testing CSV Parser")
    print("=" * 60)
    
    csv_file = "assets/新建 文本文档.txt"
    
    parser = CSVParser(csv_file)
    headers, rows = parser.parse()
    
    print(f"\n✅ Detected delimiter: '{parser.delimiter}'")
    print(f"✅ Headers: {headers}")
    print(f"✅ Total rows: {len(rows)}")
    print(f"\nFirst 3 rows:")
    for i, row in enumerate(rows[:3], 1):
        print(f"  Row {i}: {row}")

def test_gps_conversion():
    """Test GPS coordinate conversion"""
    print("\n" + "=" * 60)
    print("Testing GPS Conversion")
    print("=" * 60)
    
    # Test data
    test_cases = [
        (31.14364765909477, 'lat', 'N', "31°08'37\"N"),
        (121.4088641324521, 'lon', 'E', "121°24'32\"E"),
        (-33.8688, 'lat', 'S', "33°52'08\"S"),
        (-74.0060, 'lon', 'W', "74°00'22\"W"),
    ]
    
    for decimal, coord_type, direction, expected in test_cases:
        result = CSVConverter._decimal_to_dms_display(decimal, coord_type, direction)
        print(f"\n  {decimal} ({direction}) → {result}")
        
        # ExifTool format
        exif_result = CSVConverter.decimal_to_dms_exif(decimal, direction)
        print(f"  ExifTool format: {exif_result}")

def test_datetime_conversion():
    """Test datetime conversion"""
    print("\n" + "=" * 60)
    print("Testing DateTime Conversion")
    print("=" * 60)
    
    test_cases = [
        "2026-01-23 17:51:48",
        "2026/01/23 17:51:48",
        "2026.01.23 17:51:48",
    ]
    
    for dt_str in test_cases:
        result = CSVConverter._convert_datetime(dt_str)
        print(f"  {dt_str} → {result}")

if __name__ == "__main__":
    test_csv_parser()
    test_gps_conversion()
    test_datetime_conversion()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
