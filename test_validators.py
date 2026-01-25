#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for validators
验证器测试脚本
"""

from src.utils.validators import MetadataValidator


def test_validators():
    """Test all validators / 测试所有验证器"""
    
    print("=" * 60)
    print("Testing MetadataValidator")
    print("=" * 60)
    
    # Test aperture / 测试光圈
    print("\n1. Testing aperture validation:")
    test_cases = [
        ("f/4", True),
        ("4", True),
        ("F2.8", True),
        ("0.95", True),
        ("100", False),  # Out of range
        ("abc", False),  # Invalid
    ]
    
    for value, should_pass in test_cases:
        try:
            result = MetadataValidator.validate_aperture(value)
            print(f"  ✓ '{value}' -> '{result}'" if should_pass else f"  ✗ '{value}' should have failed but got '{result}'")
        except ValueError as e:
            print(f"  ✓ '{value}' -> Error: {e}" if not should_pass else f"  ✗ '{value}' failed: {e}")
    
    # Test shutter speed / 测试快门
    print("\n2. Testing shutter speed validation:")
    test_cases = [
        ("1/125", True),
        ("1/60s", True),
        ("2", True),
        ("0.5", True),
        ("abc", False),
        ("1/0", False),  # Division by zero
    ]
    
    for value, should_pass in test_cases:
        try:
            result = MetadataValidator.validate_shutter_speed(value)
            print(f"  ✓ '{value}' -> '{result}'" if should_pass else f"  ✗ '{value}' should have failed but got '{result}'")
        except ValueError as e:
            print(f"  ✓ '{value}' -> Error: {e}" if not should_pass else f"  ✗ '{value}' failed: {e}")
    
    # Test ISO / 测试 ISO
    print("\n3. Testing ISO validation:")
    test_cases = [
        ("400", True),
        ("100", True),
        ("409600", True),
        ("500000", False),  # Out of range
        ("abc", False),
    ]
    
    for value, should_pass in test_cases:
        try:
            result = MetadataValidator.validate_iso(value)
            print(f"  ✓ '{value}' -> {result}" if should_pass else f"  ✗ '{value}' should have failed but got {result}")
        except ValueError as e:
            print(f"  ✓ '{value}' -> Error: {e}" if not should_pass else f"  ✗ '{value}' failed: {e}")
    
    # Test focal length / 测试焦距
    print("\n4. Testing focal length validation:")
    test_cases = [
        ("80mm", True),
        ("50", True),
        ("200mm", True),
        ("3000", False),  # Out of range
        ("abc", False),
    ]
    
    for value, should_pass in test_cases:
        try:
            result = MetadataValidator.validate_focal_length(value)
            print(f"  ✓ '{value}' -> '{result}'" if should_pass else f"  ✗ '{value}' should have failed but got '{result}'")
        except ValueError as e:
            print(f"  ✓ '{value}' -> Error: {e}" if not should_pass else f"  ✗ '{value}' failed: {e}")
    
    # Test datetime / 测试日期时间
    print("\n5. Testing datetime validation:")
    test_cases = [
        ("2026:01:24 22:00:00", True),
        ("2020:12:31 23:59:59", True),
        ("2026-01-24 22:00:00", False),  # Wrong format
        ("2026:13:01 00:00:00", False),  # Invalid month
        ("abc", False),
    ]
    
    for value, should_pass in test_cases:
        try:
            result = MetadataValidator.validate_datetime(value)
            print(f"  ✓ '{value}' -> '{result}'" if should_pass else f"  ✗ '{value}' should have failed but got '{result}'")
        except ValueError as e:
            print(f"  ✓ '{value}' -> Error: {e}" if not should_pass else f"  ✗ '{value}' failed: {e}")
    
    print("\n" + "=" * 60)
    print("Validator tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_validators()
