#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Threat Intelligence System для ALADDIN Security System
Система Threat Intelligence с бесплатными источниками

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
# import hashlib  # Не используется
import json
# import os  # Не используется
import re
import sqlite3
# import time  # Не используется
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx


class ThreatType(Enum):
    """Типы угроз"""

    MALWARE = "malware"
    PHISHING = "phishing"
    BOTNET = "botnet"
    SPAM = "spam"
    EXPLOIT = "exploit"
    VULNERABILITY = "vulnerability"
    RANSOMWARE = "ransomware"
    TROJAN = "trojan"
    BACKDOOR = "backdoor"
    KEYLOGGER = "keylogger"


class IndicatorType(Enum):
    """Типы индикаторов"""

    IP_ADDRESS = "ip"
    DOMAIN = "domain"
    URL = "url"
    EMAIL = "email"
    FILE_HASH = "hash"
    EMAIL_HASH = "email_hash"
    URL_HASH = "url_hash"
    USER_AGENT = "user_agent"


class ConfidenceLevel(Enum):
    """Уровни доверия"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ThreatIndicator:
    """Индикатор угрозы"""

    indicator: str
    indicator_type: IndicatorType
    threat_type: ThreatType
    confidence: ConfidenceLevel
    source: str
    description: str
    tags: List[str]
    first_seen: datetime
    last_seen: datetime
    references: List[str]
    raw_data: Dict[str, Any]


@dataclass
class ThreatFeed:
    """Источник угроз"""

    name: str
    url: str
    format: str  # json, csv, txt
    update_frequency: int  # минуты
    enabled: bool
    last_update: Optional[datetime]
    indicators_count: int


class ThreatIntelligenceSystem:
    """Система Threat Intelligence"""

    def __init__(self, db_path: str = "threat_intelligence.db"):
        self.db_path = db_path
        self.feeds = []
        self.init_database()
        self.load_default_feeds()

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS threat_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator TEXT UNIQUE,
                indicator_type TEXT,
                threat_type TEXT,
                confidence TEXT,
                source TEXT,
                description TEXT,
                tags TEXT,
                first_seen DATETIME,
                last_seen DATETIME,
                references TEXT,
                raw_data TEXT,
                timestamp DATETIME
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS threat_feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                url TEXT,
                format TEXT,
                update_frequency INTEGER,
                enabled BOOLEAN,
                last_update DATETIME,
                indicators_count INTEGER
            )
        """
        )

        conn.commit()
        conn.close()

    def load_default_feeds(self):
        """Загрузка бесплатных источников угроз"""
        self.feeds = [
            ThreatFeed(
                name="Abuse.ch URLhaus",
                url="https://urlhaus.abuse.ch/downloads/csv_recent/",
                format="csv",
                update_frequency=60,  # 1 час
                enabled=True,
                last_update=None,
                indicators_count=0,
            ),
            ThreatFeed(
                name="Abuse.ch Feodo Tracker",
                url="https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.txt",
                format="txt",
                update_frequency=60,
                enabled=True,
                last_update=None,
                indicators_count=0,
            ),
            ThreatFeed(
                name="Malware Domain List",
                url="https://www.malwaredomainlist.com/hostslist/hosts.txt",
                format="txt",
                update_frequency=120,  # 2 часа
                enabled=True,
                last_update=None,
                indicators_count=0,
            ),
            ThreatFeed(
                name="Phishing Database",
                url="https://openphish.com/feed.txt",
                format="txt",
                update_frequency=60,
                enabled=True,
                last_update=None,
                indicators_count=0,
            ),
            ThreatFeed(
                name="Spamhaus DROP List",
                url="https://www.spamhaus.org/drop/drop.txt",
                format="txt",
                update_frequency=240,  # 4 часа
                enabled=True,
                last_update=None,
                indicators_count=0,
            ),
            ThreatFeed(
                name="CINS Score",
                url="https://cinsscore.com/list/ci-badguys.txt",
                format="txt",
                update_frequency=180,  # 3 часа
                enabled=True,
                last_update=None,
                indicators_count=0,
            ),
        ]

        # Сохранение источников в базу данных
        self.save_feeds()

    def save_feeds(self):
        """Сохранение источников в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for feed in self.feeds:
            cursor.execute(
                """
                INSERT OR REPLACE INTO threat_feeds
                (name, url, format, update_frequency, enabled, last_update, indicators_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    feed.name,
                    feed.url,
                    feed.format,
                    feed.update_frequency,
                    feed.enabled,
                    feed.last_update.isoformat() if feed.last_update else None,
                    feed.indicators_count,
                ),
            )

        conn.commit()
        conn.close()

    async def update_threat_feeds(self):
        """Обновление источников угроз"""
        print("🔄 Обновление источников угроз...")

        for feed in self.feeds:
            if not feed.enabled:
                continue

            try:
                print(f"  Обновление {feed.name}...")
                indicators = await self._fetch_feed_data(feed)

                if indicators:
                    # Сохранение индикаторов
                    for indicator in indicators:
                        self.save_threat_indicator(indicator)

                    # Обновление информации о источнике
                    feed.last_update = datetime.now()
                    feed.indicators_count = len(indicators)

                    print(f"    ✅ Получено {len(indicators)} индикаторов")
                else:
                    print("    ⚠️ Нет новых индикаторов")

                # Ограничение скорости запросов
                await asyncio.sleep(2)

            except Exception as e:
                print(f"    ❌ Ошибка обновления {feed.name}: {e}")

        # Сохранение обновленных источников
        self.save_feeds()
        print("✅ Обновление источников завершено")

    async def _fetch_feed_data(
        self, feed: ThreatFeed
    ) -> List[ThreatIndicator]:
        """Получение данных из источника"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(feed.url)

                if response.status_code == 200:
                    if feed.format == "csv":
                        return self._parse_csv_feed(response.text, feed)
                    elif feed.format == "txt":
                        return self._parse_txt_feed(response.text, feed)
                    elif feed.format == "json":
                        return self._parse_json_feed(response.text, feed)

        except Exception as e:
            print(f"Error fetching feed {feed.name}: {e}")

        return []

    def _parse_csv_feed(
        self, content: str, feed: ThreatFeed
    ) -> List[ThreatIndicator]:
        """Парсинг CSV источника"""
        indicators = []
        lines = content.strip().split("\n")

        # Пропускаем заголовок
        for line in lines[1:]:
            if not line.strip():
                continue

            parts = line.split(",")
            if len(parts) >= 3:
                url = parts[1].strip('"')
                threat_type = parts[2].strip('"')

                if url and threat_type:
                    indicator = ThreatIndicator(
                        indicator=url,
                        indicator_type=IndicatorType.URL,
                        threat_type=self._map_threat_type(threat_type),
                        confidence=ConfidenceLevel.HIGH,
                        source=feed.name,
                        description=f"Malicious URL from {feed.name}",
                        tags=[threat_type.lower()],
                        first_seen=datetime.now(),
                        last_seen=datetime.now(),
                        references=[feed.url],
                        raw_data={
                            "feed": feed.name,
                            "threat_type": threat_type,
                        },
                    )
                    indicators.append(indicator)

        return indicators

    def _parse_txt_feed(
        self, content: str, feed: ThreatFeed
    ) -> List[ThreatIndicator]:
        """Парсинг TXT источника"""
        indicators = []
        lines = content.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Определение типа индикатора
            indicator_type = self._detect_indicator_type(line)

            if indicator_type:
                indicator = ThreatIndicator(
                    indicator=line,
                    indicator_type=indicator_type,
                    threat_type=self._map_feed_threat_type(feed.name),
                    confidence=ConfidenceLevel.MEDIUM,
                    source=feed.name,
                    description=f"Threat indicator from {feed.name}",
                    tags=[feed.name.lower().replace(" ", "_")],
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    references=[feed.url],
                    raw_data={"feed": feed.name},
                )
                indicators.append(indicator)

        return indicators

    def _parse_json_feed(
        self, content: str, feed: ThreatFeed
    ) -> List[ThreatIndicator]:
        """Парсинг JSON источника"""
        indicators = []

        try:
            data = json.loads(content)

            # Обработка различных форматов JSON
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        indicator = self._parse_json_indicator(item, feed)
                        if indicator:
                            indicators.append(indicator)
            elif isinstance(data, dict):
                indicator = self._parse_json_indicator(data, feed)
                if indicator:
                    indicators.append(indicator)

        except Exception as e:
            print(f"Error parsing JSON feed {feed.name}: {e}")

        return indicators

    def _parse_json_indicator(
        self, data: Dict[str, Any], feed: ThreatFeed
    ) -> Optional[ThreatIndicator]:
        """Парсинг JSON индикатора"""
        # Попытка найти индикатор в различных полях
        indicator = None
        for field in ["indicator", "value", "ip", "domain", "url", "hash"]:
            if field in data and data[field]:
                indicator = data[field]
                break

        if not indicator:
            return None

        indicator_type = self._detect_indicator_type(indicator)
        if not indicator_type:
            return None

        return ThreatIndicator(
            indicator=indicator,
            indicator_type=indicator_type,
            threat_type=self._map_feed_threat_type(feed.name),
            confidence=ConfidenceLevel.MEDIUM,
            source=feed.name,
            description=data.get(
                "description", f"Threat indicator from {feed.name}"
            ),
            tags=data.get("tags", [feed.name.lower().replace(" ", "_")]),
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            references=[feed.url],
            raw_data=data,
        )

    def _detect_indicator_type(
        self, indicator: str
    ) -> Optional[IndicatorType]:
        """Определение типа индикатора"""
        # IP адрес
        ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if re.match(ip_pattern, indicator):
            return IndicatorType.IP_ADDRESS

        # Домен
        domain_pattern = (
            r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
            r"(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
        )
        if re.match(domain_pattern, indicator) and "." in indicator:
            return IndicatorType.DOMAIN

        # URL
        if indicator.startswith(("http://", "https://")):
            return IndicatorType.URL

        # Email
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.match(email_pattern, indicator):
            return IndicatorType.EMAIL

        # Hash (MD5, SHA1, SHA256)
        hash_pattern = r"^[a-fA-F0-9]{32,64}$"
        if re.match(hash_pattern, indicator):
            if len(indicator) == 32:
                return IndicatorType.FILE_HASH
            elif len(indicator) == 40:
                return IndicatorType.FILE_HASH
            elif len(indicator) == 64:
                return IndicatorType.FILE_HASH

        return None

    def _map_threat_type(self, threat_type: str) -> ThreatType:
        """Маппинг типа угрозы"""
        threat_type = threat_type.lower()

        if "malware" in threat_type:
            return ThreatType.MALWARE
        elif "phishing" in threat_type:
            return ThreatType.PHISHING
        elif "botnet" in threat_type:
            return ThreatType.BOTNET
        elif "spam" in threat_type:
            return ThreatType.SPAM
        elif "exploit" in threat_type:
            return ThreatType.EXPLOIT
        elif "ransomware" in threat_type:
            return ThreatType.RANSOMWARE
        elif "trojan" in threat_type:
            return ThreatType.TROJAN
        elif "backdoor" in threat_type:
            return ThreatType.BACKDOOR
        elif "keylogger" in threat_type:
            return ThreatType.KEYLOGGER
        else:
            return ThreatType.MALWARE  # По умолчанию

    def _map_feed_threat_type(self, feed_name: str) -> ThreatType:
        """Маппинг типа угрозы по источнику"""
        feed_name = feed_name.lower()

        if "phishing" in feed_name:
            return ThreatType.PHISHING
        elif "spam" in feed_name:
            return ThreatType.SPAM
        elif "botnet" in feed_name:
            return ThreatType.BOTNET
        elif "malware" in feed_name:
            return ThreatType.MALWARE
        else:
            return ThreatType.MALWARE  # По умолчанию

    def save_threat_indicator(self, indicator: ThreatIndicator):
        """Сохранение индикатора угрозы"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO threat_indicators
            (indicator, indicator_type, threat_type, confidence, source, description,
             tags, first_seen, last_seen, references, raw_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                indicator.indicator,
                indicator.indicator_type.value,
                indicator.threat_type.value,
                indicator.confidence.value,
                indicator.source,
                indicator.description,
                json.dumps(indicator.tags),
                indicator.first_seen.isoformat(),
                indicator.last_seen.isoformat(),
                json.dumps(indicator.references),
                json.dumps(indicator.raw_data),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def check_threat_indicator(
        self, indicator: str
    ) -> Optional[ThreatIndicator]:
        """Проверка индикатора угрозы"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT indicator, indicator_type, threat_type, confidence, source, description,
                   tags, first_seen, last_seen, references, raw_data
            FROM threat_indicators
            WHERE indicator = ?
        """,
            (indicator,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return ThreatIndicator(
                indicator=row[0],
                indicator_type=IndicatorType(row[1]),
                threat_type=ThreatType(row[2]),
                confidence=ConfidenceLevel(row[3]),
                source=row[4],
                description=row[5],
                tags=json.loads(row[6]),
                first_seen=datetime.fromisoformat(row[7]),
                last_seen=datetime.fromisoformat(row[8]),
                references=json.loads(row[9]),
                raw_data=json.loads(row[10]),
            )

        return None

    def get_threat_statistics(self) -> Dict[str, Any]:
        """Получение статистики угроз"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Общая статистика
        cursor.execute("SELECT COUNT(*) FROM threat_indicators")
        total_indicators = cursor.fetchone()[0]

        # Статистика по типам индикаторов
        cursor.execute(
            """
            SELECT indicator_type, COUNT(*)
            FROM threat_indicators
            GROUP BY indicator_type
        """
        )
        indicator_types = dict(cursor.fetchall())

        # Статистика по типам угроз
        cursor.execute(
            """
            SELECT threat_type, COUNT(*)
            FROM threat_indicators
            GROUP BY threat_type
        """
        )
        threat_types = dict(cursor.fetchall())

        # Статистика по источникам
        cursor.execute(
            """
            SELECT source, COUNT(*)
            FROM threat_indicators
            GROUP BY source
        """
        )
        sources = dict(cursor.fetchall())

        # Статистика по уровням доверия
        cursor.execute(
            """
            SELECT confidence, COUNT(*)
            FROM threat_indicators
            GROUP BY confidence
        """
        )
        confidence_levels = dict(cursor.fetchall())

        conn.close()

        return {
            "total_indicators": total_indicators,
            "indicator_types": indicator_types,
            "threat_types": threat_types,
            "sources": sources,
            "confidence_levels": confidence_levels,
            "last_updated": datetime.now().isoformat(),
        }

    def get_recent_threats(self, limit: int = 100) -> List[ThreatIndicator]:
        """Получение последних угроз"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT indicator, indicator_type, threat_type, confidence, source, description,
                   tags, first_seen, last_seen, references, raw_data
            FROM threat_indicators
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                ThreatIndicator(
                    indicator=row[0],
                    indicator_type=IndicatorType(row[1]),
                    threat_type=ThreatType(row[2]),
                    confidence=ConfidenceLevel(row[3]),
                    source=row[4],
                    description=row[5],
                    tags=json.loads(row[6]),
                    first_seen=datetime.fromisoformat(row[7]),
                    last_seen=datetime.fromisoformat(row[8]),
                    references=json.loads(row[9]),
                    raw_data=json.loads(row[10]),
                )
            )

        conn.close()
        return results

    def search_threats(
        self, query: str, limit: int = 100
    ) -> List[ThreatIndicator]:
        """Поиск угроз"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT indicator, indicator_type, threat_type, confidence, source, description,
                   tags, first_seen, last_seen, references, raw_data
            FROM threat_indicators
            WHERE indicator LIKE ? OR description LIKE ? OR tags LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (f"%{query}%", f"%{query}%", f"%{query}%", limit),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                ThreatIndicator(
                    indicator=row[0],
                    indicator_type=IndicatorType(row[1]),
                    threat_type=ThreatType(row[2]),
                    confidence=ConfidenceLevel(row[3]),
                    source=row[4],
                    description=row[5],
                    tags=json.loads(row[6]),
                    first_seen=datetime.fromisoformat(row[7]),
                    last_seen=datetime.fromisoformat(row[8]),
                    references=json.loads(row[9]),
                    raw_data=json.loads(row[10]),
                )
            )

        conn.close()
        return results

    def get_feeds_status(self) -> List[ThreatFeed]:
        """Получение статуса источников"""
        return self.feeds


# Пример использования
async def main():
    """Основная функция"""
    ti_system = ThreatIntelligenceSystem()

    print("🔄 Инициализация системы Threat Intelligence...")

    # Обновление источников угроз
    await ti_system.update_threat_feeds()

    # Получение статистики
    stats = ti_system.get_threat_statistics()
    print("\n📊 Статистика угроз:")
    print(f"  Всего индикаторов: {stats['total_indicators']}")
    print(f"  Типы индикаторов: {stats['indicator_types']}")
    print(f"  Типы угроз: {stats['threat_types']}")
    print(f"  Источники: {list(stats['sources'].keys())}")

    # Получение последних угроз
    recent_threats = ti_system.get_recent_threats(10)
    print(f"\n🚨 Последние {len(recent_threats)} угроз:")
    for threat in recent_threats[:5]:
        print(
            f"  {threat.indicator} ({threat.threat_type.value}) - {threat.source}"
        )

    # Тест проверки индикатора
    if recent_threats:
        test_indicator = recent_threats[0].indicator
        result = ti_system.check_threat_indicator(test_indicator)
        if result:
            print(f"\n🔍 Проверка индикатора {test_indicator}:")
            print(f"  Тип: {result.threat_type.value}")
            print(f"  Доверие: {result.confidence.value}")
            print(f"  Источник: {result.source}")
            print(f"  Описание: {result.description}")

    print("\n✅ Система Threat Intelligence готова к работе!")


if __name__ == "__main__":
    asyncio.run(main())
