#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
External Integrations Dashboard для ALADDIN Security System
Интеграция внешних сервисов с дашбордом

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse

from external_integrations import (
    ExternalIntegrations,
    IntegrationType,
    ServiceProvider,
)
from threat_intelligence_system import (
    IndicatorType,
    ThreatIntelligenceSystem,
    ThreatType,
)

# Создание роутера для API внешних интеграций
external_router = APIRouter(prefix="/api/external", tags=["external"])

# Глобальные экземпляры систем
external_integrations = None
threat_intelligence = None


def initialize_external_systems():
    """Инициализация внешних систем"""
    global external_integrations, threat_intelligence

    if external_integrations is None:
        external_integrations = ExternalIntegrations()

    if threat_intelligence is None:
        threat_intelligence = ThreatIntelligenceSystem()


# API Endpoints для внешних интеграций


@external_router.get("/status")
async def get_external_integrations_status():
    """Получение статуса внешних интеграций"""
    initialize_external_systems()

    # Статус интеграций
    integration_status = external_integrations.get_integration_status()

    # Статус Threat Intelligence
    ti_stats = threat_intelligence.get_threat_statistics()

    # Статус источников угроз
    feeds_status = threat_intelligence.get_feeds_status()

    return {
        "external_integrations": integration_status,
        "threat_intelligence": ti_stats,
        "threat_feeds": [
            {
                "name": feed.name,
                "url": feed.url,
                "enabled": feed.enabled,
                "last_update": (
                    feed.last_update.isoformat() if feed.last_update else None
                ),
                "indicators_count": feed.indicators_count,
            }
            for feed in feeds_status
        ],
        "last_updated": datetime.now().isoformat(),
    }


@external_router.get("/threat-intelligence/check")
async def check_threat_indicator(
    indicator: str, indicator_type: Optional[str] = None
):
    """Проверка индикатора угрозы"""
    initialize_external_systems()

    # Проверка в локальной базе Threat Intelligence
    local_result = threat_intelligence.check_threat_indicator(indicator)

    # Определение типа индикатора
    if not indicator_type:
        if external_integrations._detect_indicator_type(indicator) == "ip":
            indicator_type = "ip"
        elif (
            external_integrations._detect_indicator_type(indicator) == "domain"
        ):
            indicator_type = "domain"
        elif external_integrations._detect_indicator_type(indicator) == "url":
            indicator_type = "url"
        elif external_integrations._detect_indicator_type(indicator) == "hash":
            indicator_type = "hash"

    # Проверка через внешние сервисы
    external_results = []

    if indicator_type == "ip":
        ip_results = await external_integrations.check_ip_reputation(indicator)
        external_results.extend(ip_results)
    elif indicator_type == "domain":
        domain_results = await external_integrations.check_domain_reputation(
            indicator
        )
        external_results.extend(domain_results)
    elif indicator_type == "hash":
        hash_results = await external_integrations.check_file_hash(indicator)
        external_results.extend(hash_results)

    return {
        "indicator": indicator,
        "indicator_type": indicator_type,
        "local_threat_intelligence": (
            asdict(local_result) if local_result else None
        ),
        "external_results": [asdict(result) for result in external_results],
        "overall_risk": (
            "high"
            if local_result or any(r.malicious for r in external_results)
            else "low"
        ),
        "timestamp": datetime.now().isoformat(),
    }


@external_router.get("/cve/info/{cve_id}")
async def get_cve_information(cve_id: str):
    """Получение информации о CVE"""
    initialize_external_systems()

    cve_result = await external_integrations.get_cve_info(cve_id)

    if not cve_result:
        raise HTTPException(status_code=404, detail=f"CVE {cve_id} not found")

    return {
        "cve_id": cve_result.cve_id,
        "description": cve_result.description,
        "severity": cve_result.severity,
        "cvss_score": cve_result.cvss_score,
        "published_date": cve_result.published_date.isoformat(),
        "last_modified": cve_result.last_modified.isoformat(),
        "affected_products": cve_result.affected_products,
        "references": cve_result.references,
        "timestamp": datetime.now().isoformat(),
    }


@external_router.get("/cve/recent")
async def get_recent_cves(limit: int = Query(10, ge=1, le=100)):
    """Получение последних CVE"""
    initialize_external_systems()

    recent_cves = await external_integrations.get_recent_cves(limit)

    return {
        "cves": [
            {
                "cve_id": cve.cve_id,
                "description": cve.description,
                "severity": cve.severity,
                "cvss_score": cve.cvss_score,
                "published_date": cve.published_date.isoformat(),
                "affected_products": cve.affected_products[
                    :5
                ],  # Первые 5 продуктов
            }
            for cve in recent_cves
        ],
        "total": len(recent_cves),
        "timestamp": datetime.now().isoformat(),
    }


@external_router.get("/ssl/check/{domain}")
async def check_ssl_certificate(domain: str):
    """Проверка SSL сертификата"""
    initialize_external_systems()

    ssl_result = await external_integrations.check_ssl_certificate(domain)

    return ssl_result


@external_router.get("/security-headers/check/{domain}")
async def check_security_headers(domain: str):
    """Проверка security headers"""
    initialize_external_systems()

    headers_result = await external_integrations.check_security_headers(domain)

    return headers_result


@external_router.get("/threat-intelligence/statistics")
async def get_threat_intelligence_statistics():
    """Получение статистики Threat Intelligence"""
    initialize_external_systems()

    stats = threat_intelligence.get_threat_statistics()

    return stats


@external_router.get("/threat-intelligence/recent")
async def get_recent_threats(limit: int = Query(50, ge=1, le=500)):
    """Получение последних угроз"""
    initialize_external_systems()

    recent_threats = threat_intelligence.get_recent_threats(limit)

    return {
        "threats": [
            {
                "indicator": threat.indicator,
                "indicator_type": threat.indicator_type.value,
                "threat_type": threat.threat_type.value,
                "confidence": threat.confidence.value,
                "source": threat.source,
                "description": threat.description,
                "tags": threat.tags,
                "first_seen": threat.first_seen.isoformat(),
                "last_seen": threat.last_seen.isoformat(),
            }
            for threat in recent_threats
        ],
        "total": len(recent_threats),
        "timestamp": datetime.now().isoformat(),
    }


@external_router.get("/threat-intelligence/search")
async def search_threats(query: str, limit: int = Query(50, ge=1, le=500)):
    """Поиск угроз"""
    initialize_external_systems()

    search_results = threat_intelligence.search_threats(query, limit)

    return {
        "query": query,
        "results": [
            {
                "indicator": threat.indicator,
                "indicator_type": threat.indicator_type.value,
                "threat_type": threat.threat_type.value,
                "confidence": threat.confidence.value,
                "source": threat.source,
                "description": threat.description,
                "tags": threat.tags,
                "first_seen": threat.first_seen.isoformat(),
                "last_seen": threat.last_seen.isoformat(),
            }
            for threat in search_results
        ],
        "total": len(search_results),
        "timestamp": datetime.now().isoformat(),
    }


@external_router.post("/threat-intelligence/update-feeds")
async def update_threat_feeds(background_tasks: BackgroundTasks):
    """Обновление источников угроз"""
    initialize_external_systems()

    background_tasks.add_task(update_threat_feeds_task)

    return {
        "message": "Threat feeds update started",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


async def update_threat_feeds_task():
    """Фоновая задача обновления источников угроз"""
    try:
        await threat_intelligence.update_threat_feeds()
        print("✅ Threat feeds updated successfully")
    except Exception as e:
        print(f"❌ Error updating threat feeds: {e}")


@external_router.get("/threat-intelligence/feeds")
async def get_threat_feeds():
    """Получение списка источников угроз"""
    initialize_external_systems()

    feeds = threat_intelligence.get_feeds_status()

    return {
        "feeds": [
            {
                "name": feed.name,
                "url": feed.url,
                "format": feed.format,
                "update_frequency": feed.update_frequency,
                "enabled": feed.enabled,
                "last_update": (
                    feed.last_update.isoformat() if feed.last_update else None
                ),
                "indicators_count": feed.indicators_count,
            }
            for feed in feeds
        ],
        "total": len(feeds),
        "timestamp": datetime.now().isoformat(),
    }


@external_router.get("/integrations/services")
async def get_available_services():
    """Получение доступных сервисов"""
    initialize_external_systems()

    integration_status = external_integrations.get_integration_status()

    services = []
    for service, config in external_integrations.configs.items():
        services.append(
            {
                "name": service.value,
                "enabled": config.enabled,
                "free_tier": config.free_tier,
                "rate_limit": config.rate_limit,
                "has_api_key": bool(config.api_key),
                "timeout": config.timeout,
            }
        )

    return {
        "services": services,
        "total": len(services),
        "enabled": integration_status["enabled_integrations"],
        "free_tier": integration_status["free_tier_integrations"],
        "timestamp": datetime.now().isoformat(),
    }


@external_router.get("/health")
async def external_integrations_health():
    """Проверка здоровья внешних интеграций"""
    initialize_external_systems()

    try:
        # Проверка статуса интеграций
        integration_status = external_integrations.get_integration_status()

        # Проверка Threat Intelligence
        ti_stats = threat_intelligence.get_threat_statistics()

        # Проверка источников угроз
        feeds = threat_intelligence.get_feeds_status()
        enabled_feeds = len([f for f in feeds if f.enabled])

        overall_status = "healthy"
        if integration_status["enabled_integrations"] == 0:
            overall_status = "no_integrations"
        elif ti_stats["total_indicators"] == 0:
            overall_status = "no_threat_data"

        return {
            "status": overall_status,
            "components": {
                "external_integrations": (
                    "healthy"
                    if integration_status["enabled_integrations"] > 0
                    else "no_integrations"
                ),
                "threat_intelligence": (
                    "healthy"
                    if ti_stats["total_indicators"] > 0
                    else "no_data"
                ),
                "threat_feeds": "healthy" if enabled_feeds > 0 else "no_feeds",
            },
            "statistics": {
                "enabled_integrations": integration_status[
                    "enabled_integrations"
                ],
                "total_threat_indicators": ti_stats["total_indicators"],
                "enabled_feeds": enabled_feeds,
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@external_router.get("/dashboard/overview")
async def get_external_dashboard_overview():
    """Получение обзора внешних интеграций для дашборда"""
    initialize_external_systems()

    # Статус интеграций
    integration_status = external_integrations.get_integration_status()

    # Статистика Threat Intelligence
    ti_stats = threat_intelligence.get_threat_statistics()

    # Последние угрозы
    recent_threats = threat_intelligence.get_recent_threats(10)

    # Последние CVE
    recent_cves = await external_integrations.get_recent_cves(5)

    # Статус источников
    feeds = threat_intelligence.get_feeds_status()
    feeds_status = {
        "total": len(feeds),
        "enabled": len([f for f in feeds if f.enabled]),
        "last_updated": max(
            [f.last_update for f in feeds if f.last_update], default=None
        ),
    }

    return {
        "external_integrations": {
            "total_services": integration_status["total_integrations"],
            "enabled_services": integration_status["enabled_integrations"],
            "free_tier_services": integration_status["free_tier_integrations"],
        },
        "threat_intelligence": {
            "total_indicators": ti_stats["total_indicators"],
            "indicator_types": ti_stats["indicator_types"],
            "threat_types": ti_stats["threat_types"],
            "sources": ti_stats["sources"],
        },
        "recent_activity": {
            "threats": [
                {
                    "indicator": t.indicator,
                    "threat_type": t.threat_type.value,
                    "source": t.source,
                    "confidence": t.confidence.value,
                }
                for t in recent_threats[:5]
            ],
            "cves": [
                {
                    "cve_id": c.cve_id,
                    "severity": c.severity,
                    "cvss_score": c.cvss_score,
                }
                for c in recent_cves
            ],
        },
        "feeds": feeds_status,
        "last_updated": datetime.now().isoformat(),
    }


# Функция для инициализации при запуске приложения
def initialize_external_dashboard():
    """Инициализация внешних интеграций для дашборда"""
    initialize_external_systems()
    print("✅ External integrations dashboard initialized")


# Функция для получения роутера
def get_external_router():
    """Получение роутера внешних интеграций"""
    return external_router
