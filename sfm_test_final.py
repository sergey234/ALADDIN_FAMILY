import sys
import os
sys.path.insert(0, '/opt/aladdin-backend')

# Suppress logs  
import logging
logging.getLogger().setLevel(logging.CRITICAL)

try:
    from security.sfm_singleton import get_sfm
    sfm = get_sfm()
    print("SUCCESS: SFM loaded")
    print(f"Functions: {len(sfm.functions)}")
    print(f"Status: {sfm.status}")
    
except Exception as e:
    print(f"ERROR: {e}")
