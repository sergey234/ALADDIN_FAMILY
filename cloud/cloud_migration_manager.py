#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Migration Manager - Менеджер миграции в облако
"""

import os
import sys
import json
import logging
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import boto3
from google.cloud import compute_v1
from google.cloud import sql_v1
import docker
import yaml

class CloudMigrationManager:
    """Менеджер миграции в облако"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.docker_client = docker.from_env()
        
        # Инициализация облачных клиентов
        self.aws_client = self._init_aws_client()
        self.gcp_client = self._init_gcp_client()
        
    def _load_config(self) -> Dict:
        """Загрузка конфигурации миграции"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")
            return {}
    
    def _setup_logging(self) -> logging.Logger:
        """Настройка логирования"""
        logger = logging.getLogger('CloudMigrationManager')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _init_aws_client(self) -> Dict:
        """Инициализация AWS клиентов"""
        try:
            # Проверка наличия AWS credentials
            if not os.path.exists(os.path.expanduser('~/.aws/credentials')):
                self.logger.warning("AWS credentials не найдены")
                return {}
            
            return {
                'ec2': boto3.client('ec2'),
                'rds': boto3.client('rds'),
                's3': boto3.client('s3'),
                'cloudformation': boto3.client('cloudformation')
            }
        except Exception as e:
            self.logger.error(f"Ошибка инициализации AWS: {e}")
            return {}
    
    def _init_gcp_client(self) -> Dict:
        """Инициализация GCP клиентов"""
        try:
            # Проверка наличия GCP credentials
            if not os.path.exists(os.path.expanduser('~/.config/gcloud/application_default_credentials.json')):
                self.logger.warning("GCP credentials не найдены")
                return {}
            
            return {
                'compute': compute_v1.InstancesClient(),
                'sql': sql_v1.CloudSqlInstancesClient(),
                'storage': None  # Будет инициализирован при необходимости
            }
        except Exception as e:
            self.logger.error(f"Ошибка инициализации GCP: {e}")
            return {}
    
    def migrate_to_aws(self) -> bool:
        """Миграция в AWS"""
        try:
            self.logger.info("Начало миграции в AWS")
            
            # 1. Создание инфраструктуры
            if not self._create_aws_infrastructure():
                return False
            
            # 2. Сборка и загрузка Docker образов
            if not self._build_and_push_images('aws'):
                return False
            
            # 3. Настройка базы данных
            if not self._setup_aws_database():
                return False
            
            # 4. Развертывание приложения
            if not self._deploy_to_aws():
                return False
            
            # 5. Проверка работоспособности
            if not self._health_check_aws():
                return False
            
            self.logger.info("Миграция в AWS успешно завершена")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка миграции в AWS: {e}")
            return False
    
    def migrate_to_gcp(self) -> bool:
        """Миграция в GCP"""
        try:
            self.logger.info("Начало миграции в GCP")
            
            # 1. Создание инфраструктуры
            if not self._create_gcp_infrastructure():
                return False
            
            # 2. Сборка и загрузка Docker образов
            if not self._build_and_push_images('gcp'):
                return False
            
            # 3. Настройка базы данных
            if not self._setup_gcp_database():
                return False
            
            # 4. Развертывание приложения
            if not self._deploy_to_gcp():
                return False
            
            # 5. Проверка работоспособности
            if not self._health_check_gcp():
                return False
            
            self.logger.info("Миграция в GCP успешно завершена")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка миграции в GCP: {e}")
            return False
    
    def _create_aws_infrastructure(self) -> bool:
        """Создание AWS инфраструктуры"""
        try:
            self.logger.info("Создание AWS инфраструктуры")
            
            # Загрузка CloudFormation шаблона
            with open('cloud/aws_infrastructure.yaml', 'r') as f:
                template_body = f.read()
            
            # Создание CloudFormation стека
            response = self.aws_client['cloudformation'].create_stack(
                StackName='ALADDIN-Security-System',
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'Environment',
                        'ParameterValue': self.config['aws']['environment']
                    },
                    {
                        'ParameterKey': 'InstanceType',
                        'ParameterValue': self.config['aws']['instance_type']
                    },
                    {
                        'ParameterKey': 'KeyPairName',
                        'ParameterValue': self.config['aws']['key_pair']
                    }
                ],
                Capabilities=['CAPABILITY_IAM']
            )
            
            # Ожидание завершения создания стека
            self._wait_for_stack_creation('ALADDIN-Security-System')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания AWS инфраструктуры: {e}")
            return False
    
    def _create_gcp_infrastructure(self) -> bool:
        """Создание GCP инфраструктуры"""
        try:
            self.logger.info("Создание GCP инфраструктуры")
            
            # Запуск Deployment Manager
            cmd = [
                'gcloud', 'deployment-manager', 'deployments', 'create',
                'aladdin-security-system',
                '--config', 'cloud/gcp_infrastructure.yaml',
                '--project', self.config['gcp']['project_id']
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Ошибка создания GCP инфраструктуры: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания GCP инфраструктуры: {e}")
            return False
    
    def _build_and_push_images(self, cloud_provider: str) -> bool:
        """Сборка и загрузка Docker образов"""
        try:
            self.logger.info(f"Сборка и загрузка образов в {cloud_provider}")
            
            # Список сервисов для сборки
            services = [
                'safe-function-manager',
                'api-gateway',
                'security-monitoring',
                'ai-agents',
                'bots'
            ]
            
            for service in services:
                # Сборка образа
                image_name = f"aladdin/{service}"
                self.logger.info(f"Сборка образа {image_name}")
                
                # Docker build
                build_result = self.docker_client.images.build(
                    path=f"security/{service}",
                    tag=image_name,
                    rm=True
                )
                
                # Загрузка в облако
                if cloud_provider == 'aws':
                    self._push_to_aws_ecr(image_name)
                elif cloud_provider == 'gcp':
                    self._push_to_gcp_gcr(image_name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сборки и загрузки образов: {e}")
            return False
    
    def _push_to_aws_ecr(self, image_name: str) -> bool:
        """Загрузка образа в AWS ECR"""
        try:
            # Получение ECR репозитория
            ecr_client = boto3.client('ecr')
            
            # Создание репозитория если не существует
            try:
                ecr_client.create_repository(repositoryName=image_name)
            except ecr_client.exceptions.RepositoryAlreadyExistsException:
                pass
            
            # Получение токена авторизации
            token_response = ecr_client.get_authorization_token()
            token = token_response['authorizationData'][0]['authorizationToken']
            endpoint = token_response['authorizationData'][0]['proxyEndpoint']
            
            # Авторизация Docker
            subprocess.run([
                'docker', 'login', '--username', 'AWS',
                '--password-stdin', endpoint
            ], input=token, text=True)
            
            # Тегирование и загрузка
            tagged_image = f"{endpoint}/{image_name}:latest"
            self.docker_client.images.get(image_name).tag(tagged_image)
            self.docker_client.images.push(tagged_image)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки в AWS ECR: {e}")
            return False
    
    def _push_to_gcp_gcr(self, image_name: str) -> bool:
        """Загрузка образа в GCP GCR"""
        try:
            # Тегирование образа для GCR
            gcr_image = f"gcr.io/{self.config['gcp']['project_id']}/{image_name}:latest"
            self.docker_client.images.get(image_name).tag(gcr_image)
            
            # Загрузка в GCR
            self.docker_client.images.push(gcr_image)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки в GCP GCR: {e}")
            return False
    
    def _setup_aws_database(self) -> bool:
        """Настройка AWS базы данных"""
        try:
            self.logger.info("Настройка AWS базы данных")
            
            # Получение информации о RDS инстансе
            response = self.aws_client['rds'].describe_db_instances(
                DBInstanceIdentifier='aladdin-database'
            )
            
            db_endpoint = response['DBInstances'][0]['Endpoint']['Address']
            
            # Настройка подключения к базе данных
            self._configure_database_connection('aws', db_endpoint)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки AWS базы данных: {e}")
            return False
    
    def _setup_gcp_database(self) -> bool:
        """Настройка GCP базы данных"""
        try:
            self.logger.info("Настройка GCP базы данных")
            
            # Получение информации о Cloud SQL инстансе
            instance_name = f"{self.config['gcp']['project_id']}/us-central1/aladdin-database"
            
            # Настройка подключения к базе данных
            self._configure_database_connection('gcp', instance_name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки GCP базы данных: {e}")
            return False
    
    def _configure_database_connection(self, cloud_provider: str, endpoint: str) -> bool:
        """Настройка подключения к базе данных"""
        try:
            # Обновление конфигурации базы данных
            db_config = {
                'host': endpoint,
                'port': 5432,
                'database': 'aladdin_security',
                'username': 'aladdin_admin',
                'password': self.config['database']['password'],
                'ssl_mode': 'require'
            }
            
            # Сохранение конфигурации
            config_file = f"config/database_{cloud_provider}.json"
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(db_config, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки подключения к базе данных: {e}")
            return False
    
    def _deploy_to_aws(self) -> bool:
        """Развертывание в AWS"""
        try:
            self.logger.info("Развертывание в AWS")
            
            # Получение IP адреса инстанса
            response = self.aws_client['cloudformation'].describe_stacks(
                StackName='ALADDIN-Security-System'
            )
            
            outputs = response['Stacks'][0]['Outputs']
            instance_ip = next(
                output['OutputValue'] 
                for output in outputs 
                if output['OutputKey'] == 'ALADDINPublicIP'
            )
            
            # Развертывание через SSH
            self._deploy_via_ssh(instance_ip, 'aws')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка развертывания в AWS: {e}")
            return False
    
    def _deploy_to_gcp(self) -> bool:
        """Развертывание в GCP"""
        try:
            self.logger.info("Развертывание в GCP")
            
            # Получение IP адреса инстанса
            cmd = [
                'gcloud', 'compute', 'instances', 'describe',
                'aladdin-instance',
                '--zone=us-central1-a',
                '--project', self.config['gcp']['project_id'],
                '--format=value(networkInterfaces[0].accessConfigs[0].natIP)'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            instance_ip = result.stdout.strip()
            
            # Развертывание через SSH
            self._deploy_via_ssh(instance_ip, 'gcp')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка развертывания в GCP: {e}")
            return False
    
    def _deploy_via_ssh(self, instance_ip: str, cloud_provider: str) -> bool:
        """Развертывание через SSH"""
        try:
            # Создание скрипта развертывания
            deploy_script = f"""
            #!/bin/bash
            set -e
            
            # Обновление системы
            sudo apt-get update
            
            # Установка Docker
            sudo apt-get install -y docker.io docker-compose
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker ubuntu
            
            # Клонирование репозитория
            git clone https://github.com/your-repo/aladdin-security.git
            cd aladdin-security
            
            # Настройка конфигурации для облака
            cp config/database_{cloud_provider}.json config/database.json
            
            # Запуск сервисов
            docker-compose up -d
            
            # Настройка мониторинга
            docker run -d --name prometheus -p 9090:9090 prom/prometheus
            docker run -d --name grafana -p 3000:3000 grafana/grafana
            
            echo "Развертывание завершено"
            """
            
            # Сохранение скрипта
            script_path = f"deployment/deploy_{cloud_provider}.sh"
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            
            with open(script_path, 'w') as f:
                f.write(deploy_script)
            
            # Выполнение через SSH
            ssh_key = self.config[cloud_provider]['ssh_key']
            
            subprocess.run([
                'scp', '-i', ssh_key,
                script_path,
                f"ubuntu@{instance_ip}:/tmp/deploy.sh"
            ])
            
            subprocess.run([
                'ssh', '-i', ssh_key,
                f"ubuntu@{instance_ip}",
                "chmod +x /tmp/deploy.sh && /tmp/deploy.sh"
            ])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка развертывания через SSH: {e}")
            return False
    
    def _health_check_aws(self) -> bool:
        """Проверка здоровья AWS развертывания"""
        try:
            # Получение IP адреса
            response = self.aws_client['cloudformation'].describe_stacks(
                StackName='ALADDIN-Security-System'
            )
            
            outputs = response['Stacks'][0]['Outputs']
            instance_ip = next(
                output['OutputValue'] 
                for output in outputs 
                if output['OutputKey'] == 'ALADDINPublicIP'
            )
            
            # Проверка доступности API
            import requests
            
            health_url = f"http://{instance_ip}:8000/health"
            response = requests.get(health_url, timeout=30)
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки здоровья AWS: {e}")
            return False
    
    def _health_check_gcp(self) -> bool:
        """Проверка здоровья GCP развертывания"""
        try:
            # Получение IP адреса
            cmd = [
                'gcloud', 'compute', 'instances', 'describe',
                'aladdin-instance',
                '--zone=us-central1-a',
                '--project', self.config['gcp']['project_id'],
                '--format=value(networkInterfaces[0].accessConfigs[0].natIP)'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            instance_ip = result.stdout.strip()
            
            # Проверка доступности API
            import requests
            
            health_url = f"http://{instance_ip}:8000/health"
            response = requests.get(health_url, timeout=30)
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки здоровья GCP: {e}")
            return False
    
    def _wait_for_stack_creation(self, stack_name: str, timeout: int = 1800) -> bool:
        """Ожидание завершения создания CloudFormation стека"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                response = self.aws_client['cloudformation'].describe_stacks(
                    StackName=stack_name
                )
                
                stack_status = response['Stacks'][0]['StackStatus']
                
                if stack_status == 'CREATE_COMPLETE':
                    return True
                elif stack_status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE']:
                    return False
                
                time.sleep(30)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка ожидания создания стека: {e}")
            return False