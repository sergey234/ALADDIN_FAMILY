# -*- coding: utf-8 -*-
"""Static AI capabilities manifest (Capability Contract fallback)."""

from typing import Any, Dict, List


def static_capabilities_payload() -> Dict[str, Any]:
    features: List[str] = [
        "Статус защиты и компонентов (SFM)",
        "Статистика угроз за период",
        "Проверка подозрительных ссылок и фишинга",
        "Семья и родительский контроль (справка)",
        "VPN и защита сети",
        "Тарифы и функции Premium",
        "E2EE семейный чат (только iOS)",
        "Персональные рекомендации по безопасности",
        "Обратная связь по ответам AI",
    ]
    return {
        "features": features,
        "languages": ["Русский", "English"],
        "response_time": "зависит от нагрузки",
        "accuracy": "на основе данных SFM",
    }
