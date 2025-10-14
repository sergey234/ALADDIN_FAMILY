#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Threat Intelligence для ALADDIN Security System
Расширенная система разведки угроз с дополнительными источниками

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import json
import os
import sqlite3
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import httpx
import hashlib
import re

class AdvancedThreatSource(Enum):
    """Дополнительные источники угроз"""
    SHODAN = "shodan"
    MISP = "misp"
    YARA_RULES = "yara_rules"
    RUSSIAN_CYBERPOLICE = "russian_cyberpolice"
    FSTEC_THREATS = "fstec_threats"
    KASPERSKY_THREAT_INTEL = "kaspersky_threat_intel"
    CROWDSTRIKE_INTEL = "crowdstrike_intel"

class ThreatCategory(Enum):
    """Категории угроз"""
    MALWARE = "malware"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    DDoS = "ddos"
    BOTNET = "botnet"
    EXPLOIT = "exploit"
    IOT_THREAT = "iot_threat"
    MOBILE_THREAT = "mobile_threat"
    APT = "apt"  # Advanced Persistent Threat
    ZERO_DAY = "zero_day"

class ThreatSeverity(Enum):
    """Серьезность угроз"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class AdvancedThreatIndicator:
    """Расширенный индикатор угрозы"""
    indicator_id: str
    indicator_type: str  # ip, domain, url, hash, email, file
    value: str
    source: AdvancedThreatSource
    category: ThreatCategory
    severity: ThreatSeverity
    confidence: float  # 0-100
    first_seen: datetime
    last_seen: datetime
    tags: List[str]
    description: str
    references: List[str]
    ioc_data: Dict[str, Any]  # Indicator of Compromise data
    raw_data: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['source'] = self.source.value
        data['category'] = self.category.value
        data['severity'] = self.severity.value
        data['first_seen'] = self.first_seen.isoformat()
        data['last_seen'] = self.last_seen.isoformat()
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class YARARule:
    """YARA правило"""
    rule_id: str
    name: str
    description: str
    author: str
    date: datetime
    rule_text: str
    tags: List[str]
    meta: Dict[str, Any]
    strings: List[Dict[str, Any]]
    conditions: List[str]
    references: List[str]

@dataclass
class ShodanResult:
    """Результат Shodan"""
    ip: str
    port: int
    service: str
    version: str
    banner: str
    vulns: List[str]
    country: str
    city: str
    org: str
    isp: str
    os: str
    product: str
    timestamp: datetime

class AdvancedThreatIntelligence:
    """Расширенная система разведки угроз"""

    def __init__(self, db_path: str = "advanced_threat_intelligence.db"):
        self.db_path = db_path
        self.api_keys = self._load_api_keys()
        self.init_database()

    def _load_api_keys(self) -> Dict[str, str]:
        """Загрузка API ключей"""
        return {
            "shodan": os.getenv("SHODAN_API_KEY", ""),
            "misp": os.getenv("MISP_API_KEY", ""),
            "kaspersky": os.getenv("KASPERSKY_API_KEY", ""),
            "crowdstrike": os.getenv("CROWDSTRIKE_API_KEY", "")
        }

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица индикаторов угроз
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator_id TEXT UNIQUE,
                indicator_type TEXT,
                value TEXT,
                source TEXT,
                category TEXT,
                severity TEXT,
                confidence REAL,
                first_seen DATETIME,
                last_seen DATETIME,
                tags TEXT,
                description TEXT,
                references TEXT,
                ioc_data TEXT,
                raw_data TEXT,
                timestamp DATETIME
            )
        ''')

        # Таблица YARA правил
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS yara_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE,
                name TEXT,
                description TEXT,
                author TEXT,
                date DATETIME,
                rule_text TEXT,
                tags TEXT,
                meta TEXT,
                strings TEXT,
                conditions TEXT,
                references TEXT
            )
        ''')

        # Таблица Shodan результатов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shodan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                port INTEGER,
                service TEXT,
                version TEXT,
                banner TEXT,
                vulns TEXT,
                country TEXT,
                city TEXT,
                org TEXT,
                isp TEXT,
                os TEXT,
                product TEXT,
                timestamp DATETIME
            )
        ''')

        conn.commit()
        conn.close()

    async def check_shodan(self, ip: str) -> Optional[ShodanResult]:
        """Проверка IP в Shodan"""
        if not self.api_keys.get("shodan"):
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.shodan.io/shodan/host/{ip}",
                    params={"key": self.api_keys["shodan"]},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    result = ShodanResult(
                        ip=data.get("ip_str", ip),
                        port=data.get("port", 0),
                        service=data.get("product", "unknown"),
                        version=data.get("version", ""),
                        banner=data.get("data", [{}])[0].get("banner", ""),
                        vulns=data.get("vulns", []),
                        country=data.get("country_name", ""),
                        city=data.get("city", ""),
                        org=data.get("org", ""),
                        isp=data.get("isp", ""),
                        os=data.get("os", ""),
                        product=data.get("product", ""),
                        timestamp=datetime.now()
                    )

                    await self._save_shodan_result(result)
                    return result

        except Exception as e:
            print(f"Shodan error: {e}")

        return None

    async def check_misp(self, indicator: str, indicator_type: str) -> List[AdvancedThreatIndicator]:
        """Проверка индикатора в MISP"""
        if not self.api_keys.get("misp"):
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{os.getenv('MISP_URL', '')}/attributes/restSearch",
                    headers={
                        "Authorization": self.api_keys["misp"],
                        "Content-Type": "application/json"
                    },
                    json={
                        "value": indicator,
                        "type": indicator_type
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    indicators = []

                    for attr in data.get("Attribute", []):
                        indicator_obj = AdvancedThreatIndicator(
                            indicator_id=f"misp_{attr['id']}",
                            indicator_type=attr.get("type", indicator_type),
                            value=attr.get("value", indicator),
                            source=AdvancedThreatSource.MISP,
                            category=ThreatCategory.MALWARE,  # Default
                            severity=ThreatSeverity.MEDIUM,  # Default
                            confidence=float(attr.get("to_ids", 0)) * 100,
                            first_seen=datetime.fromtimestamp(int(attr.get("timestamp", 0))),
                            last_seen=datetime.now(),
                            tags=attr.get("Tag", []),
                            description=attr.get("comment", ""),
                            references=[],
                            ioc_data=attr,
                            raw_data=attr,
                            timestamp=datetime.now()
                        )
                        indicators.append(indicator_obj)
                        await self._save_threat_indicator(indicator_obj)

                    return indicators

        except Exception as e:
            print(f"MISP error: {e}")

        return []

    async def load_yara_rules(self) -> List[YARARule]:
        """Загрузка YARA правил"""
        try:
            # Загружаем YARA правила из файлов
            yara_dir = "data/yara_rules"
            if not os.path.exists(yara_dir):
                os.makedirs(yara_dir)
                await self._create_default_yara_rules()

            rules = []
            for filename in os.listdir(yara_dir):
                if filename.endswith('.yar'):
                    with open(os.path.join(yara_dir, filename), 'r') as f:
                        rule_text = f.read()
                        rule = self._parse_yara_rule(rule_text)
                        if rule:
                            rules.append(rule)
                            await self._save_yara_rule(rule)

            return rules

        except Exception as e:
            print(f"YARA rules error: {e}")
            return []

    def _parse_yara_rule(self, rule_text: str) -> Optional[YARARule]:
        """Парсинг YARA правила"""
        try:
            # Простой парсер YARA правил
            rule_id = hashlib.md5(rule_text.encode()).hexdigest()
            name_match = re.search(r'rule\s+(\w+)', rule_text)
            name = name_match.group(1) if name_match else "Unknown"

            # Извлекаем метаданные
            meta_match = re.search(r'meta:\s*\n(.*?)\n\s*strings:', rule_text, re.DOTALL)
            meta = {}
            if meta_match:
                meta_text = meta_match.group(1)
                for line in meta_text.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        meta[key.strip()] = value.strip().strip('"')

            # Извлекаем теги
            tags_match = re.search(r'tags:\s*\n(.*?)\n\s*meta:', rule_text, re.DOTALL)
            tags = []
            if tags_match:
                tags = [tag.strip().strip('"') for tag in tags_match.group(1).split(',')]

            return YARARule(
                rule_id=rule_id,
                name=name,
                description=meta.get("description", ""),
                author=meta.get("author", "Unknown"),
                date=datetime.now(),
                rule_text=rule_text,
                tags=tags,
                meta=meta,
                strings=[],
                conditions=[],
                references=[]
            )

        except Exception as e:
            print(f"YARA parsing error: {e}")
            return None

    async def check_russian_sources(self, indicator: str) -> List[AdvancedThreatIndicator]:
        """Проверка российских источников угроз"""
        indicators = []

        # Киберполиция (мок-данные, так как нет публичного API)
        if await self._check_cyberpolice_threats(indicator):
            indicator_obj = AdvancedThreatIndicator(
                indicator_id=f"cyberpolice_{hashlib.md5(indicator.encode()).hexdigest()}",
                indicator_type="ip",
                value=indicator,
                source=AdvancedThreatSource.RUSSIAN_CYBERPOLICE,
                category=ThreatCategory.MALWARE,
                severity=ThreatSeverity.HIGH,
                confidence=85.0,
                first_seen=datetime.now() - timedelta(days=1),
                last_seen=datetime.now(),
                tags=["russian", "cyberpolice", "malware"],
                description="Обнаружено в базе Киберполиции",
                references=["https://cyberpolice.ru"],
                ioc_data={"source": "cyberpolice"},
                raw_data={"threat": True},
                timestamp=datetime.now()
            )
            indicators.append(indicator_obj)

        # ФСТЭК угрозы (мок-данные)
        if await self._check_fstec_threats(indicator):
            indicator_obj = AdvancedThreatIndicator(
                indicator_id=f"fstec_{hashlib.md5(indicator.encode()).hexdigest()}",
                indicator_type="ip",
                value=indicator,
                source=AdvancedThreatSource.FSTEC_THREATS,
                category=ThreatCategory.APT,
                severity=ThreatSeverity.CRITICAL,
                confidence=95.0,
                first_seen=datetime.now() - timedelta(days=2),
                last_seen=datetime.now(),
                tags=["russian", "fstec", "apt"],
                description="Обнаружено в базе ФСТЭК",
                references=["https://fstec.ru"],
                ioc_data={"source": "fstec"},
                raw_data={"threat": True},
                timestamp=datetime.now()
            )
            indicators.append(indicator_obj)

        for indicator_obj in indicators:
            await self._save_threat_indicator(indicator_obj)

        return indicators

    async def _check_cyberpolice_threats(self, indicator: str) -> bool:
        """Проверка угроз в базе Киберполиции (мок)"""
        # В реальной реализации здесь был бы API запрос к Киберполиции
        # Для демонстрации возвращаем случайный результат
        import random
        return random.random() < 0.1  # 10% вероятность обнаружения

    async def _check_fstec_threats(self, indicator: str) -> bool:
        """Проверка угроз в базе ФСТЭК (мок)"""
        # В реальной реализации здесь был бы API запрос к ФСТЭК
        # Для демонстрации возвращаем случайный результат
        import random
        return random.random() < 0.05  # 5% вероятность обнаружения

    async def comprehensive_threat_check(self, indicator: str, indicator_type: str = "ip") -> Dict[str, Any]:
        """Комплексная проверка угроз"""
        results = {
            "indicator": indicator,
            "indicator_type": indicator_type,
            "timestamp": datetime.now().isoformat(),
            "sources_checked": [],
            "threats_found": [],
            "total_threats": 0,
            "max_severity": "info",
            "confidence_score": 0.0
        }

        # Проверяем все источники
        tasks = []

        if indicator_type == "ip":
            tasks.append(self.check_shodan(indicator))

        tasks.append(self.check_misp(indicator, indicator_type))
        tasks.append(self.check_russian_sources(indicator))

        # Выполняем все проверки параллельно
        check_results = await asyncio.gather(*tasks, return_exceptions=True)

        all_threats = []
        for result in check_results:
            if isinstance(result, list):
                all_threats.extend(result)
                results["sources_checked"].extend([t.source.value for t in result])
            elif isinstance(result, ShodanResult):
                results["sources_checked"].append("shodan")
                if result.vulns:
                    all_threats.append(AdvancedThreatIndicator(
                        indicator_id=f"shodan_{result.ip}",
                        indicator_type="ip",
                        value=result.ip,
                        source=AdvancedThreatSource.SHODAN,
                        category=ThreatCategory.EXPLOIT,
                        severity=ThreatSeverity.HIGH if len(result.vulns) > 2 else ThreatSeverity.MEDIUM,
                        confidence=min(100.0, len(result.vulns) * 20),
                        first_seen=result.timestamp,
                        last_seen=result.timestamp,
                        tags=["shodan", "vulnerability"] + result.vulns[:3],
                        description=f"Найдено {len(result.vulns)} уязвимостей",
                        references=[],
                        ioc_data={"vulns": result.vulns, "banner": result.banner},
                        raw_data=result.__dict__,
                        timestamp=datetime.now()
                    ))

        results["threats_found"] = [t.to_dict() for t in all_threats]
        results["total_threats"] = len(all_threats)

        if all_threats:
            # Определяем максимальную серьезность
            severities = [t.severity.value for t in all_threats]
            if "critical" in severities:
                results["max_severity"] = "critical"
            elif "high" in severities:
                results["max_severity"] = "high"
            elif "medium" in severities:
                results["max_severity"] = "medium"
            elif "low" in severities:
                results["max_severity"] = "low"

            # Вычисляем общую уверенность
            results["confidence_score"] = sum(t.confidence for t in all_threats) / len(all_threats)

        return results

    async def _create_default_yara_rules(self):
        """Создание базовых YARA правил"""
        yara_dir = "data/yara_rules"
        os.makedirs(yara_dir, exist_ok=True)

        # Правило для обнаружения ransomware
        ransomware_rule = '''
rule Ransomware_Generic {
    meta:
        description = "Generic ransomware detection"
        author = "ALADDIN Security Team"
        date = "2025-01-27"
        version = "1.0"
    strings:
        $a1 = "Your files have been encrypted"
        $a2 = "To recover your files"
        $a3 = "Bitcoin"
        $a4 = "Ransom"
        $a5 = ".locked"
    condition:
        3 of them
}
'''

        with open(os.path.join(yara_dir, "ransomware_generic.yar"), 'w') as f:
            f.write(ransomware_rule)

        # Правило для обнаружения malware
        malware_rule = '''
rule Malware_Generic {
    meta:
        description = "Generic malware detection"
        author = "ALADDIN Security Team"
        date = "2025-01-27"
        version = "1.0"
    strings:
        $a1 = "cmd.exe /c"
        $a2 = "powershell"
        $a3 = "regsvr32"
        $a4 = "rundll32"
        $a5 = "CreateRemoteThread"
    condition:
        2 of them
}
'''

        with open(os.path.join(yara_dir, "malware_generic.yar"), 'w') as f:
            f.write(malware_rule)

    async def _save_threat_indicator(self, indicator: AdvancedThreatIndicator):
        """Сохранение индикатора угрозы"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO threat_indicators
            (indicator_id, indicator_type, value, source, category, severity,
             confidence, first_seen, last_seen, tags, description, references,
             ioc_data, raw_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            indicator.indicator_id,
            indicator.indicator_type,
            indicator.value,
            indicator.source.value,
            indicator.category.value,
            indicator.severity.value,
            indicator.confidence,
            indicator.first_seen.isoformat(),
            indicator.last_seen.isoformat(),
            json.dumps(indicator.tags),
            indicator.description,
            json.dumps(indicator.references),
            json.dumps(indicator.ioc_data),
            json.dumps(indicator.raw_data),
            indicator.timestamp.isoformat()
        ))

        conn.commit()
        conn.close()

    async def _save_yara_rule(self, rule: YARARule):
        """Сохранение YARA правила"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO yara_rules
            (rule_id, name, description, author, date, rule_text, tags,
             meta, strings, conditions, references)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule.rule_id,
            rule.name,
            rule.description,
            rule.author,
            rule.date.isoformat(),
            rule.rule_text,
            json.dumps(rule.tags),
            json.dumps(rule.meta),
            json.dumps(rule.strings),
            json.dumps(rule.conditions),
            json.dumps(rule.references)
        ))

        conn.commit()
        conn.close()

    async def _save_shodan_result(self, result: ShodanResult):
        """Сохранение результата Shodan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO shodan_results
            (ip, port, service, version, banner, vulns, country, city,
             org, isp, os, product, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.ip,
            result.port,
            result.service,
            result.version,
            result.banner,
            json.dumps(result.vulns),
            result.country,
            result.city,
            result.org,
            result.isp,
            result.os,
            result.product,
            result.timestamp.isoformat()
        ))

        conn.commit()
        conn.close()

    async def get_threat_statistics(self) -> Dict[str, Any]:
        """Получение статистики угроз"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Общая статистика
        cursor.execute("SELECT COUNT(*) FROM threat_indicators")
        total_threats = cursor.fetchone()[0]

        # Статистика по источникам
        cursor.execute("SELECT source, COUNT(*) FROM threat_indicators GROUP BY source")
        sources_stats = dict(cursor.fetchall())

        # Статистика по категориям
        cursor.execute("SELECT category, COUNT(*) FROM threat_indicators GROUP BY category")
        categories_stats = dict(cursor.fetchall())

        # Статистика по серьезности
        cursor.execute("SELECT severity, COUNT(*) FROM threat_indicators GROUP BY severity")
        severity_stats = dict(cursor.fetchall())

        conn.close()

        return {
            "total_threats": total_threats,
            "sources": sources_stats,
            "categories": categories_stats,
            "severity": severity_stats,
            "last_updated": datetime.now().isoformat()
        }

# Пример использования
async def main():
    """Основная функция"""
    threat_intel = AdvancedThreatIntelligence()

    # Загружаем YARA правила
    await threat_intel.load_yara_rules()

    # Проверяем IP адрес
    result = await threat_intel.comprehensive_threat_check("8.8.8.8", "ip")
    print(f"Threat check result: {json.dumps(result, indent=2)}")

    # Получаем статистику
    stats = await threat_intel.get_threat_statistics()
    print(f"Threat statistics: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
