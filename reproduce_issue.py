
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

import src.utils.gps_utils as gps_utils

# Test user case
print("--- Testing 'Ugly' String Parsing ---")
lat_raw = '28deg 31\' 30.59" N North'
lon_raw = '119deg 30\' 30.44" E East'
# Simulate what happens in photo_model.py
formatted = gps_utils.format_gps_pair(lat_raw, None, lon_raw, None)
print(f"Input: Lat='{lat_raw}', Lon='{lon_raw}'")
print(f"Result: {formatted}")

assert formatted == "28°31'30.59\"N, 119°30'30.44\"E"

print("\n--- Testing Clean String Parsing ---")
# Test clean case
clean_lat = '28deg 31\' 30.59" N'
clean_lon = '119deg 30\' 30.44" E'
formatted_clean = gps_utils.format_gps_pair(clean_lat, None, clean_lon, None)
print(f"Input: Lat='{clean_lat}', Lon='{clean_lon}'")
print(f"Result: {formatted_clean}")
assert formatted_clean == "28°31'30.59\"N, 119°30'30.44\"E"

print("\n--- Testing parse_location_string ---")
ugly_full = "28deg 31' 30.59\" N North, 119deg 30' 30.44\" E East"
parsed = gps_utils.parse_location_string(ugly_full)
print(f"Input: '{ugly_full}'")
print(f"Result: {parsed}")
assert parsed == "28°31'30.59\"N, 119°30'30.44\"E"

print("\nSUCCESS: All tests passed.")
