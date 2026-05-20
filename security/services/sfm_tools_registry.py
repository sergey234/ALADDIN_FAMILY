# -*- coding: utf-8 -*-
"""Registry of SFM tools for Hermes h2 + Capability Contract."""

from typing import Dict, List

SFM_TOOLS_H2: List[Dict[str, str]] = [
    {"name": "get_analytics_overview", "intent": "threats_summary", "description": "Threat/analytics aggregates"},
    {"name": "get_components_health", "intent": "protection_status", "description": "Protection components health"},
    {"name": "get_phishing_sensitivity", "intent": "threats_summary", "description": "Phishing block stats"},
    {"name": "get_protection_status", "intent": "protection_status", "description": "Alias: overall protection status"},
    {"name": "ai_assistant_chat", "intent": "general", "description": "Chat with SFM context"},
    {"name": "ai_assistant_analyze_threat", "intent": "incident_analyze", "description": "Analyze URL/threat"},
    {"name": "ai_assistant_recommendations", "intent": "recommendations", "description": "Personal security tips"},
    {"name": "ai_assistant_capabilities", "intent": "capabilities_list", "description": "AI feature list"},
    {"name": "ai_assistant_feedback", "intent": "feedback", "description": "Record user feedback"},
    {"name": "ai_assistant_security_tips", "intent": "security_tips", "description": "Daily security tips"},
    {"name": "ai_assistant_report_incident", "intent": "report_incident", "description": "Register incident"},
    {"name": "family_members_summary", "intent": "family_overview", "description": "Family slot aggregates (no PII names)"},
]

TOOL_NAMES = [t["name"] for t in SFM_TOOLS_H2]
