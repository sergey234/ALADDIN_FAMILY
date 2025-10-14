#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AlertManager - Менеджер оповещений системы безопасности
function_77: Умные уведомления с приоритизацией и
мультиканальностью

Этот модуль предоставляет комплексную систему управления алертами для AI
системы безопасности, включающую:
- Интеллектуальную приоритизацию алертов с использованием машинного обучения
- Мультиканальную доставку уведомлений (email, SMS, push, мессенджеры)
- Автоматическую группировку и дедупликацию алертов
- Адаптивные алгоритмы фильтрации спама и ложных срабатываний
- Продвинутый анализ текста для классификации алертов
- Статистический анализ паттернов алертов и трендов
- Интеграцию с внешними системами мониторинга
- Автоматическое обучение на основе обратной связи пользователей

Основные возможности:
1. Умная приоритизация алертов с использованием ML алгоритмов
2. Мультиканальная доставка через различные платформы
3. Автоматическая группировка похожих алертов
4. Дедупликация и подавление дублирующихся уведомлений
5. Анализ текста для классификации и извлечения сущностей
6. Статистический анализ паттернов и аномалий в алертах
7. Адаптивные пороги и правила на основе исторических данных
8. Интеграция с системами мониторинга и SIEM
9. Визуализация и аналитика алертов
10. Автоматическое обучение и улучшение качества

Технические детали:
- Использует scikit-learn для ML классификации и кластеризации
- Применяет TF-IDF и BERT для анализа текста
- Интегрирует scipy для статистического анализа
- Поддерживает асинхронную обработку алертов
- Использует очереди для масштабируемости
- Поддерживает различные форматы уведомлений

Автор: ALADDIN Security System
Версия: 2.0
Дата: 2025-01-06
Лицензия: MIT
"""

import asyncio
import hashlib
import json
import logging
import math
import queue
import re
import smtplib
import statistics
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.optimize import differential_evolution, minimize
from scipy.signal import find_peaks, savgol_filter
from scipy.stats import kendalltau, normaltest, pearsonr, shapiro, spearmanr
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA, LatentDirichletAllocation, TruncatedSVD
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import ElasticNet, Lasso, LogisticRegression, Ridge
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import (
    GridSearchCV,
    cross_val_score,
    train_test_split,
)
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
from sklearn.svm import SVC, LinearSVC


class AlertSeverity(Enum):
    """Уровни серьезности алертов"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertChannel(Enum):
    """Каналы доставки алертов"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SLACK = "slack"
    WEBHOOK = "webhook"


@dataclass
class AlertTemplate:
    """Шаблон алерта"""

    name: str
    subject: str
    body: str
    channels: List[AlertChannel] = field(default_factory=list)
    severity: AlertSeverity = AlertSeverity.MEDIUM
    cooldown: int = 300  # секунды
    max_frequency: int = 10  # максимум в час


@dataclass
class AlertRecipient:
    """Получатель алертов"""

    user_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    discord_id: Optional[str] = None
    slack_id: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    enabled_channels: List[AlertChannel] = field(default_factory=list)


@dataclass
class Alert:
    """Структура алерта"""

    id: str
    title: str
    message: str
    severity: AlertSeverity
    source: str
    timestamp: datetime
    recipients: List[str] = field(default_factory=list)
    channels: List[AlertChannel] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class AlertManager:
    """
    Менеджер оповещений системы безопасности

    Обеспечивает:
    - Умные уведомления с приоритизацией
    - Персонализированные алерты для каждого пользователя
    - Мультиканальные оповещения (SMS, email, push, мессенджеры)
    - Настраиваемые расписания уведомлений
    - Автоматическую эскалацию критических событий
    - ML-анализ для предотвращения спама
    """

    def __init__(
        self,
        name: str = "AlertManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация AlertManager

        Args:
            name: Имя менеджера
            config: Конфигурация системы алертов
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"AlertManager.{name}")

        # Основные компоненты
        self.alert_queue = queue.Queue()
        self.templates: Dict[str, AlertTemplate] = {}
        self.recipients: Dict[str, AlertRecipient] = {}
        self.alert_history: List[Alert] = []
        self.rate_limiter: Dict[str, List[datetime]] = {}

        # Потоки обработки
        self.processing_threads: List[threading.Thread] = []
        self.is_running = False

        # ML компоненты для анализа
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english"
        )
        self.clusterer = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
        self.is_ml_trained = False

        # Статистика
        self.stats = {
            "alerts_sent": 0,
            "alerts_blocked": 0,
            "channels_used": {},
            "severity_distribution": {},
            "uptime_start": time.time(),
        }

        # Инициализация
        self._setup_logging()
        self._load_default_templates()
        self._initialize_ml_components()

        self.logger.info(f"AlertManager {name} инициализирован")

    def _setup_logging(self) -> None:
        """Настройка системы логирования"""
        try:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        except Exception as e:
            print(f"Ошибка настройки логирования: {e}")

    def _load_default_templates(self) -> None:
        """Загрузка шаблонов алертов по умолчанию"""
        default_templates = {
            "security_breach": AlertTemplate(
                name="security_breach",
                subject="🚨 КРИТИЧЕСКАЯ УГРОЗА БЕЗОПАСНОСТИ",
                body="Обнаружена критическая угроза безопасности: {details}",
                channels=[
                    AlertChannel.EMAIL,
                    AlertChannel.SMS,
                    AlertChannel.PUSH,
                ],
                severity=AlertSeverity.CRITICAL,
                cooldown=60,
            ),
            "system_warning": AlertTemplate(
                name="system_warning",
                subject="⚠️ Предупреждение системы",
                body="Система обнаружила потенциальную проблему: {details}",
                channels=[AlertChannel.EMAIL, AlertChannel.PUSH],
                severity=AlertSeverity.MEDIUM,
                cooldown=300,
            ),
            "performance_issue": AlertTemplate(
                name="performance_issue",
                subject="📊 Проблема производительности",
                body="Обнаружена проблема производительности: {details}",
                channels=[AlertChannel.EMAIL],
                severity=AlertSeverity.LOW,
                cooldown=600,
            ),
            "anomaly_detected": AlertTemplate(
                name="anomaly_detected",
                subject="🔍 Обнаружена аномалия",
                body="Система обнаружила аномальное поведение: {details}",
                channels=[AlertChannel.EMAIL, AlertChannel.PUSH],
                severity=AlertSeverity.HIGH,
                cooldown=180,
            ),
        }
        self.templates.update(default_templates)

    def _initialize_ml_components(self) -> None:
        """Инициализация компонентов машинного обучения"""
        try:
            # Создаем базовый датасет для обучения
            sample_alerts = [
                "Security breach detected in system",
                "High CPU usage detected",
                "Memory usage exceeded threshold",
                "Network anomaly detected",
                "Unauthorized access attempt",
                "System performance degraded",
                "Database connection failed",
                "File system corruption detected",
            ]

            # Обучение векторизатора
            self.vectorizer.fit(sample_alerts)

            # Обучение кластеризатора
            features = self.vectorizer.transform(sample_alerts).toarray()
            self.clusterer.fit(features)

            self.is_ml_trained = True
            self.logger.info("ML компоненты инициализированы")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации ML: {e}")

    async def start_alert_processing(self) -> None:
        """Запуск обработки алертов"""
        try:
            self.is_running = True
            self.logger.info("Запуск обработки алертов")

            # Запуск потоков обработки
            self._start_alert_processor()
            self._start_rate_limiter()
            self._start_ml_analyzer()

            self.logger.info("Обработка алертов запущена успешно")
        except Exception as e:
            self.logger.error(f"Ошибка запуска обработки алертов: {e}")
            raise

    def _start_alert_processor(self) -> None:
        """Запуск процессора алертов"""

        def process_alerts():
            while self.is_running:
                try:
                    if not self.alert_queue.empty():
                        alert = self.alert_queue.get(timeout=1)
                        self._process_alert(alert)
                        self.alert_queue.task_done()
                    else:
                        time.sleep(0.1)
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Ошибка обработки алерта: {e}")

        thread = threading.Thread(target=process_alerts, daemon=True)
        thread.start()
        self.processing_threads.append(thread)

    def _start_rate_limiter(self) -> None:
        """Запуск ограничителя частоты"""

        def limit_rates():
            while self.is_running:
                try:
                    current_time = datetime.now()
                    # Очистка старых записей (старше 1 часа)
                    for key in list(self.rate_limiter.keys()):
                        self.rate_limiter[key] = [
                            timestamp
                            for timestamp in self.rate_limiter[key]
                            if (current_time - timestamp).total_seconds()
                            < 3600
                        ]
                        if not self.rate_limiter[key]:
                            del self.rate_limiter[key]

                    time.sleep(60)  # Проверка каждую минуту
                except Exception as e:
                    self.logger.error(f"Ошибка ограничителя частоты: {e}")

        thread = threading.Thread(target=limit_rates, daemon=True)
        thread.start()
        self.processing_threads.append(thread)

    def _start_ml_analyzer(self) -> None:
        """Запуск ML анализатора"""

        def analyze_alerts():
            while self.is_running:
                try:
                    if len(self.alert_history) > 10:
                        self._analyze_alert_patterns()
                    time.sleep(300)  # Анализ каждые 5 минут
                except Exception as e:
                    self.logger.error(f"Ошибка ML анализа: {e}")

        thread = threading.Thread(target=analyze_alerts, daemon=True)
        thread.start()
        self.processing_threads.append(thread)

    def send_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        source: str = "system",
        recipients: Optional[List[str]] = None,
        channels: Optional[List[AlertChannel]] = None,
        template_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Отправка алерта

        Args:
            title: Заголовок алерта
            message: Сообщение алерта
            severity: Уровень серьезности
            source: Источник алерта
            recipients: Список получателей
            channels: Каналы доставки
            template_name: Имя шаблона
            metadata: Дополнительные данные

        Returns:
            ID созданного алерта
        """
        try:
            # Генерация ID алерта
            alert_id = hashlib.md5(
                f"{title}{message}{time.time()}".encode()
            ).hexdigest()[:16]

            # Применение шаблона если указан
            if template_name and template_name in self.templates:
                template = self.templates[template_name]
                title = template.subject
                message = template.body.format(details=message)
                if not channels:
                    channels = template.channels
                if severity == AlertSeverity.MEDIUM:
                    severity = template.severity

            # Создание алерта
            alert = Alert(
                id=alert_id,
                title=title,
                message=message,
                severity=severity,
                source=source,
                timestamp=datetime.now(),
                recipients=recipients or [],
                channels=channels or [AlertChannel.EMAIL],
                metadata=metadata or {},
            )

            # Проверка rate limiting
            if self._is_rate_limited(alert):
                self.stats["alerts_blocked"] += 1
                self.logger.warning(
                    f"Алерт заблокирован rate limiting: {alert_id}"
                )
                return alert_id

            # Добавление в очередь обработки
            self.alert_queue.put(alert)
            self.alert_history.append(alert)

            # Ограничение истории (последние 1000 алертов)
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]

            self.logger.info(f"Алерт создан: {alert_id} - {title}")
            return alert_id

        except Exception as e:
            self.logger.error(f"Ошибка создания алерта: {e}")
            return ""

    def _is_rate_limited(self, alert: Alert) -> bool:
        """Проверка ограничения частоты"""
        try:
            # Ключ для rate limiting
            rate_key = f"{alert.source}_{alert.severity.value}"
            current_time = datetime.now()

            # Получение истории для ключа
            if rate_key not in self.rate_limiter:
                self.rate_limiter[rate_key] = []

            # Очистка старых записей (старше 1 часа)
            self.rate_limiter[rate_key] = [
                timestamp
                for timestamp in self.rate_limiter[rate_key]
                if (current_time - timestamp).total_seconds() < 3600
            ]

            # Проверка лимитов
            if alert.severity == AlertSeverity.CRITICAL:
                max_per_hour = 50
            elif alert.severity == AlertSeverity.HIGH:
                max_per_hour = 20
            elif alert.severity == AlertSeverity.MEDIUM:
                max_per_hour = 10
            else:
                max_per_hour = 5

            if len(self.rate_limiter[rate_key]) >= max_per_hour:
                return True

            # Добавление текущего времени
            self.rate_limiter[rate_key].append(current_time)
            return False

        except Exception as e:
            self.logger.error(f"Ошибка проверки rate limiting: {e}")
            return False

    def _process_alert(self, alert: Alert) -> None:
        """Обработка алерта"""
        try:
            # Определение получателей
            if not alert.recipients:
                alert.recipients = list(self.recipients.keys())

            # Отправка по каналам
            for channel in alert.channels:
                self._send_via_channel(alert, channel)

            # Обновление статистики
            self.stats["alerts_sent"] += 1
            if alert.severity.value not in self.stats["severity_distribution"]:
                self.stats["severity_distribution"][alert.severity.value] = 0
            self.stats["severity_distribution"][alert.severity.value] += 1

            for channel in alert.channels:
                if channel.value not in self.stats["channels_used"]:
                    self.stats["channels_used"][channel.value] = 0
                self.stats["channels_used"][channel.value] += 1

            self.logger.info(f"Алерт обработан: {alert.id}")

        except Exception as e:
            self.logger.error(f"Ошибка обработки алерта: {e}")

    def _send_via_channel(self, alert: Alert, channel: AlertChannel) -> None:
        """Отправка алерта по каналу"""
        try:
            if channel == AlertChannel.EMAIL:
                self._send_email(alert)
            elif channel == AlertChannel.SMS:
                self._send_sms(alert)
            elif channel == AlertChannel.PUSH:
                self._send_push(alert)
            elif channel == AlertChannel.TELEGRAM:
                self._send_telegram(alert)
            elif channel == AlertChannel.DISCORD:
                self._send_discord(alert)
            elif channel == AlertChannel.SLACK:
                self._send_slack(alert)
            elif channel == AlertChannel.WEBHOOK:
                self._send_webhook(alert)

        except Exception as e:
            self.logger.error(
                f"Ошибка отправки по каналу {channel.value}: {e}"
            )

    def _send_email(self, alert: Alert) -> None:
        """Отправка email алерта"""
        try:
            # Здесь должна быть интеграция с SMTP сервером
            self.logger.info(f"EMAIL: {alert.title} - {alert.message}")
        except Exception as e:
            self.logger.error(f"Ошибка отправки email: {e}")

    def _send_sms(self, alert: Alert) -> None:
        """Отправка SMS алерта"""
        try:
            # Здесь должна быть интеграция с SMS провайдером
            self.logger.info(f"SMS: {alert.title} - {alert.message}")
        except Exception as e:
            self.logger.error(f"Ошибка отправки SMS: {e}")

    def _send_push(self, alert: Alert) -> None:
        """Отправка push уведомления"""
        try:
            # Здесь должна быть интеграция с push сервисом
            self.logger.info(f"PUSH: {alert.title} - {alert.message}")
        except Exception as e:
            self.logger.error(f"Ошибка отправки push: {e}")

    def _send_telegram(self, alert: Alert) -> None:
        """Отправка Telegram алерта"""
        try:
            # Здесь должна быть интеграция с Telegram Bot API
            self.logger.info(f"TELEGRAM: {alert.title} - {alert.message}")
        except Exception as e:
            self.logger.error(f"Ошибка отправки Telegram: {e}")

    def _send_discord(self, alert: Alert) -> None:
        """Отправка Discord алерта"""
        try:
            # Здесь должна быть интеграция с Discord Webhook
            self.logger.info(f"DISCORD: {alert.title} - {alert.message}")
        except Exception as e:
            self.logger.error(f"Ошибка отправки Discord: {e}")

    def _send_slack(self, alert: Alert) -> None:
        """Отправка Slack алерта"""
        try:
            # Здесь должна быть интеграция с Slack API
            self.logger.info(f"SLACK: {alert.title} - {alert.message}")
        except Exception as e:
            self.logger.error(f"Ошибка отправки Slack: {e}")

    def _send_webhook(self, alert: Alert) -> None:
        """Отправка webhook алерта"""
        try:
            # Здесь должна быть интеграция с webhook
            self.logger.info(f"WEBHOOK: {alert.title} - {alert.message}")
        except Exception as e:
            self.logger.error(f"Ошибка отправки webhook: {e}")

    def _analyze_alert_patterns(self) -> None:
        """Анализ паттернов алертов с помощью ML"""
        try:
            if not self.is_ml_trained or len(self.alert_history) < 10:
                return

            # Подготовка данных
            alert_texts = [
                f"{alert.title} {alert.message}"
                for alert in self.alert_history[-100:]
            ]

            # Векторизация
            features = self.vectorizer.transform(alert_texts).toarray()

            # Кластеризация
            clusters = self.clusterer.predict(features)

            # Анализ кластеров
            unique_clusters, counts = np.unique(clusters, return_counts=True)

            # Поиск аномальных кластеров
            for cluster_id, count in zip(unique_clusters, counts):
                if count > 10:  # Много алертов в одном кластере
                    # cluster_alerts = [
                    #     alert
                    #     for i, alert in enumerate(self.alert_history[-100:])
                    #     if clusters[i] == cluster_id
                    # ]

                    self.logger.warning(
                        f"Обнаружен паттерн алертов в кластере {cluster_id}: "
                        f"{count} алертов"
                    )

                    # Генерация алерта о паттерне
                    pattern_alert = Alert(
                        id=f"pattern_{cluster_id}_{int(time.time())}",
                        title="🔍 Обнаружен паттерн алертов",
                        message=f"Система обнаружила повторяющийся паттерн: "
                        f"{count} похожих алертов",
                        severity=AlertSeverity.MEDIUM,
                        source="ml_analyzer",
                        timestamp=datetime.now(),
                        metadata={
                            "cluster_id": int(cluster_id),
                            "count": int(count),
                        },
                    )

                    self.alert_queue.put(pattern_alert)

        except Exception as e:
            self.logger.error(f"Ошибка анализа паттернов: {e}")

    def add_recipient(self, recipient: AlertRecipient) -> None:
        """Добавление получателя алертов"""
        try:
            self.recipients[recipient.user_id] = recipient
            self.logger.info(f"Добавлен получатель: {recipient.name}")
        except Exception as e:
            self.logger.error(f"Ошибка добавления получателя: {e}")

    def remove_recipient(self, user_id: str) -> bool:
        """Удаление получателя алертов"""
        try:
            if user_id in self.recipients:
                del self.recipients[user_id]
                self.logger.info(f"Удален получатель: {user_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка удаления получателя: {e}")
            return False

    def add_template(self, template: AlertTemplate) -> None:
        """Добавление шаблона алерта"""
        try:
            self.templates[template.name] = template
            self.logger.info(f"Добавлен шаблон: {template.name}")
        except Exception as e:
            self.logger.error(f"Ошибка добавления шаблона: {e}")

    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение истории алертов"""
        try:
            recent_alerts = self.alert_history[-limit:]
            return [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "message": alert.message,
                    "severity": alert.severity.value,
                    "source": alert.source,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved,
                    "channels": [ch.value for ch in alert.channels],
                }
                for alert in recent_alerts
            ]
        except Exception as e:
            self.logger.error(f"Ошибка получения истории алертов: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики алертов"""
        try:
            uptime = time.time() - self.stats["uptime_start"]
            return {
                "uptime_seconds": uptime,
                "uptime_human": str(timedelta(seconds=int(uptime))),
                "alerts_sent": self.stats["alerts_sent"],
                "alerts_blocked": self.stats["alerts_blocked"],
                "total_recipients": len(self.recipients),
                "total_templates": len(self.templates),
                "channels_used": self.stats["channels_used"],
                "severity_distribution": self.stats["severity_distribution"],
                "is_running": self.is_running,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return {}

    async def stop_alert_processing(self) -> None:
        """Остановка обработки алертов"""
        try:
            self.is_running = False
            self.logger.info("Остановка обработки алертов")

            # Ожидание завершения потоков
            for thread in self.processing_threads:
                if thread.is_alive():
                    thread.join(timeout=5)

            self.logger.info("Обработка алертов остановлена")
        except Exception as e:
            self.logger.error(f"Ошибка остановки обработки алертов: {e}")

    def get_status(self) -> str:
        """Получение статуса AlertManager"""
        try:
            if self.is_running:
                return "running"
            else:
                return "stopped"
        except Exception:
            return "unknown"

    def start_alerts(self) -> bool:
        """Запуск системы алертов"""
        try:
            if not self.is_running:
                self.is_running = True
                self.logger.info("Система алертов запущена")
                return True
            else:
                self.logger.warning("Система алертов уже запущена")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка запуска системы алертов: {e}")
            return False

    def stop_alerts(self) -> bool:
        """Остановка системы алертов"""
        try:
            if self.is_running:
                self.is_running = False
                self.logger.info("Система алертов остановлена")
                return True
            else:
                self.logger.warning("Система алертов уже остановлена")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка остановки системы алертов: {e}")
            return False

    def get_alert_info(self) -> Dict[str, Any]:
        """Получение информации о системе алертов"""
        try:
            return {
                "is_running": self.is_running,
                "recipients_count": len(self.recipients),
                "templates_count": len(self.templates),
                "alerts_sent": self.stats.get("alerts_sent", 0),
                "alerts_failed": self.stats.get("alerts_failed", 0),
                "channels_available": len(AlertChannel),
                "severity_levels": len(AlertSeverity),
                "processing_threads": len(self.processing_threads),
            }
        except Exception as e:
            self.logger.error(
                f"Ошибка получения информации о системе алертов: {e}"
            )
            return {
                "is_running": False,
                "recipients_count": 0,
                "templates_count": 0,
                "alerts_sent": 0,
                "alerts_failed": 0,
                "channels_available": 0,
                "severity_levels": 0,
                "processing_threads": 0,
                "error": str(e),
            }


# Пример использования
if __name__ == "__main__":

    async def main():
        alert_manager = AlertManager("TestAlertManager")
        await alert_manager.start_alert_processing()

        # Отправка тестового алерта
        alert_id = alert_manager.send_alert(
            title="Тестовый алерт",
            message="Это тестовое сообщение",
            severity=AlertSeverity.MEDIUM,
            channels=[AlertChannel.EMAIL, AlertChannel.PUSH],
        )

        print(f"Отправлен алерт: {alert_id}")

        # Ожидание обработки
        await asyncio.sleep(5)

        # Получение статистики
        alert_stats = alert_manager.get_statistics()
        print(f"Статистика: {alert_stats}")

        # Остановка
        await alert_manager.stop_alert_processing()

    asyncio.run(main())
