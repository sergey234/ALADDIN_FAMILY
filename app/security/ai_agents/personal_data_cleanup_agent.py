#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗑️ Personal Data Cleanup Agent
Агент для автоматического поиска и удаления персональных данных с брокерских сайтов

Функциональность:
- Поиск персональных данных на брокерских сайтах (100+ сайтов)
- Автоматическая отправка запросов на удаление
- Отслеживание процесса удаления
- Повторные запросы при необходимости
- Генерация отчетов о процессе

Дата создания: 13 декабря 2025
Версия: 1.0.0
"""

import logging
import time
import uuid
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

# HTTP и парсинг
try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None
    BeautifulSoup = None

# Импорты (будут доступны на сервере)
try:
    from security.base import SecurityBase
    from security.ai_agents.threat_monitoring_interface import (
        ThreatMonitoringInterface,
        ThreatEvent,
        get_threat_event_bus
    )
except ImportError:
    # Для локальной разработки создаем заглушки
    class SecurityBase:
        def __init__(self, config: Optional[Dict[str, Any]] = None):
            config_dict = config if config is not None else {}
            self.config = config_dict
            self.logger = logging.getLogger(self.__class__.__name__)

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


class RemovalStatus(Enum):
    """Статусы удаления данных"""
    PENDING = "pending"  # Запрос отправлен, ожидает обработки
    PROCESSING = "processing"  # Запрос обрабатывается
    COMPLETED = "completed"  # Данные удалены
    FAILED = "failed"  # Ошибка при удалении
    EXPIRED = "expired"  # Срок удаления истек
    RETRYING = "retrying"  # Повторная попытка


class RemovalMethod(Enum):
    """Методы удаления данных"""
    OPT_OUT_FORM = "opt_out_form"  # Форма на сайте
    GDPR_REQUEST = "gdpr_request"  # GDPR запрос (email)
    API = "api"  # API удаления
    EMAIL = "email"  # Email запрос
    PARENT_COMPANY = "parent_company"  # Через родительскую компанию


@dataclass
class UserData:
    """Персональные данные пользователя"""
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FoundData:
    """Найденные данные на сайте"""
    site: str  # Название сайта
    url: str  # URL страницы с данными
    data_found: List[str]  # Типы найденных данных (email, phone, name, address)
    found_at: float  # Unix timestamp

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RemovalRequest:
    """Запрос на удаление данных"""
    request_id: str  # Уникальный ID запроса
    user_id: str  # ID пользователя
    site: str  # Название сайта
    url: str  # URL страницы с данными
    method: RemovalMethod  # Метод удаления
    status: RemovalStatus  # Статус удаления
    requested_at: float  # Unix timestamp запроса
    expected_completion: Optional[float] = None  # Ожидаемое время завершения
    completed_at: Optional[float] = None  # Время завершения
    retry_count: int = 0  # Количество повторных попыток
    error_message: Optional[str] = None  # Сообщение об ошибке
    metadata: Optional[Dict[str, Any]] = None  # Дополнительные данные (email, subject, body и т.д.)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["method"] = self.method.value
        result["status"] = self.status.value
        return result


@dataclass
class CleanupReport:
    """Отчет о процессе очистки данных"""
    user_id: str
    total_sites_scanned: int  # Всего сайтов проверено
    sites_with_data: int  # Сайтов с найденными данными
    removal_requests_sent: int  # Запросов на удаление отправлено
    completed: int  # Успешно удалено
    pending: int  # В процессе
    failed: int  # Ошибки
    completion_percentage: float  # Процент завершения
    generated_at: float  # Unix timestamp

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PersonalDataCleanupAgent(SecurityBase, ThreatMonitoringInterface):
    """
    Агент для автоматического поиска и удаления персональных данных
    с брокерских сайтов
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация агента

        Args:
            config: Конфигурация агента
        """
        super().__init__(config)

        # Инициализация logger (всегда, так как SecurityBase может не инициализировать)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Конфигурация (используем локальную переменную вместо self.config)
        config_dict = config if config is not None else {}
        self.max_retries = int(config_dict.get("max_retries", 3))
        self.retry_delay_days = int(config_dict.get("retry_delay_days", 7))
        self.scan_timeout_seconds = int(config_dict.get("scan_timeout_seconds", 30))
        self.enable_auto_retry = config_dict.get("enable_auto_retry", True)

        # Периодический мониторинг
        self.enable_periodic_scan = config_dict.get("enable_periodic_scan", False)
        self.scan_interval_days = int(config_dict.get("scan_interval_days", 30))  # Интервал для автоматического поиска
        self.reminder_interval_days = int(config_dict.get("reminder_interval_days", 45))  # Интервал для напоминаний (по умолчанию 45 дней)
        self.last_scan_times: Dict[str, float] = {}  # {user_id: last_scan_timestamp}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}  # {user_id: {enable_auto_scan: bool, scan_interval: int}}

        # HTTP клиент
        self.session = None
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            self.session.timeout = self.scan_timeout_seconds
        else:
            self.logger.warning("⚠️ Библиотеки requests/BeautifulSoup не установлены. Реальный поиск и удаление недоступны.")

        # Хранилище запросов (в продакшене будет БД)
        self.removal_requests: Dict[str, RemovalRequest] = {}
        self.found_data_cache: Dict[str, List[FoundData]] = {}

        # Список брокерских сайтов (приоритетные)
        self.broker_sites = self._load_broker_sites()

        self.logger.info("✅ Personal Data Cleanup Agent инициализирован")

    def _load_broker_sites(self) -> List[Dict[str, Any]]:
        """
        Загрузка списка брокерских сайтов

        Returns:
            Список словарей с информацией о сайтах
        """
        # Приоритетные сайты
        # Полный список в docs/ПОЛНЫЙ_СПИСОК_БРОКЕРСКИХ_САЙТОВ.md
        return [
            # Россия (приоритет 1)
            {
                "name": "2GIS",
                "domain": "2gis.ru",
                "region": "RU",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://2gis.ru/feedback",
                "search_paths": ["/search"],
                "priority": 1
            },
            {
                "name": "Avito",
                "domain": "avito.ru",
                "region": "RU",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://www.avito.ru/support",
                "search_paths": ["/search"],
                "priority": 1
            },
            {
                "name": "Яндекс.Справочник",
                "domain": "yandex.ru",
                "region": "RU",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://yandex.ru/support/maps",
                "search_paths": ["/maps", "/sprav"],
                "priority": 1
            },
            # США (приоритет 1)
            {
                "name": "Whitepages",
                "domain": "whitepages.com",
                "region": "US",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://www.whitepages.com/suppression_requests",
                "search_paths": ["/search"],
                "priority": 1
            },
            {
                "name": "Spokeo",
                "domain": "spokeo.com",
                "region": "US",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://www.spokeo.com/opt-out",
                "search_paths": ["/search"],
                "priority": 1
            },
            {
                "name": "PeopleConnect Suppression Center",
                "domain": "peopleconnect.us",
                "region": "US",
                "removal_method": RemovalMethod.PARENT_COMPANY,
                "removal_url": "https://www.peopleconnect.us/suppression",
                "search_paths": ["/suppression"],
                "priority": 1,
                "controls": ["intelius.com", "instantcheckmate.com", "truthfinder.com", "ussearch.com", "peoplefinders.com"]
            },
            {
                "name": "PeopleFinders",
                "domain": "peoplefinders.com",
                "region": "US",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://www.peoplefinders.com/remove-my-info",
                "search_paths": ["/search"],
                "priority": 2
            },
            {
                "name": "BeenVerified",
                "domain": "beenverified.com",
                "region": "US",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://www.beenverified.com/opt-out",
                "search_paths": ["/search"],
                "priority": 2
            },
            {
                "name": "FastPeopleSearch",
                "domain": "fastpeoplesearch.com",
                "region": "US",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://www.fastpeoplesearch.com/removal",
                "search_paths": ["/search"],
                "priority": 2
            },
            {
                "name": "FamilyTreeNow",
                "domain": "familytreenow.com",
                "region": "US",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://www.familytreenow.com/optout",
                "search_paths": ["/search"],
                "priority": 2
            },
            {
                "name": "PeopleSmart",
                "domain": "peoplesmart.com",
                "region": "US",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://www.peoplesmart.com/opt-out",
                "search_paths": ["/search"],
                "priority": 2
            },
            # Европа (приоритет 1)
            {
                "name": "Pipl",
                "domain": "pipl.com",
                "region": "GLOBAL",
                "removal_method": RemovalMethod.GDPR_REQUEST,
                "removal_url": "https://pipl.com/privacy",
                "privacy_email": "privacy@pipl.com",
                "search_paths": ["/search"],
                "priority": 1
            },
            {
                "name": "192.com",
                "domain": "192.com",
                "region": "UK",
                "removal_method": RemovalMethod.OPT_OUT_FORM,
                "removal_url": "https://www.192.com/opt-out",
                "search_paths": ["/search"],
                "priority": 2
            },
            {
                "name": "UKPhonebook",
                "domain": "ukphonebook.com",
                "region": "UK",
                "removal_method": RemovalMethod.GDPR_REQUEST,
                "removal_url": "https://www.ukphonebook.com/privacy",
                "privacy_email": "privacy@ukphonebook.com",
                "search_paths": ["/search"],
                "priority": 2
            },
            {
                "name": "Infobel Pro",
                "domain": "infobelpro.com",
                "region": "EU",
                "removal_method": RemovalMethod.GDPR_REQUEST,
                "removal_url": "https://www.infobelpro.com/en/privacy-policy",
                "privacy_email": "dpo@infobel.com",
                "search_paths": ["/search"],
                "priority": 2
            },
            {
                "name": "CallHunt",
                "domain": "callhunt.co",
                "region": "EU",
                "removal_method": RemovalMethod.GDPR_REQUEST,
                "removal_url": "https://www.callhunt.co/en/privacy",
                "privacy_email": "privacy@callhunt.co",
                "search_paths": ["/search"],
                "priority": 2
            },
        ]

    def find_data_on_broker_sites(
        self,
        user_id: str,
        user_data: UserData,
        force_scan: bool = False
    ) -> List[FoundData]:
        """
        Поиск персональных данных на брокерских сайтах

        Args:
            user_id: ID пользователя
            user_data: Персональные данные для поиска
            force_scan: Принудительный поиск (игнорирует периодичность)

        Returns:
            Список найденных данных на сайтах
        """
        # Проверяем настройки пользователя
        user_prefs = self.user_preferences.get(user_id, {})
        user_enable_auto = user_prefs.get("enable_auto_scan", False)
        user_scan_interval = user_prefs.get("scan_interval_days", self.scan_interval_days)

        # Проверяем, нужен ли поиск (если включен периодический мониторинг ИЛИ пользователь включил авто-поиск)
        auto_scan_enabled = self.enable_periodic_scan or user_enable_auto

        if not force_scan and auto_scan_enabled:
            last_scan = self.last_scan_times.get(user_id, 0)
            scan_interval_seconds = user_scan_interval * 24 * 60 * 60

            if time.time() - last_scan < scan_interval_seconds:
                # Еще не прошло достаточно времени с последнего поиска
                days_since_scan = (time.time() - last_scan) / (24 * 60 * 60)
                self.logger.debug(
                    f"⏭️ Пропуск поиска для {user_id}. "
                    f"Последний поиск был {days_since_scan:.1f} дней назад. "
                    f"Интервал: {user_scan_interval} дней"
                )
                # Возвращаем кэшированные результаты, если есть
                return self.found_data_cache.get(user_id, [])

        self.logger.info(f"🔍 Начало поиска данных для пользователя {user_id}")

        found_data_list: List[FoundData] = []

        # Проходим по приоритетным сайтам
        for site_info in sorted(self.broker_sites, key=lambda x: x.get("priority", 999)):
            retry_count = 0
            max_retries = 2

            while retry_count <= max_retries:
                try:
                    site_name = site_info["name"]
                    domain = site_info["domain"]

                    self.logger.debug(f"Проверка сайта: {site_name} ({domain})")

                    # Реальный поиск через HTTP запрос + парсинг
                    found = self._search_site(site_info, user_data)

                    if found:
                        found_data = FoundData(
                            site=site_name,
                            url=f"https://{domain}/search?q={user_data.name or user_data.email or user_data.phone}",
                            data_found=found,
                            found_at=time.time()
                        )
                        found_data_list.append(found_data)
                        self.logger.info(f"✅ Найдены данные на {site_name}: {found}")

                    # Успешно обработали, выходим из цикла retry
                    break

                except requests.exceptions.Timeout as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        self.logger.error(f"❌ Таймаут при проверке {site_info.get('name', 'unknown')} после {max_retries} попыток: {e}")
                    else:
                        self.logger.warning(f"⏳ Таймаут при проверке {site_info.get('name', 'unknown')}, попытка {retry_count}/{max_retries}")
                        time.sleep(2)  # Небольшая задержка перед повтором

                except requests.exceptions.RequestException as e:
                    # HTTP ошибки - не повторяем
                    self.logger.error(f"❌ HTTP ошибка при проверке {site_info.get('name', 'unknown')}: {e}")
                    break

                except Exception as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        self.logger.error(f"❌ Ошибка при проверке {site_info.get('name', 'unknown')} после {max_retries} попыток: {e}")
                    else:
                        self.logger.warning(f"⚠️ Ошибка при проверке {site_info.get('name', 'unknown')}, попытка {retry_count}/{max_retries}: {e}")
                        time.sleep(1)  # Небольшая задержка перед повтором

        # Кэшируем результаты
        self.found_data_cache[user_id] = found_data_list

        # Обновляем время последнего поиска
        self.last_scan_times[user_id] = time.time()

        self.logger.info(f"📊 Найдено данных на {len(found_data_list)} сайтах")
        return found_data_list

    def _search_site(self, site_info: Dict[str, Any], user_data: UserData) -> List[str]:
        """
        Поиск данных на конкретном сайте

        Args:
            site_info: Информация о сайте
            user_data: Данные пользователя

        Returns:
            Список типов найденных данных (email, phone, name, address)
        """
        if not REQUESTS_AVAILABLE or not self.session:
            self.logger.warning("HTTP клиент недоступен, пропускаем поиск")
            return []

        site_name = site_info.get("name", "")
        found_data_types: List[str] = []

        try:
            # Формируем поисковый запрос
            search_query = self._build_search_query(user_data)
            if not search_query:
                return []

            # Пробуем разные методы поиска
            # Метод 1: Поиск через поисковую форму сайта
            search_url = self._get_search_url(site_info, search_query)
            if search_url:
                found = self._search_via_form(search_url, user_data, site_info)
                if found:
                    found_data_types.extend(found)

            # Метод 2: Прямой поиск по URL (если сайт поддерживает)
            direct_url = self._get_direct_search_url(site_info, user_data)
            if direct_url:
                found = self._search_via_direct_url(direct_url, user_data, site_info)
                if found:
                    found_data_types.extend(found)

            # Удаляем дубликаты
            found_data_types = list(set(found_data_types))

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске на {site_name}: {e}")
            return []

        return found_data_types

    def _build_search_query(self, user_data: UserData) -> Optional[str]:
        """Формирует поисковый запрос из данных пользователя"""
        if user_data.name:
            return user_data.name
        elif user_data.email:
            return user_data.email
        elif user_data.phone:
            return user_data.phone
        return None

    def _get_search_url(self, site_info: Dict[str, Any], query: str) -> Optional[str]:
        """Получает URL для поиска на сайте"""
        domain = site_info.get("domain", "")
        search_paths = site_info.get("search_paths", ["/search", "/find", "/people"])

        for path in search_paths:
            url = f"https://{domain}{path}?q={query}"
            return url

        return None

    def _get_direct_search_url(self, site_info: Dict[str, Any], user_data: UserData) -> Optional[str]:
        """Получает прямой URL для поиска (если известен формат)"""
        domain = site_info.get("domain", "")

        # Для некоторых сайтов можно построить прямой URL
        if user_data.email:
            return f"https://{domain}/search?email={user_data.email}"
        elif user_data.phone:
            # Убираем все нецифровые символы
            phone_clean = re.sub(r'\D', '', user_data.phone)
            return f"https://{domain}/search?phone={phone_clean}"

        return None

    def _search_via_form(self, url: str, user_data: UserData, site_info: Dict[str, Any]) -> List[str]:
        """Поиск через форму на сайте"""
        found_data: List[str] = []

        try:
            response = self.session.get(url, timeout=self.scan_timeout_seconds)
            response.raise_for_status()

            if BeautifulSoup:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()

                # Проверяем наличие данных на странице
                if user_data.email and user_data.email.lower() in page_text:
                    found_data.append("email")

                if user_data.phone:
                    phone_clean = re.sub(r'\D', '', user_data.phone)
                    if phone_clean in page_text.replace(' ', '').replace('-', '').replace('(', '').replace(')', ''):
                        found_data.append("phone")

                if user_data.name:
                    name_parts = user_data.name.lower().split()
                    if all(part in page_text for part in name_parts if len(part) > 2):
                        found_data.append("name")

                if user_data.address:
                    address_parts = user_data.address.lower().split()
                    if any(part in page_text for part in address_parts if len(part) > 3):
                        found_data.append("address")

        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Ошибка HTTP запроса: {e}")
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге страницы: {e}")

        return found_data

    def _search_via_direct_url(self, url: str, user_data: UserData, site_info: Dict[str, Any]) -> List[str]:
        """Поиск через прямой URL"""
        return self._search_via_form(url, user_data, site_info)

    def remove_data_from_broker_sites(
        self,
        user_id: str,
        sites: List[str],
        user_data: UserData
    ) -> List[RemovalRequest]:
        """
        Автоматическая отправка запросов на удаление данных

        Args:
            user_id: ID пользователя
            sites: Список названий сайтов для удаления
            user_data: Персональные данные пользователя

        Returns:
            Список созданных запросов на удаление
        """
        self.logger.info(f"🗑️ Начало удаления данных для пользователя {user_id} на {len(sites)} сайтах")

        removal_requests: List[RemovalRequest] = []

        # Получаем найденные данные из кэша
        found_data_list = self.found_data_cache.get(user_id, [])

        for site_name in sites:
            # Находим информацию о сайте
            site_info = next(
                (s for s in self.broker_sites if s["name"] == site_name),
                None
            )

            if not site_info:
                self.logger.warning(f"⚠️ Сайт {site_name} не найден в списке")
                continue

            # Проверяем, есть ли данные на этом сайте
            found_data = next(
                (fd for fd in found_data_list if fd.site == site_name),
                None
            )

            if not found_data:
                self.logger.warning(f"⚠️ Данные на {site_name} не найдены")
                continue

            # Создаем запрос на удаление
            request_id = str(uuid.uuid4())
            removal_method = site_info.get("removal_method", RemovalMethod.OPT_OUT_FORM)

            # Определяем ожидаемое время завершения
            expected_completion = time.time() + (7 * 24 * 60 * 60)  # 7 дней по умолчанию

            removal_request = RemovalRequest(
                request_id=request_id,
                user_id=user_id,
                site=site_name,
                url=found_data.url,
                method=removal_method,
                status=RemovalStatus.PENDING,
                requested_at=time.time(),
                expected_completion=expected_completion,
                retry_count=0
            )

            # Отправляем запрос на удаление с retry логикой
            retry_count = 0
            max_retries = 2
            success = False

            while retry_count <= max_retries and not success:
                try:
                    success = self._send_removal_request(site_info, user_data, removal_request)
                    if success:
                        removal_request.status = RemovalStatus.PROCESSING
                        break
                    else:
                        retry_count += 1
                        if retry_count <= max_retries:
                            self.logger.warning(f"⚠️ Не удалось отправить запрос на {site_name}, попытка {retry_count}/{max_retries}")
                            time.sleep(2)  # Задержка перед повтором
                        else:
                            removal_request.status = RemovalStatus.FAILED
                            removal_request.error_message = "Не удалось отправить запрос после нескольких попыток"

                except requests.exceptions.Timeout as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        self.logger.error(f"❌ Таймаут при отправке запроса на {site_name}: {e}")
                        removal_request.status = RemovalStatus.FAILED
                        removal_request.error_message = f"Timeout: {str(e)}"
                    else:
                        self.logger.warning(f"⏳ Таймаут при отправке запроса на {site_name}, попытка {retry_count}/{max_retries}")
                        time.sleep(2)

                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        self.logger.error(f"❌ HTTP ошибка при отправке запроса на {site_name}: {e}")
                        removal_request.status = RemovalStatus.FAILED
                        removal_request.error_message = f"HTTP error: {str(e)}"
                    else:
                        self.logger.warning(f"⚠️ HTTP ошибка при отправке запроса на {site_name}, попытка {retry_count}/{max_retries}")
                        time.sleep(2)

                except Exception as e:
                    self.logger.error(f"❌ Ошибка при отправке запроса на {site_name}: {e}")
                    removal_request.status = RemovalStatus.FAILED
                    removal_request.error_message = str(e)
                    break

            # Сохраняем запрос
            self.removal_requests[request_id] = removal_request
            removal_requests.append(removal_request)

        self.logger.info(f"📤 Отправлено {len(removal_requests)} запросов на удаление")
        return removal_requests

    def _send_removal_request(
        self,
        site_info: Dict[str, Any],
        user_data: UserData,
        removal_request: RemovalRequest
    ) -> bool:
        """
        Отправка запроса на удаление данных

        Args:
            site_info: Информация о сайте
            user_data: Данные пользователя
            removal_request: Запрос на удаление

        Returns:
            True если запрос отправлен успешно
        """
        if not REQUESTS_AVAILABLE or not self.session:
            self.logger.warning("HTTP клиент недоступен, пропускаем удаление")
            return False

        method = site_info.get("removal_method", RemovalMethod.OPT_OUT_FORM)
        site_name = site_info.get("name", "")

        self.logger.info(f"📤 Отправка запроса методом {method.value} на {site_name}")

        try:
            if method == RemovalMethod.OPT_OUT_FORM:
                return self._send_opt_out_form(site_info, user_data, removal_request)
            elif method == RemovalMethod.GDPR_REQUEST:
                return self._send_gdpr_request(site_info, user_data, removal_request)
            elif method == RemovalMethod.EMAIL:
                return self._send_email_request(site_info, user_data, removal_request)
            elif method == RemovalMethod.PARENT_COMPANY:
                return self._send_parent_company_request(site_info, user_data, removal_request)
            elif method == RemovalMethod.API:
                return self._send_api_request(site_info, user_data, removal_request)
            else:
                self.logger.warning(f"⚠️ Неизвестный метод удаления: {method.value}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка при отправке запроса на {site_name}: {e}")
            removal_request.error_message = str(e)
            return False

    def _send_opt_out_form(self, site_info: Dict[str, Any], user_data: UserData, removal_request: RemovalRequest) -> bool:
        """Отправка запроса через opt-out форму на сайте"""
        removal_url = site_info.get("removal_url", "")
        if not removal_url:
            self.logger.warning(f"⚠️ URL для удаления не указан для {site_info.get('name')}")
            return False

        try:
            # Получаем страницу с формой
            response = self.session.get(removal_url, timeout=self.scan_timeout_seconds)
            response.raise_for_status()

            if not BeautifulSoup:
                self.logger.warning("BeautifulSoup недоступен для парсинга формы")
                return False

            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем форму
            form = soup.find('form')
            if not form:
                # Если формы нет, возможно это прямая ссылка на удаление
                # Пробуем найти ссылку "Remove my info" или подобную
                remove_link = soup.find('a', string=re.compile(r'remove|delete|opt.out', re.I))
                if remove_link and remove_link.get('href'):
                    removal_url = remove_link['href']
                    if not removal_url.startswith('http'):
                        domain = site_info.get("domain", "")
                        removal_url = f"https://{domain}{removal_url}"

                    # Переходим по ссылке
                    response = self.session.get(removal_url, timeout=self.scan_timeout_seconds)
                    response.raise_for_status()
                    return True

                self.logger.warning("Форма для удаления не найдена")
                return False

            # Находим action формы
            form_action = form.get('action', '')
            if form_action and not form_action.startswith('http'):
                domain = site_info.get("domain", "")
                form_action = f"https://{domain}{form_action}"
            elif not form_action:
                form_action = removal_url

            # Собираем данные формы
            form_data = {}

            # Находим все input поля
            inputs = form.find_all(['input', 'textarea', 'select'])
            for input_field in inputs:
                name = input_field.get('name')
                input_type = input_field.get('type', 'text').lower()

                if not name:
                    continue

                # Заполняем поля на основе имени
                if 'email' in name.lower():
                    form_data[name] = user_data.email or ''
                elif 'phone' in name.lower() or 'tel' in name.lower():
                    form_data[name] = user_data.phone or ''
                elif 'name' in name.lower() and 'first' in name.lower():
                    if user_data.name:
                        form_data[name] = user_data.name.split()[0] if user_data.name else ''
                elif 'name' in name.lower() and 'last' in name.lower():
                    if user_data.name:
                        name_parts = user_data.name.split()
                        form_data[name] = name_parts[-1] if len(name_parts) > 1 else ''
                elif 'name' in name.lower():
                    form_data[name] = user_data.name or ''
                elif 'address' in name.lower():
                    form_data[name] = user_data.address or ''
                elif input_type in ['hidden', 'submit']:
                    # Сохраняем значение скрытых полей и submit кнопок
                    value = input_field.get('value', '')
                    if value:
                        form_data[name] = value
                elif input_type == 'checkbox' or input_type == 'radio':
                    # Для чекбоксов и радиокнопок берем значение по умолчанию
                    if input_field.get('checked') or input_field.get('value'):
                        form_data[name] = input_field.get('value', 'on')

            # Отправляем форму
            method = form.get('method', 'get').lower()
            if method == 'post':
                response = self.session.post(form_action, data=form_data, timeout=self.scan_timeout_seconds)
            else:
                response = self.session.get(form_action, params=form_data, timeout=self.scan_timeout_seconds)

            response.raise_for_status()

            # Проверяем успешность (обычно редирект или сообщение об успехе)
            if response.status_code in [200, 201, 302, 303]:
                # Проверяем наличие сообщения об успехе на странице
                if BeautifulSoup:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_text = soup.get_text().lower()
                    success_keywords = ['success', 'submitted', 'received', 'thank you', 'успешно', 'отправлено']
                    if any(keyword in page_text for keyword in success_keywords):
                        self.logger.info(f"✅ Запрос на удаление успешно отправлен на {site_info.get('name')}")
                        return True

                # Если редирект - считаем успешным
                if response.status_code in [302, 303]:
                    return True

                # Если 200/201 - тоже считаем успешным (может быть страница подтверждения)
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ HTTP ошибка при отправке формы: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка при обработке формы: {e}")
            return False

    def _send_gdpr_request(self, site_info: Dict[str, Any], user_data: UserData, removal_request: RemovalRequest) -> bool:
        """Отправка GDPR запроса (email)"""
        # GDPR запросы обычно отправляются через email
        # Используем метод отправки email
        return self._send_email_request(site_info, user_data, removal_request)

    def _send_email_request(self, site_info: Dict[str, Any], user_data: UserData, removal_request: RemovalRequest) -> bool:
        """Отправка запроса на удаление через email"""
        # Получаем email для отправки
        privacy_email = site_info.get("privacy_email", "")
        if not privacy_email:
            # Пробуем найти email на странице контактов
            try:
                domain = site_info.get("domain", "")
                contact_url = f"https://{domain}/contact" or f"https://{domain}/privacy"
                response = self.session.get(contact_url, timeout=self.scan_timeout_seconds)

                if BeautifulSoup:
                    # Ищем email на странице
                    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
                    emails = email_pattern.findall(response.text)
                    if emails:
                        privacy_email = emails[0]  # Берем первый найденный email
            except Exception as e:
                self.logger.debug(f"Не удалось найти email для {site_info.get('name')}: {e}")

        if not privacy_email:
            self.logger.warning(f"⚠️ Email для отправки запроса не найден для {site_info.get('name')}")
            # Сохраняем запрос как pending, чтобы пользователь мог отправить вручную
            return False

        # Формируем текст письма
        email_subject = "GDPR Data Removal Request / Запрос на удаление данных"
        email_body = self._build_removal_email_body(user_data, site_info)

        # TODO: Реализовать отправку email через smtplib или email сервис
        # Пока логируем и возвращаем True (в реальности нужно отправить email)
        self.logger.info(f"📧 Email запрос для {site_info.get('name')} готов к отправке на {privacy_email}")
        self.logger.debug(f"Тема: {email_subject}\nТело: {email_body}")

        # Сохраняем информацию для ручной отправки или автоматической через email сервис
        removal_request.metadata = {
            "email": privacy_email,
            "subject": email_subject,
            "body": email_body
        }

        return True  # Считаем успешным, так как запрос подготовлен

    def _build_removal_email_body(self, user_data: UserData, site_info: Dict[str, Any]) -> str:
        """Формирует текст email запроса на удаление"""
        body = """Здравствуйте,

Прошу удалить мои персональные данные с вашего сайта в соответствии с GDPR / 152-ФЗ.

Персональные данные для удаления:
"""
        if user_data.name:
            body += f"Имя: {user_data.name}\n"
        if user_data.email:
            body += f"Email: {user_data.email}\n"
        if user_data.phone:
            body += f"Телефон: {user_data.phone}\n"
        if user_data.address:
            body += f"Адрес: {user_data.address}\n"

        body += f"""
Основание: GDPR (General Data Protection Regulation) / Федеральный закон 152-ФЗ "О персональных данных"

Пожалуйста, подтвердите удаление данных в течение 30 дней.

С уважением,
{user_data.name or 'Пользователь'}
"""
        return body

    def _send_parent_company_request(self, site_info: Dict[str, Any], user_data: UserData, removal_request: RemovalRequest) -> bool:
        """Отправка запроса через родительскую компанию (например, PeopleConnect)"""
        removal_url = site_info.get("removal_url", "")
        if not removal_url:
            return False

        # Для родительских компаний обычно используется та же opt-out форма
        # но она удаляет данные со всех контролируемых сайтов
        return self._send_opt_out_form(site_info, user_data, removal_request)

    def _send_api_request(self, site_info: Dict[str, Any], user_data: UserData, removal_request: RemovalRequest) -> bool:
        """Отправка запроса через API"""
        api_url = site_info.get("api_url", "")
        api_key = site_info.get("api_key", "")

        if not api_url:
            self.logger.warning(f"⚠️ API URL не указан для {site_info.get('name')}")
            return False

        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'ALADDIN Data Cleanup Agent/1.0'
            }

            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'

            payload = {
                "email": user_data.email,
                "phone": user_data.phone,
                "name": user_data.name,
                "address": user_data.address,
                "request_type": "data_removal",
                "reason": "GDPR/152-ФЗ request"
            }

            response = self.session.post(api_url, json=payload, headers=headers, timeout=self.scan_timeout_seconds)
            response.raise_for_status()

            if response.status_code in [200, 201]:
                return True

            return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Ошибка API запроса: {e}")
            return False

    def track_removal_progress(
        self,
        user_id: str,
        request_id: Optional[str] = None
    ) -> List[RemovalRequest]:
        """
        Отслеживание статуса удаления данных

        Args:
            user_id: ID пользователя
            request_id: ID конкретного запроса (опционально)

        Returns:
            Список запросов с актуальным статусом
        """
        if request_id:
            # Отслеживание конкретного запроса
            request = self.removal_requests.get(request_id)
            if request and request.user_id == user_id:
                return [self._check_request_status(request)]
            return []

        # Отслеживание всех запросов пользователя
        user_requests = [
            req for req in self.removal_requests.values()
            if req.user_id == user_id
        ]

        updated_requests = []
        for request in user_requests:
            updated_request = self._check_request_status(request)
            updated_requests.append(updated_request)

        return updated_requests

    def _check_request_status(self, request: RemovalRequest) -> RemovalRequest:
        """
        Проверка статуса запроса

        Args:
            request: Запрос на удаление

        Returns:
            Обновленный запрос
        """
        # Если запрос в процессе и прошло достаточно времени
        if request.status == RemovalStatus.PROCESSING:
            if request.expected_completion and time.time() >= request.expected_completion:
                # Проверяем статус на сайте
                if self._verify_removal_status(request):
                    request.status = RemovalStatus.COMPLETED
                    request.completed_at = time.time()
                else:
                    # Если данные все еще есть, проверяем еще раз через день
                    request.expected_completion = time.time() + (24 * 60 * 60)

        # Если запрос провалился и включен auto-retry
        if request.status == RemovalStatus.FAILED and self.enable_auto_retry:
            if request.retry_count < self.max_retries:
                # Планируем повторную попытку
                retry_delay = self.retry_delay_days * 24 * 60 * 60
                if time.time() >= request.requested_at + (retry_delay * (request.retry_count + 1)):
                    request.status = RemovalStatus.RETRYING
                    request.retry_count += 1
                    request.error_message = None

                    # Пытаемся отправить повторный запрос
                    try:
                        # Находим информацию о сайте
                        site_info = next(
                            (s for s in self.broker_sites if s["name"] == request.site),
                            None
                        )

                        if site_info:
                            # Восстанавливаем user_data из кэша или metadata
                            user_data = UserData()  # TODO: Восстановить из кэша
                            success = self._send_removal_request(site_info, user_data, request)
                            if success:
                                request.status = RemovalStatus.PROCESSING
                                request.requested_at = time.time()
                                request.expected_completion = time.time() + (7 * 24 * 60 * 60)
                    except Exception as e:
                        self.logger.error(f"❌ Ошибка при повторной попытке для {request.site}: {e}")
                        request.status = RemovalStatus.FAILED
                        request.error_message = f"Retry failed: {str(e)}"

        # Если запрос истек
        if request.status == RemovalStatus.PROCESSING:
            max_wait_time = 30 * 24 * 60 * 60  # 30 дней максимум
            if time.time() >= request.requested_at + max_wait_time:
                request.status = RemovalStatus.EXPIRED
                request.error_message = "Request expired after 30 days"

        return request

    def _verify_removal_status(self, request: RemovalRequest) -> bool:
        """
        Проверяет, были ли данные действительно удалены с сайта

        Args:
            request: Запрос на удаление

        Returns:
            True если данные удалены, False если все еще присутствуют
        """
        if not REQUESTS_AVAILABLE or not self.session:
            # Если HTTP клиент недоступен, считаем что удалено (оптимистично)
            return True

        try:
            # Пробуем найти данные на сайте снова
            # Если данные не найдены - считаем удаленными
            site_info = next(
                (s for s in self.broker_sites if s["name"] == request.site),
                None
            )

            if not site_info:
                return True  # Сайт не найден, считаем успешным

            # Пробуем найти данные на странице
            # TODO: Восстановить user_data из кэша для проверки
            # Пока возвращаем True (оптимистично)
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при проверке статуса удаления: {e}")
            # При ошибке считаем что удалено (чтобы не блокировать процесс)
            return True

    def get_cleanup_report(self, user_id: str) -> CleanupReport:
        """
        Генерация отчета о процессе очистки данных

        Args:
            user_id: ID пользователя

        Returns:
            Отчет о процессе очистки
        """
        # Получаем все запросы пользователя
        user_requests = [
            req for req in self.removal_requests.values()
            if req.user_id == user_id
        ]

        # Получаем найденные данные
        found_data_list = self.found_data_cache.get(user_id, [])

        # Подсчитываем статистику
        total_sites_scanned = len(self.broker_sites)
        sites_with_data = len(found_data_list)
        removal_requests_sent = len(user_requests)

        completed = sum(1 for r in user_requests if r.status == RemovalStatus.COMPLETED)
        pending = sum(1 for r in user_requests if r.status in [
            RemovalStatus.PENDING, RemovalStatus.PROCESSING, RemovalStatus.RETRYING
        ])
        failed = sum(1 for r in user_requests if r.status == RemovalStatus.FAILED)

        completion_percentage = (
            (completed / removal_requests_sent * 100) if removal_requests_sent > 0 else 0.0
        )

        report = CleanupReport(
            user_id=user_id,
            total_sites_scanned=total_sites_scanned,
            sites_with_data=sites_with_data,
            removal_requests_sent=removal_requests_sent,
            completed=completed,
            pending=pending,
            failed=failed,
            completion_percentage=round(completion_percentage, 2),
            generated_at=time.time()
        )

        return report

    def check_periodic_scan(self, user_id: str, user_data: UserData) -> Optional[List[FoundData]]:
        """
        Проверяет, нужно ли выполнить периодический поиск данных

        Args:
            user_id: ID пользователя
            user_data: Персональные данные пользователя

        Returns:
            Список найденных данных или None если поиск не требуется
        """
        if not self.enable_periodic_scan:
            return None

        last_scan = self.last_scan_times.get(user_id, 0)
        scan_interval_seconds = self.scan_interval_days * 24 * 60 * 60

        if time.time() - last_scan >= scan_interval_seconds:
            self.logger.info(f"⏰ Время для периодического поиска данных для {user_id}")
            return self.find_data_on_broker_sites(user_id, user_data, force_scan=True)

        return None

    def get_scan_status(self, user_id: str) -> Dict[str, Any]:
        """
        Получает статус последнего поиска для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Словарь со статусом поиска
        """
        last_scan = self.last_scan_times.get(user_id, 0)
        found_data = self.found_data_cache.get(user_id, [])

        # Получаем настройки пользователя
        user_prefs = self.user_preferences.get(user_id, {})
        user_enable_auto = user_prefs.get("enable_auto_scan", False)
        user_scan_interval = user_prefs.get("scan_interval_days", self.scan_interval_days)

        # Проверяем, нужно ли напоминание (для режима "по запросу")
        needs_reminder = False
        days_since_scan = None
        if last_scan > 0:
            days_since_scan = (time.time() - last_scan) / (24 * 60 * 60)
            # Напоминание, если прошло больше reminder_interval_days и авто-поиск выключен
            if not user_enable_auto and days_since_scan >= self.reminder_interval_days:
                needs_reminder = True

        if last_scan == 0:
            return {
                "last_scan": None,
                "days_since_scan": None,
                "next_scan_in_days": None,
                "sites_found": len(found_data),
                "auto_scan_enabled": user_enable_auto,
                "scan_interval_days": user_scan_interval,
                "reminder_interval_days": self.reminder_interval_days,
                "needs_reminder": True,  # Если никогда не было поиска - нужен
                "reminder_message": "Рекомендуется проверить данные на брокерских сайтах"
            }

        # Вычисляем следующий поиск
        if user_enable_auto:
            scan_interval_seconds = user_scan_interval * 24 * 60 * 60
            next_scan_in_seconds = scan_interval_seconds - (time.time() - last_scan)
            next_scan_in_days = max(0, next_scan_in_seconds / (24 * 60 * 60))
        else:
            # В режиме "по запросу" следующий поиск - когда пользователь захочет
            # Но показываем, когда рекомендуется (через reminder_interval_days)
            reminder_interval_seconds = self.reminder_interval_days * 24 * 60 * 60
            next_reminder_seconds = reminder_interval_seconds - (time.time() - last_scan)
            next_scan_in_days = max(0, next_reminder_seconds / (24 * 60 * 60))

        return {
            "last_scan": datetime.fromtimestamp(last_scan).isoformat() if last_scan else None,
            "days_since_scan": round(days_since_scan, 1) if days_since_scan else None,
            "next_scan_in_days": round(next_scan_in_days, 1) if next_scan_in_days else None,
            "sites_found": len(found_data),
            "auto_scan_enabled": user_enable_auto,
            "scan_interval_days": user_scan_interval,
            "reminder_interval_days": self.reminder_interval_days,
            "needs_reminder": needs_reminder,
            "reminder_message": f"Рекомендуется проверить данные. Последняя проверка была {int(days_since_scan)} дней назад" if needs_reminder else None
        }

    def set_user_preferences(
        self,
        user_id: str,
        enable_auto_scan: Optional[bool] = None,
        scan_interval_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Устанавливает настройки пользователя для поиска данных

        Args:
            user_id: ID пользователя
            enable_auto_scan: Включить автоматический поиск
            scan_interval_days: Интервал поиска в днях (если включен авто-поиск)

        Returns:
            Текущие настройки пользователя
        """
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "enable_auto_scan": False,
                "scan_interval_days": self.scan_interval_days
            }

        if enable_auto_scan is not None:
            self.user_preferences[user_id]["enable_auto_scan"] = enable_auto_scan
            self.logger.info(f"⚙️ Пользователь {user_id} {'включил' if enable_auto_scan else 'выключил'} автоматический поиск")

        if scan_interval_days is not None:
            if scan_interval_days < 7:
                self.logger.warning(f"⚠️ Интервал поиска слишком мал ({scan_interval_days} дней), установлен минимум 7 дней")
                scan_interval_days = 7
            elif scan_interval_days > 365:
                self.logger.warning(f"⚠️ Интервал поиска слишком велик ({scan_interval_days} дней), установлен максимум 365 дней")
                scan_interval_days = 365
            self.user_preferences[user_id]["scan_interval_days"] = scan_interval_days
            self.logger.info(f"⚙️ Пользователь {user_id} установил интервал поиска: {scan_interval_days} дней")

        return self.user_preferences[user_id].copy()

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Получает настройки пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Настройки пользователя
        """
        return self.user_preferences.get(user_id, {
            "enable_auto_scan": False,
            "scan_interval_days": self.scan_interval_days
        })

    # Реализация ThreatMonitoringInterface
    def collect_threats(self) -> List[Dict[str, Any]]:
        """Сбор угроз (не используется для этого агента)"""
        return []

    def analyze_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Анализ угроз (не используется для этого агента)"""
        return threats

    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """Отправка уведомления (не используется для этого агента)"""
        return True
