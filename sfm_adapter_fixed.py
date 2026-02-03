#!/usr/bin/env python3
"""
SFM Adapter - Исправленная версия с HTTP API
"""

import sys
import os
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import requests

# Backend path for SFM imports
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Add security module path
security_path = "/opt/aladdin-backend/security"
if security_path not in sys.path:
    sys.path.insert(0, security_path)

# Import complete function mapping
try:
    from complete_api_sfm_mapping import get_sfm_function_name, API_TO_SFM_MAPPING
    print(f"Complete function mapping loaded: {len(API_TO_SFM_MAPPING)} functions")
except ImportError as e:
    print(f"Warning: Complete mapping not available: {e}")
    # Fallback to basic mapping
    API_TO_SFM_MAPPING = {}
    def get_sfm_function_name(func_name):
        return func_name  # fallback to original name

class SFMAdapter:
    """
    Optimized Adapter for Safe Function Manager integration
    """

    def __init__(self):
        self.available = False
        self.metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'fallback_calls': 0,
            'avg_response_time': 0
        }

    def execute_function(self, func_name: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any, Optional[str]]:
        """
        Execute function through SFM HTTP API (простая версия)
        """
        self.metrics['total_calls'] += 1
        params = params or {}

        try:
            # Get the correct SFM function name
            sfm_function_name = get_sfm_function_name(func_name)

            # Вызываем SFM HTTP API
            response = requests.post(
                'http://127.0.0.1:8003/api/execute',
                json={'function': sfm_function_name, 'params': params},
                headers={'Content-Type': 'application/json'},
                timeout=5.0
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.metrics['successful_calls'] += 1
                    self.available = True  # SFM работает!
                    return True, data['result'], None
                else:
                    raise Exception(f"SFM error: {data.get('error', 'Unknown')}")

            # Fallback
            result = self._execute_mock_function(func_name, params)
            self.metrics['fallback_calls'] += 1
            return True, result, f"HTTP {response.status_code}"

        except Exception as e:
            # Fallback
            try:
                result = self._execute_mock_function(func_name, params)
                self.metrics['fallback_calls'] += 1
                return True, result, f"SFM failed: {str(e)}"
            except Exception as fallback_error:
                self.metrics['failed_calls'] += 1
                return False, None, f"All failed: {str(e)}, {str(fallback_error)}"

    def _execute_mock_function(self, func_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock function for fallback"""
        mock_responses = {
            "get_phishing_sensitivity": {"level": "medium", "source": "mock"},
            "get_analytics_overview": {"total_threats": 0, "source": "mock"},
            "get_components_health": {"status": "good", "source": "mock"},
        }
        return mock_responses.get(func_name, {"error": f"Unknown function: {func_name}", "source": "mock"})

    def get_metrics(self) -> Dict[str, Any]:
        """Get adapter metrics"""
        return {
            **self.metrics,
            "sfm_available": self.available,
            "timestamp": datetime.utcnow().isoformat()
        }

    def health_check(self) -> Dict[str, Any]:
        """Enhanced health check"""
        return {
            "status": "ok" if self.available else "fallback",
            "sfm_adapter": "available" if self.available else "fallback",
            "endpoints": 101,
            "groups": ["components", "security", "monitoring", "protection", "system"],
            "metrics": self.get_metrics()
        }

# Global instance
sfm_adapter = SFMAdapter()