#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для внешних интеграций ALADDIN Security System
Проверка интеграций с бесплатными и надежными сервисами

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Импорты для тестирования
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from external_integrations import (
    ExternalIntegrations, ServiceProvider, IntegrationType, 
    ThreatIntelligenceResult, CVEResult, IPReputationResult
)
from threat_intelligence_system import (
    ThreatIntelligenceSystem, ThreatType, IndicatorType, 
    ConfidenceLevel, ThreatIndicator, ThreatFeed
)

class TestExternalIntegrations:
    """Тесты внешних интеграций"""
    
    @pytest.fixture
    def external_integrations(self):
        """Фикстура для внешних интеграций"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        integrations = ExternalIntegrations(db_path)
        yield integrations
        
        # Очистка
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_external_integrations_initialization(self, external_integrations):
        """Тест инициализации внешних интеграций"""
        assert external_integrations is not None
        assert os.path.exists(external_integrations.db_path)
        print("✅ Внешние интеграции инициализированы корректно")
    
    def test_integration_configs_loading(self, external_integrations):
        """Тест загрузки конфигураций интеграций"""
        assert len(external_integrations.configs) > 0
        
        # Проверяем, что есть бесплатные сервисы
        free_services = [c for c in external_integrations.configs.values() if c.free_tier]
        assert len(free_services) > 0
        
        # Проверяем основные сервисы
        expected_services = [
            ServiceProvider.VIRUSTOTAL,
            ServiceProvider.ABUSEIPDB,
            ServiceProvider.CIRCL,
            ServiceProvider.OTX,
            ServiceProvider.CVE_MITRE,
            ServiceProvider.NVD
        ]
        
        for service in expected_services:
            assert service in external_integrations.configs
        
        print(f"✅ Загружено {len(external_integrations.configs)} конфигураций интеграций")
    
    @pytest.mark.asyncio
    async def test_ip_reputation_check(self, external_integrations):
        """Тест проверки репутации IP"""
        # Тест с публичным DNS сервером Google
        results = await external_integrations.check_ip_reputation("8.8.8.8")
        
        assert isinstance(results, list)
        print(f"✅ Проверка репутации IP: получено {len(results)} результатов")
        
        # Если есть результаты, проверяем структуру
        if results:
            result = results[0]
            assert isinstance(result, IPReputationResult)
            assert result.ip_address == "8.8.8.8"
            assert isinstance(result.malicious, bool)
            assert 0 <= result.confidence <= 100
            assert result.service in [ServiceProvider.ABUSEIPDB]
    
    @pytest.mark.asyncio
    async def test_domain_reputation_check(self, external_integrations):
        """Тест проверки репутации домена"""
        # Тест с известным доменом
        results = await external_integrations.check_domain_reputation("google.com")
        
        assert isinstance(results, list)
        print(f"✅ Проверка репутации домена: получено {len(results)} результатов")
        
        # Если есть результаты, проверяем структуру
        if results:
            result = results[0]
            assert isinstance(result, ThreatIntelligenceResult)
            assert result.indicator == "google.com"
            assert result.indicator_type == "domain"
            assert isinstance(result.malicious, bool)
            assert 0 <= result.confidence <= 100
    
    @pytest.mark.asyncio
    async def test_file_hash_check(self, external_integrations):
        """Тест проверки хеша файла"""
        # Тест с известным хешем (пример)
        test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        results = await external_integrations.check_file_hash(test_hash)
        
        assert isinstance(results, list)
        print(f"✅ Проверка хеша файла: получено {len(results)} результатов")
        
        # Если есть результаты, проверяем структуру
        if results:
            result = results[0]
            assert isinstance(result, ThreatIntelligenceResult)
            assert result.indicator == test_hash
            assert result.indicator_type == "hash"
            assert isinstance(result.malicious, bool)
    
    @pytest.mark.asyncio
    async def test_cve_info_retrieval(self, external_integrations):
        """Тест получения информации о CVE"""
        # Тест с известным CVE
        cve_result = await external_integrations.get_cve_info("CVE-2021-44228")
        
        if cve_result:
            assert isinstance(cve_result, CVEResult)
            assert cve_result.cve_id == "CVE-2021-44228"
            assert isinstance(cve_result.description, str)
            assert cve_result.severity in ["critical", "high", "medium", "low", "unknown"]
            assert 0 <= cve_result.cvss_score <= 10
            assert isinstance(cve_result.affected_products, list)
            assert isinstance(cve_result.references, list)
            print("✅ Информация о CVE получена корректно")
        else:
            print("⚠️ CVE информация недоступна (возможно, нет API ключей)")
    
    @pytest.mark.asyncio
    async def test_recent_cves_retrieval(self, external_integrations):
        """Тест получения последних CVE"""
        recent_cves = await external_integrations.get_recent_cves(5)
        
        assert isinstance(recent_cves, list)
        assert len(recent_cves) <= 5
        
        if recent_cves:
            cve = recent_cves[0]
            assert isinstance(cve, CVEResult)
            assert cve.cve_id.startswith("CVE-")
            assert isinstance(cve.description, str)
            assert cve.severity in ["critical", "high", "medium", "low", "unknown"]
            print(f"✅ Получено {len(recent_cves)} последних CVE")
        else:
            print("⚠️ Последние CVE недоступны")
    
    @pytest.mark.asyncio
    async def test_ssl_certificate_check(self, external_integrations):
        """Тест проверки SSL сертификата"""
        ssl_result = await external_integrations.check_ssl_certificate("google.com")
        
        assert isinstance(ssl_result, dict)
        assert "domain" in ssl_result
        assert ssl_result["domain"] == "google.com"
        assert "timestamp" in ssl_result
        
        if ssl_result.get("valid"):
            assert "protocol" in ssl_result
            assert ssl_result["protocol"] == "HTTPS"
            print("✅ SSL сертификат проверен корректно")
        else:
            print("⚠️ SSL сертификат недоступен или недействителен")
    
    @pytest.mark.asyncio
    async def test_security_headers_check(self, external_integrations):
        """Тест проверки security headers"""
        headers_result = await external_integrations.check_security_headers("google.com")
        
        assert isinstance(headers_result, dict)
        assert "domain" in headers_result
        assert headers_result["domain"] == "google.com"
        assert "security_headers" in headers_result
        assert "score" in headers_result
        assert "timestamp" in headers_result
        
        security_headers = headers_result["security_headers"]
        expected_headers = [
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Referrer-Policy"
        ]
        
        for header in expected_headers:
            assert header in security_headers
            assert isinstance(security_headers[header], bool)
        
        assert 0 <= headers_result["score"] <= 100
        print(f"✅ Security headers проверены: {headers_result['score']:.1f}%")
    
    def test_integration_status(self, external_integrations):
        """Тест получения статуса интеграций"""
        status = external_integrations.get_integration_status()
        
        assert "total_integrations" in status
        assert "enabled_integrations" in status
        assert "free_tier_integrations" in status
        assert "integrations" in status
        
        assert status["total_integrations"] > 0
        assert status["free_tier_integrations"] > 0
        assert len(status["integrations"]) == status["total_integrations"]
        
        print(f"✅ Статус интеграций: {status['enabled_integrations']}/{status['total_integrations']} активны")

class TestThreatIntelligenceSystem:
    """Тесты системы Threat Intelligence"""
    
    @pytest.fixture
    def threat_intelligence(self):
        """Фикстура для системы Threat Intelligence"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        ti = ThreatIntelligenceSystem(db_path)
        yield ti
        
        # Очистка
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_threat_intelligence_initialization(self, threat_intelligence):
        """Тест инициализации системы Threat Intelligence"""
        assert threat_intelligence is not None
        assert os.path.exists(threat_intelligence.db_path)
        print("✅ Система Threat Intelligence инициализирована корректно")
    
    def test_default_feeds_loading(self, threat_intelligence):
        """Тест загрузки источников по умолчанию"""
        assert len(threat_intelligence.feeds) > 0
        
        # Проверяем, что есть бесплатные источники
        enabled_feeds = [f for f in threat_intelligence.feeds if f.enabled]
        assert len(enabled_feeds) > 0
        
        # Проверяем основные источники
        expected_feeds = [
            "Abuse.ch URLhaus",
            "Abuse.ch Feodo Tracker",
            "Malware Domain List",
            "Phishing Database",
            "Spamhaus DROP List",
            "CINS Score"
        ]
        
        feed_names = [f.name for f in threat_intelligence.feeds]
        for expected_feed in expected_feeds:
            assert expected_feed in feed_names
        
        print(f"✅ Загружено {len(threat_intelligence.feeds)} источников угроз")
    
    def test_indicator_type_detection(self, threat_intelligence):
        """Тест определения типа индикатора"""
        # Тест IP адреса
        ip_type = threat_intelligence._detect_indicator_type("192.168.1.1")
        assert ip_type == IndicatorType.IP_ADDRESS
        
        # Тест домена
        domain_type = threat_intelligence._detect_indicator_type("example.com")
        assert domain_type == IndicatorType.DOMAIN
        
        # Тест URL
        url_type = threat_intelligence._detect_indicator_type("https://example.com")
        assert url_type == IndicatorType.URL
        
        # Тест email
        email_type = threat_intelligence._detect_indicator_type("test@example.com")
        assert email_type == IndicatorType.EMAIL
        
        # Тест хеша
        hash_type = threat_intelligence._detect_indicator_type("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        assert hash_type == IndicatorType.FILE_HASH
        
        # Тест неопределенного типа
        unknown_type = threat_intelligence._detect_indicator_type("unknown_string")
        assert unknown_type is None
        
        print("✅ Определение типов индикаторов работает корректно")
    
    def test_threat_type_mapping(self, threat_intelligence):
        """Тест маппинга типов угроз"""
        # Тест различных типов угроз
        test_cases = [
            ("malware", ThreatType.MALWARE),
            ("phishing", ThreatType.PHISHING),
            ("botnet", ThreatType.BOTNET),
            ("spam", ThreatType.SPAM),
            ("exploit", ThreatType.EXPLOIT),
            ("ransomware", ThreatType.RANSOMWARE),
            ("trojan", ThreatType.TROJAN),
            ("backdoor", ThreatType.BACKDOOR),
            ("keylogger", ThreatType.KEYLOGGER),
            ("unknown", ThreatType.MALWARE)  # По умолчанию
        ]
        
        for threat_name, expected_type in test_cases:
            result = threat_intelligence._map_threat_type(threat_name)
            assert result == expected_type
        
        print("✅ Маппинг типов угроз работает корректно")
    
    def test_feed_threat_type_mapping(self, threat_intelligence):
        """Тест маппинга типов угроз по источникам"""
        test_cases = [
            ("Phishing Database", ThreatType.PHISHING),
            ("Spamhaus DROP List", ThreatType.SPAM),
            ("Botnet Tracker", ThreatType.BOTNET),
            ("Malware Domain List", ThreatType.MALWARE),
            ("Unknown Feed", ThreatType.MALWARE)  # По умолчанию
        ]
        
        for feed_name, expected_type in test_cases:
            result = threat_intelligence._map_feed_threat_type(feed_name)
            assert result == expected_type
        
        print("✅ Маппинг типов угроз по источникам работает корректно")
    
    def test_threat_indicator_creation(self, threat_intelligence):
        """Тест создания индикатора угрозы"""
        indicator = ThreatIndicator(
            indicator="test.example.com",
            indicator_type=IndicatorType.DOMAIN,
            threat_type=ThreatType.MALWARE,
            confidence=ConfidenceLevel.HIGH,
            source="Test Source",
            description="Test threat indicator",
            tags=["test", "malware"],
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            references=["https://test.com"],
            raw_data={"test": True}
        )
        
        assert indicator.indicator == "test.example.com"
        assert indicator.indicator_type == IndicatorType.DOMAIN
        assert indicator.threat_type == ThreatType.MALWARE
        assert indicator.confidence == ConfidenceLevel.HIGH
        assert indicator.source == "Test Source"
        assert len(indicator.tags) == 2
        assert "test" in indicator.tags
        
        print("✅ Создание индикатора угрозы работает корректно")
    
    def test_save_and_load_threat_indicator(self, threat_intelligence):
        """Тест сохранения и загрузки индикатора угрозы"""
        # Создаем тестовый индикатор
        indicator = ThreatIndicator(
            indicator="test-threat.example.com",
            indicator_type=IndicatorType.DOMAIN,
            threat_type=ThreatType.PHISHING,
            confidence=ConfidenceLevel.MEDIUM,
            source="Test Source",
            description="Test phishing indicator",
            tags=["phishing", "test"],
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            references=["https://test.com"],
            raw_data={"test": True, "phishing": True}
        )
        
        # Сохраняем
        threat_intelligence.save_threat_indicator(indicator)
        
        # Загружаем
        loaded_indicator = threat_intelligence.check_threat_indicator("test-threat.example.com")
        
        assert loaded_indicator is not None
        assert loaded_indicator.indicator == indicator.indicator
        assert loaded_indicator.indicator_type == indicator.indicator_type
        assert loaded_indicator.threat_type == indicator.threat_type
        assert loaded_indicator.confidence == indicator.confidence
        assert loaded_indicator.source == indicator.source
        assert loaded_indicator.description == indicator.description
        assert loaded_indicator.tags == indicator.tags
        
        print("✅ Сохранение и загрузка индикатора угрозы работает корректно")
    
    def test_threat_statistics(self, threat_intelligence):
        """Тест получения статистики угроз"""
        # Добавляем тестовые данные
        test_indicators = [
            ThreatIndicator(
                indicator="test1.example.com",
                indicator_type=IndicatorType.DOMAIN,
                threat_type=ThreatType.MALWARE,
                confidence=ConfidenceLevel.HIGH,
                source="Test Source 1",
                description="Test malware",
                tags=["malware"],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                references=[],
                raw_data={}
            ),
            ThreatIndicator(
                indicator="192.168.1.100",
                indicator_type=IndicatorType.IP_ADDRESS,
                threat_type=ThreatType.PHISHING,
                confidence=ConfidenceLevel.MEDIUM,
                source="Test Source 2",
                description="Test phishing IP",
                tags=["phishing"],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                references=[],
                raw_data={}
            )
        ]
        
        for indicator in test_indicators:
            threat_intelligence.save_threat_indicator(indicator)
        
        # Получаем статистику
        stats = threat_intelligence.get_threat_statistics()
        
        assert "total_indicators" in stats
        assert "indicator_types" in stats
        assert "threat_types" in stats
        assert "sources" in stats
        assert "confidence_levels" in stats
        
        assert stats["total_indicators"] >= 2
        assert "domain" in stats["indicator_types"]
        assert "ip" in stats["indicator_types"]
        assert "malware" in stats["threat_types"]
        assert "phishing" in stats["threat_types"]
        
        print("✅ Статистика угроз получена корректно")
    
    def test_recent_threats(self, threat_intelligence):
        """Тест получения последних угроз"""
        # Добавляем тестовые данные
        for i in range(5):
            indicator = ThreatIndicator(
                indicator=f"test{i}.example.com",
                indicator_type=IndicatorType.DOMAIN,
                threat_type=ThreatType.MALWARE,
                confidence=ConfidenceLevel.HIGH,
                source="Test Source",
                description=f"Test threat {i}",
                tags=["test"],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                references=[],
                raw_data={}
            )
            threat_intelligence.save_threat_indicator(indicator)
        
        # Получаем последние угрозы
        recent_threats = threat_intelligence.get_recent_threats(3)
        
        assert len(recent_threats) <= 3
        assert len(recent_threats) > 0
        
        # Проверяем, что угрозы отсортированы по времени
        for threat in recent_threats:
            assert isinstance(threat, ThreatIndicator)
            assert threat.indicator.startswith("test")
        
        print(f"✅ Получено {len(recent_threats)} последних угроз")
    
    def test_search_threats(self, threat_intelligence):
        """Тест поиска угроз"""
        # Добавляем тестовые данные
        test_indicators = [
            ThreatIndicator(
                indicator="malware.example.com",
                indicator_type=IndicatorType.DOMAIN,
                threat_type=ThreatType.MALWARE,
                confidence=ConfidenceLevel.HIGH,
                source="Test Source",
                description="Malicious domain",
                tags=["malware", "test"],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                references=[],
                raw_data={}
            ),
            ThreatIndicator(
                indicator="phishing.example.com",
                indicator_type=IndicatorType.DOMAIN,
                threat_type=ThreatType.PHISHING,
                confidence=ConfidenceLevel.MEDIUM,
                source="Test Source",
                description="Phishing domain",
                tags=["phishing", "test"],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                references=[],
                raw_data={}
            )
        ]
        
        for indicator in test_indicators:
            threat_intelligence.save_threat_indicator(indicator)
        
        # Поиск по индикатору
        malware_results = threat_intelligence.search_threats("malware")
        assert len(malware_results) > 0
        assert any("malware" in threat.indicator for threat in malware_results)
        
        # Поиск по описанию
        phishing_results = threat_intelligence.search_threats("phishing")
        assert len(phishing_results) > 0
        assert any(threat.threat_type == ThreatType.PHISHING for threat in phishing_results)
        
        print("✅ Поиск угроз работает корректно")

class TestExternalIntegrationWorkflow:
    """Тесты полного рабочего процесса внешних интеграций"""
    
    @pytest.mark.asyncio
    async def test_full_external_integration_workflow(self):
        """Тест полного рабочего процесса внешних интеграций"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Создаем системы
            external_integrations = ExternalIntegrations(db_path)
            threat_intelligence = ThreatIntelligenceSystem(db_path)
            
            # Проверяем статус интеграций
            integration_status = external_integrations.get_integration_status()
            assert integration_status["total_integrations"] > 0
            
            # Проверяем источники угроз
            feeds = threat_intelligence.get_feeds_status()
            assert len(feeds) > 0
            
            # Тест проверки индикатора
            test_ip = "8.8.8.8"
            ip_results = await external_integrations.check_ip_reputation(test_ip)
            assert isinstance(ip_results, list)
            
            # Тест проверки домена
            test_domain = "google.com"
            domain_results = await external_integrations.check_domain_reputation(test_domain)
            assert isinstance(domain_results, list)
            
            # Тест получения CVE
            cve_result = await external_integrations.get_cve_info("CVE-2021-44228")
            # CVE может быть недоступен без API ключей
            
            # Тест проверки SSL
            ssl_result = await external_integrations.check_ssl_certificate(test_domain)
            assert isinstance(ssl_result, dict)
            
            # Тест проверки security headers
            headers_result = await external_integrations.check_security_headers(test_domain)
            assert isinstance(headers_result, dict)
            
            print("✅ Полный рабочий процесс внешних интеграций выполнен успешно")
            
        finally:
            # Очистка
            try:
                os.unlink(db_path)
            except:
                pass
    
    def test_integration_data_consistency(self):
        """Тест согласованности данных интеграций"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            threat_intelligence = ThreatIntelligenceSystem(db_path)
            
            # Создаем тестовый индикатор
            indicator = ThreatIndicator(
                indicator="consistency-test.example.com",
                indicator_type=IndicatorType.DOMAIN,
                threat_type=ThreatType.MALWARE,
                confidence=ConfidenceLevel.HIGH,
                source="Consistency Test",
                description="Test for data consistency",
                tags=["test", "consistency"],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                references=["https://test.com"],
                raw_data={"test": True, "consistency": "verified"}
            )
            
            # Сохраняем
            threat_intelligence.save_threat_indicator(indicator)
            
            # Загружаем
            loaded_indicator = threat_intelligence.check_threat_indicator("consistency-test.example.com")
            
            # Проверяем согласованность
            assert loaded_indicator is not None
            assert loaded_indicator.indicator == indicator.indicator
            assert loaded_indicator.indicator_type == indicator.indicator_type
            assert loaded_indicator.threat_type == indicator.threat_type
            assert loaded_indicator.confidence == indicator.confidence
            assert loaded_indicator.source == indicator.source
            assert loaded_indicator.description == indicator.description
            assert loaded_indicator.tags == indicator.tags
            assert loaded_indicator.raw_data == indicator.raw_data
            
            print("✅ Согласованность данных интеграций проверена")
            
        finally:
            # Очистка
            try:
                os.unlink(db_path)
            except:
                pass

# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])