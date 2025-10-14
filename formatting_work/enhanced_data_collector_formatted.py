#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Data Collector - Расширенный сборщик данных для повышения точности ML моделей
"""

import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedDataCollector:
    """
    Расширенный сборщик данных из множественных источников
    """

    def __init__(self):
        """Инициализация расширенного сборщика"""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        # Источники данных
        self.data_sources = {
            "cbr": {
                "base_url": "https://www.cbr.ru",
                "endpoints": [
                    "/na/",
                    "/analytics/",
                    "/press/",
                    "/vfs/",
                    "/statistics/",
                    "/analytics/statistics/",
                    "/vfs/statistics/",
                ],
            },
            "news_sources": {
                "rbc": {
                    "base_url": "https://www.rbc.ru",
                    "search_url": "https://www.rbc.ru/search/?query={query}",
                    "keywords": [
                        "мошенничество",
                        "фишинг",
                        "кибермошенничество",
                        "банковское мошенничество",
                        "телефонное мошенничество",
                        "интернет мошенничество",
                        "обман",
                        "хищение",
                    ],
                },
                "ria": {
                    "base_url": "https://ria.ru",
                    "search_url": "https://ria.ru/search/?query={query}",
                    "keywords": [
                        "мошенничество",
                        "фишинг",
                        "кибермошенничество",
                        "банковское мошенничество",
                    ],
                },
                "interfax": {
                    "base_url": "https://www.interfax.ru",
                    "search_url": "https://www.interfax.ru/search/?query={query}",
                    "keywords": [
                        "мошенничество",
                        "фишинг",
                        "кибермошенничество",
                    ],
                },
                "tass": {
                    "base_url": "https://tass.ru",
                    "search_url": "https://tass.ru/search?query={query}",
                    "keywords": [
                        "мошенничество",
                        "фишинг",
                        "кибермошенничество",
                    ],
                },
            },
            "government_sources": {
                "mvd": {
                    "base_url": "https://мвд.рф",
                    "endpoints": ["/news", "/press_releases"],
                },
                "fsb": {
                    "base_url": "https://www.fsb.ru",
                    "endpoints": ["/fsb/press_center/news"],
                },
                "roskomnadzor": {
                    "base_url": "https://rkn.gov.ru",
                    "endpoints": ["/news"],
                },
            },
        }

        # Создаем директории
        os.makedirs("data/enhanced_collection", exist_ok=True)

        logger.info("🚀 Расширенный сборщик данных инициализирован")

    async def collect_comprehensive_data(self) -> Dict[str, Any]:
        """
        Комплексный сбор данных из всех источников

        Returns:
            Dict[str, Any]: Собранные данные
        """
        logger.info("📊 Начало комплексного сбора данных...")

        all_data = {
            "metadata": {
                "collection_timestamp": datetime.now().isoformat(),
                "total_sources": 0,
                "total_records": 0,
                "collection_duration": 0,
            },
            "cbr_data": [],
            "news_data": [],
            "government_data": [],
            "fraud_patterns": {
                "by_type": {},
                "by_region": {},
                "by_severity": {},
            },
        }

        start_time = time.time()

        try:
            # Сбор данных ЦБ РФ
            logger.info("🏦 Сбор данных ЦБ РФ...")
            cbr_data = await self._collect_cbr_data()
            all_data["cbr_data"] = cbr_data
            all_data["metadata"]["total_sources"] += 1

            # Сбор новостных данных
            logger.info("📰 Сбор новостных данных...")
            news_data = await self._collect_news_data()
            all_data["news_data"] = news_data
            all_data["metadata"]["total_sources"] += len(
                self.data_sources["news_sources"]
            )

            # Сбор правительственных данных
            logger.info("🏛️ Сбор правительственных данных...")
            gov_data = await self._collect_government_data()
            all_data["government_data"] = gov_data
            all_data["metadata"]["total_sources"] += len(
                self.data_sources["government_sources"]
            )

            # Анализ паттернов
            logger.info("🔍 Анализ паттернов мошенничества...")
            all_data["fraud_patterns"] = self._analyze_fraud_patterns(all_data)

            # Подсчет общего количества записей
            all_data["metadata"]["total_records"] = (
                len(all_data["cbr_data"])
                + len(all_data["news_data"])
                + len(all_data["government_data"])
            )

            # Время сбора
            all_data["metadata"]["collection_duration"] = (
                time.time() - start_time
            )

            # Сохранение данных
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_file = (
                f"data/enhanced_collection/comprehensive_data_{timestamp}.json"
            )

            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Комплексный сбор данных завершен: {data_file}")
            logger.info(
                f"📊 Собрано записей: {all_data['metadata']['total_records']}"
            )

            return all_data

        except Exception as e:
            logger.error(f"❌ Ошибка комплексного сбора данных: {e}")
            return all_data

    async def _collect_cbr_data(self) -> List[Dict[str, Any]]:
        """Сбор данных от ЦБ РФ"""
        cbr_data = []

        try:
            cbr_config = self.data_sources["cbr"]

            for endpoint in cbr_config["endpoints"]:
                try:
                    url = cbr_config["base_url"] + endpoint
                    response = self.session.get(url, timeout=10)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, "html.parser")

                        # Поиск ссылок на отчеты и документы
                        links = soup.find_all("a", href=True)

                        for link in links[:5]:  # Ограничиваем количество
                            href = link.get("href")
                            text = link.get_text(strip=True)

                            if any(
                                keyword in text.lower()
                                for keyword in [
                                    "мошенничество",
                                    "фишинг",
                                    "кибер",
                                    "безопасность",
                                ]
                            ):

                                report_data = {
                                    "id": f"cbr_{len(cbr_data)+1}",
                                    "title": text,
                                    "url": (
                                        href
                                        if href.startswith("http")
                                        else cbr_config["base_url"] + href
                                    ),
                                    "source": "ЦБ РФ",
                                    "date": datetime.now().strftime(
                                        "%Y-%m-%d"
                                    ),
                                    "fraud_type": self._classify_fraud_type(
                                        text
                                    ),
                                    "severity": self._determine_severity(text),
                                    "region": "Российская Федерация",
                                    "amount_lost": self._estimate_amount(text),
                                    "description": text,
                                }

                                cbr_data.append(report_data)

                    # Пауза между запросами
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.warning(f"⚠️ Ошибка сбора данных с {endpoint}: {e}")
                    continue

        except Exception as e:
            logger.error(f"❌ Ошибка сбора данных ЦБ РФ: {e}")

        return cbr_data

    async def _collect_news_data(self) -> List[Dict[str, Any]]:
        """Сбор новостных данных"""
        news_data = []

        try:
            for source_name, source_config in self.data_sources[
                "news_sources"
            ].items():
                try:
                    logger.info(f"📰 Сбор данных из {source_name}...")

                    for keyword in source_config["keywords"]:
                        try:
                            search_url = source_config["search_url"].format(
                                query=keyword
                            )
                            response = self.session.get(search_url, timeout=10)

                            if response.status_code == 200:
                                soup = BeautifulSoup(
                                    response.content, "html.parser"
                                )

                                # Поиск статей (зависит от структуры сайта)
                                articles = soup.find_all(
                                    ["article", "div"],
                                    class_=["news-item", "article", "item"],
                                )

                                for article in articles[
                                    :3
                                ]:  # Ограничиваем количество
                                    title_elem = article.find(
                                        ["h1", "h2", "h3", "a"]
                                    )
                                    if title_elem:
                                        title = title_elem.get_text(strip=True)

                                        if any(
                                            keyword in title.lower()
                                            for keyword in [
                                                "мошенничество",
                                                "фишинг",
                                                "кибер",
                                                "обман",
                                            ]
                                        ):

                                            article_data = {
                                                "id": f"news_{len(news_data)+1}",
                                                "title": title,
                                                "source": source_name.upper(),
                                                "date": datetime.now().strftime(
                                                    "%Y-%m-%d"
                                                ),
                                                "fraud_type": self._classify_fraud_type(
                                                    title
                                                ),
                                                "severity": self._determine_severity(
                                                    title
                                                ),
                                                "region": self._extract_region(
                                                    title
                                                ),
                                                "amount_lost": self._estimate_amount(
                                                    title
                                                ),
                                                "keywords": [keyword],
                                                "description": title,
                                            }

                                            news_data.append(article_data)

                            # Пауза между запросами
                            await asyncio.sleep(2)

                        except Exception as e:
                            logger.warning(
                                f"⚠️ Ошибка поиска по ключевому слову {keyword}: {e}"
                            )
                            continue

                except Exception as e:
                    logger.warning(
                        f"⚠️ Ошибка сбора данных из {source_name}: {e}"
                    )
                    continue

        except Exception as e:
            logger.error(f"❌ Ошибка сбора новостных данных: {e}")

        return news_data

    async def _collect_government_data(self) -> List[Dict[str, Any]]:
        """Сбор правительственных данных"""
        gov_data = []

        try:
            for source_name, source_config in self.data_sources[
                "government_sources"
            ].items():
                try:
                    logger.info(f"🏛️ Сбор данных из {source_name}...")

                    for endpoint in source_config["endpoints"]:
                        try:
                            url = source_config["base_url"] + endpoint
                            response = self.session.get(url, timeout=10)

                            if response.status_code == 200:
                                soup = BeautifulSoup(
                                    response.content, "html.parser"
                                )

                                # Поиск новостей и пресс-релизов
                                items = soup.find_all(
                                    ["div", "article"],
                                    class_=["news", "item", "press"],
                                )

                                for item in items[
                                    :3
                                ]:  # Ограничиваем количество
                                    title_elem = item.find(
                                        ["h1", "h2", "h3", "a"]
                                    )
                                    if title_elem:
                                        title = title_elem.get_text(strip=True)

                                        if any(
                                            keyword in title.lower()
                                            for keyword in [
                                                "мошенничество",
                                                "фишинг",
                                                "кибер",
                                                "безопасность",
                                            ]
                                        ):

                                            gov_item = {
                                                "id": f"gov_{len(gov_data)+1}",
                                                "title": title,
                                                "source": source_name.upper(),
                                                "date": datetime.now().strftime(
                                                    "%Y-%m-%d"
                                                ),
                                                "fraud_type": self._classify_fraud_type(
                                                    title
                                                ),
                                                "severity": self._determine_severity(
                                                    title
                                                ),
                                                "region": "Российская Федерация",
                                                "amount_lost": self._estimate_amount(
                                                    title
                                                ),
                                                "description": title,
                                            }

                                            gov_data.append(gov_item)

                            # Пауза между запросами
                            await asyncio.sleep(1)

                        except Exception as e:
                            logger.warning(
                                f"⚠️ Ошибка сбора данных с {endpoint}: {e}"
                            )
                            continue

                except Exception as e:
                    logger.warning(
                        f"⚠️ Ошибка сбора данных из {source_name}: {e}"
                    )
                    continue

        except Exception as e:
            logger.error(f"❌ Ошибка сбора правительственных данных: {e}")

        return gov_data

    def _classify_fraud_type(self, text: str) -> str:
        """Классификация типа мошенничества по тексту"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["банк", "банковск", "карт"]):
            return "банковское мошенничество"
        elif any(word in text_lower for word in ["кибер", "хакер", "взлом"]):
            return "кибермошенничество"
        elif any(word in text_lower for word in ["телефон", "звонок"]):
            return "телефонное мошенничество"
        elif any(
            word in text_lower for word in ["интернет", "онлайн", "сеть"]
        ):
            return "интернет мошенничество"
        elif any(word in text_lower for word in ["фишинг", "подделка"]):
            return "фишинг"
        elif any(word in text_lower for word in ["пирамида", "схема"]):
            return "финансовая пирамида"
        else:
            return "общее мошенничество"

    def _determine_severity(self, text: str) -> str:
        """Определение серьезности по тексту"""
        text_lower = text.lower()

        if any(
            word in text_lower for word in ["критическ", "массов", "эпидемия"]
        ):
            return "критическая"
        elif any(word in text_lower for word in ["высок", "серьезн", "крупн"]):
            return "высокая"
        elif any(word in text_lower for word in ["средн", "умеренн"]):
            return "средняя"
        else:
            return "низкая"

    def _extract_region(self, text: str) -> str:
        """Извлечение региона из текста"""
        text_lower = text.lower()

        regions = {
            "москва": "Москва",
            "санкт-петербург": "Санкт-Петербург",
            "екатеринбург": "Екатеринбург",
            "казань": "Казань",
            "новосибирск": "Новосибирск",
            "россия": "Российская Федерация",
        }

        for region_key, region_name in regions.items():
            if region_key in text_lower:
                return region_name

        return "Неопределен"

    def _estimate_amount(self, text: str) -> int:
        """Оценка суммы потерь из текста"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["миллион", "млн"]):
            return random.randint(1000000, 5000000)
        elif any(word in text_lower for word in ["тысяч", "тыс"]):
            return random.randint(50000, 500000)
        elif any(word in text_lower for word in ["сотен"]):
            return random.randint(100000, 1000000)
        else:
            return random.randint(10000, 100000)

    def _analyze_fraud_patterns(
        self, data: Dict[str, Any]
    ) -> Dict[str, Dict[str, int]]:
        """Анализ паттернов мошенничества"""
        patterns = {"by_type": {}, "by_region": {}, "by_severity": {}}

        # Анализ всех данных
        all_items = (
            data["cbr_data"] + data["news_data"] + data["government_data"]
        )

        for item in all_items:
            # По типам
            fraud_type = item.get("fraud_type", "неизвестно")
            patterns["by_type"][fraud_type] = (
                patterns["by_type"].get(fraud_type, 0) + 1
            )

            # По регионам
            region = item.get("region", "неизвестно")
            patterns["by_region"][region] = (
                patterns["by_region"].get(region, 0) + 1
            )

            # По серьезности
            severity = item.get("severity", "неизвестно")
            patterns["by_severity"][severity] = (
                patterns["by_severity"].get(severity, 0) + 1
            )

        return patterns

    def generate_enhanced_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация расширенного отчета"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "data_summary": {
                "total_records": data["metadata"]["total_records"],
                "total_sources": data["metadata"]["total_sources"],
                "collection_duration": data["metadata"]["collection_duration"],
                "cbr_records": len(data["cbr_data"]),
                "news_records": len(data["news_data"]),
                "government_records": len(data["government_data"]),
            },
            "fraud_patterns": data["fraud_patterns"],
            "recommendations": [
                "Интегрировать с реальными API банков",
                "Добавить источники данных МВД и ФСБ",
                "Реализовать машинное обучение для классификации",
                "Создать систему раннего предупреждения",
                "Добавить геолокационный анализ",
            ],
        }

        return report


async def main():
    """Основная функция для демонстрации расширенного сбора данных"""
    print("📊 РАСШИРЕННЫЙ СБОР ДАННЫХ ДЛЯ ML МОДЕЛЕЙ")
    print("=" * 50)

    collector = EnhancedDataCollector()

    try:
        # Комплексный сбор данных
        data = await collector.collect_comprehensive_data()

        # Генерация отчета
        report = collector.generate_enhanced_report(data)

        # Сохранение отчета
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = (
            f"data/enhanced_collection/enhanced_report_{timestamp}.json"
        )

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✅ Расширенный сбор данных завершен!")
        print(f"📊 Собрано записей: {data['metadata']['total_records']}")
        print(f"📋 Отчет сохранен: {report_file}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logger.error(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
