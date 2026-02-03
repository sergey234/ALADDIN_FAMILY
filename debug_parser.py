#!/usr/bin/env python3
"""
Диагностика парсера эндпоинтов
"""

import re

def test_parser(file_path):
    endpoints = []
    with open(file_path, 'r') as f:
        lines = f.readlines()

    current_method = None
    current_path = None

    for i, line in enumerate(lines):
        line = line.strip()

        if line.startswith('@app.'):
            print(f'Найден декоратор на строке {i+1}: {line}')

            if 'get(' in line:
                current_method = 'GET'
                # Ищем путь в скобках
                match = re.search(r'@app\.get\((.*?)\)', line)
                if match:
                    path_str = match.group(1).strip()
                    # Убираем кавычки
                    current_path = path_str.strip('"\'')

            elif 'post(' in line:
                current_method = 'POST'
                match = re.search(r'@app\.post\((.*?)\)', line)
                if match:
                    path_str = match.group(1).strip()
                    current_path = path_str.strip('"\'')

            elif 'put(' in line:
                current_method = 'PUT'
                match = re.search(r'@app\.put\((.*?)\)', line)
                if match:
                    path_str = match.group(1).strip()
                    current_path = path_str.strip('"\'')

            elif 'delete(' in line:
                current_method = 'DELETE'
                match = re.search(r'@app\.delete\((.*?)\)', line)
                if match:
                    path_str = match.group(1).strip()
                    current_path = path_str.strip('"\'')

            if current_path:
                print(f'  Извлечен путь: {current_path}')

        elif current_method and current_path and line.startswith('async def '):
            func_name = line.split('async def ')[1].split('(')[0].strip()
            endpoints.append((current_method, current_path, func_name))
            print(f'  Найдена функция: {func_name}')
            print(f'  ЗАФИКСИРОВАН ЭНДПОИНТ: {current_method} {current_path}')
            current_method = None
            current_path = None

            if len(endpoints) >= 10:  # Ограничим для теста
                break

    print(f'\nВсего найдено эндпоинтов: {len(endpoints)}')
    return endpoints

if __name__ == "__main__":
    test_parser('api_gateway_complete.py')