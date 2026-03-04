# -*- coding: utf-8 -*-
"""
Package marker for security.ai_agents.

Содержит коллекцию AI-агентов, которые подключаются к Safe Function Manager.
"""

try:
    from .fake_documents_agent import FakeDocumentsAgent  # noqa: F401
except ImportError:
    pass  # cv2 не установлен, пропускаем
try:
    from .fake_news_detection_agent import FakeNewsDetectionAgent  # noqa: F401
except ImportError:
    pass  # Зависимости не установлены
try:
    from .grooming_detection_agent import GroomingDetectionAgent  # noqa: F401
except ImportError:
    pass  # Зависимости не установлены
try:
    from .online_predators_agent import OnlinePredatorsAgent  # noqa: F401
except ImportError:
    pass  # Зависимости не установлены
try:
    from .self_harm_detection_agent import SelfHarmDetectionAgent  # noqa: F401
except ImportError:
    pass  # Зависимости не установлены

__all__ = [
    "FakeDocumentsAgent",
    "FakeNewsDetectionAgent",
    "GroomingDetectionAgent",
    "OnlinePredatorsAgent",
    "SelfHarmDetectionAgent",
]

