#!/usr/bin/env python3
"""
SFM Singleton using original SafeFunctionManager
"""

import sys
import os
import time
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime

# SFM Singleton instance
_sfm_instance = None
_sfm_lock = threading.Lock()

# Try to import original SFM
try:
    from security.safe_function_manager import SafeFunctionManager
    ORIGINAL_SFM_AVAILABLE = True
except ImportError as e:
    print(f"Original SFM not available: {e}")
    ORIGINAL_SFM_AVAILABLE = False
    SafeFunctionManager = None

class OptimizedSFM:
    def __init__(self):
        self.version = "3.0.0-original"
        self._sfm = None

        if ORIGINAL_SFM_AVAILABLE and SafeFunctionManager:
            try:
                print("🔄 Initializing original SafeFunctionManager...")
                self._sfm = SafeFunctionManager()
                print(f"✅ Original SFM initialized with {len(self._sfm.functions)} functions")
            except Exception as e:
                print(f"❌ Failed to initialize original SFM: {e}")
                self._sfm = None
        else:
            print("⚠️ Original SFM not available, using mock functions")
            self._sfm = None

        print(f"🚀 SFM {self.version} initialized")

    @property
    def functions(self):
        """Get functions dictionary for compatibility"""
        if self._sfm and hasattr(self._sfm, 'functions'):
            return self._sfm.functions
        return {}

    def execute_function(self, func_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute function using original SFM
        """
        params = params or {}

        if self._sfm:
            # Use original SFM
            try:
                result = self._sfm.execute_function(func_name, params)
                return result
            except Exception as e:
                print(f"SFM execution error: {e}")
                return {"error": str(e), "function": func_name, "source": "sfm_error"}

        # Fallback - return mock
        return {
            "function": func_name,
            "params": params,
            "result": "mock_fallback",
            "timestamp": datetime.utcnow().isoformat(),
            "source": "sfm_mock",
            "version": self.version
        }

    def get_status(self) -> Dict[str, Any]:
        """Get SFM status"""
        return {
            "version": self.version,
            "original_sfm_available": self._sfm is not None,
            "functions_count": len(self.functions),
            "timestamp": datetime.utcnow().isoformat()
        }

def get_sfm() -> OptimizedSFM:
    """
    Get SFM singleton instance
    """
    global _sfm_instance

    if _sfm_instance is None:
        with _sfm_lock:
            if _sfm_instance is None:
                start_time = time.time()
                _sfm_instance = OptimizedSFM()
                init_time = time.time() - start_time
                print(f"🚀 SFM singleton initialized in {init_time:.2f} seconds")

    return _sfm_instance

# For compatibility
sfm = get_sfm()