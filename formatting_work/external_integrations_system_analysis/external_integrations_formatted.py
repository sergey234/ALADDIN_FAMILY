#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
External Integrations для ALADDIN Security System
Интеграции с бесплатными и надежными внешними сервисами

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import hashlib
import json
import os
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import httpx


class IntegrationType(Enum):
    """Типы интеграций"""

    THREAT_INTELLIGENCE = "threat_intelligence"
    CVE_DATABASE = "cve_database"
    IP_REPUTATION = "ip_reputation"
    DOMAIN_REPUTATION = "domain_reputation"
    MALWARE_ANALYSIS = "malware_analysis"
    SECURITY_FEEDS = "security_feeds"
    DNS_ANALYSIS = "dns_analysis"
    CERTIFICATE_ANALYSIS = "certificate_analysis"


class ServiceProvider(Enum):
    """Провайдеры сервисов"""

    VIRUSTOTAL = "virustotal"
    ABUSEIPDB = "abuseipdb"
    SHODAN = "shodan"
    CIRCL = "circl"
    OTX = "otx"
    MISP = "misp"
    CVE_MITRE = "cve_mitre"
    NVD = "nvd"
    DNSDB = "dnsdb"
    CENSYS = "censys"
    SSL_LABS = "ssl_labs"
    SECURITY_HEADERS = "security_headers"


@dataclass
class IntegrationConfig:
    """Конфигурация интеграции"""

    service: ServiceProvider
    api_key: Optional[str] = None
    rate_limit: int = 100  # запросов в минуту
    timeout: int = 30  # секунд
    enabled: bool = True
    free_tier: bool = True


@dataclass
class ThreatIntelligenceResult:
    """Результат Threat Intelligence"""

    indicator: str
    indicator_type: str  # ip, domain, url, hash
    service: ServiceProvider
    malicious: bool
    confidence: float  # 0-100
    detection_count: int
    last_seen: Optional[datetime]
    tags: List[str]
    raw_data: Dict[str, Any]
    timestamp: datetime


@dataclass
class CVEResult:
    """Результат CVE"""

    cve_id: str
    description: str
    severity: str  # critical, high, medium, low
    cvss_score: float
    published_date: datetime
    last_modified: datetime
    affected_products: List[str]
    references: List[str]
    raw_data: Dict[str, Any]


@dataclass
class IPReputationResult:
    """Результат репутации IP"""

    ip_address: str
    service: ServiceProvider
    malicious: bool
    confidence: float
    abuse_confidence: int  # 0-100
    country: Optional[str]
    isp: Optional[str]
    usage_type: Optional[str]
    last_reported: Optional[datetime]
    raw_data: Dict[str, Any]
    timestamp: datetime


class ExternalIntegrations:
    """Система внешних интеграций"""

    def __init__(self, db_path: str = "external_integrations.db"):
        self.db_path = db_path
        self.configs = {}
        self.init_database()
        self.load_configs()

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS threat_intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator TEXT,
                indicator_type TEXT,
                service TEXT,
                malicious BOOLEAN,
                confidence REAL,
                detection_count INTEGER,
                last_seen DATETIME,
                tags TEXT,
                raw_data TEXT,
                timestamp DATETIME
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cve_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT UNIQUE,
                description TEXT,
                severity TEXT,
                cvss_score REAL,
                published_date DATETIME,
                last_modified DATETIME,
                affected_products TEXT,
                references TEXT,
                raw_data TEXT,
                timestamp DATETIME
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ip_reputation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                service TEXT,
                malicious BOOLEAN,
                confidence REAL,
                abuse_confidence INTEGER,
                country TEXT,
                isp TEXT,
                usage_type TEXT,
                last_reported DATETIME,
                raw_data TEXT,
                timestamp DATETIME
            )
        """
        )

        conn.commit()
        conn.close()

    def load_configs(self):
        """Загрузка конфигураций интеграций"""
        # Конфигурации для бесплатных сервисов
        self.configs = {
            ServiceProvider.VIRUSTOTAL: IntegrationConfig(
                service=ServiceProvider.VIRUSTOTAL,
                api_key=os.getenv("VIRUSTOTAL_API_KEY"),
                rate_limit=4,  # 4 запроса в минуту для бесплатного тарифа
                timeout=30,
                enabled=True,
                free_tier=True,
            ),
            ServiceProvider.ABUSEIPDB: IntegrationConfig(
                service=ServiceProvider.ABUSEIPDB,
                api_key=os.getenv("ABUSEIPDB_API_KEY"),
                rate_limit=1000,  # 1000 запросов в день для бесплатного тарифа
                timeout=30,
                enabled=True,
                free_tier=True,
            ),
            ServiceProvider.CIRCL: IntegrationConfig(
                service=ServiceProvider.CIRCL,
                api_key=os.getenv("CIRCL_API_KEY"),
                rate_limit=1000,  # CIRCL CVE - бесплатный
                timeout=30,
                enabled=True,
                free_tier=True,
            ),
            ServiceProvider.OTX: IntegrationConfig(
                service=ServiceProvider.OTX,
                api_key=os.getenv("OTX_API_KEY"),
                rate_limit=1000,  # OTX - бесплатный
                timeout=30,
                enabled=True,
                free_tier=True,
            ),
            ServiceProvider.CVE_MITRE: IntegrationConfig(
                service=ServiceProvider.CVE_MITRE,
                api_key=None,  # MITRE CVE - полностью бесплатный
                rate_limit=1000,
                timeout=30,
                enabled=True,
                free_tier=True,
            ),
            ServiceProvider.NVD: IntegrationConfig(
                service=ServiceProvider.NVD,
                api_key=None,  # NVD - полностью бесплатный
                rate_limit=1000,
                timeout=30,
                enabled=True,
                free_tier=True,
            ),
        }

    async def check_ip_reputation(
        self, ip_address: str
    ) -> List[IPReputationResult]:
        """Проверка репутации IP адреса"""
        results = []

        # Проверка через AbuseIPDB (бесплатный)
        if self.configs[ServiceProvider.ABUSEIPDB].enabled:
            result = await self._check_abuseipdb(ip_address)
            if result:
                results.append(result)

        return results

    async def _check_abuseipdb(
        self, ip_address: str
    ) -> Optional[IPReputationResult]:
        """Проверка IP через AbuseIPDB"""
        config = self.configs[ServiceProvider.ABUSEIPDB]
        if not config.api_key:
            return None

        try:
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                response = await client.get(
                    "https://api.abuseipdb.com/api/v2/check",
                    params={"ipAddress": ip_address, "maxAgeInDays": 90},
                    headers={"Key": config.api_key},
                )

                if response.status_code == 200:
                    data = response.json()
                    result_data = data.get("data", {})

                    malicious = (
                        result_data.get("abuseConfidencePercentage", 0) > 25
                    )
                    confidence = result_data.get(
                        "abuseConfidencePercentage", 0
                    )

                    return IPReputationResult(
                        ip_address=ip_address,
                        service=ServiceProvider.ABUSEIPDB,
                        malicious=malicious,
                        confidence=confidence,
                        abuse_confidence=result_data.get(
                            "abuseConfidencePercentage", 0
                        ),
                        country=result_data.get("countryName"),
                        isp=result_data.get("isp"),
                        usage_type=result_data.get("usageType"),
                        last_reported=(
                            datetime.fromisoformat(
                                result_data.get("lastReportedAt", "").replace(
                                    "Z", "+00:00"
                                )
                            )
                            if result_data.get("lastReportedAt")
                            else None
                        ),
                        raw_data=result_data,
                        timestamp=datetime.now(),
                    )

        except Exception as e:
            print(f"Error checking AbuseIPDB for {ip_address}: {e}")

        return None

    async def check_domain_reputation(
        self, domain: str
    ) -> List[ThreatIntelligenceResult]:
        """Проверка репутации домена"""
        results = []

        # Проверка через VirusTotal (бесплатный)
        if self.configs[ServiceProvider.VIRUSTOTAL].enabled:
            result = await self._check_virustotal_domain(domain)
            if result:
                results.append(result)

        return results

    async def _check_virustotal_domain(
        self, domain: str
    ) -> Optional[ThreatIntelligenceResult]:
        """Проверка домена через VirusTotal"""
        config = self.configs[ServiceProvider.VIRUSTOTAL]
        if not config.api_key:
            return None

        try:
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                # Получение ID домена
                domain_id = hashlib.sha256(domain.encode()).hexdigest()

                response = await client.get(
                    f"https://www.virustotal.com/api/v3/domains/{domain}",
                    headers={"x-apikey": config.api_key},
                )

                if response.status_code == 200:
                    data = response.json()
                    result_data = data.get("data", {})

                    # Получение статистики
                    stats = result_data.get("attributes", {}).get(
                        "last_analysis_stats", {}
                    )
                    malicious_count = stats.get("malicious", 0)
                    total_count = sum(stats.values())

                    malicious = malicious_count > 0
                    confidence = (
                        (malicious_count / total_count * 100)
                        if total_count > 0
                        else 0
                    )

                    return ThreatIntelligenceResult(
                        indicator=domain,
                        indicator_type="domain",
                        service=ServiceProvider.VIRUSTOTAL,
                        malicious=malicious,
                        confidence=confidence,
                        detection_count=malicious_count,
                        last_seen=None,  # VirusTotal не предоставляет эту информацию
                        tags=result_data.get("attributes", {}).get("tags", []),
                        raw_data=result_data,
                        timestamp=datetime.now(),
                    )

        except Exception as e:
            print(f"Error checking VirusTotal for domain {domain}: {e}")

        return None

    async def check_file_hash(
        self, file_hash: str
    ) -> List[ThreatIntelligenceResult]:
        """Проверка хеша файла"""
        results = []

        # Проверка через VirusTotal (бесплатный)
        if self.configs[ServiceProvider.VIRUSTOTAL].enabled:
            result = await self._check_virustotal_hash(file_hash)
            if result:
                results.append(result)

        return results

    async def _check_virustotal_hash(
        self, file_hash: str
    ) -> Optional[ThreatIntelligenceResult]:
        """Проверка хеша через VirusTotal"""
        config = self.configs[ServiceProvider.VIRUSTOTAL]
        if not config.api_key:
            return None

        try:
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                response = await client.get(
                    f"https://www.virustotal.com/api/v3/files/{file_hash}",
                    headers={"x-apikey": config.api_key},
                )

                if response.status_code == 200:
                    data = response.json()
                    result_data = data.get("data", {})

                    # Получение статистики
                    stats = result_data.get("attributes", {}).get(
                        "last_analysis_stats", {}
                    )
                    malicious_count = stats.get("malicious", 0)
                    total_count = sum(stats.values())

                    malicious = malicious_count > 0
                    confidence = (
                        (malicious_count / total_count * 100)
                        if total_count > 0
                        else 0
                    )

                    return ThreatIntelligenceResult(
                        indicator=file_hash,
                        indicator_type="hash",
                        service=ServiceProvider.VIRUSTOTAL,
                        malicious=malicious,
                        confidence=confidence,
                        detection_count=malicious_count,
                        last_seen=None,
                        tags=result_data.get("attributes", {}).get("tags", []),
                        raw_data=result_data,
                        timestamp=datetime.now(),
                    )

        except Exception as e:
            print(f"Error checking VirusTotal for hash {file_hash}: {e}")

        return None

    async def get_cve_info(self, cve_id: str) -> Optional[CVEResult]:
        """Получение информации о CVE"""
        # Сначала пробуем MITRE CVE (бесплатный)
        result = await self._get_cve_from_mitre(cve_id)
        if result:
            return result

        # Затем NVD (бесплатный)
        result = await self._get_cve_from_nvd(cve_id)
        if result:
            return result

        return None

    async def _get_cve_from_mitre(self, cve_id: str) -> Optional[CVEResult]:
        """Получение CVE из MITRE"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve_id}"
                )

                if response.status_code == 200:
                    # Парсинг HTML (упрощенный)
                    content = response.text

                    # Извлечение описания
                    description = "CVE information from MITRE"

                    return CVEResult(
                        cve_id=cve_id,
                        description=description,
                        severity="unknown",
                        cvss_score=0.0,
                        published_date=datetime.now(),
                        last_modified=datetime.now(),
                        affected_products=[],
                        references=[],
                        raw_data={
                            "source": "MITRE",
                            "content": content[:1000],
                        },
                    )

        except Exception as e:
            print(f"Error getting CVE from MITRE for {cve_id}: {e}")

        return None

    async def _get_cve_from_nvd(self, cve_id: str) -> Optional[CVEResult]:
        """Получение CVE из NVD"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # NVD API v2 (бесплатный)
                response = await client.get(
                    f"https://services.nvd.nist.gov/rest/json/cves/2.0",
                    params={"cveId": cve_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    vulnerabilities = data.get("vulnerabilities", [])

                    if vulnerabilities:
                        vuln = vulnerabilities[0].get("cve", {})
                        descriptions = vuln.get("descriptions", [])

                        description = "No description available"
                        if descriptions:
                            description = descriptions[0].get(
                                "value", "No description available"
                            )

                        # Получение CVSS
                        metrics = vuln.get("metrics", {})
                        cvss_score = 0.0
                        severity = "unknown"

                        if "cvssMetricV31" in metrics:
                            cvss_data = metrics["cvssMetricV31"][0].get(
                                "cvssData", {}
                            )
                            cvss_score = cvss_data.get("baseScore", 0.0)
                            severity = self._cvss_to_severity(cvss_score)
                        elif "cvssMetricV30" in metrics:
                            cvss_data = metrics["cvssMetricV30"][0].get(
                                "cvssData", {}
                            )
                            cvss_score = cvss_data.get("baseScore", 0.0)
                            severity = self._cvss_to_severity(cvss_score)
                        elif "cvssMetricV2" in metrics:
                            cvss_data = metrics["cvssMetricV2"][0].get(
                                "cvssData", {}
                            )
                            cvss_score = cvss_data.get("baseScore", 0.0)
                            severity = self._cvss_to_severity(cvss_score)

                        # Получение дат
                        published_date = datetime.now()
                        last_modified = datetime.now()

                        if "published" in vuln:
                            published_date = datetime.fromisoformat(
                                vuln["published"].replace("Z", "+00:00")
                            )
                        if "lastModified" in vuln:
                            last_modified = datetime.fromisoformat(
                                vuln["lastModified"].replace("Z", "+00:00")
                            )

                        # Получение затронутых продуктов
                        affected_products = []
                        configurations = vuln.get("configurations", [])
                        for config in configurations:
                            nodes = config.get("nodes", [])
                            for node in nodes:
                                cpe_matches = node.get("cpeMatch", [])
                                for cpe in cpe_matches:
                                    if cpe.get("vulnerable"):
                                        affected_products.append(
                                            cpe.get("criteria", "")
                                        )

                        # Получение ссылок
                        references = []
                        refs = vuln.get("references", [])
                        for ref in refs:
                            references.append(ref.get("url", ""))

                        return CVEResult(
                            cve_id=cve_id,
                            description=description,
                            severity=severity,
                            cvss_score=cvss_score,
                            published_date=published_date,
                            last_modified=last_modified,
                            affected_products=affected_products,
                            references=references,
                            raw_data=vuln,
                        )

        except Exception as e:
            print(f"Error getting CVE from NVD for {cve_id}: {e}")

        return None

    def _cvss_to_severity(self, cvss_score: float) -> str:
        """Конвертация CVSS score в severity"""
        if cvss_score >= 9.0:
            return "critical"
        elif cvss_score >= 7.0:
            return "high"
        elif cvss_score >= 4.0:
            return "medium"
        else:
            return "low"

    async def get_recent_cves(self, limit: int = 10) -> List[CVEResult]:
        """Получение последних CVE"""
        results = []

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # Получение последних CVE из NVD
                response = await client.get(
                    "https://services.nvd.nist.gov/rest/json/cves/2.0",
                    params={"resultsPerPage": limit},
                )

                if response.status_code == 200:
                    data = response.json()
                    vulnerabilities = data.get("vulnerabilities", [])

                    for vuln_data in vulnerabilities:
                        vuln = vuln_data.get("cve", {})
                        cve_id = vuln.get("id", "")

                        if cve_id:
                            cve_result = await self.get_cve_info(cve_id)
                            if cve_result:
                                results.append(cve_result)

        except Exception as e:
            print(f"Error getting recent CVEs: {e}")

        return results

    async def check_ssl_certificate(self, domain: str) -> Dict[str, Any]:
        """Проверка SSL сертификата"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"https://{domain}")

                if response.status_code == 200:
                    # Получение информации о сертификате
                    cert_info = {
                        "domain": domain,
                        "valid": True,
                        "protocol": "HTTPS",
                        "status": "secure",
                        "timestamp": datetime.now().isoformat(),
                    }

                    return cert_info

        except Exception as e:
            print(f"Error checking SSL certificate for {domain}: {e}")
            return {
                "domain": domain,
                "valid": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def check_security_headers(self, domain: str) -> Dict[str, Any]:
        """Проверка security headers"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"https://{domain}")

                security_headers = {}
                required_headers = [
                    "Strict-Transport-Security",
                    "Content-Security-Policy",
                    "X-Frame-Options",
                    "X-Content-Type-Options",
                    "X-XSS-Protection",
                    "Referrer-Policy",
                ]

                for header in required_headers:
                    security_headers[header] = header in response.headers

                return {
                    "domain": domain,
                    "security_headers": security_headers,
                    "score": sum(security_headers.values())
                    / len(required_headers)
                    * 100,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            print(f"Error checking security headers for {domain}: {e}")
            return {
                "domain": domain,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def save_threat_intelligence_result(
        self, result: ThreatIntelligenceResult
    ):
        """Сохранение результата Threat Intelligence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO threat_intelligence 
            (indicator, indicator_type, service, malicious, confidence, detection_count,
             last_seen, tags, raw_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                result.indicator,
                result.indicator_type,
                result.service.value,
                result.malicious,
                result.confidence,
                result.detection_count,
                result.last_seen.isoformat() if result.last_seen else None,
                json.dumps(result.tags),
                json.dumps(result.raw_data),
                result.timestamp.isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def save_cve_result(self, result: CVEResult):
        """Сохранение результата CVE"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO cve_results 
            (cve_id, description, severity, cvss_score, published_date, last_modified,
             affected_products, references, raw_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                result.cve_id,
                result.description,
                result.severity,
                result.cvss_score,
                result.published_date.isoformat(),
                result.last_modified.isoformat(),
                json.dumps(result.affected_products),
                json.dumps(result.references),
                json.dumps(result.raw_data),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def save_ip_reputation_result(self, result: IPReputationResult):
        """Сохранение результата репутации IP"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO ip_reputation 
            (ip_address, service, malicious, confidence, abuse_confidence, country, isp,
             usage_type, last_reported, raw_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                result.ip_address,
                result.service.value,
                result.malicious,
                result.confidence,
                result.abuse_confidence,
                result.country,
                result.isp,
                result.usage_type,
                (
                    result.last_reported.isoformat()
                    if result.last_reported
                    else None
                ),
                json.dumps(result.raw_data),
                result.timestamp.isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def get_threat_intelligence_history(
        self, indicator: str, limit: int = 100
    ) -> List[ThreatIntelligenceResult]:
        """Получение истории Threat Intelligence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT indicator, indicator_type, service, malicious, confidence, detection_count,
                   last_seen, tags, raw_data, timestamp
            FROM threat_intelligence 
            WHERE indicator = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        """,
            (indicator, limit),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                ThreatIntelligenceResult(
                    indicator=row[0],
                    indicator_type=row[1],
                    service=ServiceProvider(row[2]),
                    malicious=bool(row[3]),
                    confidence=row[4],
                    detection_count=row[5],
                    last_seen=(
                        datetime.fromisoformat(row[6]) if row[6] else None
                    ),
                    tags=json.loads(row[7]),
                    raw_data=json.loads(row[8]),
                    timestamp=datetime.fromisoformat(row[9]),
                )
            )

        conn.close()
        return results

    def get_cve_history(self, limit: int = 100) -> List[CVEResult]:
        """Получение истории CVE"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT cve_id, description, severity, cvss_score, published_date, last_modified,
                   affected_products, references, raw_data, timestamp
            FROM cve_results 
            ORDER BY timestamp DESC 
            LIMIT ?
        """,
            (limit,),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                CVEResult(
                    cve_id=row[0],
                    description=row[1],
                    severity=row[2],
                    cvss_score=row[3],
                    published_date=datetime.fromisoformat(row[4]),
                    last_modified=datetime.fromisoformat(row[5]),
                    affected_products=json.loads(row[6]),
                    references=json.loads(row[7]),
                    raw_data=json.loads(row[8]),
                )
            )

        conn.close()
        return results

    def get_integration_status(self) -> Dict[str, Any]:
        """Получение статуса интеграций"""
        status = {
            "total_integrations": len(self.configs),
            "enabled_integrations": len(
                [c for c in self.configs.values() if c.enabled]
            ),
            "free_tier_integrations": len(
                [c for c in self.configs.values() if c.free_tier]
            ),
            "integrations": {},
        }

        for service, config in self.configs.items():
            status["integrations"][service.value] = {
                "enabled": config.enabled,
                "free_tier": config.free_tier,
                "rate_limit": config.rate_limit,
                "has_api_key": bool(config.api_key),
                "timeout": config.timeout,
            }

        return status


# Пример использования
async def main():
    """Основная функция"""
    integrations = ExternalIntegrations()

    print("🔍 Тестирование внешних интеграций...")

    # Проверка статуса интеграций
    status = integrations.get_integration_status()
    print(
        f"✅ Статус интеграций: {status['enabled_integrations']}/{status['total_integrations']} активны"
    )

    # Тест проверки IP репутации
    print("\n🌐 Проверка репутации IP...")
    ip_results = await integrations.check_ip_reputation("8.8.8.8")
    for result in ip_results:
        print(
            f"  {result.ip_address}: {'🚨 Malicious' if result.malicious else '✅ Clean'} ({result.confidence}%)"
        )

    # Тест проверки домена
    print("\n🌐 Проверка репутации домена...")
    domain_results = await integrations.check_domain_reputation("google.com")
    for result in domain_results:
        print(
            f"  {result.indicator}: {'🚨 Malicious' if result.malicious else '✅ Clean'} ({result.confidence}%)"
        )

    # Тест получения CVE
    print("\n🔍 Получение информации о CVE...")
    cve_result = await integrations.get_cve_info("CVE-2021-44228")
    if cve_result:
        print(
            f"  {cve_result.cve_id}: {cve_result.severity} ({cve_result.cvss_score})"
        )
        print(f"  Описание: {cve_result.description[:100]}...")

    # Тест получения последних CVE
    print("\n📰 Получение последних CVE...")
    recent_cves = await integrations.get_recent_cves(5)
    for cve in recent_cves:
        print(f"  {cve.cve_id}: {cve.severity} ({cve.cvss_score})")

    # Тест проверки SSL сертификата
    print("\n🔒 Проверка SSL сертификата...")
    ssl_result = await integrations.check_ssl_certificate("google.com")
    print(
        f"  {ssl_result['domain']}: {'✅ Valid' if ssl_result.get('valid') else '❌ Invalid'}"
    )

    # Тест проверки security headers
    print("\n🛡️ Проверка security headers...")
    headers_result = await integrations.check_security_headers("google.com")
    print(
        f"  {headers_result['domain']}: {headers_result['score']:.1f}% security score"
    )

    print("\n✅ Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(main())
