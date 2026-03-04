#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 Dark Web Monitoring Agent
Агент для мониторинга утечек данных в Dark Web

Гибридный подход:
- Отдельный агент для изоляции персональных данных
- Использует общие утилиты из ThreatIntelligenceAgent
- Регистрируется в SFM как отдельный модуль

Дата создания: 9 декабря 2025
Версия: 1.0.0
"""

import hashlib
import logging
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
import json

# Импорты (будут доступны на сервере)
try:
    from security.base import SecurityBase
    from security.ai_agents.threat_intelligence_agent import ThreatIntelligenceAgent
    from security.ai_agents.threat_monitoring_interface import (
        ThreatMonitoringInterface,
        ThreatEvent,
        get_threat_event_bus
    )
except ImportError:
    # Для локальной разработки создаем заглушки
    class SecurityBase:
        def __init__(self, config: Optional[Dict[str, Any]] = None):
            self.config = config or {}
            self.logger = logging.getLogger(self.__class__.__name__)

    # Заглушки для интерфейса мониторинга угроз
    class ThreatMonitoringInterface:
        pass

    @dataclass
    class ThreatEvent:
        event_id: str = ""
        agent_name: str = ""
        threat_type: str = ""
        severity: str = ""
        source: str = ""
        target: str = ""
        timestamp: str = ""
        metadata: Dict[str, Any] = None
        description: Optional[str] = None

    def get_threat_event_bus():
        return None


@dataclass
class BreachInfo:
    """Информация об утечке данных"""
    id: str
    email: str
    breach_name: str
    count: int
    detected_at: str
    severity: str  # "low", "medium", "high", "critical"
    description: Optional[str] = None
    affected_data: Optional[List[str]] = None  # ["Email", "Passwords", "Phone"]
    breach_date: Optional[str] = None
    added_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DarkWebMonitoringAgent(SecurityBase, ThreatMonitoringInterface):
    """
    Агент для мониторинга утечек данных в Dark Web

    Гибридный подход:
    - Использует общие утилиты из ThreatIntelligenceAgent
    - Изолированная обработка персональных данных
    - K-анонимность для Have I Been Pwned API
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация агента

        Args:
            config: Конфигурация агента
                - hibp_api_key: API ключ для Have I Been Pwned
                - breachdirectory_api_key: API ключ для BreachDirectory
                - cache_ttl: TTL для кэша (секунды, по умолчанию 86400 = 24 часа)
                - monitoring_interval: Интервал мониторинга (часы, по умолчанию 24)
        """
        super().__init__(config)

        # Устанавливаем config явно (SecurityBase не устанавливает его)
        self.config = config if config is not None else {}

        # Инициализация логгера
        self.logger = logging.getLogger(self.__class__.__name__)

        # Конфигурация
        self.hibp_api_key = self.config.get("hibp_api_key", "")
        self.breachdirectory_api_key = self.config.get("breachdirectory_api_key", "")
        self.cache_ttl = self.config.get("cache_ttl", 86400)  # 24 часа
        self.monitoring_interval = self.config.get("monitoring_interval", 24)  # 24 часа

        # Гибридный подход: используем утилиты из ThreatIntelligenceAgent
        try:
            self.threat_intel = ThreatIntelligenceAgent(config)
            # Переиспользование методов валидации и HTTP клиента
            self._validate_email = getattr(self.threat_intel, '_validate_email', self._default_validate_email)
            self._validate_phone = getattr(self.threat_intel, '_validate_phone', self._default_validate_phone)
            self._make_http_request = getattr(self.threat_intel, '_make_http_request', self._default_http_request)
            self.logger.info("✅ Успешно подключены утилиты из ThreatIntelligenceAgent")
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось подключить ThreatIntelligenceAgent: {e}. Используются методы по умолчанию.")
            self._validate_email = self._default_validate_email
            self._validate_phone = self._default_validate_phone
            self._make_http_request = self._default_http_request

        # Кэш для результатов проверок (in-memory, для продакшена использовать Redis)
        self.cache: Dict[str, Dict[str, Any]] = {}

        # Словарь активных мониторингов: {user_id: {email, phone, last_check, next_check, interval}}
        self.active_monitoring: Dict[str, Dict[str, Any]] = {}

        # Интеграция с ThreatEventBus для обмена данными
        try:
            self.event_bus = get_threat_event_bus()
            if self.event_bus:
                self.event_bus.subscribe(self, event_types=["breach", "*"])
                self.logger.info("✅ Подписан на ThreatEventBus")
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось подключиться к ThreatEventBus: {e}")
            self.event_bus = None

        self.logger.info("🌐 DarkWebMonitoringAgent инициализирован")

    # MARK: - Утилиты валидации (по умолчанию, если ThreatIntelligenceAgent недоступен)

    def _default_validate_email(self, email: str) -> bool:
        """Валидация email адреса"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _default_validate_phone(self, phone: str) -> bool:
        """Валидация номера телефона"""
        import re
        # Убираем все нецифровые символы
        digits_only = re.sub(r'\D', '', phone)
        # Проверяем, что осталось 10-15 цифр
        return 10 <= len(digits_only) <= 15

    def _default_http_request(
            self, url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None,
            data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        HTTP запрос по умолчанию (для локальной разработки)

        Args:
            url: URL для запроса
            method: HTTP метод (GET, POST, etc.)
            headers: Заголовки запроса
            data: Тело запроса (для POST)

        Returns:
            Словарь с результатом запроса:
            {
                "status_code": int,
                "data": dict/list - JSON ответ, если доступен
                "headers": dict - заголовки ответа
                "error": str - сообщение об ошибке, если есть
            }
        """
        try:
            import requests
            response = requests.request(
                method=method,
                url=url,
                headers=headers or {},
                json=data if method in ["POST", "PUT", "PATCH"] else None,
                params=data if method == "GET" else None,
                timeout=30
            )

            # Пытаемся распарсить JSON ответ
            try:
                response_data = response.json() if response.content else []
            except (ValueError, json.JSONDecodeError):
                # Если не JSON, возвращаем текст
                response_data = response.text if response.content else []

            return {
                "status_code": response.status_code,
                "data": response_data,
                "headers": dict(response.headers)
            }
        except requests.exceptions.Timeout:
            self.logger.error(f"❌ HTTP запрос превысил время ожидания: {url}")
            return {"status_code": 504, "error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Ошибка HTTP запроса: {e}")
            return {"status_code": 500, "error": str(e)}
        except Exception as e:
            self.logger.error(f"❌ Неожиданная ошибка HTTP запроса: {e}")
            return {"status_code": 500, "error": str(e)}

    # MARK: - K-анонимность для Have I Been Pwned API

    def _hash_email(self, email: str) -> Tuple[str, str]:
        """
        Хеширование email для k-анонимности (Have I Been Pwned API)

        Returns:
            (hash_prefix, full_hash): Префикс из 5 символов и полный хеш
        """
        email_lower = email.lower().strip()
        email_hash = hashlib.sha1(email_lower.encode()).hexdigest().upper()
        hash_prefix = email_hash[:5]
        return hash_prefix, email_hash

    def _check_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Проверка кэша

        Args:
            key: Ключ кэша

        Returns:
            Закэшированные данные или None, если кэш пуст или истек
        """
        if key in self.cache:
            cached_data = self.cache[key]
            cache_time = cached_data.get("cached_at", 0)
            current_time = time.time()

            # Проверяем TTL
            age = current_time - cache_time
            if age < self.cache_ttl:
                remaining_ttl = self.cache_ttl - age
                self.logger.debug(f"✅ Данные найдены в кэше для ключа: {key} (TTL осталось: {int(remaining_ttl)}s)")
                return cached_data.get("data")
            else:
                # Удаляем устаревшие данные
                del self.cache[key]
                self.logger.debug(f"⏰ Кэш истек для ключа: {key} (возраст: {int(age)}s)")

        return None

    def _set_cache(self, key: str, data: Dict[str, Any]):
        """
        Сохранение в кэш

        Args:
            key: Ключ кэша
            data: Данные для сохранения
        """
        # Очистка старых записей, если кэш переполнен (максимум 1000 записей)
        if len(self.cache) >= 1000:
            # Удаляем самые старые записи (оставляем 800)
            sorted_cache = sorted(
                self.cache.items(),
                key=lambda x: x[1].get("cached_at", 0)
            )
            for old_key, _ in sorted_cache[:200]:
                del self.cache[old_key]
            self.logger.debug("🧹 Очистка кэша: удалено 200 старых записей")

        self.cache[key] = {
            "data": data,
            "cached_at": time.time()
        }
        self.logger.debug(f"💾 Данные сохранены в кэш: {key} (всего записей: {len(self.cache)})")

    def clear_cache(self, pattern: Optional[str] = None) -> int:
        """
        Очистка кэша

        Args:
            pattern: Опциональный паттерн для удаления только соответствующих ключей
                    Если None, очищает весь кэш

        Returns:
            Количество удаленных записей
        """
        if pattern is None:
            count = len(self.cache)
            self.cache.clear()
            self.logger.info(f"🧹 Весь кэш очищен ({count} записей)")
            return count
        else:
            # Удаляем записи, соответствующие паттерну
            keys_to_delete = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self.cache[key]
            self.logger.info(f"🧹 Удалено {len(keys_to_delete)} записей по паттерну: {pattern}")
            return len(keys_to_delete)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Получение статистики кэша

        Returns:
            Словарь со статистикой кэша
        """
        current_time = time.time()
        expired_count = 0
        valid_count = 0
        oldest_age = 0
        newest_age = float('inf')

        for cached_data in self.cache.values():
            cache_time = cached_data.get("cached_at", 0)
            age = current_time - cache_time

            if age < self.cache_ttl:
                valid_count += 1
            else:
                expired_count += 1

            oldest_age = max(oldest_age, age)
            newest_age = min(newest_age, age) if newest_age != float('inf') else age

        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_count,
            "expired_entries": expired_count,
            "oldest_entry_age": int(oldest_age) if len(self.cache) > 0 else 0,
            "newest_entry_age": int(newest_age) if len(self.cache) > 0 and newest_age != float('inf') else 0,
            "cache_ttl": self.cache_ttl,
            "max_entries": 1000
        }

    # MARK: - Проверка через Have I Been Pwned API

    def check_email_breach_hibp(self, email: str) -> List[BreachInfo]:
        """
        Проверка email на утечки через Have I Been Pwned API с k-анонимностью

        Args:
            email: Email адрес для проверки

        Returns:
            Список найденных утечек (BreachInfo)
        """
        if not self._validate_email(email):
            self.logger.warning(f"❌ Некорректный email: {email}")
            return []

        # Проверяем кэш
        cache_key = f"hibp:{email}"
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return [BreachInfo(**breach) for breach in cached_result]

        try:
            # K-анонимность: отправляем только первые 5 символов хеша
            hash_prefix, full_hash = self._hash_email(email)

            url = f"https://api.haveibeenpwned.com/v3/range/{hash_prefix}"
            headers = {
                "hibp-api-key": self.hibp_api_key,
                "User-Agent": "ALADDIN-Security-Agent/1.0"
            }

            self.logger.info(f"🔍 Проверка утечек для email через HIBP (k-анонимность: {hash_prefix}...)")
            response = self._make_http_request(url, method="GET", headers=headers)

            if response.get("status_code") == 200:
                # HIBP возвращает список хешей в формате "HASH:COUNT"
                hash_data = response.get("data", "")

                breaches = []
                # Ищем полный хеш в ответе
                for line in hash_data.split("\n"):
                    if ":" in line:
                        hash_suffix, count = line.split(":", 1)
                        if hash_prefix + hash_suffix.upper() == full_hash:
                            breach = BreachInfo(
                                id=f"hibp_{hash_prefix}_{hash_suffix}",
                                email=email,
                                breach_name=f"Have I Been Pwned - {count} раз",
                                count=int(count.strip()),
                                detected_at=datetime.now().isoformat(),
                                severity="high" if int(count) > 1000 else "medium",
                                description="Найдено в базе Have I Been Pwned",
                                affected_data=["Email", "Passwords"]
                            )
                            breaches.append(breach)

                # Сохраняем в кэш
                self._set_cache(cache_key, [breach.to_dict() for breach in breaches])

                self.logger.info(f"✅ Найдено утечек через HIBP: {len(breaches)}")
                return breaches
            else:
                self.logger.warning(f"⚠️ HIBP API вернул статус: {response.get('status_code')}")
                return []

        except Exception as e:
            self.logger.error(f"❌ Ошибка при проверке через HIBP: {e}")
            return []

    # MARK: - Проверка через BreachDirectory API

    def check_email_breach_breachdirectory(self, email: str) -> List[BreachInfo]:
        """
        Проверка email на утечки через BreachDirectory API

        API Endpoint: https://BreachDirectory.com/api_usage
        Format: GET ?method=email&key=$Key&query=$Email
        Response: Array of breach objects with fields: title, domain, email, username, ip

        Args:
            email: Email адрес для проверки

        Returns:
            Список найденных утечек (BreachInfo)
        """
        if not self._validate_email(email):
            return []

        if not self.breachdirectory_api_key:
            self.logger.warning("⚠️ BreachDirectory API ключ не настроен")
            return []

        # Проверяем кэш
        cache_key = f"breachdirectory:{email}"
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return [BreachInfo(**breach) for breach in cached_result]

        try:
            # BreachDirectory API использует GET запрос с параметрами
            base_url = "https://BreachDirectory.com/api_usage"
            params = {
                "method": "email",
                "key": self.breachdirectory_api_key,
                "query": email
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"

            headers = {
                "User-Agent": "ALADDIN-Security-Agent/1.0",
                "Accept": "application/json"
            }

            self.logger.info(f"🔍 Проверка утечек для email через BreachDirectory: {email}")
            response = self._make_http_request(url, method="GET", headers=headers)

            status_code = response.get("status_code")
            response_data = response.get("data", [])

            # Обработка успешного ответа
            if status_code == 200:
                breaches = []

                # BreachDirectory возвращает массив объектов напрямую
                if isinstance(response_data, list) and len(response_data) > 0:
                    # Группируем по названию утечки (title)
                    breach_groups: Dict[str, List[Dict]] = {}

                    for breach_item in response_data:
                        title = breach_item.get("title", "Unknown Breach")
                        domain = breach_item.get("domain", "")

                        # Создаем уникальный ключ для группировки
                        breach_key = f"{title}_{domain}".lower()

                        if breach_key not in breach_groups:
                            breach_groups[breach_key] = []
                        breach_groups[breach_key].append(breach_item)

                    # Создаем BreachInfo для каждой группы
                    for breach_key, breach_items in breach_groups.items():
                        first_item = breach_items[0]
                        title = first_item.get("title", "Unknown Breach")
                        domain = first_item.get("domain", "")

                        # Определяем тяжесть по количеству найденных записей
                        severity = "medium"
                        if len(breach_items) > 10:
                            severity = "critical"
                        elif len(breach_items) > 5:
                            severity = "high"
                        elif len(breach_items) == 1:
                            severity = "low"

                        # Формируем список затронутых данных
                        affected_data = ["Email"]
                        if any(item.get("username") for item in breach_items):
                            affected_data.append("Username")
                        if any(item.get("ip") for item in breach_items):
                            affected_data.append("IP Address")
                        if domain:
                            affected_data.append(f"Domain: {domain}")

                        breach = BreachInfo(
                            id=f"bd_{breach_key}_{hash(email)}",
                            email=email,
                            breach_name=title if title else f"Breach on {domain}" if domain else "Unknown Breach",
                            count=len(breach_items),
                            detected_at=datetime.now().isoformat(),
                            severity=severity,
                            description=f"Найдено в базе BreachDirectory. Домен: {domain}" if domain else "Найдено в базе BreachDirectory",
                            affected_data=affected_data
                        )
                        breaches.append(breach)

                # Сохраняем в кэш
                self._set_cache(cache_key, [breach.to_dict() for breach in breaches])

                self.logger.info(f"✅ Найдено утечек через BreachDirectory: {len(breaches)}")
                return breaches

            # Обработка ошибок API
            elif status_code == 401:
                error_msg = "Invalid or expired API key"
                if isinstance(response_data, dict):
                    error_msg = response_data.get("error", error_msg)
                self.logger.error(f"❌ BreachDirectory API: {error_msg}")
                return []
            elif status_code == 429:
                self.logger.warning("⚠️ BreachDirectory API: Rate limit exceeded. Попробуйте позже.")
                return []
            elif status_code == 400:
                error_msg = "Invalid request"
                if isinstance(response_data, dict):
                    error_msg = response_data.get("error", error_msg)
                self.logger.warning(f"⚠️ BreachDirectory API: {error_msg}")
                return []
            else:
                # Пустой ответ означает, что утечек не найдено
                if isinstance(response_data, list) and len(response_data) == 0:
                    self.logger.info(f"✅ Email не найден в базе BreachDirectory: {email}")
                    # Сохраняем пустой результат в кэш на более короткое время
                    self._set_cache(cache_key, [])
                    return []
                else:
                    self.logger.warning(f"⚠️ BreachDirectory API вернул статус: {status_code}")
                    return []

        except Exception as e:
            self.logger.error(f"❌ Ошибка при проверке через BreachDirectory: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return []

    # MARK: - Проверка через российские базы утечек

    def check_email_breach_russian(self, email: str) -> List[BreachInfo]:
        """
        Проверка email на утечки через российские базы утечек

        Поддерживаемые источники:
        - DLBI (Data Leakage & Breach Intelligence) - если доступен API
        - Российские публичные базы утечек
        - Внутренние базы ALADDIN (если доступны)

        Args:
            email: Email адрес для проверки

        Returns:
            Список найденных утечек (BreachInfo)
        """
        if not self._validate_email(email):
            return []

        # Проверяем кэш
        cache_key = f"russian:{email}"
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return [BreachInfo(**breach) for breach in cached_result]

        all_breaches: List[BreachInfo] = []

        # Проверка через DLBI API (если настроен)
        dlbi_api_key = self.config.get("dlbi_api_key")
        if dlbi_api_key:
            try:
                dlbi_breaches = self._check_dlbi_breach(email, dlbi_api_key)
                all_breaches.extend(dlbi_breaches)
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка при проверке через DLBI: {e}")

        # Проверка через внутренние базы ALADDIN (если доступны)
        # TODO: Интеграция с внутренними базами утечек ALADDIN
        # if self.config.get("internal_db_enabled"):
        #     try:
        #         internal_breaches = self._check_internal_breach_db(email)
        #         all_breaches.extend(internal_breaches)
        #     except Exception as e:
        #         self.logger.warning(f"⚠️ Ошибка при проверке внутренней БД: {e}")

        # Сохраняем в кэш (даже пустой результат)
        self._set_cache(cache_key, [breach.to_dict() for breach in all_breaches])

        if len(all_breaches) > 0:
            self.logger.info(f"✅ Найдено утечек через российские базы: {len(all_breaches)}")
        else:
            self.logger.debug(f"✅ Email не найден в российских базах утечек: {email}")

        return all_breaches

    def _check_dlbi_breach(self, email: str, api_key: str) -> List[BreachInfo]:
        """
        Проверка через DLBI (Data Leakage & Breach Intelligence) API

        Args:
            email: Email для проверки
            api_key: API ключ DLBI

        Returns:
            Список найденных утечек
        """
        # TODO: Интеграция с DLBI API после получения доступа
        # Примерная структура запроса (нужно уточнить с документацией DLBI):
        # url = "https://api.dlbi.ru/v1/check"
        # headers = {"Authorization": f"Bearer {api_key}"}
        # data = {"email": email}

        self.logger.debug("🔍 Проверка через DLBI API (TODO - требуется доступ к API)")
        return []

    def _check_internal_breach_db(self, email: str) -> List[BreachInfo]:
        """
        Проверка через внутренние базы утечек ALADDIN

        Args:
            email: Email для проверки

        Returns:
            Список найденных утечек
        """
        # TODO: Интеграция с внутренними базами данных ALADDIN
        # Это может быть локальная база данных или внутренний API сервера

        self.logger.debug("🔍 Проверка через внутренние базы ALADDIN (TODO)")
        return []

    # MARK: - Основной метод проверки

    def check_email_breach(
            self, email: str, include_hibp: bool = True,
            include_breachdirectory: bool = True,
            include_russian: bool = True) -> Dict[str, Any]:
        """
        Комплексная проверка email на утечки через все доступные источники

        Args:
            email: Email адрес для проверки
            include_hibp: Включить проверку через Have I Been Pwned
            include_breachdirectory: Включить проверку через BreachDirectory
            include_russian: Включить проверку через российские базы

        Returns:
            Словарь с результатами проверки:
            {
                "email": str,
                "breaches_found": int,
                "breaches": List[BreachInfo],
                "checked_at": str,
                "sources": List[str]
            }
        """
        self.logger.info(f"🔍 Начало проверки email на утечки: {email}")

        all_breaches: List[BreachInfo] = []
        sources_checked = []

        # Проверка через Have I Been Pwned
        if include_hibp:
            try:
                hibp_breaches = self.check_email_breach_hibp(email)
                all_breaches.extend(hibp_breaches)
                sources_checked.append("Have I Been Pwned")
            except Exception as e:
                self.logger.error(f"❌ Ошибка при проверке через HIBP: {e}")

        # Проверка через BreachDirectory
        if include_breachdirectory:
            try:
                bd_breaches = self.check_email_breach_breachdirectory(email)
                all_breaches.extend(bd_breaches)
                sources_checked.append("BreachDirectory")
            except Exception as e:
                self.logger.error(f"❌ Ошибка при проверке через BreachDirectory: {e}")

        # Проверка через российские базы
        if include_russian:
            try:
                russian_breaches = self.check_email_breach_russian(email)
                all_breaches.extend(russian_breaches)
                sources_checked.append("Russian databases")
            except Exception as e:
                self.logger.error(f"❌ Ошибка при проверке через российские базы: {e}")

        # Убираем дубликаты (по breach_name)
        unique_breaches = {}
        for breach in all_breaches:
            key = breach.breach_name.lower()
            if key not in unique_breaches or breach.count > unique_breaches[key].count:
                unique_breaches[key] = breach

        result = {
            "email": email,
            "breaches_found": len(unique_breaches),
            "breaches": [breach.to_dict() for breach in unique_breaches.values()],
            "checked_at": datetime.now().isoformat(),
            "sources": sources_checked
        }

        self.logger.info(f"✅ Проверка завершена. Найдено утечек: {len(unique_breaches)}")
        return result

    # MARK: - Проверка телефона

    def check_phone_breach(self, phone: str) -> Dict[str, Any]:
        """
        Проверка номера телефона на утечки

        Args:
            phone: Номер телефона для проверки

        Returns:
            Словарь с результатами проверки
        """
        if not self._validate_phone(phone):
            return {
                "error": "Invalid phone number",
                "phone": phone
            }

        # TODO: Интеграция с API для проверки телефонов
        self.logger.info(f"🔍 Проверка телефона на утечки: {phone} (TODO)")

        return {
            "phone": phone,
            "breaches_found": 0,
            "breaches": [],
            "checked_at": datetime.now().isoformat()
        }

    # MARK: - Мониторинг данных пользователя

    def monitor_user_data(
            self, user_id: str, email: Optional[str] = None,
            phone: Optional[str] = None) -> Dict[str, Any]:
        """
        Мониторинг данных пользователя (email и/или телефон)

        Args:
            user_id: ID пользователя
            email: Email для мониторинга
            phone: Телефон для мониторинга

        Returns:
            Результат проверки
        """
        results = {}

        if email:
            results["email_check"] = self.check_email_breach(email)

        if phone:
            results["phone_check"] = self.check_phone_breach(phone)

        return {
            "user_id": user_id,
            "checked_at": datetime.now().isoformat(),
            "results": results
        }

    # MARK: - Запуск автоматического мониторинга

    def start_monitoring(
            self, user_id: str, email: Optional[str] = None,
            phone: Optional[str] = None, interval_hours: int = 24) -> Dict[str, Any]:
        """
        Запуск автоматического мониторинга данных пользователя

        Args:
            user_id: ID пользователя
            email: Email для мониторинга
            phone: Телефон для мониторинга
            interval_hours: Интервал проверки в часах (по умолчанию 24)

        Returns:
            Результат запуска мониторинга
        """
        if not email and not phone:
            return {
                "error": "Email или phone должен быть указан",
                "user_id": user_id
            }

        next_check = datetime.now() + timedelta(hours=interval_hours)

        self.active_monitoring[user_id] = {
            "email": email,
            "phone": phone,
            "interval_hours": interval_hours,
            "last_check": None,
            "next_check": next_check.isoformat(),
            "started_at": datetime.now().isoformat()
        }

        self.logger.info(f"✅ Запущен мониторинг для пользователя {user_id}. Следующая проверка: {next_check}")

        return {
            "success": True,
            "user_id": user_id,
            "next_check": next_check.isoformat(),
            "interval_hours": interval_hours
        }

    def stop_monitoring(self, user_id: str) -> Dict[str, Any]:
        """
        Остановка автоматического мониторинга

        Args:
            user_id: ID пользователя

        Returns:
            Результат остановки
        """
        if user_id in self.active_monitoring:
            del self.active_monitoring[user_id]
            self.logger.info(f"⏹️ Мониторинг остановлен для пользователя {user_id}")
            return {
                "success": True,
                "user_id": user_id
            }
        else:
            return {
                "success": False,
                "error": "Мониторинг не найден",
                "user_id": user_id
            }

    def get_monitoring_status(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Получение статуса мониторинга

        Args:
            user_id: ID пользователя (если None, возвращает статус всех мониторингов)

        Returns:
            Статус мониторинга
        """
        if user_id:
            if user_id in self.active_monitoring:
                return {
                    "is_monitoring": True,
                    "user_id": user_id,
                    "status": self.active_monitoring[user_id]
                }
            else:
                return {
                    "is_monitoring": False,
                    "user_id": user_id
                }
        else:
            return {
                "total_active": len(self.active_monitoring),
                "monitoring": self.active_monitoring
            }

    # MARK: - Реализация ThreatMonitoringInterface

    def collect_threats(self) -> List[Dict[str, Any]]:
        """
        Сбор угроз (утечек данных) из всех активных мониторингов

        Returns:
            Список словарей с информацией об утечках
        """
        all_threats = []

        for user_id, monitoring_info in self.active_monitoring.items():
            email = monitoring_info.get("email")

            if email:
                try:
                    result = self.check_email_breach(email)
                    if result.get("breaches_found", 0) > 0:
                        for breach in result.get("breaches", []):
                            threat = {
                                "user_id": user_id,
                                "type": "email_breach",
                                "target": email,
                                "breach": breach,
                                "collected_at": datetime.now().isoformat()
                            }
                            all_threats.append(threat)
                except Exception as e:
                    self.logger.error(f"❌ Ошибка при сборе угроз для {user_id}: {e}")

        return all_threats

    def analyze_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Анализ собранных угроз (утечек)

        Args:
            threats: Список угроз для анализа

        Returns:
            Список проанализированных угроз с рекомендациями
        """
        analyzed_threats = []

        for threat in threats:
            breach = threat.get("breach", {})
            severity = breach.get("severity", "medium")
            affected_data = breach.get("affected_data", [])

            # Определяем приоритет на основе тяжести
            priority = "medium"
            if severity == "critical":
                priority = "critical"
            elif severity == "high":
                priority = "high"
            elif severity == "low":
                priority = "low"

            # Формируем рекомендации
            recommendations = []
            if "Passwords" in affected_data:
                recommendations.append("Немедленно смените пароль")
            if "Email" in affected_data:
                recommendations.append("Включите двухфакторную аутентификацию")
            if "Phone" in affected_data:
                recommendations.append("Будьте осторожны с входящими звонками и SMS")

            analyzed_threat = {
                **threat,
                "priority": priority,
                "recommendations": recommendations,
                "requires_immediate_action": severity in ["critical", "high"],
                "analyzed_at": datetime.now().isoformat()
            }
            analyzed_threats.append(analyzed_threat)

        return analyzed_threats

    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Отправка уведомления об утечке данных

        Args:
            alert: Словарь с информацией об уведомлении

        Returns:
            True если уведомление отправлено успешно
        """
        try:
            user_id = alert.get("user_id")
            breach = alert.get("breach", {})
            severity = breach.get("severity", "medium")

            # Создаем событие для публикации в шине событий
            if self.event_bus:
                event = ThreatEvent(
                    event_id=f"breach_{user_id}_{int(time.time())}",
                    agent_name=self.__class__.__name__,
                    threat_type="breach",
                    severity=severity,
                    source="dark_web_monitoring",
                    target=alert.get("target", ""),
                    timestamp=datetime.now().isoformat(),
                    metadata=alert,
                    description=f"Обнаружена утечка данных: {breach.get('breach_name', 'Unknown')}"
                )

                notified = self.event_bus.publish(event)
                self.logger.info(f"📢 Событие опубликовано, уведомлено агентов: {notified}")

            # Здесь можно добавить отправку уведомления пользователю
            # через email, push-уведомление, SMS и т.д.

            self.logger.info(f"✅ Уведомление отправлено для пользователя {user_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при отправке уведомления: {e}")
            return False

    def receive_threat_event(self, event: ThreatEvent) -> bool:
        """
        Получение информации об угрозе от другого агента

        Args:
            event: Событие угрозы от другого агента

        Returns:
            True если событие успешно обработано
        """
        try:
            # Если другой агент сообщил об утечке, можем синхронизировать информацию
            if event.threat_type == "breach" and event.target:
                # Проверяем, не мониторим ли мы этот email/телефон
                for user_id, monitoring_info in self.active_monitoring.items():
                    if event.target in [monitoring_info.get("email"), monitoring_info.get("phone")]:
                        # Можно обновить информацию или добавить в кэш
                        self.logger.info(f"🔄 Получено событие от {event.agent_name} для {event.target}")
                        return True

            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при обработке события: {e}")
            return False


# MARK: - Точка входа для тестирования

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Тестирование агента
    print("🌐 Тестирование DarkWebMonitoringAgent")

    config = {
        "hibp_api_key": "your-api-key-here",  # Заменить на реальный ключ
        "cache_ttl": 86400
    }

    agent = DarkWebMonitoringAgent(config)

    # Тестовый email
    test_email = "test@example.com"
    print(f"\n🔍 Проверка email: {test_email}")
    result = agent.check_email_breach(test_email)
    print(f"Результат: {json.dumps(result, indent=2, ensure_ascii=False)}")
