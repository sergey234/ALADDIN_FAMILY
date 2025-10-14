#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERACTIVE ALADDIN SECURITY DEMO
Интерактивная демонстрация системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class InteractiveSecurityDemo:
    def __init__(self, project_root="/Users/sergejhlystov/ALADDIN_NEW"):
        self.project_root = Path(project_root)
        self.sfm_dir = self.project_root / "data" / "sfm"
        self.registry_file = self.sfm_dir / "data" / "sfm" / "function_registry.json"
        
        # Угрозы для выбора
        self.threats = {
            "1": {
                "name": "Фишинг в WhatsApp",
                "type": "phishing",
                "message": "🎁 Поздравляем! Вы выиграли iPhone! Перейдите по ссылке: bit.ly/fake123",
                "source": "WhatsApp",
                "risk_level": "high",
                "description": "Подозрительное сообщение с поддельной ссылкой"
            },
            "2": {
                "name": "Вредоносное ПО",
                "type": "malware",
                "message": "⚠️ Ваш компьютер заражен! Скачайте антивирус: virus-cleaner.exe",
                "source": "Email",
                "risk_level": "critical",
                "description": "Поддельный антивирус с вредоносным кодом"
            },
            "3": {
                "name": "Игровое мошенничество",
                "type": "gaming_fraud",
                "message": "🎮 Получите 1000 монет бесплатно! Введите данные карты:",
                "source": "Gaming App",
                "risk_level": "high",
                "description": "Попытка кражи данных банковской карты"
            },
            "4": {
                "name": "Социальная инженерия",
                "type": "social_engineering",
                "message": "👨‍💼 Это IT отдел. Ваш аккаунт взломан! Срочно смените пароль:",
                "source": "Telegram",
                "risk_level": "medium",
                "description": "Поддельное уведомление от IT отдела"
            },
            "5": {
                "name": "Случайная угроза",
                "type": "random",
                "message": "🎲 Выбираю случайную угрозу...",
                "source": "Random",
                "risk_level": "random",
                "description": "Система выберет случайную угрозу для демонстрации"
            }
        }
        
        # Функции защиты
        self.protection_functions = {
            "phishing": ["MessageBlocker", "ParentNotifier", "LogWriter", "ThreatAnalyzer"],
            "malware": ["FileScanner", "ParentNotifier", "LogWriter", "SystemProtector"],
            "gaming_fraud": ["PaymentBlocker", "ParentNotifier", "LogWriter", "GamingProtector"],
            "social_engineering": ["MessageBlocker", "ParentNotifier", "LogWriter", "BehaviorAnalyzer"],
            "random": ["UniversalBlocker", "ParentNotifier", "LogWriter", "ThreatAnalyzer"]
        }

    def show_menu(self) -> None:
        """Показ меню выбора угрозы"""
        print("🎬 ИНТЕРАКТИВНАЯ ДЕМОНСТРАЦИЯ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
        print("=" * 70)
        print("Выберите тип угрозы для демонстрации:")
        print()
        
        for key, threat in self.threats.items():
            print(f"  {key}. {threat['name']}")
            print(f"     📝 {threat['description']}")
            print(f"     ⚠️ Уровень риска: {threat['risk_level'].upper()}")
            print()
        
        print("  0. Выход")
        print("=" * 70)

    def get_user_choice(self) -> str:
        """Получение выбора пользователя"""
        while True:
            try:
                choice = input("Введите номер угрозы (0-5): ").strip()
                if choice in self.threats or choice == "0":
                    return choice
                else:
                    print("❌ Неверный выбор! Попробуйте снова.")
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                return "0"

    def load_sfm_registry(self) -> Dict:
        """Загрузка реестра SFM"""
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("functions", {})
        except Exception as e:
            print(f"❌ Ошибка загрузки реестра: {e}")
            return {}

    def simulate_threat_detection(self, threat: Dict) -> None:
        """Симуляция обнаружения угрозы"""
        print(f"🔍 {threat['source']} BOT: Обнаружил подозрительное сообщение!")
        print(f"   📱 Сообщение: {threat['message']}")
        print(f"   ⚠️ Уровень риска: {threat['risk_level'].upper()}")
        time.sleep(1.5)

    def simulate_ai_analysis(self, threat: Dict) -> None:
        """Симуляция AI анализа"""
        print(f"🤖 {threat['type'].upper()} AGENT: Анализирую угрозу...")
        time.sleep(1)
        print(f"   🔍 Тип угрозы: {threat['type']}")
        print(f"   🧠 Анализ завершен: {threat['type'].upper()} обнаружен!")
        print(f"   ⚡ Решение: БЛОКИРОВАТЬ И УВЕДОМИТЬ!")
        time.sleep(1.5)

    def simulate_sfm_request(self, threat: Dict) -> List[str]:
        """Симуляция запроса к SFM"""
        print(f"⚙️ SFM: Получаю запрос на защиту от {threat['type']}")
        functions_needed = self.protection_functions.get(threat['type'], [])
        print(f"   🎯 Нужны функции: {', '.join(functions_needed)}")
        time.sleep(1)
        return functions_needed

    def check_function_status(self, function_name: str, registry: Dict) -> Dict:
        """Проверка статуса функции в реестре"""
        # Ищем функцию в реестре
        for func_id, func_data in registry.items():
            if func_data.get('name') == function_name:
                return {
                    "found": True,
                    "status": func_data.get('status', 'unknown'),
                    "function_id": func_id,
                    "data": func_data
                }
        
        # Если не найдена, создаем симуляцию
        statuses = ['active', 'sleeping', 'disabled']
        status = random.choice(statuses)
        return {
            "found": False,
            "status": status,
            "function_id": f"sim_{function_name.lower()}",
            "data": {"name": function_name, "status": status}
        }

    def simulate_sfm_activation(self, functions: List[str], registry: Dict) -> None:
        """Симуляция активации функций через SFM"""
        print(f"📋 РЕЕСТР: Проверяю статус функций...")
        time.sleep(1)
        
        for function in functions:
            status_info = self.check_function_status(function, registry)
            
            if status_info["found"]:
                print(f"   ✅ {function}: найдена в реестре, статус: {status_info['status']}")
            else:
                print(f"   🔍 {function}: не найдена в реестре, симулирую статус: {status_info['status']}")
            
            time.sleep(0.5)
        
        print(f"\n⚙️ SFM: Активирую нужные функции...")
        time.sleep(1)
        
        for function in functions:
            status_info = self.check_function_status(function, registry)
            if status_info["status"] == "sleeping":
                print(f"   🔄 {function}: ПРОБУЖДАЮ из спящего режима...")
                time.sleep(0.5)
                print(f"   ✅ {function}: АКТИВИРОВАНА!")
            elif status_info["status"] == "active":
                print(f"   ✅ {function}: уже активна, готова к работе!")
            else:
                print(f"   ⚠️ {function}: отключена, активирую принудительно...")
                time.sleep(0.5)
                print(f"   ✅ {function}: ПРИНУДИТЕЛЬНО АКТИВИРОВАНА!")

    def simulate_protection_execution(self, functions: List[str], threat: Dict) -> None:
        """Симуляция выполнения защитных функций"""
        print(f"\n🛡️ ЗАЩИТНЫЕ ФУНКЦИИ: Выполняю защиту...")
        time.sleep(1)
        
        for function in functions:
            print(f"   🔧 {function}: ", end="")
            time.sleep(0.5)
            
            if "Blocker" in function:
                print("БЛОКИРУЮ угрозу!")
            elif "Notifier" in function:
                print("УВЕДОМЛЯЮ родителей!")
            elif "Log" in function:
                print("ЗАПИСЫВАЮ в журнал безопасности!")
            elif "Analyzer" in function:
                print("АНАЛИЗИРУЮ поведение!")
            elif "Scanner" in function:
                print("СКАНИРУЮ систему на угрозы!")
            elif "Protector" in function:
                print("ЗАЩИЩАЮ систему!")
            else:
                print("ВЫПОЛНЯЮ защитные действия!")
            
            time.sleep(0.5)

    def simulate_result(self, threat: Dict) -> None:
        """Симуляция результата защиты"""
        print(f"\n✅ РЕЗУЛЬТАТ ЗАЩИТЫ:")
        print(f"   🛡️ Угроза нейтрализована: {threat['type'].upper()}")
        print(f"   👶 Ребенок защищен от: {threat['message'][:50]}...")
        print(f"   👨‍👩‍👧‍👦 Родители уведомлены о попытке атаки")
        print(f"   📊 Действия записаны в журнал безопасности")
        print(f"   🔒 Система продолжает мониторинг")
        print(f"   ⏰ Время реакции: {random.randint(50, 200)} мс")

    def run_demo_for_threat(self, threat: Dict) -> None:
        """Запуск демонстрации для выбранной угрозы"""
        print(f"\n🎯 ДЕМОНСТРАЦИЯ: {threat['name']}")
        print("=" * 50)
        
        # Загружаем реестр SFM
        print("📋 Загружаю реестр SFM...")
        registry = self.load_sfm_registry()
        print(f"   ✅ Загружено {len(registry)} функций из реестра")
        time.sleep(1)
        
        # Шаг 1: Обнаружение угрозы
        print("\n1️⃣ ОБНАРУЖЕНИЕ УГРОЗЫ:")
        self.simulate_threat_detection(threat)
        
        # Шаг 2: AI анализ
        print(f"\n2️⃣ AI АНАЛИЗ:")
        self.simulate_ai_analysis(threat)
        
        # Шаг 3: Запрос к SFM
        print(f"\n3️⃣ ЗАПРОС К SFM:")
        functions_needed = self.simulate_sfm_request(threat)
        
        # Шаг 4: Проверка и активация функций
        print(f"\n4️⃣ АКТИВАЦИЯ ФУНКЦИЙ:")
        self.simulate_sfm_activation(functions_needed, registry)
        
        # Шаг 5: Выполнение защиты
        print(f"\n5️⃣ ВЫПОЛНЕНИЕ ЗАЩИТЫ:")
        self.simulate_protection_execution(functions_needed, threat)
        
        # Шаг 6: Результат
        print(f"\n6️⃣ РЕЗУЛЬТАТ:")
        self.simulate_result(threat)
        
        # Итоговая статистика
        print(f"\n📊 СТАТИСТИКА ДЕМОНСТРАЦИИ:")
        print(f"   🎯 Тип угрозы: {threat['type']}")
        print(f"   🔧 Активировано функций: {len(functions_needed)}")
        print(f"   ⚡ Время реакции: < 1 секунды")
        print(f"   🛡️ Уровень защиты: МАКСИМАЛЬНЫЙ")
        print(f"   ✅ Статус: УГРОЗА НЕЙТРАЛИЗОВАНА")
        
        print(f"\n🏆 СИСТЕМА БЕЗОПАСНОСТИ ALADDIN РАБОТАЕТ ИДЕАЛЬНО!")
        print("=" * 50)

    def run_interactive_demo(self) -> None:
        """Запуск интерактивной демонстрации"""
        while True:
            self.show_menu()
            choice = self.get_user_choice()
            
            if choice == "0":
                print("👋 До свидания! Спасибо за использование ALADDIN!")
                break
            
            if choice == "5":
                # Случайная угроза
                random_threats = [t for k, t in self.threats.items() if k != "5"]
                threat = random.choice(random_threats)
                threat["name"] = "Случайная угроза"
                threat["description"] = "Система выбрала случайную угрозу"
            else:
                threat = self.threats[choice]
            
            self.run_demo_for_threat(threat)
            
            # Предложение повторить
            print("\n🔄 Хотите протестировать другую угрозу?")
            repeat = input("Нажмите Enter для продолжения или 'q' для выхода: ").strip().lower()
            if repeat == 'q':
                print("👋 До свидания!")
                break

def main():
    """Главная функция"""
    demo = InteractiveSecurityDemo()
    demo.run_interactive_demo()

if __name__ == "__main__":
    main()