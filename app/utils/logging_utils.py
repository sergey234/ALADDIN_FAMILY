# -*- coding: utf-8 -*-
"""
Утилита для настройки централизованного логирования
"""
import json
import logging
import logging.config
from pathlib import Path

def setup_logging(config_path="/opt/aladdin-backend/logging_config.json"):
    """Настроить логирование из JSON конфигурации"""
    if Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        # Fallback к базовому логированию
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

def get_logger(name):
    """Получить logger с правильным именем"""
    return logging.getLogger(name)

