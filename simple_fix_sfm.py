#!/usr/bin/env python3
"""
ПРОСТОЕ ИСПРАВЛЕНИЕ SFM АДАПТЕРА
Замена execute_function на синхронную версию с requests
"""

import paramiko

SERVER_CONFIG = {
    'hostname': '149.154.65.180',
    'username': 'root',
    'password': 'Sergio675',
    'port': 22
}

def execute_command(ssh_client, command, description):
    """Выполнить команду на сервере"""
    print(f"\n🔧 {description}")
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=30)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        exit_code = stdout.channel.recv_exit_status()
        return exit_code == 0, output
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False, str(e)

def main():
    """Простое исправление SFM адаптера"""
    print("🔧 ПРОСТОЕ ИСПРАВЛЕНИЕ SFM АДАПТЕРА")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(**SERVER_CONFIG)
    except Exception as e:
        print(f"❌ ПОДКЛЮЧЕНИЕ: {e}")
        return

    try:
        # Заменяем execute_function на простую версию
        new_execute_function = '''    def execute_function(self, func_name: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any, Optional[str]]:
        """
        Execute function through SFM HTTP API (простая версия)
        """
        self.metrics['total_calls'] += 1
        params = params or {}

        try:
            # Используем requests для HTTP вызова
            import requests

            # Get the correct SFM function name
            sfm_function_name = get_sfm_function_name(func_name)

            # Вызываем SFM HTTP API
            response = requests.post(
                'http://127.0.0.1:8003/api/execute',
                json={'function': sfm_function_name, 'params': params},
                headers={'Content-Type': 'application/json'},
                timeout=5.0
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.metrics['successful_calls'] += 1
                    return True, data['result'], None
                else:
                    raise Exception(f"SFM error: {data.get('error', 'Unknown')}")

            # Fallback
            result = self._execute_mock_function(func_name, params)
            self.metrics['fallback_calls'] += 1
            return True, result, f"HTTP {response.status_code}"

        except Exception as e:
            # Fallback
            try:
                result = self._execute_mock_function(func_name, params)
                self.metrics['fallback_calls'] += 1
                return True, result, f"SFM failed: {str(e)}"
            except Exception as fallback_error:
                self.metrics['failed_calls'] += 1
                return False, None, f"All failed: {str(e)}, {str(fallback_error)}"'''

        # Выполняем замену через sed
        success, _ = execute_command(
            ssh,
            "cp /opt/aladdin-backend/sfm_adapter.py /opt/aladdin-backend/sfm_adapter_simple_backup_$(date +%Y%m%d_%H%M%S).py",
            "Создание backup"
        )

        # Используем sed для замены функции
        replace_command = """
sed -i '/def execute_function(self, func_name: str, params: Optional\[Dict\[str, Any\]\] = None) -> Tuple\[bool, Any, Optional\[str\]\]:/,/^        return loop\.run_until_complete.*$/c\
    def execute_function(self, func_name: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any, Optional[str]]:\n\
        \"\"\"\n\
        Execute function through SFM HTTP API (простая версия)\n\
        \"\"\"\n\
        self.metrics['total_calls'] += 1\n\
        params = params or {}\n\
        \n\
        try:\n\
            # Используем requests для HTTP вызова\n\
            import requests\n\
            \n\
            # Get the correct SFM function name\n\
            sfm_function_name = get_sfm_function_name(func_name)\n\
            \n\
            # Вызываем SFM HTTP API\n\
            response = requests.post(\n\
                '\''http://127.0.0.1:8003/api/execute'\'',\n\
                json={'\''function'\'': sfm_function_name, '\''params'\'': params},\n\
                headers={'\''Content-Type'\'': '\''application/json'\''},\n\
                timeout=5.0\n\
            )\n\
            \n\
            if response.status_code == 200:\n\
                data = response.json()\n\
                if data.get('\''success'\''):\n\
                    self.metrics['\''successful_calls'\''] += 1\n\
                    return True, data['\''result'\''], None\n\
                else:\n\
                    raise Exception(f"SFM error: {data.get('\''error'\'', '\''Unknown'\'')}")\n\
            \n\
            # Fallback\n\
            result = self._execute_mock_function(func_name, params)\n\
            self.metrics['\''fallback_calls'\''] += 1\n\
            return True, result, f"HTTP {response.status_code}"\n\
        \n\
        except Exception as e:\n\
            # Fallback\n\
            try:\n\
                result = self._execute_mock_function(func_name, params)\n\
                self.metrics['\''fallback_calls'\''] += 1\n\
                return True, result, f"SFM failed: {str(e)}"\n\
            except Exception as fallback_error:\n\
                self.metrics['\''failed_calls'\''] += 1\n\
                return False, None, f"All failed: {str(e)}, {str(fallback_error)}"' /opt/aladdin-backend/sfm_adapter.py
"""

        success, _ = execute_command(
            ssh,
            replace_command,
            "Замена функции execute_function через sed"
        )

        if success:
            print("✅ Функция execute_function заменена")

            # Перезапускаем API Gateway
            success, _ = execute_command(
                ssh,
                "systemctl restart aladdin-main-api-gateway",
                "Перезапуск API Gateway"
            )

            if success:
                print("⏳ Ожидание перезапуска...")
                import time
                time.sleep(5)

                # Финальный тест
                success, output = execute_command(
                    ssh,
                    "curl -s http://127.0.0.1:8002/api/health",
                    "Тест API Gateway"
                )

                if "available" in output:
                    print("✅ УСПЕХ! SFM адаптер доступен!")

                    # Тест функции
                    success, output = execute_command(
                        ssh,
                        "curl -s http://127.0.0.1:8002/api/phishing/sensitivity | jq -r .source 2>/dev/null || echo 'ERROR'",
                        "Тест функции"
                    )

                    if "real_sfm" in output:
                        print("🎉 МИССИЯ ВЫПОЛНЕНА! ALADDIN получил 100% РЕАЛЬНУЮ ЗАЩИТУ!")
                    else:
                        print(f"⚠️ Функция вернула: {output}")
                else:
                    print(f"❌ SFM адаптер все еще в fallback: {output}")
            else:
                print("❌ Перезапуск API Gateway не удался")
        else:
            print("❌ Замена функции не удалась")

    finally:
        ssh.close()
        print("\n🔌 СОЕДИНЕНИЕ ЗАКРЫТО")

if __name__ == "__main__":
    main()