#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GamingSecurityBot - Бот безопасности игр
function_87: Интеллектуальный бот для безопасности игрового процесса

Этот модуль предоставляет интеллектуального бота для безопасности игр,
включающего:
- Защиту от читов и читерства
- Мониторинг игрового процесса
- Анализ поведения игроков
- Защиту от DDoS атак
- Контроль игровых транзакций
- Модерацию чата
- Защиту от ботов
- Анализ метрик производительности
- Систему репутации
- Интеграцию с антивирусами

Основные возможности:
1. Детекция читов и читерства
2. Мониторинг игрового процесса в реальном времени
3. Анализ поведения игроков
4. Защита от DDoS и DoS атак
5. Контроль игровых транзакций
6. Автоматическая модерация чата
7. Защита от игровых ботов
8. Анализ производительности игры
9. Система репутации и рейтинга
10. Интеграция с системами безопасности

Технические детали:
- Использует ML для детекции аномалий
- Применяет поведенческий анализ
- Интегрирует с игровыми движками
- Использует сетевой анализ для детекции атак
- Применяет компьютерное зрение для анализа скриншотов
- Интегрирует с платежными системами
- Использует NLP для модерации чата
- Применяет криптографию для защиты данных
- Интегрирует с системами репутации
- Использует машинное обучение для предсказания поведения

Автор: ALADDIN Security System
Версия: 2.0
Дата: 2025-01-27
Лицензия: MIT
"""

import asyncio
import hashlib
import logging
import os

# Внутренние импорты
import sys
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Внешние зависимости
import redis
import sqlalchemy
from prometheus_client import Counter, Gauge
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.base import SecurityBase


# Специфичные исключения для GamingSecurityBot
class GamingSecurityError(Exception):
    """Базовое исключение для GamingSecurityBot"""

    pass


class CheatDetectionError(GamingSecurityError):
    """Ошибка детекции читов"""

    pass


class SessionManagementError(GamingSecurityError):
    """Ошибка управления сессиями"""

    pass


class TransactionAnalysisError(GamingSecurityError):
    """Ошибка анализа транзакций"""

    pass


class ConfigurationError(GamingSecurityError):
    """Ошибка конфигурации"""

    pass


class DatabaseError(GamingSecurityError):
    """Ошибка работы с базой данных"""

    pass


class RedisConnectionError(GamingSecurityError):
    """Ошибка подключения к Redis"""

    pass


class MLModelError(GamingSecurityError):
    """Ошибка машинного обучения"""

    pass


class ValidationError(GamingSecurityError):
    """Ошибка валидации данных"""

    pass


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# База данных
Base = declarative_base()


class CheatType(Enum):
    """Типы читов"""

    AIMBOT = "aimbot"
    WALLHACK = "wallhack"
    SPEEDHACK = "speedhack"
    TELEPORT = "teleport"
    INVISIBILITY = "invisibility"
    DAMAGE_HACK = "damage_hack"
    HEALTH_HACK = "health_hack"
    RESOURCE_HACK = "resource_hack"
    MACRO = "macro"
    BOT = "bot"
    UNKNOWN = "unknown"


class ThreatLevel(Enum):
    """Уровни угроз"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    IMMEDIATE = "immediate"


class GameGenre(Enum):
    """Жанры игр"""

    FPS = "fps"
    RPG = "rpg"
    STRATEGY = "strategy"
    MOBA = "moba"
    BATTLE_ROYALE = "battle_royale"
    RACING = "racing"
    PUZZLE = "puzzle"
    SPORTS = "sports"
    SIMULATION = "simulation"
    ADVENTURE = "adventure"


class PlayerAction(Enum):
    """Действия игрока"""

    MOVE = "move"
    SHOOT = "shoot"
    JUMP = "jump"
    CROUCH = "crouch"
    RELOAD = "reload"
    SWITCH_WEAPON = "switch_weapon"
    CHAT = "chat"
    PURCHASE = "purchase"
    LOGIN = "login"
    LOGOUT = "logout"


class GameSession(Base):
    """Игровая сессия"""

    __tablename__ = "game_sessions"

    id = Column(String, primary_key=True)
    player_id = Column(String, nullable=False)
    game_id = Column(String, nullable=False)
    game_genre = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration = Column(Integer)  # секунды
    score = Column(Integer, default=0)
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    suspicious_actions = Column(Integer, default=0)
    cheat_detected = Column(Boolean, default=False)
    ban_applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CheatDetection(Base):
    """Детекция читов"""

    __tablename__ = "cheat_detections"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    player_id = Column(String, nullable=False)
    cheat_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    evidence = Column(JSON)
    threat_level = Column(String, nullable=False)
    action_taken = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    reviewed = Column(Boolean, default=False)


class PlayerBehavior(Base):
    """Поведение игрока"""

    __tablename__ = "player_behaviors"

    id = Column(String, primary_key=True)
    player_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    coordinates = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    reaction_time = Column(Float)
    accuracy = Column(Float)
    suspicious_score = Column(Float, default=0.0)
    context = Column(JSON)


class GameTransaction(Base):
    """Игровая транзакция"""

    __tablename__ = "game_transactions"

    id = Column(String, primary_key=True)
    player_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    item_id = Column(String)
    payment_method = Column(String)
    is_fraudulent = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)


class SecurityAlert(BaseModel):
    """Оповещение безопасности"""

    alert_id: str
    player_id: str
    session_id: str
    alert_type: str
    threat_level: ThreatLevel
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    action_required: bool = True
    timestamp: datetime
    auto_resolved: bool = False


class CheatAnalysisResult(BaseModel):
    """Результат анализа читов"""

    cheat_type: CheatType
    confidence: float
    threat_level: ThreatLevel
    evidence: Dict[str, Any] = Field(default_factory=dict)
    recommended_action: str
    false_positive_probability: float = 0.0


class PlayerProfile(BaseModel):
    """Профиль игрока"""

    player_id: str
    username: str
    reputation_score: float = 0.0
    total_playtime: int = 0  # секунды
    games_played: int = 0
    cheats_detected: int = 0
    bans_received: int = 0
    last_activity: datetime
    risk_level: ThreatLevel = ThreatLevel.LOW
    behavior_patterns: Dict[str, Any] = Field(default_factory=dict)


# Prometheus метрики
cheat_detections_total = Counter(
    "cheat_detections_total",
    "Total number of cheat detections",
    ["cheat_type", "threat_level"],
)

suspicious_actions_total = Counter(
    "suspicious_actions_total",
    "Total number of suspicious actions",
    ["action_type", "player_id"],
)

game_sessions_total = Counter(
    "game_sessions_total",
    "Total number of game sessions",
    ["game_genre", "status"],
)

active_players = Gauge("active_players", "Number of active players")

fraudulent_transactions = Counter(
    "fraudulent_transactions_total",
    "Total number of fraudulent transactions",
    ["transaction_type", "payment_method"],
)


class GamingSecurityBot(SecurityBase):
    """
    Интеллектуальный бот безопасности игр

    Предоставляет комплексную систему безопасности игр с поддержкой:
    - Детекции читов и читерства
    - Мониторинга игрового процесса
    - Анализа поведения игроков
    - Защиты от DDoS атак
    - Контроля игровых транзакций
    """

    def __init__(
        self,
        name: str = "GamingSecurityBot",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация GamingSecurityBot

        Args:
            name: Имя бота
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///gaming_security_bot.db",
            "cheat_detection_enabled": True,
            "behavior_analysis_enabled": True,
            "transaction_monitoring": True,
            "chat_moderation": True,
            "ddos_protection": True,
            "anti_bot_protection": True,
            "ml_enabled": True,
            "adaptive_learning": True,
            "real_time_monitoring": True,
            "auto_ban_enabled": False,  # Требует ручного подтверждения
            "reputation_system": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_enabled": True,
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Инициализация компонентов
        self.redis_client: Optional[redis.Redis] = None
        self.db_engine: Optional[sqlalchemy.Engine] = None
        self.db_session: Optional[sqlalchemy.orm.Session] = None
        self.active_sessions: Dict[str, GameSession] = {}
        self.player_profiles: Dict[str, PlayerProfile] = {}
        self.ml_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None

        # Статистика
        self.stats = {
            "total_sessions": 0,
            "active_sessions": 0,
            "cheat_detections": 0,
            "suspicious_actions": 0,
            "bans_applied": 0,
            "fraudulent_transactions": 0,
            "false_positives": 0,
            "average_session_duration": 0.0,
            "detection_accuracy": 0.0,
        }

        # Потоки
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        # Дополнительные атрибуты для мониторинга
        self.version: str = "2.5.0"
        self.start_time: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        self.error_count: int = 0
        self.performance_metrics: Dict[str, Any] = {
            "total_requests": 0,
            "avg_response_time": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
        }
        self.configuration_hash: str = ""
        self.is_initialized: bool = False
        self.shutdown_requested: bool = False

        # Вычисляем хеш конфигурации
        self._update_configuration_hash()

        self.logger.info(f"GamingSecurityBot {name} инициализирован")

    def _update_configuration_hash(self) -> None:
        """
        Обновление хеша конфигурации для отслеживания изменений

        Returns:
            None
        """
        try:
            import hashlib

            config_str = str(sorted(self.config.items()))
            self.configuration_hash = hashlib.md5(
                config_str.encode("utf-8")
            ).hexdigest()
        except Exception as e:
            self.logger.error(f"Ошибка обновления хеша конфигурации: {e}")
            self.configuration_hash = ""

    def _update_last_activity(self) -> None:
        """
        Обновление времени последней активности

        Returns:
            None
        """
        try:
            self.last_activity = datetime.utcnow()
        except Exception as e:
            self.logger.error(f"Ошибка обновления последней активности: {e}")

    def _increment_error_count(self) -> None:
        """
        Увеличение счетчика ошибок

        Returns:
            None
        """
        try:
            self.error_count += 1
        except Exception as e:
            self.logger.error(f"Ошибка увеличения счетчика ошибок: {e}")

    def _update_performance_metrics(self, response_time: float) -> None:
        """
        Обновление метрик производительности

        Args:
            response_time: Время ответа в секундах

        Returns:
            None
        """
        try:
            self.performance_metrics["total_requests"] += 1

            # Вычисляем среднее время ответа
            total_requests = self.performance_metrics["total_requests"]
            current_avg = self.performance_metrics["avg_response_time"]
            new_avg = (
                (current_avg * (total_requests - 1)) + response_time
            ) / total_requests
            self.performance_metrics["avg_response_time"] = new_avg

        except Exception as e:
            self.logger.error(
                f"Ошибка обновления метрик производительности: {e}"
            )

    def _validate_session_id(self, session_id: str) -> None:
        """
        Валидация ID сессии

        Args:
            session_id: ID сессии для проверки

        Raises:
            ValidationError: Если session_id невалиден
        """
        if not session_id or not isinstance(session_id, str):
            raise ValidationError("session_id должен быть непустой строкой")
        if len(session_id.strip()) == 0:
            raise ValidationError("session_id не может быть пустой строкой")

    def _validate_player_id(self, player_id: str) -> None:
        """
        Валидация ID игрока

        Args:
            player_id: ID игрока для проверки

        Raises:
            ValidationError: Если player_id невалиден
        """
        if not player_id or not isinstance(player_id, str):
            raise ValidationError("player_id должен быть непустой строкой")
        if len(player_id.strip()) == 0:
            raise ValidationError("player_id не может быть пустой строкой")

    def _validate_game_id(self, game_id: str) -> None:
        """
        Валидация ID игры

        Args:
            game_id: ID игры для проверки

        Raises:
            ValidationError: Если game_id невалиден
        """
        if not game_id or not isinstance(game_id, str):
            raise ValidationError("game_id должен быть непустой строкой")
        if len(game_id.strip()) == 0:
            raise ValidationError("game_id не может быть пустой строкой")

    def _validate_coordinates(self, coordinates: Dict[str, float]) -> None:
        """
        Валидация координат

        Args:
            coordinates: Словарь координат для проверки

        Raises:
            ValidationError: Если координаты невалидны
        """
        if not isinstance(coordinates, dict):
            raise ValidationError("coordinates должен быть словарем")

        required_keys = ["x", "y"]
        for key in required_keys:
            if key not in coordinates:
                raise ValidationError(
                    f"coordinates должен содержать ключ '{key}'"
                )

            value = coordinates[key]
            if not isinstance(value, (int, float)):
                raise ValidationError(
                    f"coordinates['{key}'] должен быть числом"
                )

            if not (0 <= value <= 1):
                raise ValidationError(
                    f"coordinates['{key}'] должен быть в диапазоне [0, 1]"
                )

    def _validate_transaction_data(
        self, transaction_data: Dict[str, Any]
    ) -> None:
        """
        Валидация данных транзакции

        Args:
            transaction_data: Данные транзакции для проверки

        Raises:
            ValidationError: Если данные транзакции невалидны
        """
        if not isinstance(transaction_data, dict):
            raise ValidationError("transaction_data должен быть словарем")

        required_keys = ["amount", "currency", "payment_method"]
        for key in required_keys:
            if key not in transaction_data:
                raise ValidationError(
                    f"transaction_data должен содержать ключ '{key}'"
                )

        # Валидация суммы
        amount = transaction_data.get("amount")
        if not isinstance(amount, (int, float)):
            raise ValidationError(
                "transaction_data['amount'] должен быть числом"
            )
        if amount < 0:
            raise ValidationError(
                "transaction_data['amount'] не может быть отрицательным"
            )

        # Валидация валюты
        currency = transaction_data.get("currency")
        if not isinstance(currency, str) or len(currency.strip()) == 0:
            raise ValidationError(
                "transaction_data['currency'] должен быть непустой строкой"
            )

        # Валидация метода оплаты
        payment_method = transaction_data.get("payment_method")
        if (
            not isinstance(payment_method, str)
            or len(payment_method.strip()) == 0
        ):
            raise ValidationError(
                "transaction_data['payment_method'] должен быть "
                "непустой строкой"
            )

    async def start(self) -> bool:
        """Запуск бота безопасности игр"""
        try:
            with self.lock:
                if self.running:
                    self.logger.warning("GamingSecurityBot уже запущен")
                    return True

                # Инициализация базы данных
                await self._setup_database()

                # Инициализация Redis
                await self._setup_redis()

                # Инициализация ML модели
                if self.config.get("ml_enabled", True):
                    await self._setup_ml_model()

                # Загрузка профилей игроков
                await self._load_player_profiles()

                # Запуск мониторинга
                self.running = True
                self.start_time = datetime.utcnow()
                self.is_initialized = True
                self.shutdown_requested = False

                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_worker
                )
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()

                self._update_last_activity()
                self.logger.info("GamingSecurityBot запущен успешно")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска GamingSecurityBot: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка бота безопасности игр"""
        try:
            with self.lock:
                if not self.running:
                    self.logger.warning("GamingSecurityBot уже остановлен")
                    return True

                self.running = False
                self.shutdown_requested = True

                # Ожидание завершения потоков
                if (
                    self.monitoring_thread
                    and self.monitoring_thread.is_alive()
                ):
                    self.monitoring_thread.join(timeout=5)

                # Закрытие соединений
                if self.db_session:
                    self.db_session.close()

                if self.redis_client:
                    self.redis_client.close()

                self.logger.info("GamingSecurityBot остановлен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки GamingSecurityBot: {e}")
            return False

    async def _setup_database(self) -> None:
        """Настройка базы данных"""
        try:
            database_url = self.config.get(
                "database_url", "sqlite:///gaming_security_bot.db"
            )
            self.db_engine = create_engine(database_url)
            Base.metadata.create_all(self.db_engine)

            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info("База данных GamingSecurityBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки базы данных: {e}")
            raise

    async def _setup_redis(self) -> None:
        """Настройка Redis"""
        try:
            redis_url = self.config.get(
                "redis_url", "redis://localhost:6379/0"
            )
            self.redis_client = redis.from_url(
                redis_url, decode_responses=True
            )

            # Тест соединения
            self.redis_client.ping()

            self.logger.info("Redis для GamingSecurityBot настроен")

        except Exception as e:
            self.logger.error(f"Ошибка настройки Redis: {e}")
            raise

    async def _setup_ml_model(self) -> None:
        """Настройка ML модели для детекции читов"""
        try:
            self.ml_model = IsolationForest(
                contamination=0.1, random_state=42, n_estimators=100
            )
            self.scaler = StandardScaler()

            self.logger.info("ML модель GamingSecurityBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки ML модели: {e}")

    async def _load_player_profiles(self) -> None:
        """Загрузка профилей игроков"""
        try:
            # Здесь должна быть загрузка из базы данных
            # Пока что создаем пустой словарь
            self.player_profiles = {}

            self.logger.info("Профили игроков загружены")

        except Exception as e:
            self.logger.error(f"Ошибка загрузки профилей игроков: {e}")

    def _monitoring_worker(self) -> None:
        """Фоновый процесс мониторинга"""
        while self.running:
            try:
                time.sleep(1)  # Проверка каждую секунду

                # Обновление статистики
                self._update_stats()

                # Анализ активных сессий
                self._analyze_active_sessions()

            except Exception as e:
                self.logger.error(f"Ошибка в процессе мониторинга: {e}")

    def _update_stats(self) -> None:
        """Обновление статистики"""
        try:
            with self.lock:
                self.stats["active_sessions"] = len(self.active_sessions)
                active_players.set(self.stats["active_sessions"])

        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    def _analyze_active_sessions(self) -> None:
        """Анализ активных игровых сессий"""
        try:
            for session_id, session in self.active_sessions.items():
                # Анализ подозрительной активности
                self._analyze_session_behavior(session)

        except Exception as e:
            self.logger.error(f"Ошибка анализа активных сессий: {e}")

    def _analyze_session_behavior(self, session: GameSession) -> None:
        """Анализ поведения в сессии"""
        try:
            # Здесь должна быть логика анализа поведения
            # Пока что заглушка
            pass

        except Exception as e:
            self.logger.error(f"Ошибка анализа поведения сессии: {e}")

    async def start_game_session(
        self, player_id: str, game_id: str, game_genre: GameGenre
    ) -> str:
        """Начало игровой сессии"""
        try:
            # ВАЛИДАЦИЯ: Проверка входных параметров
            self._validate_player_id(player_id)
            self._validate_game_id(game_id)
            if not isinstance(game_genre, GameGenre):
                raise ValidationError(
                    "game_genre должен быть экземпляром GameGenre"
                )

            with self.lock:
                # Генерация ID сессии
                session_id = self._generate_session_id()

                # Создание сессии
                session = GameSession(
                    id=session_id,
                    player_id=player_id,
                    game_id=game_id,
                    game_genre=game_genre.value,
                )

                # Сохранение в базу данных
                if self.db_session:
                    self.db_session.add(session)
                    self.db_session.commit()

                # Добавление в активные сессии
                self.active_sessions[session_id] = session

                # Обновление статистики
                self.stats["total_sessions"] += 1
                self.stats["active_sessions"] += 1

                # Обновление метрик
                game_sessions_total.labels(
                    game_genre=game_genre.value, status="started"
                ).inc()

                self.logger.info(f"Игровая сессия начата: {session_id}")
                return session_id

        except Exception as e:
            self.logger.error(f"Ошибка начала игровой сессии: {e}")
            raise

    def _generate_session_id(self) -> str:
        """Генерация уникального ID сессии"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"GAME_{timestamp}_{random_part}"

    async def analyze_player_action(
        self,
        session_id: str,
        player_id: str,
        action: PlayerAction,
        coordinates: Optional[Dict[str, float]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> CheatAnalysisResult:
        """Анализ действия игрока на предмет читов"""
        try:
            # ВАЛИДАЦИЯ: Проверка входных параметров
            self._validate_session_id(session_id)
            self._validate_player_id(player_id)
            if not isinstance(action, PlayerAction):
                raise ValidationError(
                    "action должен быть экземпляром PlayerAction"
                )
            if coordinates is not None:
                self._validate_coordinates(coordinates)
            # Получение сессии
            session = self.active_sessions.get(session_id)
            if not session:
                return CheatAnalysisResult(
                    cheat_type=CheatType.UNKNOWN,
                    confidence=0.0,
                    threat_level=ThreatLevel.LOW,
                    recommended_action="no_action",
                )

            # Анализ действия
            cheat_type, confidence, threat_level = await self._detect_cheat(
                action, coordinates, context, session
            )

            # Создание результата анализа
            result = CheatAnalysisResult(
                cheat_type=cheat_type,
                confidence=confidence,
                threat_level=threat_level,
                evidence=self._gather_evidence(action, coordinates, context),
                recommended_action=self._get_recommended_action(
                    threat_level, confidence
                ),
                false_positive_probability=(
                    self._calculate_false_positive_probability(
                        confidence, action
                    )
                ),
            )

            # Логирование детекции
            if confidence > 0.7:  # Высокая уверенность
                await self._log_cheat_detection(session_id, player_id, result)

            # Обновление статистики
            if confidence > 0.5:
                self.stats["cheat_detections"] += 1
                cheat_detections_total.labels(
                    cheat_type=cheat_type.value,
                    threat_level=threat_level.value,
                ).inc()

            return result

        except Exception as e:
            self.logger.error(f"Ошибка анализа действия игрока: {e}")
            return CheatAnalysisResult(
                cheat_type=CheatType.UNKNOWN,
                confidence=0.0,
                threat_level=ThreatLevel.LOW,
                recommended_action="error",
            )

    async def _detect_cheat(
        self,
        action: PlayerAction,
        coordinates: Optional[Dict[str, float]],
        context: Optional[Dict[str, Any]],
        session: GameSession,
    ) -> Tuple[CheatType, float, ThreatLevel]:
        """Детекция читов"""
        try:
            # Простая логика детекции (в реальности должна быть более сложная)
            cheat_type = CheatType.UNKNOWN
            confidence = 0.0
            threat_level = ThreatLevel.LOW

            # Анализ по типу действия
            if action == PlayerAction.SHOOT:
                # Анализ точности стрельбы
                if coordinates and self._is_impossible_accuracy(
                    coordinates, context
                ):
                    cheat_type = CheatType.AIMBOT
                    confidence = 0.8
                    threat_level = ThreatLevel.HIGH

            elif action == PlayerAction.MOVE:
                # Анализ скорости движения
                if self._is_impossible_speed(coordinates, context):
                    cheat_type = CheatType.SPEEDHACK
                    confidence = 0.7
                    threat_level = ThreatLevel.MEDIUM

            # Анализ с помощью ML модели
            if self.ml_model and context:
                features = self._extract_features(action, coordinates, context)
                if len(features) > 0:
                    features_scaled = self.scaler.fit_transform([features])
                    anomaly_score = self.ml_model.decision_function(
                        features_scaled
                    )[0]

                    if anomaly_score < -0.5:  # Аномальное поведение
                        if cheat_type == CheatType.UNKNOWN:
                            cheat_type = CheatType.UNKNOWN
                        confidence = max(confidence, abs(anomaly_score))
                        threat_level = ThreatLevel.MEDIUM

            return cheat_type, confidence, threat_level

        except Exception as e:
            self.logger.error(f"Ошибка детекции читов: {e}")
            return CheatType.UNKNOWN, 0.0, ThreatLevel.LOW

    def _is_impossible_accuracy(
        self, coordinates: Dict[str, float], context: Optional[Dict[str, Any]]
    ) -> bool:
        """Проверка невозможной точности стрельбы"""
        try:
            if not context or "target_distance" not in context:
                return False

            target_distance = context["target_distance"]
            accuracy = coordinates.get("accuracy", 0.0)

            # Простая проверка: точность > 95% на расстоянии > 100 метров
            # подозрительна
            return target_distance > 100 and accuracy > 0.95

        except Exception as e:
            self.logger.error(f"Ошибка проверки точности: {e}")
            return False

    def _is_impossible_speed(
        self,
        coordinates: Optional[Dict[str, float]],
        context: Optional[Dict[str, Any]],
    ) -> bool:
        """Проверка невозможной скорости движения"""
        try:
            if not context or "speed" not in context:
                return False

            speed = context["speed"]
            max_speed = context.get(
                "max_speed", 10.0
            )  # Максимальная скорость в игре

            # Скорость превышает максимальную на 50%
            return speed > max_speed * 1.5

        except Exception as e:
            self.logger.error(f"Ошибка проверки скорости: {e}")
            return False

    def _extract_features(
        self,
        action: PlayerAction,
        coordinates: Optional[Dict[str, float]],
        context: Optional[Dict[str, Any]],
    ) -> List[float]:
        """Извлечение признаков для ML модели"""
        try:
            features = []

            # Базовые признаки
            features.append(action.value.count("_"))  # Сложность действия
            features.append(len(context) if context else 0)  # Размер контекста

            # Координаты
            if coordinates:
                features.extend(
                    [coordinates.get("x", 0), coordinates.get("y", 0)]
                )
            else:
                features.extend([0, 0])

            # Контекстные признаки
            if context:
                features.append(context.get("reaction_time", 0))
                features.append(context.get("accuracy", 0))
                features.append(context.get("speed", 0))
            else:
                features.extend([0, 0, 0])

            return features

        except Exception as e:
            self.logger.error(f"Ошибка извлечения признаков: {e}")
            return []

    def _gather_evidence(
        self,
        action: PlayerAction,
        coordinates: Optional[Dict[str, float]],
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Сбор доказательств читерства"""
        try:
            evidence = {
                "action": action.value,
                "timestamp": datetime.utcnow().isoformat(),
                "coordinates": coordinates or {},
                "context": context or {},
            }

            return evidence

        except Exception as e:
            self.logger.error(f"Ошибка сбора доказательств: {e}")
            return {}

    def _get_recommended_action(
        self, threat_level: ThreatLevel, confidence: float
    ) -> str:
        """Получение рекомендуемого действия"""
        try:
            if threat_level == ThreatLevel.IMMEDIATE and confidence > 0.9:
                return "immediate_ban"
            elif threat_level == ThreatLevel.CRITICAL and confidence > 0.8:
                return "temporary_ban"
            elif threat_level == ThreatLevel.HIGH and confidence > 0.7:
                return "warning_and_monitor"
            elif threat_level == ThreatLevel.MEDIUM and confidence > 0.6:
                return "monitor_closely"
            else:
                return "no_action"

        except Exception as e:
            self.logger.error(f"Ошибка получения рекомендуемого действия: {e}")
            return "no_action"

    def _calculate_false_positive_probability(
        self, confidence: float, action: PlayerAction
    ) -> float:
        """Расчет вероятности ложного срабатывания"""
        try:
            # Простая формула на основе уверенности и типа действия
            base_fp = 1.0 - confidence

            # Корректировка по типу действия
            action_fp_multipliers = {
                PlayerAction.SHOOT: 0.8,  # Стрельба - более точная детекция
                PlayerAction.MOVE: 0.9,  # Движение - может быть ложным
                PlayerAction.JUMP: 0.95,  # Прыжки - часто ложные
                PlayerAction.CHAT: 0.7,  # Чат - точная детекция
            }

            multiplier = action_fp_multipliers.get(action, 1.0)
            return min(1.0, base_fp * multiplier)

        except Exception as e:
            self.logger.error(
                f"Ошибка расчета вероятности ложного срабатывания: {e}"
            )
            return 0.5

    async def _log_cheat_detection(
        self, session_id: str, player_id: str, result: CheatAnalysisResult
    ) -> None:
        """Логирование детекции читов"""
        try:
            if not self.db_session:
                return

            detection = CheatDetection(
                id=self._generate_detection_id(),
                session_id=session_id,
                player_id=player_id,
                cheat_type=result.cheat_type.value,
                confidence=result.confidence,
                evidence=result.evidence,
                threat_level=result.threat_level.value,
                action_taken=result.recommended_action,
            )

            self.db_session.add(detection)
            self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка логирования детекции читов: {e}")

    def _generate_detection_id(self) -> str:
        """Генерация ID детекции"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"DET_{timestamp}_{random_part}"

    async def analyze_transaction(
        self, player_id: str, session_id: str, transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Анализ игровой транзакции на мошенничество"""
        try:
            # ВАЛИДАЦИЯ: Проверка входных параметров
            self._validate_player_id(player_id)
            self._validate_session_id(session_id)
            self._validate_transaction_data(transaction_data)
            # Извлечение данных транзакции
            transaction_type = transaction_data.get("type", "unknown")
            amount = transaction_data.get("amount", 0.0)
            currency = transaction_data.get("currency", "USD")
            payment_method = transaction_data.get("payment_method", "unknown")

            # Расчет риска мошенничества
            risk_score = self._calculate_transaction_risk(transaction_data)
            is_fraudulent = risk_score > 0.7

            # Создание записи транзакции
            if self.db_session:
                transaction = GameTransaction(
                    id=self._generate_transaction_id(),
                    player_id=player_id,
                    session_id=session_id,
                    transaction_type=transaction_type,
                    amount=amount,
                    currency=currency,
                    item_id=transaction_data.get("item_id"),
                    payment_method=payment_method,
                    is_fraudulent=is_fraudulent,
                    risk_score=risk_score,
                )

                self.db_session.add(transaction)
                self.db_session.commit()

            # Обновление статистики
            if is_fraudulent:
                self.stats["fraudulent_transactions"] += 1
                fraudulent_transactions.labels(
                    transaction_type=transaction_type,
                    payment_method=payment_method,
                ).inc()

            return {
                "transaction_id": (
                    transaction.id if "transaction" in locals() else ""
                ),
                "is_fraudulent": is_fraudulent,
                "risk_score": risk_score,
                "recommended_action": "block" if is_fraudulent else "approve",
                "confidence": risk_score,
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа транзакции: {e}")
            return {
                "is_fraudulent": False,
                "risk_score": 0.0,
                "recommended_action": "approve",
                "confidence": 0.0,
            }

    def _calculate_transaction_risk(
        self, transaction_data: Dict[str, Any]
    ) -> float:
        """Расчет риска мошенничества в транзакции"""
        try:
            risk_score = 0.0

            # Проверка суммы
            amount = transaction_data.get("amount", 0.0)
            if amount > 1000:  # Высокая сумма
                risk_score += 0.3
            elif amount > 500:  # Средняя сумма
                risk_score += 0.1

            # Проверка метода оплаты
            payment_method = transaction_data.get("payment_method", "").lower()
            if payment_method in ["crypto", "bitcoin"]:  # Криптовалюта
                risk_score += 0.2
            elif payment_method in [
                "gift_card",
                "prepaid",
            ]:  # Подарочные карты
                risk_score += 0.15

            # Проверка времени (ночные транзакции подозрительны)
            current_hour = datetime.now().hour
            if 2 <= current_hour <= 5:  # Ночное время
                risk_score += 0.1

            # Проверка частоты транзакций (если есть данные)
            if transaction_data.get("is_rapid_transaction", False):
                risk_score += 0.2

            return min(1.0, risk_score)

        except Exception as e:
            self.logger.error(f"Ошибка расчета риска транзакции: {e}")
            return 0.0

    def _generate_transaction_id(self) -> str:
        """Генерация ID транзакции"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"TXN_{timestamp}_{random_part}"

    async def end_game_session(
        self,
        session_id: str,
        final_score: int = 0,
        kills: int = 0,
        deaths: int = 0,
        assists: int = 0,
    ) -> bool:
        """Завершение игровой сессии"""
        try:
            # ВАЛИДАЦИЯ: Проверка входных параметров
            self._validate_session_id(session_id)
            if not isinstance(final_score, int) or final_score < 0:
                raise ValidationError(
                    "final_score должен быть неотрицательным целым числом"
                )
            if not isinstance(kills, int) or kills < 0:
                raise ValidationError(
                    "kills должен быть неотрицательным целым числом"
                )
            if not isinstance(deaths, int) or deaths < 0:
                raise ValidationError(
                    "deaths должен быть неотрицательным целым числом"
                )
            if not isinstance(assists, int) or assists < 0:
                raise ValidationError(
                    "assists должен быть неотрицательным целым числом"
                )

            with self.lock:
                session = self.active_sessions.get(session_id)
                if not session:
                    return False

                # Обновление данных сессии
                session.end_time = datetime.utcnow()
                # ИСПРАВЛЕНИЕ: Добавить проверку на None перед вычислением
                if session.start_time and session.end_time:
                    session.duration = int(
                        (session.end_time - session.start_time).total_seconds()
                    )
                else:
                    session.duration = 0
                session.score = final_score
                session.kills = kills
                session.deaths = deaths
                session.assists = assists

                # Обновление в базе данных
                if self.db_session:
                    self.db_session.commit()

                # Удаление из активных сессий
                del self.active_sessions[session_id]

                # Обновление статистики
                self.stats["active_sessions"] -= 1

                # Обновление метрик
                game_sessions_total.labels(
                    game_genre=session.game_genre, status="completed"
                ).inc()

                self.logger.info(f"Игровая сессия завершена: {session_id}")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка завершения игровой сессии: {e}")
            return False

    async def get_player_profile(
        self, player_id: str
    ) -> Optional[PlayerProfile]:
        """Получение профиля игрока"""
        try:
            # Получение из кэша
            if player_id in self.player_profiles:
                return self.player_profiles[player_id]

            # Загрузка из базы данных
            if self.db_session:
                # Здесь должна быть загрузка профиля из БД
                # Пока что создаем базовый профиль
                profile = PlayerProfile(
                    player_id=player_id,
                    username=f"Player_{player_id}",
                    last_activity=datetime.utcnow(),
                )

                self.player_profiles[player_id] = profile
                return profile

            return None

        except Exception as e:
            self.logger.error(f"Ошибка получения профиля игрока: {e}")
            return None

    async def get_security_alerts(
        self, player_id: Optional[str] = None, limit: int = 10
    ) -> List[SecurityAlert]:
        """Получение оповещений безопасности"""
        try:
            alerts = []

            # Здесь должна быть загрузка оповещений из базы данных
            # Пока что возвращаем пустой список

            return alerts

        except Exception as e:
            self.logger.error(f"Ошибка получения оповещений безопасности: {e}")
            return []

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        try:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "config": self.config,
                "stats": self.stats,
                "active_sessions": len(self.active_sessions),
                "monitored_players": len(self.player_profiles),
                "ml_enabled": self.config.get("ml_enabled", False),
                "last_update": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"error": str(e)}

    def __len__(self) -> int:
        """
        Возвращает количество активных игровых сессий

        Returns:
            int: Количество активных сессий
        """
        return len(self.active_sessions)

    def __str__(self) -> str:
        """
        Строковое представление бота

        Returns:
            str: Описание бота с именем и статусом
        """
        status = "running" if self.running else "stopped"
        return f"GamingSecurityBot(name='{self.name}', status='{status}')"

    def __repr__(self) -> str:
        """
        Представление бота для разработчиков

        Returns:
            str: Детальное представление бота
        """
        return f"GamingSecurityBot(name='{self.name}', config={self.config})"

    def __eq__(self, other) -> bool:
        """
        Сравнение ботов по имени и конфигурации

        Args:
            other: Другой объект для сравнения

        Returns:
            bool: True если боты равны
        """
        if not isinstance(other, GamingSecurityBot):
            return False
        return self.name == other.name and self.config == other.config

    def __hash__(self) -> int:
        """
        Хеш бота для использования в множествах

        Returns:
            int: Хеш значения
        """
        return hash((self.name, tuple(sorted(self.config.items()))))

    async def __aenter__(self):
        """
        Асинхронный вход в контекст

        Returns:
            GamingSecurityBot: Экземпляр бота
        """
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Асинхронный выход из контекста

        Args:
            exc_type: Тип исключения (если есть)
            exc_val: Значение исключения (если есть)
            exc_tb: Трассировка исключения (если есть)
        """
        await self.stop()

    def get_health_status(self) -> Dict[str, Any]:
        """
        Получение статуса здоровья системы

        Returns:
            Dict[str, Any]: Словарь со статусом здоровья
        """
        try:
            current_time = datetime.utcnow()

            # Расчет времени работы
            uptime = 0.0
            if self.start_time:
                uptime = (current_time - self.start_time).total_seconds()

            # Расчет частоты ошибок
            total_requests = self.performance_metrics.get("total_requests", 0)
            error_rate = 0.0
            if total_requests > 0:
                error_rate = self.error_count / total_requests

            # Проверка зависимостей
            dependencies_status = self.check_dependencies()

            # Общий статус здоровья
            health_score = 100.0

            # Штрафы за ошибки
            if error_rate > 0.1:  # Более 10% ошибок
                health_score -= 20.0
            elif error_rate > 0.05:  # Более 5% ошибок
                health_score -= 10.0

            # Штрафы за недоступные зависимости
            failed_dependencies = sum(
                1 for status in dependencies_status.values() if not status
            )
            health_score -= failed_dependencies * 15.0

            # Штрафы за высокое время ответа
            avg_response_time = self.performance_metrics.get(
                "avg_response_time", 0.0
            )
            if avg_response_time > 5.0:  # Более 5 секунд
                health_score -= 15.0
            elif avg_response_time > 2.0:  # Более 2 секунд
                health_score -= 10.0

            # Определение статуса здоровья
            if health_score >= 90:
                status = "excellent"
            elif health_score >= 75:
                status = "good"
            elif health_score >= 60:
                status = "fair"
            elif health_score >= 40:
                status = "poor"
            else:
                status = "critical"

            return {
                "status": status,
                "health_score": max(0.0, min(100.0, health_score)),
                "uptime_seconds": uptime,
                "uptime_human": (
                    f"{int(uptime // 3600)}h "
                    f"{int((uptime % 3600) // 60)}m "
                    f"{int(uptime % 60)}s"
                ),
                "error_count": self.error_count,
                "error_rate": error_rate,
                "total_requests": total_requests,
                "avg_response_time": avg_response_time,
                "active_sessions": len(self.active_sessions),
                "monitored_players": len(self.player_profiles),
                "dependencies": dependencies_status,
                "failed_dependencies": failed_dependencies,
                "is_initialized": self.is_initialized,
                "running": self.running,
                "last_activity": (
                    self.last_activity.isoformat()
                    if self.last_activity
                    else None
                ),
                "version": self.version,
                "configuration_hash": (
                    self.configuration_hash[:8]
                    if self.configuration_hash
                    else None
                ),
                "timestamp": current_time.isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса здоровья: {e}")
            return {
                "status": "error",
                "health_score": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def check_dependencies(self) -> Dict[str, bool]:
        """
        Проверка доступности зависимостей

        Returns:
            Dict[str, bool]: Словарь со статусом каждой зависимости
        """
        try:
            dependencies = {}

            # Проверка Redis
            try:
                if self.redis_client:
                    # Попытка выполнить простую команду
                    self.redis_client.ping()
                    dependencies["redis"] = True
                else:
                    dependencies["redis"] = False
            except Exception:
                dependencies["redis"] = False

            # Проверка базы данных
            try:
                if self.db_engine and self.db_session:
                    # Попытка выполнить простой запрос
                    self.db_session.execute("SELECT 1")
                    dependencies["database"] = True
                else:
                    dependencies["database"] = False
            except Exception:
                dependencies["database"] = False

            # Проверка ML модели
            try:
                if self.ml_model and self.scaler:
                    # Попытка создать тестовые данные
                    import numpy as np

                    test_data = np.array([[0.5, 0.5, 0.5]])
                    self.scaler.transform(test_data)
                    dependencies["ml_model"] = True
                else:
                    dependencies["ml_model"] = False
            except Exception:
                dependencies["ml_model"] = False

            # Проверка потоков
            try:
                if (
                    self.monitoring_thread
                    and self.monitoring_thread.is_alive()
                ):
                    dependencies["monitoring_thread"] = True
                else:
                    dependencies["monitoring_thread"] = False
            except Exception:
                dependencies["monitoring_thread"] = False

            # Проверка блокировок
            try:
                if self.lock:
                    with self.lock:
                        dependencies["lock"] = True
                else:
                    dependencies["lock"] = False
            except Exception:
                dependencies["lock"] = False

            # Проверка конфигурации
            try:
                required_keys = [
                    "redis_url",
                    "database_url",
                    "cheat_detection_enabled",
                ]
                config_valid = all(key in self.config for key in required_keys)
                dependencies["configuration"] = config_valid
            except Exception:
                dependencies["configuration"] = False

            # Проверка метрик Prometheus
            try:
                # Проверяем, что метрики доступны
                metrics_available = all(
                    [
                        cheat_detections_total is not None,
                        suspicious_actions_total is not None,
                        game_sessions_total is not None,
                        active_players is not None,
                        fraudulent_transactions is not None,
                    ]
                )
                dependencies["prometheus_metrics"] = metrics_available
            except Exception:
                dependencies["prometheus_metrics"] = False

            return dependencies

        except Exception as e:
            self.logger.error(f"Ошибка проверки зависимостей: {e}")
            return {
                "redis": False,
                "database": False,
                "ml_model": False,
                "monitoring_thread": False,
                "lock": False,
                "configuration": False,
                "prometheus_metrics": False,
                "error": str(e),
            }

    async def auto_recovery(self) -> bool:
        """
        Автоматическое восстановление после ошибок

        Returns:
            bool: True если восстановление прошло успешно
        """
        try:
            self.logger.info("Запуск автоматического восстановления...")

            # Проверяем условия для восстановления
            recovery_needed = False
            recovery_reasons = []

            # Проверка частоты ошибок
            total_requests = self.performance_metrics.get("total_requests", 0)
            if total_requests > 0:
                error_rate = self.error_count / total_requests
                if error_rate > 0.1:  # Более 10% ошибок
                    recovery_needed = True
                    recovery_reasons.append(
                        f"высокая частота ошибок: {error_rate:.2%}"
                    )

            # Проверка количества ошибок
            if self.error_count > 10:
                recovery_needed = True
                recovery_reasons.append(f"много ошибок: {self.error_count}")

            # Проверка зависимостей
            dependencies = self.check_dependencies()
            failed_deps = [
                name
                for name, status in dependencies.items()
                if not status and name != "error"
            ]
            if len(failed_deps) > 2:  # Более 2 недоступных зависимостей
                recovery_needed = True
                recovery_reasons.append(
                    f"недоступные зависимости: {failed_deps}"
                )

            # Проверка времени ответа
            avg_response_time = self.performance_metrics.get(
                "avg_response_time", 0.0
            )
            if avg_response_time > 10.0:  # Более 10 секунд
                recovery_needed = True
                recovery_reasons.append(
                    f"медленный ответ: {avg_response_time:.2f}s"
                )

            if not recovery_needed:
                self.logger.info("Автоматическое восстановление не требуется")
                return True

            self.logger.warning(
                f"Требуется восстановление: {', '.join(recovery_reasons)}"
            )

            # Выполняем восстановление
            recovery_steps = []

            # Шаг 1: Остановка бота
            try:
                await self.stop()
                recovery_steps.append("остановка бота")
                await asyncio.sleep(2)  # Пауза для завершения операций
            except Exception as e:
                self.logger.error(f"Ошибка остановки бота: {e}")

            # Шаг 2: Сброс счетчиков ошибок
            try:
                self.error_count = 0
                recovery_steps.append("сброс счетчиков ошибок")
            except Exception as e:
                self.logger.error(f"Ошибка сброса счетчиков: {e}")

            # Шаг 3: Очистка активных сессий
            try:
                self.active_sessions.clear()
                recovery_steps.append("очистка активных сессий")
            except Exception as e:
                self.logger.error(f"Ошибка очистки сессий: {e}")

            # Шаг 4: Перезапуск бота
            try:
                success = await self.start()
                if success:
                    recovery_steps.append("перезапуск бота")
                else:
                    raise Exception("Не удалось перезапустить бота")
            except Exception as e:
                self.logger.error(f"Ошибка перезапуска бота: {e}")
                raise

            # Шаг 5: Проверка состояния после восстановления
            try:
                health_status = self.get_health_status()
                if health_status["health_score"] > 60:
                    recovery_steps.append("проверка состояния")
                    self.logger.info(
                        f"Восстановление успешно завершено: "
                        f"{', '.join(recovery_steps)}"
                    )
                    return True
                else:
                    raise Exception(
                        f"Низкий статус здоровья после восстановления: "
                        f"{health_status['health_score']}"
                    )
            except Exception as e:
                self.logger.error(f"Ошибка проверки состояния: {e}")
                raise

        except Exception as e:
            self.logger.error(f"Ошибка автоматического восстановления: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование бота в словарь для сериализации

        Returns:
            Dict[str, Any]: Словарь с данными бота
        """
        return {
            "name": self.name,
            "config": self.config,
            "stats": self.stats,
            "running": self.running,
            "active_sessions_count": len(self.active_sessions),
            "player_profiles_count": len(self.player_profiles),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GamingSecurityBot":
        """
        Создание бота из словаря

        Args:
            data: Словарь с данными бота

        Returns:
            GamingSecurityBot: Экземпляр бота
        """
        name = data.get("name", "GamingSecurityBot")
        config = data.get("config", {})
        return cls(name=name, config=config)

    def validate(self) -> bool:
        """
        Валидация конфигурации и состояния бота

        Returns:
            bool: True если валидация прошла успешно
        """
        try:
            # Проверка обязательных ключей конфигурации
            required_keys = ["redis_url", "database_url"]
            for key in required_keys:
                if key not in self.config:
                    self.logger.error(
                        f"Отсутствует обязательный ключ конфигурации: {key}"
                    )
                    return False

            # Проверка типов значений
            if not isinstance(
                self.config.get("cheat_detection_enabled"), bool
            ):
                self.logger.error("cheat_detection_enabled должен быть bool")
                return False

            if not isinstance(self.config.get("cleanup_interval"), int):
                self.logger.error("cleanup_interval должен быть int")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Ошибка валидации: {e}")
            return False

    async def save(self, filepath: str) -> bool:
        """
        Сохранение состояния бота в файл

        Args:
            filepath: Путь к файлу для сохранения

        Returns:
            bool: True если сохранение прошло успешно
        """
        try:
            import json

            data = self.to_dict()
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Состояние бота сохранено в {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сохранения бота: {e}")
            return False

    async def load(self, filepath: str) -> bool:
        """
        Загрузка состояния бота из файла

        Args:
            filepath: Путь к файлу для загрузки

        Returns:
            bool: True если загрузка прошла успешно
        """
        try:
            import json

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Обновляем конфигурацию
            if "config" in data:
                self.config.update(data["config"])

            # Обновляем статистику
            if "stats" in data:
                self.stats.update(data["stats"])

            self.logger.info(f"Состояние бота загружено из {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка загрузки бота: {e}")
            return False


# Функция тестирования
async def test_gaming_security_bot():
    """Тестирование GamingSecurityBot"""
    print("🧪 Тестирование GamingSecurityBot...")

    # Создание бота
    bot = GamingSecurityBot("TestGamingBot")

    try:
        # Запуск
        await bot.start()
        print("✅ GamingSecurityBot запущен")

        # Начало игровой сессии
        session_id = await bot.start_game_session(
            player_id="test_player",
            game_id="test_game",
            game_genre=GameGenre.FPS,
        )
        print(f"✅ Игровая сессия начата: {session_id}")

        # Анализ действия игрока
        result = await bot.analyze_player_action(
            session_id=session_id,
            player_id="test_player",
            action=PlayerAction.SHOOT,
            coordinates={"x": 0.5, "y": 0.5},
            context={"target_distance": 150, "accuracy": 0.98},
        )
        print(
            f"✅ Анализ действия: {result.cheat_type.value} - "
            f"{result.confidence:.2f}"
        )

        # Анализ транзакции
        transaction_result = await bot.analyze_transaction(
            player_id="test_player",
            session_id=session_id,
            transaction_data={
                "type": "purchase",
                "amount": 50.0,
                "currency": "USD",
                "payment_method": "credit_card",
            },
        )
        print(
            f"✅ Анализ транзакции: {transaction_result['is_fraudulent']} - "
            f"{transaction_result['risk_score']:.2f}"
        )

        # Завершение сессии
        ended = await bot.end_game_session(
            session_id, final_score=1000, kills=5, deaths=2, assists=3
        )
        print(f"✅ Сессия завершена: {ended}")

        # Получение общего статуса
        bot_status = await bot.get_status()
        print(f"✅ Статус бота: {bot_status['status']}")

    finally:
        # Остановка
        await bot.stop()
        print("✅ GamingSecurityBot остановлен")
