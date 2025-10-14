#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MobileUserAIAgent - Гибридный AI Агент-Бот для мобильного приложения
Максимально простой и понятный язык для пользователей

Функции:
- Простые объяснения функций системы безопасности
- Геймификация и мотивация пользователей
- Интерактивные руководства и туториалы
- Эмоциональная поддержка и помощь
- Персонализированные рекомендации

Автор: ALADDIN Security System
Версия: 1.0
Дата: 2025-09-08
"""

import os
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Добавляем путь к core модулям

try:
    from core.base import SecurityBase
except ImportError:
    # Fallback для совместимости
    class SecurityBase:
        def __init__(self, name, config=None):
            self.name = name
            self.config = config or {}
            self.is_active = True
            self.created_at = datetime.now()
            self.last_update = datetime.now()


class UserLevel(Enum):
    """Уровни пользователей"""

    НОВИЧОК = "новичок"
    ПОЛЬЗОВАТЕЛЬ = "пользователь"
    ОПЫТНЫЙ = "опытный"
    ЭКСПЕРТ = "эксперт"
    МАСТЕР = "мастер"


class FunctionCategory(Enum):
    """Категории функций"""

    ЗАЩИТА = "защита"
    МОНИТОРИНГ = "мониторинг"
    АНАЛИЗ = "анализ"
    УВЕДОМЛЕНИЯ = "уведомления"
    СЕМЬЯ = "семья"
    ДЕТИ = "дети"
    СЕТЬ = "сеть"
    УСТРОЙСТВА = "устройства"
    ДАННЫЕ = "данные"
    ПРИЛОЖЕНИЯ = "приложения"


class EmotionType(Enum):
    """Типы эмоций пользователя"""

    РАДОСТЬ = "радость"
    УДИВЛЕНИЕ = "удивление"
    СПОКОЙСТВИЕ = "спокойствие"
    БЕСПОКОЙСТВО = "беспокойство"
    ЗАИНТЕРЕСОВАННОСТЬ = "заинтересованность"
    СМУЩЕНИЕ = "смущение"
    ГОРДОСТЬ = "гордость"


@dataclass
class SecurityFunction:
    """Функция системы безопасности"""

    english_name: str
    russian_name: str
    category: FunctionCategory
    description: str
    what_it_does: str
    what_protects: str
    for_users: str
    features: List[str]
    icon: str
    color: str
    difficulty: int  # 1-5 (1 - очень просто, 5 - сложно)
    importance: int  # 1-5 (1 - низкая, 5 - критическая)


@dataclass
class UserProfile:
    """Профиль пользователя"""

    user_id: str
    name: str
    level: UserLevel
    experience_points: int = 0
    achievements: List[str] = field(default_factory=list)
    favorite_functions: List[str] = field(default_factory=list)
    learned_functions: List[str] = field(default_factory=list)
    current_emotion: EmotionType = EmotionType.СПОКОЙСТВИЕ
    last_activity: datetime = field(default_factory=datetime.now)
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TutorialStep:
    """Шаг туториала"""

    step_id: str
    title: str
    description: str
    action: str
    reward: int
    is_completed: bool = False


class MobileUserAIAgent(SecurityBase):
    """
    Гибридный AI Агент-Бот для мобильного приложения

    Объясняет функции системы безопасности простым и понятным языком
    Мотивирует пользователей через геймификацию
    Обеспечивает максимально комфортное использование системы
    """

    def __init__(self, name="MobileUserAIAgent", config=None):
        SecurityBase.__init__(self, name, config)

        # База данных функций системы
        self.functions_database = self._create_functions_database()

        # Пользовательские профили
        self.user_profiles: Dict[str, UserProfile] = {}

        # Система достижений
        self.achievements = self._create_achievements_system()

        # Туториалы и руководства
        self.tutorials = self._create_tutorials()

        # Эмоциональные реакции
        self.emotional_responses = self._create_emotional_responses()

        # Простые ответы (бот-режим)
        self.quick_responses = self._create_quick_responses()

        # AI компоненты
        self.learning_engine = None
        self.recommendation_engine = None
        self.emotion_analyzer = None

        # Настройка логгера
        self.logger = self._setup_logger()

        self.logger.info("MobileUserAIAgent инициализирован")

    def _setup_logger(self):
        """Настройка логгера"""
        import logging

        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _create_functions_database(self) -> Dict[str, SecurityFunction]:
        """Создание базы данных функций системы с простыми названиями"""
        functions = {}

        # Основные функции безопасности
        functions["temporal_analysis"] = SecurityFunction(
            english_name="Temporal Analysis Engine",
            russian_name="Движок временного анализа",
            category=FunctionCategory.АНАЛИЗ,
            description="Умный анализатор активности по времени",
            what_it_does=(
                "Анализирует активность пользователей во времени "
                "для выявления подозрительных паттернов"
            ),
            what_protects=(
                "Временные атаки, необычная активность " "в неположенное время"
            ),
            for_users="Как временной страж - следит за активностью по часам",
            features=[
                "Анализ временных паттернов активности",
                "Детекция необычной активности в неположенное время",
                "Предотвращение временных атак",
                "Уведомления о подозрительной активности",
                "Статистика использования по времени",
            ],
            icon="⏰",
            color="#FF6B6B",
            difficulty=2,
            importance=4,
        )

        functions["threat_detection"] = SecurityFunction(
            english_name="Advanced Threat Detection",
            russian_name="Умный детектор угроз",
            category=FunctionCategory.ЗАЩИТА,
            description="Искусственный интеллект для поиска опасностей",
            what_it_does=(
                "Автоматически находит и блокирует все виды киберугроз"
            ),
            what_protects=(
                "Вирусы, хакерские атаки, фишинг, вредоносные программы"
            ),
            for_users="Как личный охранник - всегда на страже",
            features=[
                "Мгновенное обнаружение угроз",
                "Блокировка опасных сайтов",
                "Защита от вирусов",
                "Предупреждения о подозрительных действиях",
                "Автоматическое лечение заражений",
            ],
            icon="🛡️",
            color="#4ECDC4",
            difficulty=1,
            importance=5,
        )

        functions["family_protection"] = SecurityFunction(
            english_name="Family Security Manager",
            russian_name="Семейный защитник",
            category=FunctionCategory.СЕМЬЯ,
            description="Защита всей семьи в одном приложении",
            what_it_does=(
                "Обеспечивает безопасность всех членов семьи "
                "на всех устройствах"
            ),
            what_protects="Детей от опасного контента, семью от киберугроз",
            for_users="Как семейный психолог - заботится о каждом",
            features=[
                "Родительский контроль",
                "Защита детей в интернете",
                "Мониторинг активности семьи",
                "Безопасное общение",
                "Семейные правила безопасности",
            ],
            icon="👨‍👩‍👧‍👦",
            color="#45B7D1",
            difficulty=2,
            importance=5,
        )

        functions["vpn_protection"] = SecurityFunction(
            english_name="VPN Security System",
            russian_name="Защитный туннель",
            category=FunctionCategory.СЕТЬ,
            description="Невидимый щит для вашего интернета",
            what_it_does="Создает защищенное соединение с интернетом",
            what_protects="Отслеживание, кража данных, блокировки сайтов",
            for_users="Как невидимый плащ - скрывает вашу активность",
            features=[
                "Шифрование всего трафика",
                "Смена IP-адреса",
                "Обход блокировок",
                "Защита в публичных сетях",
                "Анонимность в интернете",
            ],
            icon="🔒",
            color="#96CEB4",
            difficulty=2,
            importance=4,
        )

        functions["antivirus"] = SecurityFunction(
            english_name="Antivirus Protection",
            russian_name="Антивирусный щит",
            category=FunctionCategory.ЗАЩИТА,
            description="Мощная защита от вирусов и вредоносов",
            what_it_does="Сканирует и удаляет все вредоносные программы",
            what_protects="Вирусы, трояны, шпионские программы, рекламное ПО",
            for_users="Как врач для вашего устройства - лечит и защищает",
            features=[
                "Реальное время сканирования",
                "Обнаружение новых угроз",
                "Карантин подозрительных файлов",
                "Очистка системы",
                "Защита от фишинга",
            ],
            icon="💊",
            color="#FFEAA7",
            difficulty=1,
            importance=5,
        )

        functions["behavioral_analysis"] = SecurityFunction(
            english_name="Behavioral Analysis Engine",
            russian_name="Анализатор поведения",
            category=FunctionCategory.АНАЛИЗ,
            description="Умный наблюдатель за поведением",
            what_it_does=(
                "Изучает привычки пользователей и находит отклонения"
            ),
            what_protects=(
                "Кража аккаунтов, подозрительная активность, аномалии"
            ),
            for_users="Как внимательный друг - замечает изменения",
            features=[
                "Изучение привычек пользователя",
                "Выявление необычного поведения",
                "Предупреждения о подозрительной активности",
                "Адаптация к новым привычкам",
                "Статистика активности",
            ],
            icon="👁️",
            color="#DDA0DD",
            difficulty=3,
            importance=4,
        )

        functions["data_encryption"] = SecurityFunction(
            english_name="Data Encryption Manager",
            russian_name="Шифровальщик данных",
            category=FunctionCategory.ДАННЫЕ,
            description="Неприступная защита ваших файлов",
            what_it_does="Шифрует все важные данные на устройстве",
            what_protects=(
                "Кража данных, утечки информации, несанкционированный доступ"
            ),
            for_users="Как сейф для документов - хранит в безопасности",
            features=[
                "Шифрование файлов и папок",
                "Защита паролей",
                "Безопасное хранение документов",
                "Автоматическое шифрование",
                "Восстановление доступа",
            ],
            icon="🔐",
            color="#98D8C8",
            difficulty=3,
            importance=5,
        )

        functions["network_monitor"] = SecurityFunction(
            english_name="Network Security Monitor",
            russian_name="Сетевой страж",
            category=FunctionCategory.МОНИТОРИНГ,
            description="Бдительный охранник вашей сети",
            what_it_does="Следит за всеми подключениями к интернету",
            what_protects=(
                "Взломы сети, подозрительные подключения, утечки данных"
            ),
            for_users="Как охранник дома - проверяет всех гостей",
            features=[
                "Мониторинг сетевого трафика",
                "Блокировка подозрительных подключений",
                "Анализ безопасности сети",
                "Уведомления о нарушениях",
                "Статистика использования сети",
            ],
            icon="🌐",
            color="#F7DC6F",
            difficulty=2,
            importance=4,
        )

        functions["child_safety"] = SecurityFunction(
            english_name="Child Safety Manager",
            russian_name="Детский защитник",
            category=FunctionCategory.ДЕТИ,
            description="Заботливый няня для детей в интернете",
            what_it_does="Обеспечивает безопасность детей в цифровом мире",
            what_protects="Опасный контент, незнакомцы, кибербуллинг",
            for_users="Как заботливая няня - всегда рядом с ребенком",
            features=[
                "Фильтрация контента по возрасту",
                "Блокировка опасных сайтов",
                "Контроль времени использования",
                "Мониторинг общения",
                "Образовательные материалы",
            ],
            icon="👶",
            color="#FFB6C1",
            difficulty=1,
            importance=5,
        )

        functions["notification_system"] = SecurityFunction(
            english_name="Smart Notification System",
            russian_name="Умные уведомления",
            category=FunctionCategory.УВЕДОМЛЕНИЯ,
            description="Интеллектуальная система оповещений",
            what_it_does="Отправляет важные уведомления в нужное время",
            what_protects="Пропуск важных событий, информационная перегрузка",
            for_users="Как личный секретарь - напоминает о важном",
            features=[
                "Умная приоритизация уведомлений",
                "Персонализация по времени",
                "Группировка похожих сообщений",
                "Тихие часы",
                "Анализ важности",
            ],
            icon="📢",
            color="#87CEEB",
            difficulty=1,
            importance=3,
        )

        return functions

    def _create_achievements_system(self) -> Dict[str, Dict[str, Any]]:
        """Создание системы достижений"""
        return {
            "первый_шаг": {
                "name": "Первый шаг",
                "description": "Изучили первую функцию безопасности",
                "icon": "🎯",
                "points": 10,
                "requirement": "learned_functions >= 1",
            },
            "защитник": {
                "name": "Защитник",
                "description": "Активировали 5 функций защиты",
                "icon": "🛡️",
                "points": 50,
                "requirement": "active_functions >= 5",
            },
            "семейный_герой": {
                "name": "Семейный герой",
                "description": "Настроили защиту для всей семьи",
                "icon": "👨‍👩‍👧‍👦",
                "points": 100,
                "requirement": "family_protection_active == True",
            },
            "эксперт_безопасности": {
                "name": "Эксперт безопасности",
                "description": "Изучили все функции системы",
                "icon": "🎓",
                "points": 200,
                "requirement": "learned_functions >= 10",
            },
            "мастер_защиты": {
                "name": "Мастер защиты",
                "description": "Достигли максимального уровня защиты",
                "icon": "👑",
                "points": 500,
                "requirement": "security_level == 5",
            },
        }

    def _create_tutorials(self) -> Dict[str, List[TutorialStep]]:
        """Создание туториалов"""
        return {
            "первое_знакомство": [
                TutorialStep(
                    step_id="welcome",
                    title="Добро пожаловать!",
                    description="Давайте познакомимся с системой безопасности",
                    action="Нажмите 'Далее' чтобы продолжить",
                    reward=5,
                ),
                TutorialStep(
                    step_id="explore_functions",
                    title="Изучите функции",
                    description="Посмотрите на доступные функции защиты",
                    action="Нажмите на любую функцию",
                    reward=10,
                ),
                TutorialStep(
                    step_id="activate_protection",
                    title="Активируйте защиту",
                    description="Включите первую функцию защиты",
                    action="Нажмите 'Включить' на любой функции",
                    reward=15,
                ),
            ],
            "настройка_семьи": [
                TutorialStep(
                    step_id="add_family_member",
                    title="Добавьте члена семьи",
                    description="Создайте профиль для члена семьи",
                    action="Нажмите 'Добавить члена семьи'",
                    reward=20,
                ),
                TutorialStep(
                    step_id="set_parental_controls",
                    title="Настройте родительский контроль",
                    description="Установите правила для детей",
                    action="Перейдите в настройки детей",
                    reward=25,
                ),
            ],
        }

    def _create_emotional_responses(self) -> Dict[EmotionType, List[str]]:
        """Создание эмоциональных реакций"""
        return {
            EmotionType.РАДОСТЬ: [
                "Отлично! Вы делаете большие успехи! 🎉",
                "Превосходно! Ваша безопасность в надежных руках! ✨",
                "Замечательно! Вы становитесь настоящим экспертом! 🌟",
            ],
            EmotionType.УДИВЛЕНИЕ: [
                "Вау! Вы только что узнали что-то новое! 😲",
                "Невероятно! Эта функция действительно крутая! 🤩",
                "Потрясающе! Вы открыли новый уровень защиты! 🚀",
            ],
            EmotionType.СПОКОЙСТВИЕ: [
                "Все хорошо, вы в безопасности 😌",
                "Система работает стабильно, можете расслабиться 🛡️",
                "Ваша защита активна, беспокоиться не о чем 🧘‍♀️",
            ],
            EmotionType.БЕСПОКОЙСТВО: [
                "Не волнуйтесь, я помогу вам разобраться! 🤗",
                "Все будет хорошо, давайте решим это вместе! 💪",
                "Я здесь, чтобы помочь вам! Не переживайте! 🆘",
            ],
            EmotionType.ЗАИНТЕРЕСОВАННОСТЬ: [
                "Интересно! Расскажу вам больше об этом! 🤔",
                "Отличный вопрос! Давайте разберем подробнее! 💡",
                "Любопытно! Покажу вам, как это работает! 🔍",
            ],
            EmotionType.СМУЩЕНИЕ: [
                "Не переживайте, все с чего-то начинают! 😊",
                "Это нормально! Я объясню все простыми словами! 📚",
                "Не стесняйтесь! Я здесь, чтобы помочь! 🤝",
            ],
            EmotionType.ГОРДОСТЬ: [
                "Вы молодец! Горжусь вашими успехами! 🏆",
                "Потрясающе! Вы настоящий мастер безопасности! 🎖️",
                "Великолепно! Вы стали примером для других! 👑",
            ],
        }

    def _create_quick_responses(self) -> Dict[str, str]:
        """Создание быстрых ответов (бот-режим)"""
        return {
            "привет": (
                "Привет! Я ваш помощник по безопасности! Как дела? 😊"
            ),
            "помощь": (
                "Конечно! Чем могу помочь? Выберите функцию или "
                "задайте вопрос! 🤝"
            ),
            "функции": (
                "У нас есть много крутых функций! Посмотрите список ниже! 📋"
            ),
            "безопасность": (
                "Безопасность - это важно! Давайте настроим защиту! 🛡️"
            ),
            "семья": (
                "Защита семьи - наш приоритет! Покажу, как настроить! 👨‍👩‍👧‍👦"
            ),
            "спасибо": (
                "Пожалуйста! Рад помочь! Если что-то еще - обращайтесь! 😊"
            ),
            "пока": "До свидания! Берегите себя и будьте в безопасности! 👋",
        }

    def get_function_info(
        self, function_key: str, user_id: str = None
    ) -> Dict[str, Any]:
        """Получение информации о функции простым языком"""
        if function_key not in self.functions_database:
            return {"error": "Функция не найдена"}

        function = self.functions_database[function_key]
        user_profile = self.user_profiles.get(user_id)

        # Адаптируем объяснение под уровень пользователя
        if user_profile and user_profile.level == UserLevel.НОВИЧОК:
            explanation = self._simplify_explanation(function, "новичок")
        elif user_profile and user_profile.level == UserLevel.ЭКСПЕРТ:
            explanation = self._detailed_explanation(function, "эксперт")
        else:
            explanation = self._standard_explanation(function)

        return {
            "russian_name": function.russian_name,
            "icon": function.icon,
            "color": function.color,
            "explanation": explanation,
            "difficulty": function.difficulty,
            "importance": function.importance,
            "features": function.features,
        }

    def _simplify_explanation(
        self, function: SecurityFunction, level: str
    ) -> str:
        """Упрощенное объяснение для новичков"""
        explanations = {
            "temporal_analysis": (
                f"🕐 {function.russian_name} - это как умные часы для вашего "
                f"интернета! Он следит, когда вы обычно пользуетесь "
                f"телефоном, "
                f"и если заметит что-то странное (например, кто-то заходит в "
                f"ваш аккаунт ночью), сразу предупредит!"
            ),
            "threat_detection": (
                f"🛡️ {function.russian_name} - это как охранник для вашего "
                f"телефона! Он постоянно ищет вирусы и опасности, и если "
                f"что-то найдет, сразу заблокирует!"
            ),
            "family_protection": (
                f"👨‍👩‍👧‍👦 {function.russian_name} - это как няня для всей "
                f"семьи! Он следит, чтобы дети не попали на плохие сайты, "
                f"а взрослые были в безопасности!"
            ),
            "vpn_protection": (
                f"🔒 {function.russian_name} - это как невидимый плащ для "
                f"интернета! Он скрывает, что вы делаете в интернете, "
                f"чтобы никто не мог подсмотреть!"
            ),
            "antivirus": (
                f"💊 {function.russian_name} - это как врач для телефона! "
                f"Он лечит вирусы и не дает им заразить ваше устройство!"
            ),
        }
        return explanations.get(
            function.english_name.lower().replace(" ", "_"),
            f"🤖 {function.russian_name} - {function.for_users}",
        )

    def _standard_explanation(self, function: SecurityFunction) -> str:
        """Стандартное объяснение"""
        return (
            f"🤖 **{function.russian_name}**\n\n"
            f"**Что делает:** {function.what_it_does}\n\n"
            f"**От чего защищает:** {function.what_protects}\n\n"
            f"**Для пользователей:** {function.for_users}"
        )

    def _detailed_explanation(
        self, function: SecurityFunction, level: str
    ) -> str:
        """Подробное объяснение для экспертов"""
        return (
            f"🔬 **{function.russian_name}** "
            f"(Техническое название: {function.english_name})\n\n"
            f"**Описание:** {function.description}\n\n"
            f"**Функциональность:** {function.what_it_does}\n\n"
            f"**Защита от:** {function.what_protects}\n\n"
            f"**Пользовательский интерфейс:** {function.for_users}\n\n"
            f"**Возможности:**\n"
            + "\n".join([f"• {feature}" for feature in function.features])
        )

    def explain_function(self, function_key: str, user_id: str = None) -> str:
        """Объяснение функции пользователю"""
        function_info = self.get_function_info(function_key, user_id)

        if "error" in function_info:
            return f"❌ {function_info['error']}"

        # Добавляем эмоциональную реакцию
        emotion_response = self._get_emotional_response(user_id)

        return f"{emotion_response}\n\n{function_info['explanation']}"

    def _get_emotional_response(self, user_id: str = None) -> str:
        """Получение эмоциональной реакции"""
        if not user_id or user_id not in self.user_profiles:
            return random.choice(
                self.emotional_responses[EmotionType.СПОКОЙСТВИЕ]
            )

        user_profile = self.user_profiles[user_id]
        responses = self.emotional_responses.get(
            user_profile.current_emotion,
            self.emotional_responses[EmotionType.СПОКОЙСТВИЕ],
        )
        return random.choice(responses)

    def get_all_functions_simple(self) -> List[Dict[str, Any]]:
        """Получение всех функций простым языком"""
        functions_list = []

        for key, function in self.functions_database.items():
            functions_list.append(
                {
                    "key": key,
                    "russian_name": function.russian_name,
                    "icon": function.icon,
                    "color": function.color,
                    "category": function.category.value,
                    "difficulty": function.difficulty,
                    "importance": function.importance,
                    "simple_description": function.for_users,
                }
            )

        return functions_list

    def get_functions_by_category(
        self, category: FunctionCategory
    ) -> List[Dict[str, Any]]:
        """Получение функций по категории"""
        return [
            func
            for func in self.get_all_functions_simple()
            if func["category"] == category.value
        ]

    def get_recommended_functions(self, user_id: str) -> List[Dict[str, Any]]:
        """Получение рекомендуемых функций для пользователя"""
        if user_id not in self.user_profiles:
            return self.get_all_functions_simple()[:5]  # Первые 5 функций

        user_profile = self.user_profiles[user_id]

        # Простая логика рекомендаций
        if user_profile.level == UserLevel.НОВИЧОК:
            # Рекомендуем простые и важные функции
            return [
                func
                for func in self.get_all_functions_simple()
                if func["difficulty"] <= 2 and func["importance"] >= 4
            ]
        elif user_profile.level == UserLevel.ЭКСПЕРТ:
            # Рекомендуем сложные функции
            return [
                func
                for func in self.get_all_functions_simple()
                if func["difficulty"] >= 3
            ]
        else:
            # Стандартные рекомендации
            return [
                func
                for func in self.get_all_functions_simple()
                if func["importance"] >= 3
            ]

    def create_user_profile(self, user_id: str, name: str) -> UserProfile:
        """Создание профиля пользователя"""
        profile = UserProfile(
            user_id=user_id, name=name, level=UserLevel.НОВИЧОК
        )
        self.user_profiles[user_id] = profile
        return profile

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Получение профиля пользователя"""
        return self.user_profiles.get(user_id)

    def update_user_emotion(self, user_id: str, emotion: EmotionType):
        """Обновление эмоции пользователя"""
        if user_id in self.user_profiles:
            self.user_profiles[user_id].current_emotion = emotion

    def add_experience(self, user_id: str, points: int):
        """Добавление опыта пользователю"""
        if user_id in self.user_profiles:
            self.user_profiles[user_id].experience_points += points
            self._check_level_up(user_id)

    def _check_level_up(self, user_id: str):
        """Проверка повышения уровня"""
        profile = self.user_profiles[user_id]

        if (
            profile.experience_points >= 500
            and profile.level != UserLevel.МАСТЕР
        ):
            profile.level = UserLevel.МАСТЕР
            self._unlock_achievement(user_id, "мастер_защиты")
        elif (
            profile.experience_points >= 200
            and profile.level != UserLevel.ЭКСПЕРТ
        ):
            profile.level = UserLevel.ЭКСПЕРТ
            self._unlock_achievement(user_id, "эксперт_безопасности")
        elif (
            profile.experience_points >= 100
            and profile.level != UserLevel.ОПЫТНЫЙ
        ):
            profile.level = UserLevel.ОПЫТНЫЙ
        elif (
            profile.experience_points >= 50
            and profile.level != UserLevel.ПОЛЬЗОВАТЕЛЬ
        ):
            profile.level = UserLevel.ПОЛЬЗОВАТЕЛЬ

    def _unlock_achievement(self, user_id: str, achievement_key: str):
        """Разблокировка достижения"""
        if (
            user_id in self.user_profiles
            and achievement_key in self.achievements
        ):
            profile = self.user_profiles[user_id]
            if achievement_key not in profile.achievements:
                profile.achievements.append(achievement_key)
                achievement = self.achievements[achievement_key]
                self.add_experience(user_id, achievement["points"])
                return (
                    f"🎉 Поздравляем! Вы получили достижение "
                    f"'{achievement['name']}'!"
                )
        return None

    def get_quick_response(self, message: str) -> str:
        """Получение быстрого ответа (бот-режим)"""
        message_lower = message.lower().strip()

        # Поиск ключевых слов
        for key, response in self.quick_responses.items():
            if key in message_lower:
                return response

        # Если не найдено, возвращаем общий ответ
        return (
            "Не совсем понял, что вы имеете в виду. Попробуйте спросить "
            "по-другому или выберите функцию из списка! 🤔"
        )

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса агента"""
        return {
            "name": self.name,
            "status": "RUNNING" if self.is_active else "STOPPED",
            "total_functions": len(self.functions_database),
            "total_users": len(self.user_profiles),
            "created_at": self.created_at.isoformat(),
            "last_update": self.last_update.isoformat(),
        }


def main():
    """Тестирование MobileUserAIAgent"""
    print("🤖 Тестирование MobileUserAIAgent")
    print("=" * 50)

    # Создаем агента
    agent = MobileUserAIAgent()

    # Создаем тестового пользователя
    user_id = "test_user_123"
    agent.create_user_profile(user_id, "Тестовый Пользователь")

    # Тестируем объяснение функций
    print("\n📚 Тестирование объяснения функций:")
    print("-" * 30)

    test_functions = [
        "temporal_analysis",
        "threat_detection",
        "family_protection",
    ]

    for func_key in test_functions:
        print(f"\n🔍 Функция: {func_key}")
        explanation = agent.explain_function(func_key, user_id)
        print(explanation)
        print("-" * 50)

    # Тестируем быстрые ответы
    print("\n💬 Тестирование быстрых ответов:")
    print("-" * 30)

    test_messages = ["привет", "помощь", "функции", "спасибо"]

    for message in test_messages:
        response = agent.get_quick_response(message)
        print(f"Пользователь: {message}")
        print(f"Агент: {response}")
        print()

    # Тестируем получение всех функций
    print("\n📋 Все доступные функции:")
    print("-" * 30)

    all_functions = agent.get_all_functions_simple()
    for func in all_functions:
        print(
            f"{func['icon']} {func['russian_name']} - "
            f"{func['simple_description']}"
        )

    print(f"\n✅ Тестирование завершено! Всего функций: {len(all_functions)}")


if __name__ == "__main__":
    main()
