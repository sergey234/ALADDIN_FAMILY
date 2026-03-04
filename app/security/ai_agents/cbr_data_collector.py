#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CBRDataCollector - Сборщик данных от Центрального Банка РФ
Собирает данные о мошенничестве из открытых источников ЦБ РФ
"""

import hashlib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Добавляем путь к модулям

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/cbr_data_collector.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CBRDataCollectorError(Exception):
    """Базовый класс для ошибок сборщика данных ЦБ РФ"""
    pass


class CBRConnectionError(CBRDataCollectorError):
    """Ошибка подключения к сайту ЦБ РФ"""
    pass


class CBRDataProcessingError(CBRDataCollectorError):
    """Ошибка обработки данных от ЦБ РФ"""
    pass


class CBRDataCollector:
    """Сборщик данных о мошенничестве от Центрального Банка РФ

    Обеспечивает сбор, обработку и структурирование данных
    о мошенничестве из открытых источников ЦБ РФ
    """

    def __init__(self, base_url: str = "https://www.cbr.ru"):
        """Инициализация сборщика данных ЦБ РФ

        Args:
            base_url: Базовый URL сайта ЦБ РФ
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36')
        })

        # Конфигурация для сбора данных
        self.config = {
            'max_retries': 3,
            'retry_delay': 2,
            'request_timeout': 30,
            'rate_limit_delay': 1.0,  # Пауза между запросами
            'max_pages': 50,  # Максимальное количество страниц
        }

        # Статистика сбора
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_records': 0,
            'start_time': None,
            'end_time': None,
        }

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

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
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

        for attempt in range(self.config['max_retries']):
            try:
                self.stats['total_requests'] += 1

                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.config['request_timeout']
                )

                if response.status_code == 200:
                    self.stats['successful_requests'] += 1
                    logger.info(f"Успешный запрос к {url}")
                    return response
                else:
                    logger.warning(f"HTTP {response.status_code} для {url}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка запроса к {url}: {e}")
                self.stats['failed_requests'] += 1

                if attempt < self.config['max_retries'] - 1:
                    time.sleep(self.config['retry_delay'] * (attempt + 1))

        return None

    def _parse_fraud_report(self, html_content: str) -> Dict[str, Any]:
        """Парсинг отчета о мошенничестве

        Args:
            html_content: HTML содержимое страницы

        Returns:
            Dict с данными о мошенничестве
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Поиск основных данных
            fraud_data = {
                'title': '',
                'date': '',
                'content': '',
                'statistics': {},
                'recommendations': [],
                'affected_regions': [],
                'fraud_types': [],
                'source_url': '',
                'extracted_at': datetime.now().isoformat()
            }

            # Извлечение заголовка
            title_element = soup.find('h1') or soup.find('title')
            if title_element:
                fraud_data['title'] = title_element.get_text(strip=True)

            # Извлечение даты
            date_patterns = [
                r'\d{1,2}\.\d{1,2}\.\d{4}',
                r'\d{4}-\d{2}-\d{2}',
                r'\d{1,2}\s+\w+\s+\d{4}'
            ]

            text_content = soup.get_text()
            for pattern in date_patterns:
                date_match = re.search(pattern, text_content)
                if date_match:
                    fraud_data['date'] = date_match.group()
                    break

            # Извлечение статистики
            stats_patterns = {
                'amount': r'(?:сумма|размер|объем).*?(\d+(?:\s+\d+)*\s*(?:млн|млрд|тыс)?\s*(?:руб|₽))',
                'cases': r'(?:случаев|инцидентов|преступлений).*?(\d+)',
                'losses': r'(?:ущерб|потери|убытки).*?(\d+(?:\s+\d+)*\s*(?:млн|млрд|тыс)?\s*(?:руб|₽))'
            }

            for key, pattern in stats_patterns.items():
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    fraud_data['statistics'][key] = match.group(1)

            # Извлечение рекомендаций
            recommendations = []
            rec_elements = soup.find_all(['li', 'p'], string=re.compile(
                r'(?:рекомендуем|советуем|необходимо|следует)',
                re.IGNORECASE
            ))

            for element in rec_elements:
                recommendations.append(element.get_text(strip=True))

            fraud_data['recommendations'] = recommendations

            # Извлечение типов мошенничества
            fraud_types = []
            fraud_keywords = [
                'фишинг', 'мошенничество', 'обман', 'хищение',
                'подделка', 'взлом', 'кража', 'манипуляции'
            ]

            for keyword in fraud_keywords:
                if re.search(keyword, text_content, re.IGNORECASE):
                    fraud_types.append(keyword)

            fraud_data['fraud_types'] = fraud_types

            # Извлечение основного контента
            content_elements = soup.find_all(['p', 'div'], class_=re.compile(
                r'(?:content|text|article|news)', re.IGNORECASE
            ))

            content_text = []
            for element in content_elements:
                text = element.get_text(strip=True)
                if len(text) > 50:  # Только значимый контент
                    content_text.append(text)

            fraud_data['content'] = ' '.join(content_text[:5])  # Первые 5 абзацев

            return fraud_data

        except Exception as e:
            logger.error(f"Ошибка парсинга отчета: {e}")
            raise CBRDataProcessingError(f"Не удалось обработать данные: {e}")

    def collect_fraud_reports(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Сбор отчетов о мошенничестве

        Args:
            max_pages: Максимальное количество страниц для сбора

        Returns:
            List с данными о мошенничестве
        """
        logger.info("Начало сбора отчетов о мошенничестве от ЦБ РФ")
        self.stats['start_time'] = datetime.now()

        all_reports = []

        # Основные разделы ЦБ РФ для поиска информации о мошенничестве
        sections = [
            '/na/',  # Правовые акты
            '/analytics/',  # Аналитика
            '/press/',  # Пресс-релизы
            '/vfs/',  # Финансовая стабильность
        ]

        for section in sections:
            try:
                section_url = urljoin(self.base_url, section)
                logger.info(f"Обработка раздела: {section_url}")

                # Поиск страниц с упоминанием мошенничества
                search_params = {
                    'q': 'мошенничество',
                    'page': 1
                }

                for page in range(1, min(max_pages, self.config['max_pages']) + 1):
                    search_params['page'] = page

                    response = self._make_request(section_url, search_params)
                    if not response:
                        continue

                    # Поиск ссылок на отчеты
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = soup.find_all('a', href=True)

                    fraud_links = []
                    for link in links:
                        link_text = link.get_text(strip=True).lower()
                        link_href = link.get('href', '')

                        if any(keyword in link_text for keyword in [
                            'мошенничество', 'обман', 'хищение', 'фишинг'
                        ]):
                            full_url = urljoin(self.base_url, link_href)
                            fraud_links.append(full_url)

                    # Сбор данных с найденных страниц
                    for link_url in fraud_links[:5]:  # Максимум 5 ссылок на страницу
                        try:
                            report_response = self._make_request(link_url)
                            if report_response:
                                fraud_data = self._parse_fraud_report(
                                    report_response.text
                                )
                                fraud_data['source_url'] = link_url
                                fraud_data['source_section'] = section

                                # Генерация уникального ID
                                fraud_data['id'] = hashlib.md5(
                                    f"{link_url}{fraud_data['title']}".encode()
                                ).hexdigest()

                                all_reports.append(fraud_data)
                                self.stats['total_records'] += 1

                                logger.info(f"Собран отчет: {fraud_data['title'][:50]}...")

                        except Exception as e:
                            logger.error(f"Ошибка обработки ссылки {link_url}: {e}")
                            continue

                    # Пауза между страницами
                    time.sleep(self.config['rate_limit_delay'])

            except Exception as e:
                logger.error(f"Ошибка обработки раздела {section}: {e}")
                continue

        self.stats['end_time'] = datetime.now()
        logger.info(f"Сбор завершен. Получено {len(all_reports)} отчетов")

        return all_reports

    def collect_statistics(self) -> Dict[str, Any]:
        """Сбор статистических данных о мошенничестве

        Returns:
            Dict со статистикой мошенничества
        """
        logger.info("Сбор статистических данных о мошенничестве")

        statistics = {
            'period': datetime.now().strftime('%Y-%m'),
            'total_fraud_cases': 0,
            'total_losses': 0,
            'fraud_by_type': {},
            'fraud_by_region': {},
            'trends': {},
            'source': 'ЦБ РФ',
            'collected_at': datetime.now().isoformat()
        }

        # URL для статистики
        stats_urls = [
            '/analytics/statistics/',
            '/vfs/statistics/',
        ]

        for url in stats_urls:
            try:
                full_url = urljoin(self.base_url, url)
                response = self._make_request(full_url)

                if response:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Поиск числовых данных
                    text_content = soup.get_text()

                    # Паттерны для поиска статистики
                    patterns = {
                        'cases': r'(?:случаев|инцидентов|преступлений).*?(\d+(?:\s+\d+)*)',
                        'losses': r'(?:ущерб|потери|убытки).*?(\d+(?:\s+\d+)*)\s*(?:млн|млрд|тыс)?',
                        'growth': r'(?:рост|увеличение|снижение).*?(\d+(?:\.\d+)?%)'
                    }

                    for key, pattern in patterns.items():
                        matches = re.findall(pattern, text_content, re.IGNORECASE)
                        if matches:
                            statistics[key] = matches[0] if len(matches) == 1 else matches

            except Exception as e:
                logger.error(f"Ошибка сбора статистики с {url}: {e}")
                continue

        return statistics

    def save_data(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """Сохранение собранных данных

        Args:
            data: Данные для сохранения
            filename: Имя файла (опционально)

        Returns:
            str: Путь к сохраненному файлу
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cbr_fraud_data_{timestamp}.json"

        # Создание директории если не существует
        data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cbr")
        os.makedirs(data_dir, exist_ok=True)

        filepath = os.path.join(data_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

                logger.info("Данные сохранены в %s", filepath)
            return filepath

        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
            raise CBRDataProcessingError(f"Не удалось сохранить данные: {e}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Получение статистики сбора данных

        Returns:
            Dict со статистикой
        """
        stats = self.stats.copy()

        if stats['start_time'] and stats['end_time']:
            stats['duration'] = (
                stats['end_time'] - stats['start_time']
            ).total_seconds()

        stats['success_rate'] = (
            stats['successful_requests'] / stats['total_requests']
            if stats['total_requests'] > 0 else 0
        )

        return stats

    def close(self):
        """Закрытие соединений"""
        if hasattr(self, 'session'):
            self.session.close()


# Пример использования
if __name__ == "__main__":
    collector = CBRDataCollector()

    try:
        # Сбор отчетов о мошенничестве
        fraud_reports = collector.collect_fraud_reports(max_pages=5)

        # Сбор статистики
        statistics = collector.collect_statistics()

        # Объединение данных
        all_data = {
            'reports': fraud_reports,
            'statistics': statistics,
            'collection_stats': collector.get_collection_stats(),
            'metadata': {
                'collected_at': datetime.now().isoformat(),
                'source': 'ЦБ РФ',
                'total_reports': len(fraud_reports)
            }
        }

        # Сохранение данных
        filepath = collector.save_data(all_data)
        print(f"Данные сохранены в: {filepath}")

        # Вывод статистики
        stats = collector.get_collection_stats()
        print(f"\nСтатистика сбора:")
        print(f"Всего запросов: {stats['total_requests']}")
        print(f"Успешных: {stats['successful_requests']}")
        print(f"Неудачных: {stats['failed_requests']}")
        print(f"Собрано записей: {stats['total_records']}")
        print(f"Время выполнения: {stats.get('duration', 0):.2f} сек")

    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
    finally:
        collector.close()
