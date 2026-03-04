#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NewsScraper - Сборщик новостных данных о мошенничестве
Собирает данные о мошенничестве из российских новостных сайтов
"""

import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# Добавляем путь к модулям

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/news_scraper.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class NewsScraperError(Exception):
    """Базовый класс для ошибок новостного сборщика"""

    pass


class NewsConnectionError(NewsScraperError):
    """Ошибка подключения к новостному сайту"""

    pass


class NewsDataProcessingError(NewsScraperError):
    """Ошибка обработки новостных данных"""

    pass


class NewsSource:
    """Конфигурация новостного источника"""

    def __init__(
        self,
        name: str,
        base_url: str,
        search_url: str,
        article_selectors: Dict[str, str],
        search_keywords: List[str],
    ):
        self.name = name
        self.base_url = base_url
        self.search_url = search_url
        self.article_selectors = article_selectors
        self.search_keywords = search_keywords


class NewsScraper:
    """Сборщик новостных данных о мошенничестве

    Обеспечивает сбор, обработку и структурирование данных
    о мошенничестве из российских новостных источников
    """

    def __init__(self):
        """Инициализация новостного сборщика"""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;"
                    "q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        # Конфигурация для сбора данных
        self.config = {
            "max_retries": 3,
            "retry_delay": 2,
            "request_timeout": 30,
            "rate_limit_delay": 2.0,  # Пауза между запросами
            "max_articles_per_source": 20,
            "min_content_length": 100,  # Минимальная длина контента
        }

        # Настройка новостных источников
        self.news_sources = self._setup_news_sources()

        # Статистика сбора
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_articles": 0,
            "start_time": None,
            "end_time": None,
            "sources_processed": 0,
        }

    def _setup_news_sources(self) -> List[NewsSource]:
        """Настройка новостных источников

        Returns:
            List с конфигурацией источников
        """
        sources = [
            NewsSource(
                name="РБК",
                base_url="https://www.rbc.ru",
                search_url="https://www.rbc.ru/search/?query={query}",
                article_selectors={
                    "title": "h1, .article__title",
                    "content": ".article__text, .article__content",
                    "date": ".article__date, .article__header__date",
                    "author": ".article__author, .article__header__author",
                    "tags": ".article__tags a, .tags a",
                    "links": ".article__text a, .article__content a",
                },
                search_keywords=[
                    "мошенничество",
                    "фишинг",
                    "кибермошенничество",
                    "банковское мошенничество",
                    "телефонное мошенничество",
                    "интернет мошенничество",
                    "обман",
                    "хищение",
                ],
            ),
            NewsSource(
                name="Ведомости",
                base_url="https://www.vedomosti.ru",
                search_url="https://www.vedomosti.ru/search?query={query}",
                article_selectors={
                    "title": "h1, .article-header__title",
                    "content": ".article__text, .article__body",
                    "date": ".article-header__date, .article__date",
                    "author": ".article-header__author, .article__author",
                    "tags": ".article__tags a, .tags a",
                    "links": ".article__text a, .article__body a",
                },
                search_keywords=[
                    "мошенничество",
                    "фишинг",
                    "кибермошенничество",
                    "банковское мошенничество",
                    "телефонное мошенничество",
                    "интернет мошенничество",
                    "обман",
                    "хищение",
                ],
            ),
            NewsSource(
                name="Коммерсантъ",
                base_url="https://www.kommersant.ru",
                search_url="https://www.kommersant.ru/search?query={query}",
                article_selectors={
                    "title": "h1, .article__title",
                    "content": ".article__text, .article__content",
                    "date": ".article__date, .article__header__date",
                    "author": ".article__author, .article__header__author",
                    "tags": ".article__tags a, .tags a",
                    "links": ".article__text a, .article__content a",
                },
                search_keywords=[
                    "мошенничество",
                    "фишинг",
                    "кибермошенничество",
                    "банковское мошенничество",
                    "телефонное мошенничество",
                    "интернет мошенничество",
                    "обман",
                    "хищение",
                ],
            ),
            NewsSource(
                name="РИА Новости",
                base_url="https://ria.ru",
                search_url="https://ria.ru/search/?query={query}",
                article_selectors={
                    "title": "h1, .article__title",
                    "content": ".article__text, .article__content",
                    "date": ".article__date, .article__header__date",
                    "author": ".article__author, .article__header__author",
                    "tags": ".article__tags a, .tags a",
                    "links": ".article__text a, .article__content a",
                },
                search_keywords=[
                    "мошенничество",
                    "фишинг",
                    "кибермошенничество",
                    "банковское мошенничество",
                    "телефонное мошенничество",
                    "интернет мошенничество",
                    "обман",
                    "хищение",
                ],
            ),
        ]

        return sources

    def _validate_url(self, url: str) -> bool:
        """Валидация URL

        Args:
            url: URL для проверки

        Returns:
            bool: True если URL валиден
        """
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except Exception:
            return False

    def _make_request(
        self, url: str, params: Optional[Dict] = None
    ) -> Optional[requests.Response]:
        """Выполнение HTTP запроса с обработкой ошибок

        Args:
            url: URL для запроса
            params: Параметры запроса

        Returns:
            Response object или None при ошибке
        """
        if not self._validate_url(url):
            logger.error(f"Некорректный URL: {url}")
            return None

        for attempt in range(self.config["max_retries"]):
            try:
                self.stats["total_requests"] += 1

                response = self.session.get(
                    url, params=params, timeout=self.config["request_timeout"]
                )

                if response.status_code == 200:
                    self.stats["successful_requests"] += 1
                    logger.info(f"Успешный запрос к {url}")
                    return response
                else:
                    logger.warning(f"HTTP {response.status_code} для {url}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка запроса к {url}: {e}")
                self.stats["failed_requests"] += 1

                if attempt < self.config["max_retries"] - 1:
                    time.sleep(self.config["retry_delay"] * (attempt + 1))

        return None

    def _extract_article_data(
        self, soup: BeautifulSoup, source: NewsSource
    ) -> Dict[str, Any]:
        """Извлечение данных статьи

        Args:
            soup: BeautifulSoup объект страницы
            source: Конфигурация источника

        Returns:
            Dict с данными статьи
        """
        article_data = {
            "title": "",
            "content": "",
            "date": "",
            "author": "",
            "tags": [],
            "links": [],
            "fraud_indicators": [],
            "extracted_at": datetime.now().isoformat(),
        }

        try:
            # Извлечение заголовка
            title_element = soup.select_one(source.article_selectors["title"])
            if title_element:
                article_data["title"] = title_element.get_text(strip=True)

            # Извлечение контента
            content_elements = soup.select(source.article_selectors["content"])
            content_text = []

            for element in content_elements:
                text = element.get_text(strip=True)
                if len(text) > 50:  # Только значимый контент
                    content_text.append(text)

            article_data["content"] = " ".join(content_text)

            # Извлечение даты
            date_element = soup.select_one(source.article_selectors["date"])
            if date_element:
                article_data["date"] = date_element.get_text(strip=True)

            # Извлечение автора
            author_element = soup.select_one(
                source.article_selectors["author"]
            )
            if author_element:
                article_data["author"] = author_element.get_text(strip=True)

            # Извлечение тегов
            tag_elements = soup.select(source.article_selectors["tags"])
            for tag_element in tag_elements:
                tag_text = tag_element.get_text(strip=True)
                if tag_text:
                    article_data["tags"].append(tag_text)

            # Извлечение ссылок
            link_elements = soup.select(source.article_selectors["links"])
            for link_element in link_elements:
                link_text = link_element.get_text(strip=True)
                link_href = link_element.get("href", "")
                if link_text and link_href:
                    article_data["links"].append(
                        {"text": link_text, "url": link_href}
                    )

            # Анализ на признаки мошенничества
            article_data["fraud_indicators"] = self._analyze_fraud_indicators(
                article_data["content"]
            )

            return article_data

        except Exception as e:
            logger.error(f"Ошибка извлечения данных статьи: {e}")
            return article_data

    def _analyze_fraud_indicators(self, content: str) -> List[str]:
        """Анализ контента на признаки мошенничества

        Args:
            content: Текст для анализа

        Returns:
            List с найденными индикаторами
        """
        indicators = []
        content_lower = content.lower()

        # Словарь индикаторов мошенничества
        fraud_patterns = {
            "phone_fraud": [
                "звонок из банка",
                "подтвердите операцию",
                "блокировка карты",
                "подозрительная операция",
                "мошенники звонят",
                "телефонное мошенничество",
            ],
            "banking_fraud": [
                "поддельная карта",
                "снятие денег",
                "несанкционированная операция",
                "банковское мошенничество",
                "фишинг сайт",
                "поддельный сайт",
            ],
            "internet_fraud": [
                "интернет мошенничество",
                "онлайн обман",
                "поддельный магазин",
                "фейковый сайт",
                "ложная реклама",
                "мошенническая схема",
            ],
            "identity_theft": [
                "кража личности",
                "поддельные документы",
                "фиктивная личность",
                "использование чужих данных",
                "кража персональных данных",
            ],
            "social_engineering": [
                "социальная инженерия",
                "психологическое воздействие",
                "манипуляции",
                "обман пожилых",
                "доверие мошенникам",
            ],
        }

        for category, patterns in fraud_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    indicators.append(category)
                    break

        return list(set(indicators))  # Убираем дубликаты

    def _search_articles(
        self, source: NewsSource, keyword: str, max_pages: int = 3
    ) -> List[str]:
        """Поиск статей по ключевому слову

        Args:
            source: Конфигурация источника
            keyword: Ключевое слово для поиска
            max_pages: Максимальное количество страниц

        Returns:
            List с URL статей
        """
        article_urls = []

        try:
            search_url = source.search_url.format(query=keyword)
            logger.info(
                f"Поиск статей по ключевому слову '{keyword}' в {source.name}"
            )

            for page in range(1, max_pages + 1):
                params = {"page": page} if "page" in search_url else {}

                response = self._make_request(search_url, params)
                if not response:
                    continue

                soup = BeautifulSoup(response.content, "html.parser")

                # Поиск ссылок на статьи (универсальные селекторы)
                article_links = soup.find_all("a", href=True)

                for link in article_links:
                    href = link.get("href", "")
                    link_text = link.get_text(strip=True).lower()

                    # Фильтрация ссылок на статьи
                    if any(
                        indicator in link_text
                        for indicator in [
                            "мошенничество",
                            "обман",
                            "хищение",
                            "фишинг",
                        ]
                    ) or any(
                        indicator in href
                        for indicator in ["article", "news", "story"]
                    ):
                        full_url = urljoin(source.base_url, href)
                        if self._validate_url(full_url):
                            article_urls.append(full_url)

                # Пауза между страницами
                time.sleep(self.config["rate_limit_delay"])

        except Exception as e:
            logger.error(f"Ошибка поиска статей в {source.name}: {e}")

        return article_urls[: self.config["max_articles_per_source"]]

    def collect_news_data(
        self, max_sources: int = None
    ) -> List[Dict[str, Any]]:
        """Сбор новостных данных о мошенничестве

        Args:
            max_sources: Максимальное количество источников

        Returns:
            List с новостными данными
        """
        logger.info("Начало сбора новостных данных о мошенничестве")
        self.stats["start_time"] = datetime.now()

        all_articles = []
        sources_to_process = (
            self.news_sources[:max_sources]
            if max_sources
            else self.news_sources
        )

        for source in sources_to_process:
            try:
                logger.info(f"Обработка источника: {source.name}")
                self.stats["sources_processed"] += 1

                source_articles = []

                # Поиск статей по каждому ключевому слову
                for keyword in source.search_keywords:
                    try:
                        article_urls = self._search_articles(source, keyword)

                        # Сбор данных с найденных статей
                        for url in article_urls:
                            try:
                                response = self._make_request(url)
                                if not response:
                                    continue

                                soup = BeautifulSoup(
                                    response.content, "html.parser"
                                )
                                article_data = self._extract_article_data(
                                    soup, source
                                )

                                # Проверка минимальной длины контента
                                if (
                                    len(article_data["content"])
                                    < self.config["min_content_length"]
                                ):
                                    continue

                                # Дополнение метаданных
                                article_data.update(
                                    {
                                        "source": source.name,
                                        "source_url": source.base_url,
                                        "article_url": url,
                                        "search_keyword": keyword,
                                        "id": hashlib.md5(
                                            f"{url}{article_data['title']}"
                                            .encode()
                                        ).hexdigest(),
                                    }
                                )

                                source_articles.append(article_data)
                                self.stats["total_articles"] += 1

                                logger.info(
                                    f"Собрана статья: "
                                    f"{article_data['title'][:50]}..."
                                )

                                # Пауза между статьями
                                time.sleep(self.config["rate_limit_delay"])

                            except Exception as e:
                                logger.error(
                                    f"Ошибка обработки статьи {url}: {e}"
                                )
                                continue

                    except Exception as e:
                        logger.error(
                            f"Ошибка поиска по ключевому слову "
                            f"'{keyword}': {e}"
                        )
                        continue

                all_articles.extend(source_articles)
                logger.info(
                    f"Источник {source.name}: собрано "
                    f"{len(source_articles)} статей"
                )

            except Exception as e:
                logger.error(f"Ошибка обработки источника {source.name}: {e}")
                continue

        self.stats["end_time"] = datetime.now()
        logger.info(
            f"Сбор новостей завершен. Получено {len(all_articles)} статей"
        )

        return all_articles

    def save_data(
        self, data: List[Dict[str, Any]], filename: str = None
    ) -> str:
        """Сохранение собранных данных

        Args:
            data: Данные для сохранения
            filename: Имя файла (опционально)

        Returns:
            str: Путь к сохраненному файлу
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_fraud_data_{timestamp}.json"

        # Создание директории если не существует
        data_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "news"
        )
        os.makedirs(data_dir, exist_ok=True)

        filepath = os.path.join(data_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Новостные данные сохранены в {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Ошибка сохранения новостных данных: {e}")
            raise NewsDataProcessingError(f"Не удалось сохранить данные: {e}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Получение статистики сбора данных

        Returns:
            Dict со статистикой
        """
        stats = self.stats.copy()

        if stats["start_time"] and stats["end_time"]:
            stats["duration"] = (
                stats["end_time"] - stats["start_time"]
            ).total_seconds()

        stats["success_rate"] = (
            stats["successful_requests"] / stats["total_requests"]
            if stats["total_requests"] > 0
            else 0
        )

        stats["articles_per_source"] = (
            stats["total_articles"] / stats["sources_processed"]
            if stats["sources_processed"] > 0
            else 0
        )

        return stats

    def close(self):
        """Закрытие соединений"""
        if hasattr(self, "session"):
            self.session.close()


# Пример использования
if __name__ == "__main__":
    scraper = NewsScraper()

    try:
        # Сбор новостных данных
        news_data = scraper.collect_news_data(max_sources=2)

        # Сохранение данных
        filepath = scraper.save_data(news_data)
        print(f"Новостные данные сохранены в: {filepath}")

        # Вывод статистики
        stats = scraper.get_collection_stats()
        print("\nСтатистика сбора новостей:")
        print(f"Всего запросов: {stats['total_requests']}")
        print("Успешных:", stats['successful_requests'])
        print(f"Неудачных: {stats['failed_requests']}")
        print(f"Собрано статей: {stats['total_articles']}")
        print(f"Обработано источников: {stats['sources_processed']}")
        print(f"Время выполнения: {stats.get('duration', 0):.2f} сек")

        # Примеры собранных данных
        if news_data:
            print("\nПримеры собранных статей:")
            for i, article in enumerate(news_data[:3]):
                print(f"{i+1}. {article['title'][:80]}...")
                print(f"   Источник: {article['source']}")
                print(
                    f"   Индикаторы: {', '.join(article['fraud_indicators'])}"
                )
                print()

    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
    finally:
        scraper.close()
