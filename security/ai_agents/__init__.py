# -*- coding: utf-8 -*-
"""
Package marker for security.ai_agents.

Содержит коллекцию AI-агентов, которые подключаются к Safe Function Manager.
"""

from .fake_documents_agent import FakeDocumentsAgent  # noqa: F401
from .fake_news_detection_agent import FakeNewsDetectionAgent  # noqa: F401
from .grooming_detection_agent import GroomingDetectionAgent  # noqa: F401
from .online_predators_agent import OnlinePredatorsAgent  # noqa: F401
from .self_harm_detection_agent import SelfHarmDetectionAgent  # noqa: F401
from .dark_web_monitoring_agent import DarkWebMonitoringAgent  # noqa: F401
from .russian_identity_theft_protection_agent import (  # noqa: F401
    RussianIdentityTheftProtectionAgent,
    FraudRecord,
    IdentityTheftAlert
)
from .threat_monitoring_interface import (  # noqa: F401
    ThreatMonitoringInterface,
    ThreatEvent,
    ThreatEventBus,
    get_threat_event_bus
)

__all__ = [
    "FakeDocumentsAgent",
    "FakeNewsDetectionAgent",
    "GroomingDetectionAgent",
    "OnlinePredatorsAgent",
    "SelfHarmDetectionAgent",
    "DarkWebMonitoringAgent",
    "RussianIdentityTheftProtectionAgent",
    "FraudRecord",
    "IdentityTheftAlert",
    "CreditReport",
    "CreditChange",
    "ThreatMonitoringInterface",
    "ThreatEvent",
    "ThreatEventBus",
    "get_threat_event_bus",
]
