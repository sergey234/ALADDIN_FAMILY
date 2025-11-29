#!/bin/bash
# Скрипт для запуска payment_service

cd /opt/aladdin-backend
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

