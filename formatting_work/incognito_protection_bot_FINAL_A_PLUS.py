#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
function_302: IncognitoProtectionBot - Бот защиты от режима инкогнито и VPN
Максимальная защита от обхода родительского контроля
"""

import asyncio
import json
import logging
import time
import subprocess
import psutil
import requests
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import sqlite3
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Уровни угроз"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BypassMethod(Enum):
    """Методы обхода"""

    INCOGNITO_MODE = "incognito_mode"
    VPN_CONNECTION = "vpn_connection"
    PROXY_SERVER = "proxy_server"
    TOR_BROWSER = "tor_browser"
    PRIVATE_BROWSER = "private_browser"
    CLEAR_HISTORY = "clear_history"
    DISABLE_EXTENSIONS = "disable_extensions"
    SAFE_MODE = "safe_mode"


class ProtectionAction(Enum):
    """Действия защиты"""

    BLOCK = "block"
    WARN = "warn"
    NOTIFY_PARENTS = "notify_parents"
    EMERGENCY_LOCK = "emergency_lock"
    LOG_ACTIVITY = "log_activity"
    SCREENSHOT = "screenshot"


@dataclass
class BypassAttempt:
    """Попытка обхода"""

    attempt_id: str
    child_id: str
    bypass_method: BypassMethod
    timestamp: datetime
    ip_address: str
    user_agent: str
    browser_type: str
    threat_level: ThreatLevel
    blocked_urls: List[str]
    success: bool
    parent_notified: bool


@dataclass
class VPNDetection:
    """Детекция VPN"""

    vpn_detected: bool
    vpn_provider: str
    vpn_country: str
    original_country: str
    confidence: float
    detection_method: str


@dataclass
class IncognitoDetection:
    """Детекция инкогнито"""

    incognito_detected: bool
    browser_type: str
    detection_method: str
    confidence: float
    session_data: Dict[str, Any]


class IncognitoProtectionBot:
    """Бот максимальной защиты от обхода родительского контроля"""

    def __init__(self, name: str = "IncognitoProtectionBot"):
        self.name = name
        self.status = "enabled"
        self.description = "Бот защиты от режима инкогнито и VPN"
        self.name = name
        self.db_path = Path("data/incognito_protection.db")
        self.setup_database()

        # Настройки защиты
        self.protection_level = "MAXIMUM"  # MAXIMUM, HIGH, MEDIUM, LOW
        self.block_vpn = True
        self.block_incognito = True
        self.block_proxy = True
        self.block_tor = True
        self.emergency_lock_enabled = True

        # Списки блокировки
        self.blocked_vpn_providers = [
            "nordvpn",
            "expressvpn",
            "surfshark",
            "cyberghost",
            "protonvpn",
            "windscribe",
            "tunnelbear",
            "private internet access",
            "ipvanish",
            "vyprvpn",
            "strongvpn",
            "hide.me",
            "purevpn",
            "zenmate",
        ]

        self.blocked_tor_indicators = [
            "tor browser",
            "torproject",
            "onion",
            ".onion",
            "tor network",
        ]

        # Мониторинг процессов
        self.monitored_processes = [
            "chrome",
            "firefox",
            "safari",
            "edge",
            "opera",
            "brave",
            "tor",
            "vpn",
            "proxy",
            "tunnel",
        ]

    def setup_database(self):
        """Настройка базы данных"""
        self.db_path.parent.mkdir(exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bypass_attempts (
                    attempt_id TEXT PRIMARY KEY,
                    child_id TEXT NOT NULL,
                    bypass_method TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    browser_type TEXT,
                    threat_level TEXT NOT NULL,
                    blocked_urls TEXT,
                    success BOOLEAN NOT NULL,
                    parent_notified BOOLEAN NOT NULL,
                    screenshot_path TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS vpn_detections (
                    detection_id TEXT PRIMARY KEY,
                    child_id TEXT NOT NULL,
                    vpn_provider TEXT,
                    vpn_country TEXT,
                    original_country TEXT,
                    confidence REAL NOT NULL,
                    detection_method TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    blocked BOOLEAN NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS incognito_detections (
                    detection_id TEXT PRIMARY KEY,
                    child_id TEXT NOT NULL,
                    browser_type TEXT NOT NULL,
                    detection_method TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    session_data TEXT,
                    timestamp DATETIME NOT NULL,
                    blocked BOOLEAN NOT NULL
                )
            """)

    async def detect_vpn_connection(self, child_id: str) -> VPNDetection:
        """Детекция VPN соединения"""
        try:
            # Проверка через внешний API
            response = requests.get("http://ip-api.com/json/", timeout=5)
            if response.status_code == 200:
                data = response.json()

                # Проверка на VPN индикаторы
                vpn_indicators = [
                    data.get("org", "").lower(),
                    data.get("isp", "").lower(),
                    data.get("as", "").lower(),
                ]

                vpn_detected = any(
                    any(
                        provider in indicator
                        for provider in self.blocked_vpn_providers
                    )
                    for indicator in vpn_indicators
                )

                if vpn_detected:
                    vpn_provider = next(
                        provider
                        for provider in self.blocked_vpn_providers
                        if any(
                            provider in indicator
                            for indicator in vpn_indicators
                        )
                    )

                    # Логирование детекции
                    detection_id = f"vpn_{int(time.time())}"
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute(
                            """
                            INSERT INTO vpn_detections
                            (detection_id, child_id, vpn_provider, vpn_country,
                        browser in proc.info['name'].lower()
                        for browser in [
                            'chrome', 'firefox', 'safari', 'edge', 'opera',
                            'brave'
                        ]
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                detection_id,
                                child_id,
                                vpn_provider,
                                data.get("country", ""),
                                data.get("country", ""),
                                0.9,
                                "API_DETECTION",
                                datetime.now(),
                                True,
                            ),
                        )

                    return VPNDetection(
                        vpn_detected=True,
                        vpn_provider=vpn_provider,
                        vpn_country=data.get("country", ""),
                        original_country=data.get("country", ""),
                        confidence=0.9,
                        detection_method="API_DETECTION",
                    )

            return VPNDetection(
                vpn_detected=False,
                vpn_provider="",
                vpn_country="",
                original_country="",
                confidence=0.0,
                detection_method="API_DETECTION",
            )

        except Exception as e:
            logger.error(f"Ошибка детекции VPN: {e}")
            return VPNDetection(
                vpn_detected=False,
                vpn_provider="",
                vpn_country="",
                original_country="",
                confidence=0.0,
                detection_method="ERROR",
            )

    async def detect_incognito_mode(self, child_id: str) -> IncognitoDetection:
        """Детекция режима инкогнито"""
        try:
            # Проверка запущенных браузеров
            running_browsers = []
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if proc.info["name"] and any(
                        browser in proc.info["name"].lower()
                        for browser in [
                            "chrome",
                            "firefox",
                            "safari",
                            "edge",
                            "opera",
                            "brave",
                        ]
                    ):
                        running_browsers.append({
                            "name": proc.info["name"],
                            "cmdline": proc.info["cmdline"],
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Анализ командной строки на индикаторы инкогнито
            incognito_indicators = [
                "--incognito",
                "--private",
                "--inprivate",
                "--stealth",
                "--headless",
                "--no-sandbox",
                "--disable-extensions",
            ]

            incognito_detected = False
            browser_type = ""
            detection_method = ""

            for browser in running_browsers:
                cmdline = " ".join(browser["cmdline"] or [])
                if any(
                    indicator in cmdline.lower()
                    for indicator in incognito_indicators
                ):
                    incognito_detected = True
                    browser_type = browser["name"]
                    detection_method = "PROCESS_ANALYSIS"
                    break

            # Дополнительная проверка через файловую систему
            if not incognito_detected:
                # Проверка временных файлов браузеров
                temp_paths = [
                    Path.home()
                    / "AppData/Local/Google/Chrome/User Data/Default",
                    Path.home()
                    / "Library/Application Support/Google/Chrome/Default",
                    Path.home() / ".mozilla/firefox/profiles",
                ]

                for temp_path in temp_paths:
                    if temp_path.exists():
                        # Проверка на признаки инкогнито
                        if self._check_incognito_files(temp_path):
                            incognito_detected = True
                            browser_type = "DETECTED"
                            detection_method = "FILE_ANALYSIS"
                            break

            # Логирование детекции
            if incognito_detected:
                detection_id = f"incognito_{int(time.time())}"
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO incognito_detections
                    "-p", "tcp", "--dport", str(port),
                    "-j", "DROP"
                         confidence, session_data, timestamp, blocked)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            detection_id,
                            child_id,
                            browser_type,
                            detection_method,
                            0.8,
                            json.dumps({}),
                            datetime.now(),
                            True,
                        ),
                    )

            return IncognitoDetection(
                incognito_detected=incognito_detected,
                browser_type=browser_type,
                detection_method=detection_method,
                confidence=0.8 if incognito_detected else 0.0,
                session_data={},
            )

        except Exception as e:
            logger.error(f"Ошибка детекции инкогнито: {e}")
            return IncognitoDetection(
                incognito_detected=False,
                browser_type="",
                detection_method="ERROR",
                confidence=0.0,
                session_data={},
            )

    def _check_incognito_files(self, path: Path) -> bool:
        """Проверка файлов на признаки инкогнито"""
        try:
            # Проверка на отсутствие истории (признак инкогнито)
            history_files = list(path.glob("*History*"))
            if not history_files:
                return True

            # Проверка на пустые файлы истории
            for history_file in history_files:
                if history_file.stat().st_size == 0:
                    return True

            return False
        except Exception:
            return False

    async def block_bypass_attempt(
        self, child_id: str, bypass_method: BypassMethod
    ) -> bool:
        """Блокировка попытки обхода"""
        try:
            if bypass_method == BypassMethod.VPN_CONNECTION:
                return await self._block_vpn_connection()
            elif bypass_method == BypassMethod.INCOGNITO_MODE:
                return await self._block_incognito_mode()
            elif bypass_method == BypassMethod.TOR_BROWSER:
                return await self._block_tor_browser()
            elif bypass_method == BypassMethod.PROXY_SERVER:
                return await self._block_proxy_connection()

            return False
        except Exception as e:
            logger.error(f"Ошибка блокировки: {e}")
            return False

    async def _block_vpn_connection(self) -> bool:
        """Блокировка VPN соединения"""
        try:
            # Блокировка через firewall (требует прав администратора)
            vpn_ports = [1194, 443, 80, 53, 500, 4500, 1723]

            for port in vpn_ports:
                # Блокировка исходящих соединений на VPN порты
                subprocess.run(
                    [
                        "sudo",
                        "iptables",
                        "-A",
                        "OUTPUT",
                        "-p",
                        "tcp",
                        "--dport",
                        str(port),
                        "-j",
                        "DROP",
                    ],
                    check=False,
                )

                subprocess.run(
                    [
                        "sudo",
                        "iptables",
                        "-A",
                        "OUTPUT",
                        "-p",
                        "udp",
                        "--dport",
                        str(port),
                        "-j",
                        "DROP",
                    ],
                    check=False,
                )

            return True
        except Exception as e:
            logger.error(f"Ошибка блокировки VPN: {e}")
            return False

    async def _block_incognito_mode(self) -> bool:
        """Блокировка режима инкогнито"""
        try:
            # Завершение процессов браузеров в инкогнито
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if proc.info["name"] and any(
                        browser in proc.info["name"].lower()
                        for browser in [
                            "chrome",
                            "firefox",
                            "safari",
                            "edge",
                            "opera",
                            "brave",
                        ]
                    ):
                        cmdline = " ".join(proc.info["cmdline"] or [])
                        if any(
                            indicator in cmdline.lower()
                            for indicator in [
                                "--incognito",
                                "--private",
                                "--inprivate",
                            ]
                        ):
                            proc.terminate()
                            logger.info(
                                "Завершен процесс браузера в инкогнито:"
                                f" {proc.info['name']}"
                            )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return True
        except Exception as e:
            logger.error(f"Ошибка блокировки инкогнито: {e}")
            return False

    async def _block_tor_browser(self) -> bool:
        """Блокировка Tor браузера"""
        try:
            # Завершение процессов Tor
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if (
                        proc.info["name"]
                        and "tor" in proc.info["name"].lower()
                    ):
                        proc.terminate()
                        logger.info(
                            f"Завершен процесс Tor: {proc.info['name']}"
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Блокировка Tor портов
            tor_ports = [9050, 9051, 9150, 9151]
            for port in tor_ports:
                subprocess.run(
                    [
                        "sudo",
                        "iptables",
                        "-A",
                        "OUTPUT",
                        "-p",
                        "tcp",
                        "--dport",
                        str(port),
                        "-j",
                        "DROP",
                    ],
                    check=False,
                )

            return True
        except Exception as e:
            logger.error(f"Ошибка блокировки Tor: {e}")
            return False

    async def _block_proxy_connection(self) -> bool:
        """Блокировка прокси соединений"""
        try:
            # Блокировка популярных прокси портов
            proxy_ports = [8080, 3128, 1080, 8118, 8888, 9999]
            for port in proxy_ports:
                subprocess.run(
                    [
                        "sudo",
                        "iptables",
                        "-A",
                        "OUTPUT",
                        "-p",
                        "tcp",
                        "--dport",
                        str(port),
                        "-j",
                        "DROP",
                    ],
                    check=False,
                )

            return True
        except Exception as e:
            logger.error(f"Ошибка блокировки прокси: {e}")
            return False

    async def notify_parents(
        self, child_id: str, bypass_attempt: BypassAttempt
    ):
        """Уведомление родителей о попытке обхода"""
        try:
            # Создание уведомления
            notification = {
                "child_id": child_id,
                "alert_type": "BYPASS_ATTEMPT",
                "severity": "CRITICAL",
                "message": (
                    f"Ребенок {child_id} пытается обойти защиту:"
                    f" {bypass_attempt.bypass_method.value}"
                ),
                "timestamp": datetime.now().isoformat(),
                "bypass_method": bypass_attempt.bypass_method.value,
                "ip_address": bypass_attempt.ip_address,
                "browser_type": bypass_attempt.browser_type,
            }

            # Отправка уведомления (SMS, Email, Push)
            await self._send_emergency_notification(notification)

            # Логирование
            logger.critical(
                f"КРИТИЧЕСКОЕ УВЕДОМЛЕНИЕ: {notification['message']}"
            )

            return True
        except Exception as e:
            logger.error(f"Ошибка уведомления родителей: {e}")
            return False

    async def _send_emergency_notification(self, notification: Dict[str, Any]):
        """Отправка экстренного уведомления"""
        # Здесь можно интегрировать с SMS/Email/Push сервисами
        print(f"🚨 ЭКСТРЕННОЕ УВЕДОМЛЕНИЕ: {notification['message']}")

        # Сохранение в файл для демонстрации
        with open("data/emergency_notifications.json", "a") as f:
            f.write(json.dumps(notification) + "\n")

    async def take_screenshot(self, child_id: str) -> str:
        """Создание скриншота экрана"""
        try:
            screenshot_path = (
                f"data/screenshots/incognito_attempt_{child_id}_"
                f"{int(time.time())}.png"
            )
            Path(screenshot_path).parent.mkdir(exist_ok=True)

            # Создание скриншота (требует дополнительных библиотек)
            # subprocess.run(["screencapture", screenshot_path], check=True)

            return screenshot_path
        except Exception as e:
            logger.error(f"Ошибка создания скриншота: {e}")
            return ""

    async def emergency_lock_device(self, child_id: str) -> bool:
        """Экстренная блокировка устройства"""
        try:
            if self.emergency_lock_enabled:
                # Блокировка всех браузеров
                for proc in psutil.process_iter(["pid", "name"]):
                    try:
                        if proc.info["name"] and any(
                            browser in proc.info["name"].lower()
                            for browser in [
                                "chrome",
                                "firefox",
                                "safari",
                                "edge",
                                "opera",
                                "brave",
                            ]
                        ):
                            proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                # Блокировка интернета (требует прав администратора)
                subprocess.run(
                    ["sudo", "iptables", "-A", "OUTPUT", "-j", "DROP"],
                    check=False,
                )

                logger.critical(
                    f"ЭКСТРЕННАЯ БЛОКИРОВКА УСТРОЙСТВА для ребенка {child_id}"
                )
                return True

            return False
        except Exception as e:
            logger.error(f"Ошибка экстренной блокировки: {e}")
            return False

    async def monitor_continuous_protection(self, child_id: str):
        """Непрерывный мониторинг защиты"""
        while True:
            try:
                # Проверка VPN
                vpn_detection = await self.detect_vpn_connection(child_id)
                if vpn_detection.vpn_detected:
                    bypass_attempt = BypassAttempt(
                        attempt_id=f"vpn_{int(time.time())}",
                        child_id=child_id,
                        bypass_method=BypassMethod.VPN_CONNECTION,
                        timestamp=datetime.now(),
                        ip_address="",
                        user_agent="",
                        browser_type="",
                        threat_level=ThreatLevel.CRITICAL,
                        blocked_urls=[],
                        success=False,
                        parent_notified=False,
                    )

                    await self.block_bypass_attempt(
                        child_id, BypassMethod.VPN_CONNECTION
                    )
                    await self.notify_parents(child_id, bypass_attempt)

                # Проверка инкогнито
                incognito_detection = await self.detect_incognito_mode(
                    child_id
                )
                if incognito_detection.incognito_detected:
                    bypass_attempt = BypassAttempt(
                        attempt_id=f"incognito_{int(time.time())}",
                        child_id=child_id,
                        bypass_method=BypassMethod.INCOGNITO_MODE,
                        timestamp=datetime.now(),
                        ip_address="",
                        user_agent="",
                        browser_type=incognito_detection.browser_type,
                        threat_level=ThreatLevel.HIGH,
                        blocked_urls=[],
                        success=False,
                        parent_notified=False,
                    )

                    await self.block_bypass_attempt(
                        child_id, BypassMethod.INCOGNITO_MODE
                    )
                    await self.notify_parents(child_id, bypass_attempt)

                # Пауза между проверками
                await asyncio.sleep(5)  # Проверка каждые 5 секунд

            except Exception as e:
                logger.error(f"Ошибка мониторинга: {e}")
                await asyncio.sleep(10)

    def get_protection_statistics(self, child_id: str) -> Dict[str, Any]:
        """Получение статистики защиты"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Статистика попыток обхода
                cursor = conn.execute(
                    """
                    SELECT bypass_method, COUNT(*) as count,
                           SUM(CASE WHEN success THEN 1 ELSE 0 END)
                           as successful
                    FROM bypass_attempts
                    WHERE child_id = ?
                    GROUP BY bypass_method
                """,
                    (child_id,),
                )

                bypass_stats = {}
                for row in cursor.fetchall():
                    bypass_stats[row[0]] = {
                        "total_attempts": row[1],
                        "successful_attempts": row[2],
                        "blocked_attempts": row[1] - row[2],
                    }

                # Статистика VPN детекций
                cursor = conn.execute(
                    """
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN blocked THEN 1 ELSE 0 END) as blocked
                    FROM vpn_detections
                    WHERE child_id = ?
                """,
                    (child_id,),
                )

                vpn_stats = cursor.fetchone()

                # Статистика инкогнито детекций
                cursor = conn.execute(
                    """
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN blocked THEN 1 ELSE 0 END) as blocked
                    FROM incognito_detections
                    WHERE child_id = ?
                """,
                    (child_id,),
                )

                incognito_stats = cursor.fetchone()

                return {
                    "bypass_attempts": bypass_stats,
                    "vpn_detections": {
                        "total": vpn_stats[0] if vpn_stats else 0,
                        "blocked": vpn_stats[1] if vpn_stats else 0,
                    },
                    "incognito_detections": {
                        "total": incognito_stats[0] if incognito_stats else 0,
                        "blocked": (
                            incognito_stats[1] if incognito_stats else 0
                        ),
                    },
                    "protection_level": self.protection_level,
                    "last_check": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}


# Пример использования
async def main():
    """Пример использования IncognitoProtectionBot"""
    bot = IncognitoProtectionBot()

    # Запуск мониторинга для ребенка
    child_id = "child_001"

    print(f"🛡️ Запуск максимальной защиты для ребенка {child_id}")
    print("🔍 Мониторинг VPN, инкогнито, прокси, Tor...")
    print("🚨 Экстренные уведомления включены")
    print("🔒 Автоматическая блокировка включена")

    # Запуск непрерывного мониторинга
    await bot.monitor_continuous_protection(child_id)


if __name__ == "__main__":
    asyncio.run(main())
