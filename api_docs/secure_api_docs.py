#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive API Documentation - Интерактивная документация API
Система безопасности ALADDIN
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import hmac

# FastAPI и связанные модули
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# JWT для аутентификации
import jwt
from cryptography.fernet import Fernet

# Для сканирования API endpoints
import inspect
import importlib.util
import re

class InteractiveAPIDocs:
    """Интерактивная документация API системы ALADDIN"""
    
    def __init__(self, config_path: str = "api_docs/security_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.app = self._create_app()
        self.api_endpoints = []
        self._scan_api_endpoints()
        
    def _load_config(self) -> Dict:
        """Загрузка конфигурации безопасности"""
        default_config = {
            "jwt": {
                "secret_key": "aladdin_security_super_secret_key_2024",
                "algorithm": "HS256",
                "expiration_hours": 24
            },
            "cors": {
                "allowed_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["GET", "POST", "PUT", "DELETE"],
                "allow_headers": ["*"]
            },
            "access": {
                "allowed_roles": ["admin", "developer", "security_analyst"],
                "allowed_users": ["admin", "developer", "security"]
            },
            "testing": {
                "allowed_endpoints": [
                    "/api/security/threat-detection",
                    "/api/security/behavioral-analysis", 
                    "/api/security/incident-response",
                    "/api/security/password-security",
                    "/api/security/network-monitoring",
                    "/api/security/data-protection"
                ],
                "rate_limit": {
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000
                }
            },
            "api": {
                "base_url": "http://localhost:8006",
                "title": "ALADDIN Security System API",
                "version": "1.0.0",
                "description": "Интерактивная документация API системы безопасности ALADDIN"
            },
            "flask": {
                "secret_key": "aladdin_docs_secret_key_2024",
                "host": "0.0.0.0",
                "port": 8008
            },
            "auditing": {
                "enabled": True,
                "log_file": "logs/api_docs_audit.log"
            },
            "security": {
                "mask_sensitive_data": True,
                "require_https": False,
                "input_validation": True
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                import yaml
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
        except Exception as e:
            self.logger.warning(f"Не удалось загрузить конфигурацию: {e}, используются настройки по умолчанию")
        
        return default_config
        
    def _setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/api_docs.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(self.__class__.__name__)
        
    def _create_app(self) -> FastAPI:
        """Создание FastAPI приложения"""
        app = FastAPI(
            title=self.config['api']['title'],
            description=self.config['api']['description'],
            version=self.config['api']['version'],
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        
        # CORS настройки
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config['cors']['allowed_origins'],
            allow_credentials=self.config['cors']['allow_credentials'],
            allow_methods=self.config['cors']['allow_methods'],
            allow_headers=self.config['cors']['allow_headers'],
        )
        
        # Статические файлы
        app.mount("/static", StaticFiles(directory="api_docs/static"), name="static")
        
        # Шаблоны
        templates = Jinja2Templates(directory="api_docs/templates")
        
        # Аутентификация
        security = HTTPBearer()
        
        @app.get("/", response_class=HTMLResponse)
        async def interactive_docs(request: Request):
            """Главная страница интерактивной документации"""
            return templates.TemplateResponse("api_docs.html", {
                "request": request,
                "title": self.config['api']['title'],
                "endpoints": self.api_endpoints
            })
        
        @app.get("/api/endpoints")
        async def get_api_endpoints(credentials: HTTPAuthorizationCredentials = Depends(security)):
            """Получение списка всех API endpoints"""
            if not self._verify_token(credentials.credentials):
                raise HTTPException(status_code=401, detail="Неверный токен")
            
            return {
                "endpoints": self.api_endpoints,
                "total_count": len(self.api_endpoints),
                "timestamp": datetime.now().isoformat()
            }
        
        @app.post("/api/test")
        async def test_api_endpoint(
            endpoint: str,
            method: str,
            params: Dict[str, Any],
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Тестирование API endpoint"""
            if not self._verify_token(credentials.credentials):
                raise HTTPException(status_code=401, detail="Неверный токен")
            
            if not self._is_endpoint_allowed(endpoint):
                raise HTTPException(status_code=403, detail="Endpoint не разрешен для тестирования")
            
            # Аудит запроса
            self._audit_request(endpoint, method, params, credentials.credentials)
            
            return await self._test_endpoint(endpoint, method, params)
        
        @app.get("/api/docs/openapi.json")
        async def get_openapi_spec():
            """Получение OpenAPI спецификации"""
            return self._generate_openapi_spec()
        
        return app
        
    def _verify_token(self, token: str) -> bool:
        """Проверка JWT токена"""
        try:
            payload = jwt.decode(
                token,
                self.config['jwt']['secret_key'],
                algorithms=[self.config['jwt']['algorithm']]
            )
            
            # Проверка срока действия
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                return False
            
            # Проверка прав доступа
            if payload.get('role') not in self.config['access']['allowed_roles']:
                return False
            
            return True
            
        except jwt.InvalidTokenError:
            return False
    
    def _is_endpoint_allowed(self, endpoint: str) -> bool:
        """Проверка разрешения тестирования endpoint"""
        allowed_endpoints = self.config['testing']['allowed_endpoints']
        return endpoint in allowed_endpoints
    
    def _audit_request(self, endpoint: str, method: str, params: Dict, token: str):
        """Аудит запроса"""
        if not self.config['auditing']['enabled']:
            return
            
        try:
            # Декодирование токена для получения информации о пользователе
            payload = jwt.decode(token, self.config['jwt']['secret_key'], algorithms=[self.config['jwt']['algorithm']])
            user = payload.get('user', 'unknown')
            role = payload.get('role', 'unknown')
        except:
            user = 'unknown'
            role = 'unknown'
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "role": role,
            "endpoint": endpoint,
            "method": method,
            "params": params if not self.config['security']['mask_sensitive_data'] else "MASKED"
        }
        
        # Запись в лог аудита
        os.makedirs("logs", exist_ok=True)
        with open(self.config['auditing']['log_file'], 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
    
    async def _test_endpoint(self, endpoint: str, method: str, params: Dict) -> Dict:
        """Тестирование API endpoint"""
        try:
            import httpx
            
            # Подготовка URL
            url = f"{self.config['api']['base_url']}{endpoint}"
            
            # Выполнение запроса
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, json=params)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=params)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, params=params)
                else:
                    raise HTTPException(status_code=400, detail="Неподдерживаемый HTTP метод")
                
                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    "request_url": str(response.url),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "status_code": 500,
                "timestamp": datetime.now().isoformat()
            }
    
    def _scan_api_endpoints(self):
        """Сканирование API endpoints в системе"""
        self.logger.info("Сканирование API endpoints...")
        
        # Поиск в директории security/microservices
        api_dirs = [
            "security/microservices",
            "security/managers", 
            "core",
            "scripts"
        ]
        
        for api_dir in api_dirs:
            if os.path.exists(api_dir):
                for root, dirs, files in os.walk(api_dir):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            self._parse_api_file(file_path)
        
        self.logger.info(f"Найдено {len(self.api_endpoints)} API endpoints")
    
    def _parse_api_file(self, file_path: str):
        """Парсинг файла API для извлечения endpoints"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Поиск FastAPI endpoints
            patterns = [
                r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',  # FastAPI
                r'@route\s*\(\s*["\']([^"\']+)["\']',  # Flask
                r'def\s+(\w+)\s*\([^)]*\):\s*#\s*API:\s*([^\n]+)',  # Комментарии API
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:  # FastAPI
                        method, path = match
                        method = method.upper()
                    else:  # Flask или комментарии
                        path = match[0] if isinstance(match, tuple) else match
                        method = "GET"  # По умолчанию
                    
                    endpoint = {
                        "method": method,
                        "path": path,
                        "summary": f"{method} {path}",
                        "description": f"API endpoint для {method} запросов к {path}",
                        "file": file_path,
                        "parameters": self._extract_parameters(content, path),
                        "responses": {
                            "200": {"description": "Успешный ответ"},
                            "401": {"description": "Не авторизован"},
                            "403": {"description": "Доступ запрещен"},
                            "500": {"description": "Внутренняя ошибка сервера"}
                        }
                    }
                    
                    # Добавление специфических описаний для известных endpoints
                    endpoint = self._enhance_endpoint_description(endpoint)
                    
                    self.api_endpoints.append(endpoint)
                    
        except Exception as e:
            self.logger.error(f"Ошибка парсинга файла {file_path}: {e}")
    
    def _extract_parameters(self, content: str, path: str) -> List[Dict]:
        """Извлечение параметров из кода"""
        parameters = []
        
        # Поиск параметров в пути
        path_params = re.findall(r'\{(\w+)\}', path)
        for param in path_params:
            parameters.append({
                "name": param,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": f"Параметр пути {param}"
            })
        
        return parameters
    
    def _enhance_endpoint_description(self, endpoint: Dict) -> Dict:
        """Улучшение описания endpoint на основе пути"""
        path = endpoint["path"]
        method = endpoint["method"]
        
        # Специфические описания для известных endpoints
        descriptions = {
            "/api/security/threat-detection": {
                "summary": "Детекция угроз безопасности",
                "description": "Анализ и детекция потенциальных угроз безопасности в системе"
            },
            "/api/security/behavioral-analysis": {
                "summary": "Анализ поведения пользователей",
                "description": "Анализ поведенческих паттернов для выявления аномалий"
            },
            "/api/security/incident-response": {
                "summary": "Реагирование на инциденты",
                "description": "Обработка и реагирование на инциденты безопасности"
            },
            "/api/security/password-security": {
                "summary": "Безопасность паролей",
                "description": "Проверка и управление безопасностью паролей"
            },
            "/api/security/network-monitoring": {
                "summary": "Мониторинг сети",
                "description": "Мониторинг сетевого трафика и безопасности"
            },
            "/api/security/data-protection": {
                "summary": "Защита данных",
                "description": "Управление защитой и шифрованием данных"
            }
        }
        
        if path in descriptions:
            endpoint.update(descriptions[path])
        
        return endpoint
    
    def _generate_openapi_spec(self) -> Dict:
        """Генерация OpenAPI спецификации"""
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.config['api']['title'],
                "version": self.config['api']['version'],
                "description": self.config['api']['description']
            },
            "servers": [
                {
                    "url": self.config['api']['base_url'],
                    "description": "Production server"
                }
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
        
        # Добавление endpoints
        for endpoint in self.api_endpoints:
            path = endpoint["path"]
            method = endpoint["method"].lower()
            
            if path not in openapi_spec["paths"]:
                openapi_spec["paths"][path] = {}
            
            openapi_spec["paths"][path][method] = {
                "summary": endpoint["summary"],
                "description": endpoint["description"],
                "parameters": endpoint.get("parameters", []),
                "responses": endpoint.get("responses", {}),
                "security": [{"bearerAuth": []}]
            }
        
        return openapi_spec
    
    def generate_jwt_token(self, user: str = "developer", role: str = "developer") -> str:
        """Генерация JWT токена для тестирования"""
        payload = {
            "user": user,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=self.config['jwt']['expiration_hours'])
        }
        
        return jwt.encode(payload, self.config['jwt']['secret_key'], algorithm=self.config['jwt']['algorithm'])
    
    def start_server(self):
        """Запуск сервера документации"""
        self.logger.info(f"Запуск Interactive API Docs на порту {self.config['flask']['port']}")
        
        # Генерация тестового токена
        test_token = self.generate_jwt_token()
        self.logger.info(f"Тестовый JWT токен: {test_token}")
        
        # Запуск сервера
        uvicorn.run(
            self.app,
            host=self.config['flask']['host'],
            port=self.config['flask']['port'],
            log_level="info"
        )

def main():
    """Главная функция"""
    try:
        # Создание экземпляра документации
        api_docs = InteractiveAPIDocs()
        
        # Запуск сервера
        api_docs.start_server()
        
    except KeyboardInterrupt:
        print("\\n🛑 Остановка Interactive API Docs...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()