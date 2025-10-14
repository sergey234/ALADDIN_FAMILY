#!/usr/bin/env python3
"""
Мастер настройки системы безопасности ALADDIN
Автоматическая настройка системы за 5 минут
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
import getpass

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))


class SetupWizard:
    """Мастер настройки системы ALADDIN"""

    def __init__(self):
        self.config = {}
        self.setup_type = None
        self.start_time = time.time()

    def print_header(self):
        """Вывод заголовка мастера"""
        print("=" * 60)
        print("🧙‍♂️ МАСТЕР НАСТРОЙКИ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
        print("=" * 60)
        print("Добро пожаловать! Этот мастер поможет вам настроить")
        print("систему безопасности ALADDIN за несколько минут.")
        print("=" * 60)
        print()

    def select_setup_type(self):
        """Выбор типа установки"""
        print("📋 ВЫБЕРИТЕ ТИП УСТАНОВКИ:")
        print()
        print("1. 🏠 Домашняя безопасность")
        print("   - Семейная защита")
        print("   - Родительский контроль")
        print("   - Защита детей")
        print()
        print("2. 🏢 Бизнес безопасность")
        print("   - Защита малого бизнеса")
        print("   - Управление пользователями")
        print("   - Сетевая безопасность")
        print()
        print("3. 🏭 Корпоративная безопасность")
        print("   - Enterprise функции")
        print("   - Zero Trust архитектура")
        print("   - Интеграции с SIEM")
        print()

        while True:
            try:
                choice = input("Введите номер (1-3): ").strip()
                if choice in ['1', '2', '3']:
                    self.setup_type = int(choice)
                    break
                else:
                    print("❌ Пожалуйста, введите 1, 2 или 3")
            except KeyboardInterrupt:
                print("\n\n❌ Установка отменена пользователем")
                sys.exit(1)

        print(f"\n✅ Выбран тип установки: {self.get_setup_type_name()}")
        print()

    def get_setup_type_name(self):
        """Получение названия типа установки"""
        types = {
            1: "Домашняя безопасность",
            2: "Бизнес безопасность",
            3: "Корпоративная безопасность"
        }
        return types.get(self.setup_type, "Неизвестно")

    def configure_basic_settings(self):
        """Настройка базовых параметров"""
        print("⚙️ НАСТРОЙКА БАЗОВЫХ ПАРАМЕТРОВ:")
        print()

        # Уровень безопасности
        print("🛡️ Уровень безопасности:")
        print("1. Стандартный (рекомендуется)")
        print("2. Высокий")
        print("3. Максимальный")

        while True:
            try:
                security_choice = input("Выберите уровень (1-3): ").strip()
                if security_choice in ['1', '2', '3']:
                    security_levels = {
                        '1': 'standard',
                        '2': 'high',
                        '3': 'maximum'
                    }
                    self.config['security_level'] = (
                        security_levels[security_choice]
                    )
                    break
                else:
                    print("❌ Пожалуйста, введите 1, 2 или 3")
            except KeyboardInterrupt:
                print("\n\n❌ Установка отменена пользователем")
                sys.exit(1)

        # Мобильная поддержка
        print("\n📱 Мобильная поддержка:")
        mobile_support = input(
            "Включить мобильную поддержку? (y/n): ").strip().lower()
        self.config['mobile_support'] = mobile_support in [
            'y', 'yes', 'да', 'д']

        # AI анализ
        print("\n🤖 AI анализ угроз:")
        ai_analysis = input("Включить AI анализ? (y/n): ").strip().lower()
        self.config['ai_analysis'] = ai_analysis in ['y', 'yes', 'да', 'д']

        print(f"\n✅ Базовые параметры настроены")
        print()

    def configure_family_settings(self):
        """Настройка семейных параметров"""
        if self.setup_type != 1:
            return

        print("👨‍👩‍👧‍👦 НАСТРОЙКА СЕМЕЙНЫХ ПАРАМЕТРОВ:")
        print()

        # Режим семьи
        self.config['family_mode'] = True

        # Родительский контроль
        print("👨‍👩‍👧‍👦 Родительский контроль:")
        parental_controls = input(
            "Включить родительский контроль? (y/n): ").strip().lower()
        self.config['parental_controls'] = parental_controls in [
            'y', 'yes', 'да', 'д']

        if self.config['parental_controls']:
            # Максимальное время экрана
            print("\n⏰ Максимальное время экрана (минуты в день):")
            while True:
                try:
                    screen_time = input(
                        "Введите время (по умолчанию 120): ").strip()
                    if not screen_time:
                        screen_time = 120
                    else:
                        screen_time = int(screen_time)
                    if screen_time > 0:
                        self.config['max_screen_time'] = screen_time
                        break
                    else:
                        print("❌ Время должно быть больше 0")
                except ValueError:
                    print("❌ Пожалуйста, введите число")
                except KeyboardInterrupt:
                    print("\n\n❌ Установка отменена пользователем")
                    sys.exit(1)

            # Время отхода ко сну
            print("\n🌙 Время отхода ко сну (HH:MM):")
            while True:
                bedtime = input("Введите время (по умолчанию 21:00): ").strip()
                if not bedtime:
                    bedtime = "21:00"
                if self.validate_time(bedtime):
                    self.config['bedtime'] = bedtime
                    break
                else:
                    print("❌ Неверный формат времени. Используйте HH:MM")

        # Защита детей
        print("\n👶 Защита детей:")
        child_protection = input(
            "Включить защиту детей? (y/n): ").strip().lower()
        self.config['child_protection'] = child_protection in [
            'y', 'yes', 'да', 'д']

        if self.config['child_protection']:
            # Возрастные ограничения
            print("\n🔞 Возрастные ограничения:")
            age_restrictions = input(
                "Включить возрастные ограничения? (y/n): ").strip().lower()
            self.config['age_restrictions'] = age_restrictions in [
                'y', 'yes', 'да', 'д']

            # Отслеживание местоположения
            print("\n📍 Отслеживание местоположения:")
            location_tracking = input(
                "Включить отслеживание? (y/n): ").strip().lower()
            self.config['location_tracking'] = location_tracking in [
                'y', 'yes', 'да', 'д']

        print(f"\n✅ Семейные параметры настроены")
        print()

    def configure_business_settings(self):
        """Настройка бизнес параметров"""
        if self.setup_type not in [2, 3]:
            return

        print("🏢 НАСТРОЙКА БИЗНЕС ПАРАМЕТРОВ:")
        print()

        # Режим бизнеса
        self.config['business_mode'] = True

        # Управление пользователями
        print("👥 Управление пользователями:")
        user_management = input(
            "Включить управление пользователями? (y/n): ").strip().lower()
        self.config['user_management'] = user_management in [
            'y', 'yes', 'да', 'д']

        if self.config['user_management']:
            # Политика паролей
            print("\n🔐 Политика паролей:")
            print("1. Стандартная (8 символов)")
            print("2. Строгая (12 символов)")
            print("3. Максимальная (16 символов)")

            while True:
                try:
                    password_choice = input(
                        "Выберите политику (1-3): ").strip()
                    if password_choice in ['1', '2', '3']:
                        password_policies = {
                            '1': {'min_length': 8, 'require_special': False},
                            '2': {'min_length': 12, 'require_special': True},
                            '3': {'min_length': 16, 'require_special': True}
                        }
                        self.config['password_policy'] = (
                            password_policies[password_choice]
                        )
                        break
                    else:
                        print("❌ Пожалуйста, введите 1, 2 или 3")
                except KeyboardInterrupt:
                    print("\n\n❌ Установка отменена пользователем")
                    sys.exit(1)

        # Сетевая безопасность
        print("\n🌐 Сетевая безопасность:")
        network_security = input(
            "Включить сетевую безопасность? (y/n): ").strip().lower()
        self.config['network_security'] = network_security in [
            'y', 'yes', 'да', 'д']

        if self.config['network_security']:
            # Firewall
            print("\n🔥 Firewall:")
            firewall = input("Включить firewall? (y/n): ").strip().lower()
            self.config['firewall'] = firewall in ['y', 'yes', 'да', 'д']

            # VPN
            print("\n🔒 VPN:")
            vpn = input("Включить VPN? (y/n): ").strip().lower()
            self.config['vpn'] = vpn in ['y', 'yes', 'да', 'д']

        # Соответствие стандартам
        if self.setup_type == 3:
            print("\n📋 Соответствие стандартам:")
            gdpr = input("Включить GDPR? (y/n): ").strip().lower()
            self.config['gdpr'] = gdpr in ['y', 'yes', 'да', 'д']

            iso27001 = input("Включить ISO 27001? (y/n): ").strip().lower()
            self.config['iso27001'] = iso27001 in ['y', 'yes', 'да', 'д']

        print(f"\n✅ Бизнес параметры настроены")
        print()

    def configure_enterprise_settings(self):
        """Настройка корпоративных параметров"""
        if self.setup_type != 3:
            return

        print("🏭 НАСТРОЙКА КОРПОРАТИВНЫХ ПАРАМЕТРОВ:")
        print()

        # Режим корпорации
        self.config['enterprise_mode'] = True

        # Zero Trust
        print("🔐 Zero Trust архитектура:")
        zero_trust = input("Включить Zero Trust? (y/n): ").strip().lower()
        self.config['zero_trust'] = zero_trust in ['y', 'yes', 'да', 'д']

        if self.config['zero_trust']:
            # Проверка устройств
            print("\n📱 Проверка устройств:")
            device_verification = input(
                "Включить проверку устройств? (y/n): ").strip().lower()
            self.config['device_verification'] = device_verification in [
                'y', 'yes', 'да', 'д']

            # Непрерывный мониторинг
            print("\n👁️ Непрерывный мониторинг:")
            continuous_monitoring = input(
                "Включить непрерывный мониторинг? (y/n): ").strip().lower()
            self.config['continuous_monitoring'] = continuous_monitoring in [
                'y', 'yes', 'да', 'д']

        # Продвинутая защита от угроз
        print("\n🛡️ Продвинутая защита от угроз:")
        advanced_threat_protection = input(
            "Включить продвинутую защиту? (y/n): "
        ).strip().lower()
        self.config['advanced_threat_protection'] = (
            advanced_threat_protection in ['y', 'yes', 'да', 'д']
        )

        if self.config['advanced_threat_protection']:
            # AI анализ
            print("\n🤖 AI анализ:")
            ai_analysis = input("Включить AI анализ? (y/n): ").strip().lower()
            self.config['ai_analysis'] = ai_analysis in ['y', 'yes', 'да', 'д']

            # Анализ поведения
            print("\n🧠 Анализ поведения:")
            behavioral_analysis = input(
                "Включить анализ поведения? (y/n): ").strip().lower()
            self.config['behavioral_analysis'] = behavioral_analysis in [
                'y', 'yes', 'да', 'д']

        # Интеграции
        print("\n🔗 Интеграции:")
        siem = input("Включить интеграцию с SIEM? (y/n): ").strip().lower()
        self.config['siem_integration'] = siem in ['y', 'yes', 'да', 'д']

        ldap = input("Включить интеграцию с LDAP? (y/n): ").strip().lower()
        self.config['ldap_integration'] = ldap in ['y', 'yes', 'да', 'д']

        print(f"\n✅ Корпоративные параметры настроены")
        print()

    def configure_notifications(self):
        """Настройка уведомлений"""
        print("📧 НАСТРОЙКА УВЕДОМЛЕНИЙ:")
        print()

        # Email уведомления
        print("📧 Email уведомления:")
        email_notifications = input(
            "Включить email уведомления? (y/n): ").strip().lower()
        self.config['email_notifications'] = email_notifications in [
            'y', 'yes', 'да', 'д']

        if self.config['email_notifications']:
            email = input("Введите email адрес: ").strip()
            if self.validate_email(email):
                self.config['email_address'] = email
            else:
                print("❌ Неверный формат email")
                self.config['email_notifications'] = False

        # SMS уведомления
        print("\n📱 SMS уведомления:")
        sms_notifications = input(
            "Включить SMS уведомления? (y/n): ").strip().lower()
        self.config['sms_notifications'] = sms_notifications in [
            'y', 'yes', 'да', 'д']

        if self.config['sms_notifications']:
            phone = input("Введите номер телефона: ").strip()
            if self.validate_phone(phone):
                self.config['phone_number'] = phone
            else:
                print("❌ Неверный формат номера телефона")
                self.config['sms_notifications'] = False

        # Push уведомления
        print("\n🔔 Push уведомления:")
        push_notifications = input(
            "Включить push уведомления? (y/n): ").strip().lower()
        self.config['push_notifications'] = push_notifications in [
            'y', 'yes', 'да', 'д']

        print(f"\n✅ Уведомления настроены")
        print()

    def configure_admin_user(self):
        """Настройка администратора"""
        print("👤 НАСТРОЙКА АДМИНИСТРАТОРА:")
        print()

        # Имя пользователя
        print("👤 Имя пользователя администратора:")
        while True:
            username = input("Введите имя пользователя: ").strip()
            if username and len(username) >= 3:
                self.config['admin_username'] = username
                break
            else:
                print("❌ Имя пользователя должно содержать минимум 3 символа")

        # Пароль
        print("\n🔐 Пароль администратора:")
        while True:
            password = getpass.getpass("Введите пароль: ")
            if len(password) >= 8:
                confirm_password = getpass.getpass("Подтвердите пароль: ")
                if password == confirm_password:
                    self.config['admin_password'] = password
                    break
                else:
                    print("❌ Пароли не совпадают")
            else:
                print("❌ Пароль должен содержать минимум 8 символов")

        # Email администратора
        print("\n📧 Email администратора:")
        while True:
            email = input("Введите email (необязательно): ").strip()
            if not email:
                break
            elif self.validate_email(email):
                self.config['admin_email'] = email
                break
            else:
                print("❌ Неверный формат email")

        print(f"\n✅ Администратор настроен")
        print()

    def validate_time(self, time_str):
        """Валидация времени"""
        try:
            time.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False

    def validate_email(self, email):
        """Валидация email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        """Валидация номера телефона"""
        import re
        pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(pattern, phone) is not None

    def save_configuration(self):
        """Сохранение конфигурации"""
        print("💾 СОХРАНЕНИЕ КОНФИГУРАЦИИ:")
        print()

        try:
            # Создаем директорию конфигурации
            config_dir = Path('config')
            config_dir.mkdir(exist_ok=True)

            # Сохраняем конфигурацию
            config_file = config_dir / 'setup_config.json'
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            print(f"✅ Конфигурация сохранена в {config_file}")

            # Применяем конфигурацию к системе
            self.apply_configuration()

        except Exception as e:
            print(f"❌ Ошибка сохранения конфигурации: {e}")
            return False

        return True

    def apply_configuration(self):
        """Применение конфигурации к системе"""
        print("\n🔧 ПРИМЕНЕНИЕ КОНФИГУРАЦИИ:")
        print()

        try:
            from core.configuration import ConfigurationManager

            # Создаем менеджер конфигурации
            config_manager = ConfigurationManager()

            # Применяем настройки
            for key, value in self.config.items():
                config_manager.set_configuration(key, value)

            print("✅ Конфигурация применена к системе")

            # Создаем администратора
            if 'admin_username' in self.config:
                self.create_admin_user()

            # Запускаем тест
            self.run_initial_test()

        except Exception as e:
            print(f"❌ Ошибка применения конфигурации: {e}")

    def create_admin_user(self):
        """Создание пользователя администратора"""
        try:
            from security.authentication import AuthenticationManager

            auth_manager = AuthenticationManager()
            auth_manager.create_user(
                username=self.config['admin_username'],
                password=self.config['admin_password'],
                role='admin',
                email=self.config.get('admin_email', '')
            )

            print("✅ Пользователь администратора создан")

        except Exception as e:
            print(f"❌ Ошибка создания администратора: {e}")

    def run_initial_test(self):
        """Запуск начального теста"""
        print("\n🧪 ЗАПУСК НАЧАЛЬНОГО ТЕСТА:")
        print()

        try:
            # Запускаем ультра-быстрый тест
            import subprocess
            result = subprocess.run([
                'python3', 'scripts/ultra_fast_test.py'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print("✅ Начальный тест пройден успешно")
                print("✅ Система готова к использованию")
            else:
                print("❌ Начальный тест не пройден")
                print("❌ Проверьте конфигурацию")

        except Exception as e:
            print(f"❌ Ошибка запуска теста: {e}")

    def show_summary(self):
        """Показ сводки настройки"""
        print("\n" + "=" * 60)
        print("📊 СВОДКА НАСТРОЙКИ")
        print("=" * 60)

        setup_time = time.time() - self.start_time

        print(f"Тип установки: {self.get_setup_type_name()}")
        print(f"Время настройки: {setup_time:.1f} секунд")
        print(f"Настроено параметров: {len(self.config)}")
        print()

        print("📋 НАСТРОЕННЫЕ ПАРАМЕТРЫ:")
        for key, value in self.config.items():
            if 'password' not in key.lower():
                print(f"  ✅ {key}: {value}")

        print()
        print("🎯 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
        print("=" * 60)

    def run(self):
        """Запуск мастера настройки"""
        try:
            self.print_header()
            self.select_setup_type()
            self.configure_basic_settings()
            self.configure_family_settings()
            self.configure_business_settings()
            self.configure_enterprise_settings()
            self.configure_notifications()
            self.configure_admin_user()

            if self.save_configuration():
                self.show_summary()
                return True
            else:
                print("❌ Ошибка настройки системы")
                return False

        except KeyboardInterrupt:
            print("\n\n❌ Установка отменена пользователем")
            return False
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            return False


def main():
    """Главная функция"""
    wizard = SetupWizard()
    success = wizard.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
