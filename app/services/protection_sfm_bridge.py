"""Wire protection category enable/disable to SFM agents via :8003."""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

SFM_EXECUTE_URL = "http://127.0.0.1:8003/api/execute"

# Category → SFM function ids (W09 / sfm-06)
CATEGORY_AGENT_FUNCTIONS: Dict[str, List[str]] = {
    "cyberThreats": [
        "malware_protection",
        "phishing_protection_agent",
        "threat_detection_agent",
    ],
    "fraud": ["anti_fraud_master_ai", "security_useridentity"],
    "childThreats": ["parental_control_agent", "child_protection_agent"],
    "dataLeaks": ["data_cleanup_agent", "dark_web_monitoring_agent"],
    "deepfakes": [
        "fake_news_detection_agent",
        "ai_agent_deepfakeprotectionsystem",
        "audio_deepfake_detection",
    ],
    "internetThreats": [
        "network_security_agent",
        "phishing_protection_agent",
    ],
    "mobileThreats": ["mobile_security_agent", "malware_protection"],
    "familyThreats": ["family_protection_agent", "parental_control_agent"],
    "iotThreats": ["iot_security_agent", "smart_home_security_agent"],
}


def _sfm_execute(function_id: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = json.dumps({"function": function_id, "params": params or {}}).encode("utf-8")
    request = urllib.request.Request(
        SFM_EXECUTE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"success": False, "error": body or str(exc)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def activate_agents_for_category(category_id: str) -> Dict[str, Any]:
    agents = CATEGORY_AGENT_FUNCTIONS.get(category_id, [])
    results: List[Dict[str, Any]] = []
    for function_id in agents:
        outcome = _sfm_execute(
            function_id,
            {"action": "activate", "categoryId": category_id},
        )
        results.append(
            {
                "function": function_id,
                "success": bool(outcome.get("success")),
                "error": outcome.get("error"),
            }
        )
        logger.info(
            "protection_sfm_activate category=%s function=%s success=%s",
            category_id,
            function_id,
            outcome.get("success"),
        )
    return {"categoryId": category_id, "agents": results, "activated_count": len(agents)}


def deactivate_agents_for_category(category_id: str) -> Dict[str, Any]:
    agents = CATEGORY_AGENT_FUNCTIONS.get(category_id, [])
    results: List[Dict[str, Any]] = []
    for function_id in agents:
        outcome = _sfm_execute(
            function_id,
            {"action": "deactivate", "categoryId": category_id},
        )
        results.append(
            {
                "function": function_id,
                "success": bool(outcome.get("success")),
                "error": outcome.get("error"),
            }
        )
    return {"categoryId": category_id, "agents": results, "deactivated_count": len(agents)}
